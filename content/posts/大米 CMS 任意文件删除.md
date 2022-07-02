---
title: "大米 CMS 任意文件删除"
date: 2018-04-02T00:00:00+08:00
draft: false
tags: ['cms','php']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

鸡肋漏洞 需要登录后台

<!--more-->

Admin/Lib/Action/TplAction.class.php

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/01/1522580912.png)

没有任何过滤将 id 的内容 unlink

调用了 `str_replace` 和 `dami_url_replace`

前者将 * 替换为 .

`dami_url_replace` 定义处

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/01/1522580913.png)

将 | 替换为 / @ 替换为 = # 替换为 &

后台 - 模板管理 - 删除 抓包

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/01/1522580915.png)

删除锁定文件

重装

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/04/01/1522580916.png)