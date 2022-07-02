---
title: "SQLmap udf dll 解码"
date: 2018-06-07T00:00:00+08:00
draft: false
tags: ['sqli','mysql']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

SQLmap udf dll 解码

<!--more-->

文件.

`udf/mysql/windows/32/lib_mysqludf_sys.dll_`

用 extra/cloak 下的 cloak.py 解码.

`cloak.py -d -i lib_mysqludf_sys.dll_`

mysql 导入执行.

`select sys_eval('whoami');`