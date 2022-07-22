---
title: "ctfshow Web入门[爆破] WriteUp"
date: 2022-07-22T14:00:43+08:00
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

爆破类, 有个 PHP 伪随机数漏洞的知识点

涉及 burp Intruder 的使用

<!--more-->

# web21

题目给了一份字典

![20220721230034](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230034.png)

401 授权

![20220721230136](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230136.png)

`Authorization: Basic YWRtaW46YWRtaW4=`

base64 加密, 后面的内容解码后为 `admin:admin`

401 登录一般的格式就是 `username:password`

这里使用 burp 的 custom iterator, 用来自定义 payload 格式

position 1 填 admin

![20220721230338](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230338.png)

position 2 填 :

![20220721230353](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230353.png)

position 3 导入之前下载的字典

![20220721230444](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230444.png)

设置好 base64 encode

![20220721230501](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230501.png)

取消勾选, 不然 `=` 会被 url encode

![20220721230527](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230527.png)

得到 flag

![20220721230548](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721230548.png)

# web22

看起来应该是爆破子域名, 得到 `flag.ctf.show`

不过域名失效了, 就直接填 flag 了

# web23

![20220721231345](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721231345.png)

明显的碰撞 md5

循环单个 a-z 0-9 字符试了发现不行

循环两个字符试出来这些

```
kv
k0
ll
mw
1m
3j
```

挨个挨个试发现 3j 可以

附上脚本

```
import hashlib

dicts = 'qwertyuiopasdfghjklzxcvbnm1234567890'

for a in dicts:
    for b in dicts:
        s = a+b
        m = hashlib.md5(s)
        mm = m.hexdigest()
        if mm[1] == mm[14] and mm[14] == mm[17]:
            print(s)
```

# web24

![20220721233031](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220721233031.png)

这里有个 `mt_srand(372619038)`, 猜测为 PHP 伪随机数漏洞

简单来说只要种子已知且为定值, 使用 `mt_srand()` 播种后, 无论什么情况下, 每次用 `mt_rand()` 产生的随机数, 都是一样的

比如在本机使用 `123` 这个种子, `mt_rand()` 执行三次产生三个随机数 a b c

而服务器也使用了 `123` 这个种子, 这时候用 `mt_rand()` 生成的三个随机数和 a b c 是一模一样的

也就是说, PHP 的伪随机数漏洞具有可预测性

本机运行 PHP 代码

```
<?php

mt_srand(372619038);
echo mt_rand();

?>
```

显示 999695185, 传参后却显示空白

网上搜了一下好像是 PHP 版本的原因, PHP 5 和 PHP 7 生成的随机数会不一样

更换版本后显示 1155388967, 传参后得到 flag

# web25

![20220722112625](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722112625.png)

md5 flag 截取前8位然后转10进制作为种子`

`http://bae73641-ed2c-4237-af90-0e68675b4648.challenge.ctf.show/?r=1` -55428564

`http://bae73641-ed2c-4237-af90-0e68675b4648.challenge.ctf.show/?r=2` -55428563

`http://bae73641-ed2c-4237-af90-0e68675b4648.challenge.ctf.show/?r=3` -55428562

`r=0` 是 -55428564

也就是说第一次 `mt_rand()` 的结果是 55428564

前面一题可以通过种子来预测伪随机数, 这里当然也可以利用伪随机数来猜测种子

自己写了个 PHP 脚本死活跑不出来...

网上搜到个很厉害的脚本 [https://www.openwall.com/php_mt_seed/](https://www.openwall.com/php_mt_seed/)

![20220722115858](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722115858.png)

293358836

PHP 本机执行

```
<?php

mt_srand(293358836);
mt_rand();

echo mt_rand()+mt_rand();

?>
```

得到 token 后改 cookie 后访问 `http://bae73641-ed2c-4237-af90-0e68675b4648.challenge.ctf.show/?r=55428565` 得到 flag

# web26

安装界面

![20220722120528](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722120528.png)

右键查看源码

![20220722120552](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722120552.png)

checkdb.php

burp 爆破 top3000 字典

![20220722120923](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722120923.png)

得到 flag

# web27

![20220722121340](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722121340.png)

查看录取名单

![20220722124545](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722124545.png)

观察一下发现身份证加星号的是出生日期

主页登录需要学号

有一个录取信息查询的界面

![20220722124701](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722124701.png)

估计应该能查到学号

burp 对日期进行爆破, 但不知道具体范围是啥, 看到底部 1999-2017, 2017年的新生应该是 1999 左右的, 但看了 hint 之后发现字典是从 1990-1992, 无语了...

![20220722130530](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722130530.png)

查询

![20220722132635](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722132635.png)

主页登录有点问题, 右键可以看到 ajax 提交的地址

构造数据包登录

![20220722132923](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220722132923.png)


# web28

`http://37200ed3-546f-4f5b-bc08-49dcbfd8c18d.challenge.ctf.show/0/1/2.txt`

去掉 2.txt

爆破后是 `/72/20`