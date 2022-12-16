---
title: "HTTP 头伪造 IP"
date: 2018-03-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['http header']
categories: ['Web安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

http 头 伪造 IP.

<!--more-->

```
Client-IP: 127.0.0.1
X-Client-IP: 127.0.0.1
X-Real-IP: 127.0.0.1
True-Client-IP: 127.0.0.1
X-Originating-IP: 127.0.0.1
X-Forwarded-For: 127.0.0.1
X-Remote-IP: 127.0.0.1
X-Remote-Addr: 127.0.0.1
X-Forwarded-Host: 127.0.0.1
```