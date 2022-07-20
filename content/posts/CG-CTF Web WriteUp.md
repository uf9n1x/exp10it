---
title: "CG CTF Web WriteUp"
date: 2022-07-20T13:12:17+08:00
draft: false
tags: ['php','ctf','sqli']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

好久没打 ctf 了

南邮的 CG-CTF, 不过有一点老

Web 题除了访问不了的都做完了, 一些过程比较长的题会单独拎出来一篇文章, 个别访问不了和暂时无法做的题我就不写了

<!--more-->


## 签到题

右键源代码

## md5 collision

```
$md51 = md5('QNKCDZO');
$a = @$_GET['a'];
$md52 = @md5($a);
if(isset($a)){
if ($a != 'QNKCDZO' && $md51 == $md52) {
    echo "nctf{*****************}";
} else {
    echo "false!!!";
}}
else{echo "please input a";}
```

涉及到 PHP 的弱类型漏洞

简单来说 PHP 使用 `==` 进行比较时, 会先将左右两个变量转换成相同的数据类型, 然后再进行比较

```
'a' == 0 // true

'1a' == 0 // false
'1a' == 1 // true

'a1' == 0 // true
'a1' == 1 // false

'0e123' == '0e456'
```

PHP 会将 `1a` 转换成 `1` (因为开头是数字, 后面的字符串直接被截断了)

而 `a1` 这种, 因为开头是字符串, 会自动转换成 `0`

至于 `0exxx` 这是因为其中含有 `e`, 相当于科学技术法, 比如 `1e3` 就是 `1x10^3`, 而 `0` 乘以任何数都是 `0`, 所以 `'0e123' ==  '0e456'` 显示 true

这里 `QNKCDZO` 的 md5 值是 `0e830400451993494058024219903391`

我们只需要找到另一个数据, md5 加密之后也是以 `0e` 开头的就行了

```
QNKCDZO
0e830400451993494058024219903391
240610708
0e462097431906509019562988736854
s878926199a
0e545993274517709034328855841020
s155964671a
0e342768416822451524974117254469
s214587387a
0e848240448830537924465865611904
s214587387a
0e848240448830537924465865611904
s878926199a
0e545993274517709034328855841020
s1091221200a
0e940624217856561557816327384675
s1885207154a
0e509367213418206700842008763514
s1502113478a
0e861580163291561247404381396064
s1885207154a
0e509367213418206700842008763514
s1836677006a
0e481036490867661113260034900752
s155964671a
0e342768416822451524974117254469
s1184209335a
0e072485820392773389523109082030
s1665632922a
0e731198061491163073197128363787
s1502113478a
0e861580163291561247404381396064
s1836677006a
0e481036490867661113260034900752
s1091221200a
0e940624217856561557816327384675
s155964671a
0e342768416822451524974117254469
s1502113478a
0e861580163291561247404381396064
s155964671a
0e342768416822451524974117254469
s1665632922a
0e731198061491163073197128363787
s155964671a
0e342768416822451524974117254469
s1091221200a
0e940624217856561557816327384675
s1836677006a
0e481036490867661113260034900752
s1885207154a
0e509367213418206700842008763514
s532378020a
0e220463095855511507588041205815
s878926199a
0e545993274517709034328855841020
s1091221200a
0e940624217856561557816327384675
s214587387a
0e848240448830537924465865611904
s1502113478a
0e861580163291561247404381396064
s1091221200a
0e940624217856561557816327384675
s1665632922a
0e731198061491163073197128363787
s1885207154a
0e509367213418206700842008763514
s1836677006a
0e481036490867661113260034900752
s1665632922a
0e731198061491163073197128363787
s878926199a
0e545993274517709034328855841020
```

传参后得到 flag

## 签到2

```
<p>输入框：<input type="password" value="" name="text1" maxlength="10"><br>
```

前端限制 maxlength, 审查元素改一下就行

## 这题不是Web

相当于隐写

图片下载到本地后用 hexeditor 打开拉到末尾会有 flag

## 层层递进

这题感觉出的有点怪....

右键查看源代码会发现一个 `SO.html`, 点进去再看会有个 `S0.html`, 然后是 `SO.htm` `S0.htm`

最后出现 `404.html`

flag 写在注释里面, 一开始还没发现...

![20220720140839](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720140839.png)

## AAencode

这题访问不了, 但就是简单的颜文字加解密, 网上找一下文件然后解出来 flag 就行

## 单身二十年

