---
title: "PHP 常用伪协议"
date: 2018-02-13T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php']
categories: ['编程']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

php://stdin php://stdout php://sterr php://input php://output php://filter

<!--more-->

## php://stdin

从控制台读取输入

```
<?php
$f = fopen('php://stdin','r');
while(!feof($f)){
	echo 'output:'.fgets($f);
}
?>
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518416933.jpg)

## php://stdout

输出 类似于 echo

```
<?php
$f = fopen('php://stdout','w');
fwrite($f,'test');
fclose($f);
?>
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417021.jpg)

## php://stderr

和 php://stdout 一样

## php://input

读取 POST 数据 作为 php 代码执行

```
<?php
echo file_get_contents('php://input');
?>
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417157.jpg)

## php://output

输出

```
<?php
$f = fopen('php://output','w');
fwrite($f,'test');
fclose($f)
?>
```

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417229.jpg)

## php://filter

php 元封装器 类似于 `readfile() file_get_contents()`

读取文件内容

这个在 ctf 中用的比较多

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417286.jpg)

常用过滤器

```
string.rot13
string.toupper
string.tolower
string.strip_tags

convert.base64-encode
convert.base64-decode

convert.quoted-printable-encode
convert.quoted-printable-decode
```

代码

```
<?php
echo file_get_contents($_GET['file']);
?>
```

base64 encode

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417373.jpg)

tolower

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/12/1518417564.jpg)