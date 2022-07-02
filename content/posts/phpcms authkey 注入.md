---
title: "phpcms authkey 注入"
date: 2018-02-04T00:00:00+08:00
draft: false
tags: ['cms']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

phpcms 在安装时, 由于在同一个页面中连续使用 mt_rand(), 未进行有效 mt_srand() 种子随机化操作, 导致 authkey 存在泄漏风险.

<!--more-->

访问获取 authkey

`/phpsso_server/index.php?m=phpsso&c=index&a=getapplist&auth_data=v=1&appid=1&data=662dCAZSAwgFUlUJBAxbVQJXVghTWVQHVFME`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517544257.jpg)

在 exp 中更改 url 与 authkey

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517544268.jpg)

运行

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517544284.jpg)

原来是直接 echo 出来的

序列化后不方便看 我就直接反序列化再 print_r 输出了

更改 uid 可以爆出不同的账户信息

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517544406.jpg)

exp

[phpv9 authkey.zip](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/02/1517544420.zip)