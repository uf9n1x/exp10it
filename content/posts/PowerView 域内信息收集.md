---
title: "PowerView 域内信息收集"
date: 2019-07-26T00:00:00+08:00
draft: false
tags: ['powershell']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

PowerView 是基于 PowerShell 的域渗透信息收集脚本, 该脚本完全通过 PowerShell, WMI 和 Win32 API 的方式实现诸如 net 等一系列命令以达到躲避检测的效果.

PowerView 脚本大体可分为 Misc Domain GPO Enum Meta Trust 六类.

限于篇幅原因, 仅对常用脚本进行说明.

<!--more-->

## Misc

**Export-PowerViewCSV**

将 PowerView 输出导出为 CSV 格式.

```
Get-DomainUser | Export-PowerViewCSV -Path C:\Windows\Temp\out.csv
```

**Resolve-IPAddress**

将主机名解析为 IP.

```
Resolve-IPAddress -ComputerName DC
```

**ConvertTo-SID**

将用户名/组名转换为 SID.

```
ConvertTo-SID TEST\Administrator
```

**Get-DomainSPNTicket**

请求指定 SPN 的 Kerberos 票据.

```
Get-DomainSPNTicket -SPN MSSQLSvc/DC.test.com
```

**Invoke-Kerberoast**

提取请求的 Kerberos 票据中的 Hash.

```
Invoke-Kerberoast | fl
```

**Get-PathACL**

返回指定文件路径的 ACL.

```
Get-PathACL .\Documents
```

## Domain

**Get-DomainDNSZone**

返回指定域的 DNS 区域.

```
Get-DomainDNSZone
```

**Get-DomainDNSRecord**

返回指定域的 DNS 记录.

```
Get-DomainDNSRecord -ZoneName test.com | Select Name
```

**Get-Domain**

返回当前域的信息.

```
Get-Domain
```

**Get-DomainController**

返回当前域的域控制器.

```
Get-DomainController
```

**Get-Forest**

返回当前域林的信息.

```
Get-Forest
```

**Get-ForestDomain**

返回域林中的所有域.

```
Get-ForestDomain
```

**Get-DomainUser**

返回当前域的所有用户.

```
Get-DomainUser | Select SAMAccountName
```

**New-DomainUser**

在当前域中新建用户.

```
$Password = ConvertTo-SecureString '123456' -AsPlainText -Force
New-DomainUser -SamAccountName test -AccountPassword $Password
```

**Set-DomainUserPassword**

更改域中用户的密码.

```
$Password = ConvertTo-SecureString '123456' -AsPlainText -Force
Set-DomainUserPassword -Identity test -AccountPassword $Password
```

**Get-DomainUserEvent**

枚举用户登录事件.

```
Get-DomainUserEvent
```

**Get-DomainComputer**

返回当前域中的所有计算机.

```
Get-DomainComputer | Select name
```

**Get-DomainSID**

返回当前域的 SID.

```
Get-DomainSID
```

**Get-DomainGroup**

返回当前域的所有组. 实际测试中只能查看域内管理员组, 本地无法查看, 以下同.

```
Get-DomainGroup | Select SAMAccountName
```

**New-DomainGroup**

在当前域中新建组.

```
New-DomainGroup -SamAccountName TestGroup
```

**Get-DomainGroupMember**

返回指定域组的成员.

```
Get-DomainGroupMember "Domain Admins"
```

**Add-DomainGroupMember**

将域用户添加到指定域组.

```
Add-DomainGroupMember -Identity "Domain Admins" -Members "Administrator"
```

## GPO

**Get-DomainGPO**

返回域内所有组策略.

```
Get-DomainGPO | Select DisplayName
```

**Get-DomainPolicy**

返回当前域使用的组策略.

```
Get-DomainPolicy
```

## Enum

**Get-NetLocalGroup**

返回计算机上的所有本地组.

```
Get-NetLocalGroup
```

**Get-NetLocalGroupMember**

返回计算机上指定本地组的所有成员.

```
Get-NetLocalGroupMember -GroupName Administrators
```

**Get-NetShare**

返回计算机上的开放共享.

```
Get-NetShare
```

**Get-NetLoggedOn**

返回计算机上已登录的用户.

```
Get-NetLoggedOn
```

**Get-NetSession**

返回计算机上的会话信息.

```
Get-NetSession
```

**Get-WMIRegProxy**

返回当前用户的代理信息.

```
Get-WMIRegProxy
```

**Get-WMIRegLastLoggedOn**

返回登录计算机的最后一个用户.

```
Get-WMIRegLastLoggedOn
```

**Get-WMIRegCachedRDPConnection**

返回计算机上缓存的 RDP 连接信息.

```
Get-WMIRegCachedRDPConnection
```

**Get-WMIRegMountedDrive**

返回计算机上映射的网络驱动器.

```
Get-WMIRegMountedDrive
```

**Get-WMIProcess**

返回计算机上正在运行的进程.

```
Get-WMIProcess
```

**Find-InterestingFile**

搜索计算机上的敏感文件.

```
Find-InterestingFile
```

## Meta

Meta 个人感觉翻译为 "对全体域内计算机进行操作的脚本" 更为合适, 当然, 需要域管权限.

**Find-DomainUserLocation**

查找特定用户登录的计算机.

```
Find-DomainUserLocation -UserIdentity test
```

**Find-DomainProcess**

查找运行特定进程的计算机.

```
Find-DomainProcess -ProcessName powershell.exe
```

**Find-DomainUserEvent**

查找特定用户的登录事件.

```
Find-DomainUserEvent -UserIdentity test
```

**Find-DomainShare**

查找域内开放的共享.

```
Find-DomainShare
```

**Find-DomainLocalGroupMember**

枚举域内计算机上指定本地组的成员.

```
Find-DomainLocalGroupMember -ComputerName TEST -GroupName Administrators
```

## Trust

**Get-DomainTrust**

返回当前域的所有域信任.

```
Get-DomainTrust
```

**Get-ForestTrust**

返回当前林的所有林信任

```
Get-ForestTrust
```

**Get-DomainTrustMapping**

枚举当前域的所有域信任, 然后枚举它找到的每个域的所有信任.

```
Get-DomainTrustMapping
```

## 注意

格式不止以上几种, 凭借其强大的管道, 可任意组合命令.