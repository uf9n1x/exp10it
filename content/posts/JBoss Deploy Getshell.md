---
title: "JBoss Deploy Getshell"
date: 2018-04-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['jboss']
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


JBoss Deploy Getshell

<!--more-->

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/06/1522981732.jpg)

访问 `/jmx-console/`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/05/1522920435.jpg)

找到  `jboss.system`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/05/1522920436.jpg)

点击 `service=MainDeployer`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/05/1522920438.jpg)

找到 `void deploy()`

将 xx.jsp 打包成 xx.war

ParamValue 填入 war 的 url

最后点击 `Invoke`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/05/1522920439.jpg)

访问 /test/xx.jsp

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/05/1522920440.jpg)