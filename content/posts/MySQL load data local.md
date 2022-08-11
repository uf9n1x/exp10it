---
title: "MySQL load data local"
date: 2018-07-22T00:00:00+08:00
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


当 LOAD DATA INFILE 指定 LOCAL 时, 用户无需 FILE 权限, 文件将由客户端读取, 并把数据发送至服务器上.

**以当前执行命令用户的权限读取文件.**

<!--more-->

例如从 phpmyadmin 中执行语句, 用户权限就为 web 容器的权限.

```
create table `localfile` ( `content` LONGTEXT );
LOAD DATA LOCAL INFILE 'C:/WWWROOT/index.php' INTO TABLE `localfile` fields terminated by '';
select `content` from `localfile`;
```

如果显示不全或者其它奇怪的原因就在语句后面加上 `LINES TERMINATED BY '\0'`.