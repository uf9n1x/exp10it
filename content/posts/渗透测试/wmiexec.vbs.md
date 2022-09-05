---
title: "wmiexec.vbs"
date: 2018-04-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ["vbs",'windows']
categories: ["内网渗透"]

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


WMI 是一项核心的 Windows 管理技术, 用户可以使用 WMI 管理本地和远程计算机.

<!--more-->

[wmiexec.vbs](https://raw.githubusercontent.com/l3m0n/pentest_study/master/tools/wmiexec.vbs)

t00ls 大牛的作品 替代 psexec

通过 wmiexec 可以获取到一个半交互式 shell

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/06/1522981729.jpg)

获取 shell

`cscript //nologo wmiexec.vbs /shell 127.0.0.1 user pass`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/06/1522981730.jpg)

执行 cmd 命令

`cscript //nologo wmiexec.vbs /cmd 127.0.0.1 user pass cmd`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/06/1522981731.jpg)

persist 后台运行 对于 nc lcx 等程序非常有用

`ping www.baidu.com -persist`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/06/1522981732.jpg)