---
title: "MSSQL 读取文件"
date: 2018-05-31T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mssql']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

MSSQL 读取文件

<!--more-->

注意反斜杠转义.

需要 SA 或 BULK INSERT 权限.

```
create table test(
	context ntext
);

BULK INSERT test FROM 'c:/pass.txt'
WITH (
   DATAFILETYPE = 'char',
   KEEPNULLS
);

select * from test;

drop table test;
```