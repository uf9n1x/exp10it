---
title: "绕过 PowerShell 的执行策略"
date: 2018-05-04T00:00:00+08:00
draft: false
tags: ['powershell','bypass']
categories: ['bypass']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

PowerShell Execution Policy 是用来决定哪些类型的 PowerShell 代码可以在系统中运行.

```
Restricted - 不允许任何脚本运行.
AllSigned - 只能允许经过数字签名的脚本.
RemoteSigned - 运行本地脚本不需要数字签名 远程的需要.
Unrestricted - 允许任何脚本运行.
```

<!--more-->

查看当前的策略

```
Get-ExecutionPolicy
```

## Bypass

将 ExecutionPolicy 设置为 Bypass.

```
powershell.exe -ExecutionPolicy Bypass -File .\test.ps1
```

## UnRestricted

将 ExecutionPolicy 设置为 UnRestricted.

```
powershell.exe -ExecutionPolicy UnRestricted -File .\test.ps1
```

## RemoteSigned

将 ExecutionPolicy 设置为 RemoteSigned.

```
powershell.exe -ExecutionPolicy RemoteSigned -File .\test.ps1
```

## Pipe

通过管道执行脚本.

```
PGet-Content .\test.ps1 | powershell.exe -
```

类似的还有 type 命令.

```
type .\test.ps1 | powershell.exe -
```

## IEX

通过 IEX 远程下载脚本执行.

```
powershell.exe "IEX (New-Object Net.WebClient).DownloadString('http://localhost/test.ps1')"
```

## Encode

unicode + base64 编码执行.

```
$command = Get-Content .\test.ps1
$bytes = [System.Text.Encoding]::Unicode.GetBytes($command)
$encodedCommand = [Convert]::ToBase64String($bytes)
powershell.exe -EncodedCommand $encodedCommand
```

## Command

好像会有引号的转义问题, 更改了下执行的脚本.

```
echo "echo 'hello world'" > .\test.ps1
$command = Get-Content .\test.ps1
powershell -command "$command"
```

## Invoke-Expression (IEX)

Invoke-Expression 将它接受到的任何字符串当作 powershell 代码执行.

```
Get-Content .\test.ps1 | Invoke-Expression
```