js `windows.location` 跳转, 浏览器 `view-source` 直接绕过

## php decode

```
<?php
function CLsI($ZzvSWE) {
 
    $ZzvSWE = gzinflate(base64_decode($ZzvSWE));
 
    for ($i = 0; $i < strlen($ZzvSWE); $i++) {
 
        $ZzvSWE[$i] = chr(ord($ZzvSWE[$i]) - 1);
 
    }
 
    return $ZzvSWE;
 
}
eval(CLsI("+7DnQGFmYVZ+eoGmlg0fd3puUoZ1fkppek1GdVZhQnJSSZq5aUImGNQBAA=="));
?>
```

这题感觉也很怪, eval 改成 echo 就出来 flag 了

## 文件包含

`http://4.chinalover.sinaapp.com/web7/index.php?file=show.php`

文件包含, 但因为是 PHP 文件, 在服务端执行, 所以浏览器看不到源码

可以使用 PHP 的伪协议 `php://filter` 配合 base64 读取源代码

`http://4.chinalover.sinaapp.com/web7/index.php?file=php://filter/read=convert.base64-encode/resource=index.php`

show.php 内容太少了, flag 是在 index.php 里面, 之后 base64 解码就行

## 单身一百年也没用

302 跳转, `view-source` 绕过不了

可以用 F12 开发者工具里的 `网络`

![20220720141555](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720141555.png)

## COOKIE

cookie 中的 Login 改成1

![20220720141638](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720141638.png)

## MYSQL

查看 robots.txt

```
TIP:sql.php

<?php
if($_GET[id]) {
   mysql_connect(SAE_MYSQL_HOST_M . ':' . SAE_MYSQL_PORT,SAE_MYSQL_USER,SAE_MYSQL_PASS);
  mysql_select_db(SAE_MYSQL_DB);
  $id = intval($_GET[id]);
  $query = @mysql_fetch_array(mysql_query("select content from ctf2 where id='$id'"));
  if ($_GET[id]==1024) {
      echo "<p>no! try again</p>";
  }
  else{
    echo($query[content]);
  }
}
?>
```

涉及到 `intval()` 函数

刚开始以为就是强制转换成 int 类型的, 但仔细看发现是 "获取变量的整数值"

![20220720141944](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720141944.png)

这里 if 判断的时候用的是 `$_GET[id]` 而不是 `$id`, 很明显是让我们找到一个 `intval()` 之后等于 1024 但本身不是 1024 的数据

将 1024 转换成八进制和十六进制都不行, 因为弱类型转换之后还是以 1024 进行比较, 绕不过 `==`

但上面强调了是 "取整", 因此可以使用 1024.123 这种带小数点的数值进去

带入之后得到 flag

## GBK Injection

宽字节注入

![20220720142345](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720142345.png)

`'` `"` 和 `\` 都会被转义, 可以找到一个数据, 让他和后面被转义之后的 `\'` 中的 `\` 连在一起构成一个宽字符, 从而 "吃掉" 反斜杠, 让引号单独露出来

网上使用的是 `%bf%27`

![20220720142727](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720142727.png)

但我这里试了一下, 使用 `啊'` 也是可以的

![20220720142857](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720142857.png)

之后就是正常的注入流程

## /x00

```
<?php
if (isset ($_GET['nctf'])) {
    if (@ereg ("^[1-9]+$", $_GET['nctf']) === FALSE)
        echo '必须输入数字才行';
    else if (strpos ($_GET['nctf'], '#biubiubiu') !== FALSE)   
        die('Flag: '.$flag);
    else
        echo '骚年，继续努力吧啊~';
    }
?>
```

PHP 中的正则匹配会有00截断漏洞, 就是说程序遇到00之后就会终止, 不会再往下匹配

但 strpos 没有这个问题

`http://teamxlc.sinaapp.com/web4/f5a14f5e6e3453b78cd73899bad98d53/index.php?nctf=123%00%23biubiubiu`

或者使用数组

`http://teamxlc.sinaapp.com/web4/f5a14f5e6e3453b78cd73899bad98d53/index.php?nctf[]=%23biubiubiu`

## bypass again

```
<?php
if (isset($_GET['a']) and isset($_GET['b'])) {
if ($_GET['a'] != $_GET['b'])
if (md5($_GET['a']) == md5($_GET['b']))
die('Flag: '.$flag);
else
print 'Wrong.';
}
?>
```

还是弱类型, 用上面的 `0e` md5 即可

## 变量覆盖

