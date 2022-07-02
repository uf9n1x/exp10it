---
title: "Windows 绕过 AppLocker 限制"
date: 2019-07-12T00:00:00+08:00
draft: false
tags: ['applocker','windows']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

applocker 即 "应用程序控制策略", 顾名思义, 该策略对计算机上的应用程序具有严格的限制.

具体来说, applocker 限制你能运行哪些软件, 哪些脚本, 在哪运行, 能安装哪些软件, 什么厂商的软件, 等等.

<!--more-->

在渗透测试中, 目标主机可能配置了 applocker 以禁止例如第三方 exe, vbs ps1 脚本的运行, 不过就现在看来却是个很鸡肋的功能.

applocker 的默认策略允许 `C:\Program Files (x86)\`, `C:\Program Files\`, `C:\Windows\` 中可执行文件和脚本的运行, 同时允许带数字签名或在 `C:\Windows\Installer\` 中 msi 程序的运行.
 
即使 applocker 限制了可执行文件的路径, 但我们可以利用 windows 自带的程序间接的运行指定的 payload.

以下程序(包括但不限于)可间接执行 payload 绕过 applocker.

```
mshta
msbuild
msiexec
rundll32
regasm
regsvcs
regsvr32
installutil
```

演示略.