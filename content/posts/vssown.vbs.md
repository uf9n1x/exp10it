---
title: "vssown.vbs"
date: 2018-04-07T00:00:00+08:00
draft: false
tags: ["vbs",'windows']
categories: ["内网渗透"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

vshadow 是一个简单的指令行工具, 它允许任何人创建卷影拷贝. 用户可以在最新版本的 VSS SDK 中找到这个工具.

<!--more-->

[vssown.vbs](https://raw.githubusercontent.com/l3m0n/pentest_study/master/tools/vssown.vbs)

相当于对指定的卷映射一份拷贝

看操作就明白了

开始映射

`cscript //nologo vssown.vbs /start`
`cscript //nologo vssown.vbs /create C`
`cscript //nologo vssown.vbs /list`

![20220701152310](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701152310.png)

其中的 Device Object 为 C 盘的映射

复制 SAM

![1522982735](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/1522982735.jpg)

停止映射

`cscript //nologo vssown.vbs /delete *`
`cscript //nologo vssown.vbs /stop`

![1522982736](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/1522982736.jpg)

gethashes 读取 SAM 文件

![1522982738](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/1522982738.jpg)

获取 域中的 ndts.dit 也是同样的方法