```
<?php
extract($_POST);
if ($pass == $thepassword_123) { ?>
    <div class="alert alert-success">
    <code><?php echo $theflag; ?></code>
    </div>
<?php } ?>
<?php } ?>
```

注意这里的 `extract()` 函数

![20220720143546](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720143546.png)

POST 构造数据覆盖掉原来的 `$pass` 和 `$thepassword_123`

`pass=123&thepassword_123=123`

## 伪装者

![20220720143718](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720143718.png)

显然是 Header 头伪造 IP

```
Client-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
X-Real-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Forwarded-For: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Forwarded-Host: 127.0.0.1
```

## 上传绕过

![20220720150417](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720150417.png)

提示要上传 PHP, 对文件名进行了验证

![20220720150437](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720150437.png)

源代码中有 upload path

filename 00 截断不行, 但 upload path 截断可以

![20220720150633](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720150633.png)

## SQL注入1

```
<html>
<head>
Secure Web Login
</head>
<body>
<?php
if($_POST[user] && $_POST[pass]) {
    mysql_connect(SAE_MYSQL_HOST_M . ':' . SAE_MYSQL_PORT,SAE_MYSQL_USER,SAE_MYSQL_PASS);
  mysql_select_db(SAE_MYSQL_DB);
  $user = trim($_POST[user]);
  $pass = md5(trim($_POST[pass]));
  $sql="select user from ctf where (user='".$user."') and (pw='".$pass."')";
    echo '</br>'.$sql;
  $query = mysql_fetch_array(mysql_query($sql));
  if($query[user]=="admin") {
      echo "<p>Logged in! flag:******************** </p>";
  }
  if($query[user] != "admin") {
    echo("<p>You are not admin!</p>");
  }
}
echo $query[user];
?>
<form method=post action=index.php>
<input type=text name=user value="Username">
<input type=password name=pass value="Password">
<input type=submit>
</form>
</body>
<a href="index.phps">Source</a>
</html>
```

user 可以注入, 直接把后面的 pw 注释掉, 注意闭合 `')`, 密码随便填

`admin')#`

## pass check

```
$pass=@$_POST['pass'];
$pass1=***********;//被隐藏起来的密码
if(isset($pass))
{
if(@!strcmp($pass,$pass1)){
echo "flag:nctf{*}";
}else{
echo "the pass is wrong!";
}
}else{
echo "please input pass!";
}
?>
```

注意 `strcmp()` 函数

![20220720151933](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720151933.png)

这里 if 中加了 `!`, 即我们要使 `strcmp($pass,$pass1)` 的结果是 0, 才能显示出 flag

`strcmp()` 在 PHP 的一些版本中存在这数组绕过漏洞, 因为函数比较的是字符串, 如果我们给参数传递一个数组进去, 就会爆 Warning 同时返回 0

POST 传递

`pass[]=1`

`[]` 表示传递数组, PHP 的特性, 其他语言不太清楚能不能这样写

## 起名字真难

```
<?php
function noother_says_correct($number)
{
       $one = ord('1');
       $nine = ord('9');
       for ($i = 0; $i < strlen($number); $i++)
       {   
               $digit = ord($number{$i});
               if ( ($digit >= $one) && ($digit <= $nine) )
               {
                       return false;
               }
       }
          return $number == '54975581388';
}
$flag='*******';
if(noother_says_correct($_GET['key']))
   echo $flag;
else 
   echo 'access denied';
?>
```

这里面的意思是遍历 key 字符串中的每一个字符, 如果发现其中含有 0-9 的数字就会返回 False

但最后有一句 `return $number == '54975581388';`, 所以我们必须传入 `54975581388` 值

很熟悉了, PHP 的弱类型转换, 试了一下转成十六进制发现刚好都是字母, 记得前面加上 `0x`

`0xccccccccc`

## 密码重置

当时看到这题心里一惊, 在想是不是跟自己之前出过的重置密码 伪随机数相关的题目差不多 (已经有点忘了...), 后来发现就是个简单的改重置密码 url 的题目

点击题目地址, 默认 url 后面跟了 user1 参数

`http://nctf.nuptzj.cn/web13/index.php?user1=Y3RmdXNlcg==`

base64 解码是 `ctfuser`, 改成 `admin` 再编码回去, 接着 POST 数据修改 user 也为 `admin`, 输入验证码提交即可

![20220720153106](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720153106.png)

## SQL Injection

