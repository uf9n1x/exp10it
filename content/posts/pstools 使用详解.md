---
title: "pstools 使用详解"
date: 2018-02-17T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['windows']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

pstools 是微软用于管理员更方便的管理服务器的工具套件

提供很多功能比如: 远程执行命令 远程停止进程 远程更改密码 远程关机

<!--more-->

```
psexec
psfile
psgetsid
psinfo
pskill
pslist
psloggedon
psloglist
pspasswd
psping
psservice
psshutdown
pssuspend
```

## psexec

psexec 执行命令

pstools 中最强大的工具

内网渗透中也经常用到

`psexec \\IP -u username -p password cmd arguments [-c upload-file-to-exec]`

## pspasswd

更改密码 不受密码策略的限制

`pspasswd \\IP -u username -p password change-pass-user change-password`

## pskill

杀掉进程

`pskill \\IP -u username -p password process-name`

## pslist

列出进程

`pslist \\IP -u username -p password`

## psinfo

查看系统信息

`psinfo \\IP -u username -p password`

## psloggedon

查看当前登录用户

`psloggendon \\IP`

## psgetsid

获取系统 sid 用于创建黄金票据

`psgetsid \\IP`