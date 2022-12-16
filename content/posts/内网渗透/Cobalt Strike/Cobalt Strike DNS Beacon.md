---
title: "Cobalt Strike DNS Beacon"
date: 2019-07-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ["cobalt strike"]
categories: ["内网渗透"]

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

通过添加 DNS Beacon 达到利用 DNS staging payload 的目的.

隐蔽性好, 但传输速度慢.

<!--more-->

首先需要配置 A 记录指向 teamserver 的 IP (NS 记录的目标只能为域名).

之后配置 NS 记录 (名称任意 不必为其子域名) 指向 teamserver 所在域名.

```
malwarec2  A   192.168.1.1
profile    NS  malwarec2.exp10it.cn
games      NS  malwarec2.exp10it.cn
pictures   NS  malwarec2.exp10it.cn
```

添加 DNS Beacon, 这里以 `windows/beacon_http/reverse_http` 为例.

![add dns beacon 1](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/add_dns_beacon_1.jpg)

![add dns beacon 2](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/add_dns_beacon_2.jpg)

至此, 对 NS 域名及其子域的所有请求都将被发送至 teamserver 所在服务器.

```
request profile.exp10it.cn to malwarec2.exp10it.cn
request test.profile.exp10it.cn to malwarec2.exp10it.cn
```

在 cobalt strike 添加 DNS Beacon 后将会启动 DNS Server, 开放 53 端口, 注意防火墙设置.

除此之外还有 `windows/beacon_dns/reverse_dns_txt`, 该 payload 完全利用 DNS TXT 记录传输数据, 因此 Listener 的端口是非必需的, 但可能会有数以千计的 DNS 请求被发送.

在 interact 中使用 `mode` 命令切换传输模式.

```
mode http //switch to HTTP mode
mode dns // switch to DNS A mode
mode dns6 // switch to DNS AAAA mode
mode dns-txt //switch to DNS TXT mode
```