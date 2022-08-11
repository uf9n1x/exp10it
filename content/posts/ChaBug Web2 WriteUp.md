---
title: "ChaBug Web2 WriteUp"
date: 2018-05-16T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

题目主要为 PHP 伪随机数种子爆破.

<!--more-->

*详情请看 白帽子讲 Web 安全 伪随机数安全*

index header 有 seed 范围, login csrf_token base64 decode 后就能看到随机数.

writeup

[web2-writeup.docx](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/16/1526477653.docx)

源码

[web2.zip](http://exp10it-1252109039.cossh.myqcloud.com/2018/05/16/1526477655.zip)
