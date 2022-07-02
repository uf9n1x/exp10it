---
title: "dirtyc0w linux 提权"
date: 2018-01-21T00:00:00+08:00
draft: false
tags: ['linux']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Linux 内核的内存子系统在处理写时拷贝 (Copy-on-Write) 时存在条件竞争漏洞, 导致可以破坏私有只读内存映射.

影响范围 Linux kernel >= 2.6.22

基本上2007年到2016年的版本都有这个漏洞

<!--more-->

[FireFart/dirtyc0w](https://github.com/FireFart/dirtycow)

内核版本

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/26/1516963898.jpg)

编译

`gcc -pthread dirty.c -o dirty -lcrypt`

运行

`./dirty yourpassword`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/26/1516964034.jpg)

切换到 firefart 用户

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/26/1516964048.jpg)

uid = 0 root 权限

如果是在反弹的 shell 里执行 直接连接 ssh

别忘了恢复原来的 passwd 文件