```

<!--
#GOAL: login as admin,then get the flag;
error_reporting(0);
require 'db.inc.php';

function clean($str){
	if(get_magic_quotes_gpc()){
		$str=stripslashes($str);
	}
	return htmlentities($str, ENT_QUOTES);
}

$username = @clean((string)$_GET['username']);
$password = @clean((string)$_GET['password']);

$query='SELECT * FROM users WHERE name=\''.$username.'\' AND pass=\''.$password.'\';';
$result=mysql_query($query);
if(!$result || mysql_num_rows($result) < 1){
	die('Invalid password!');
}

echo $flag;
-->
```

使用了 `htmlentities()` 进行实体化, 就是说 `'` `"` 这些会被转义成 html 的实体符号, 但是反斜杠 `\` 不受影响

username 和 password 配合一下

`http://chinalover.sinaapp.com/web15/index.php?username=admin\&password=%20or%201=1%20%23`

sql 语句如下

`SELECT * FROM users WHERE name='admin\' AND pass=' or 1=1 #';`

可以看到 admin 后面的 `\' AND pass='` 都变成字符串了, 然后 pass 后面的引号又自动闭合, 最后跟上 `or 1=1 #` 使结果为 true, 并且注释掉后面的引号

## 综合题

这题其实不是很综合...

![20220720153806](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720153806.png)

jsfuck 直接在控制台执行

![20220720153843](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720153843.png)

访问对应文件

![20220720153923](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720153923.png)

history of bash, 就是 bash 的历史纪录 `.bash_history`

![20220720153953](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720153953.png)

下载 flagbak.zip, 解压后打开 flag.txt 查看 flag

## SQL注入2

这题也很有意思

```
<html>
<head>
Secure Web Login II
</head>
<body>

<?php
if($_POST[user] && $_POST[pass]) {
   mysql_connect(SAE_MYSQL_HOST_M . ':' . SAE_MYSQL_PORT,SAE_MYSQL_USER,SAE_MYSQL_PASS);
  mysql_select_db(SAE_MYSQL_DB);
  $user = $_POST[user];
  $pass = md5($_POST[pass]);
  $query = @mysql_fetch_array(mysql_query("select pw from ctf where user='$user'"));
  if (($query[pw]) && (!strcasecmp($pass, $query[pw]))) {
      echo "<p>Logged in! Key: ntcf{**************} </p>";
  }
  else {
    echo("<p>Log in failure!</p>");
  }
}
?>


<form method=post action=index.php>
<input type=text name=user value="Username">
<input type=password name=pass value="Password">
<input type=submit>
</form>
</body>
<a href="index.phps">Source</a>
</html>
```

这题只有 user 是注入点, 而且数据库只查询了 user, pw 是查询的结果

输出 flag 的条件是: 存在 pw 记录并且记录跟 POST 传入的 md5 加密后的 pass 相等

存在时间盲注, 但比较费时间...

![20220720154707](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720154707.png)

tips 说是 union 查询, 想了想可以通过 union 构造一条"虚假"的数据传递到 `$query['pw]` 里

POST 提交

`user='union select md5(1)#&pass=1`

注意 url 编码, 以及我们要把 union 前面的数据设置为空, 这样才能保证输出的结果都是 union 后面的结果

这里的 `select md5(1)` 返回的结果就相当于 `select pw` 了, 列名是对应的

![20220720155033](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720155033.png)

## 综合题2

这题比较长, 单独拎出来写

## 密码重置2

tips 提示已经很明显了

右键查看源代码得到管理员邮箱为 `admin@nuptzj.cn`

vi vim 异常退出的备份文件名为 `.filename.swp`

![20220720155255](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720155255.png)

```
if(strlen($token)!=10) die('fail');
if($token!='0') die('fail');
```

直接输入 `0000000000`

因为 PHP 弱类型的问题, 在使用 `==` 进行比较时, `0` `'0'` 和 `'0000000000'` 是"相同"的

## file_get_contents

```
<!--$file = $_GET['file'];
if(@file_get_contents($file) == "meizijiu"){
    echo $nctf;
}-->
```

GET 传参, 还要读取文件, 用 PHP 伪协议

`php://input` 可以将 POST 中的内容作为 PHP 代码来执行

![20220720160134](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220720160134.png)

## 变量覆盖 (另一道)

```
<!--foreach($_GET as $key => $value){  
        $$key = $value;  
}  
if($name == "meizijiu233"){
    echo $flag;
}-->
```

`http://chinalover.sinaapp.com/web24/?name=meizijiu233`