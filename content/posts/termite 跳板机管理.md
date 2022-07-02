---
title: "termite 跳板机管理"
date: 2018-02-22T00:00:00+08:00
draft: false
tags: ['windows','linux']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Termite 是一款跳板机管理工具, 支持多种平台, 跳板机间可相互连接, 支持正反向 shell, socks 代理, 端口转发.

<!--more-->

程序分为 admin 和 agent

首先运行 agent

`agent -l port`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519283903.jpg)

admin 连接

`admin -c ip -p port`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519283908.jpg)

agent 显示信息

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519283913.jpg)

输入 help 查看命令

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519283941.jpg)

show 查看拓补

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284082.jpg)

W windows

M MacOS

L Linux

## 选择主机

`goto id`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284166.jpg)

## 反弹 shell

`shell port`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284183.jpg)

netcat 连接

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284198.jpg)

## 开启 socks 代理

`socks port`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284236.jpg)

之后用 proxychians 连接

## 上传/下载文件

`upfile 1.txt 2.txt`
`downfile 1.txt 2.txt`

我这失败了 应该是只支持 linux

## 端口转发

`lcxtran local-port ip remote-port`

将目标服务器所在网段的某个 ip 的 remote-port 转发到本地的 local-port

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284366.jpg)

## 添加拓补

将其他主机加入拓补

`agent -c agent-ip port`

连接已有的 agent (之前的 agent -l port)

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/22/1519284476.jpg)

因为连接的是前面的 agent 所以 2W 在 1W 下面