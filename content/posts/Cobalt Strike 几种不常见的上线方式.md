---
title: "Cobalt Strike 几种不常见的上线方式"
date: 2019-08-11T00:00:00+08:00
draft: false
tags: ['cobalt strike']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

开头先膜膜 m 师傅.

Cobalt Strike 中在内网中比较常用的通过 SMB, Bind TCP, Reverse TCP 上线的三种方式.

<!--more-->

## SMB Beacon

这种上线方式走的是 SMB 协议, 正向连接, 目标机器必须开启 445 端口, 同时利用命名管道来执行命令, 对于那些在内网中无法出网的机器就特别好用. 但是并不能直接生成可用载荷, 只能使用 PsExec 或 Stageless Payload 上线.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811110335.png)

不难看出, 这是在已有 Beacon (父 Beacon) 中使用 SMB 进行连接的, 在实际测试中可能会在多个 Beacon 上分别连接对应的 SMB Beacon, 所以溯源就比较困难, 在一定程度上可以达到规避防火墙的效果.

下面新建 SMB Beacon Listener, 其中的 Host 和 Port 并没有什么用.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811111009.png)

在已有 Beacon 中通过 PsExec 上线.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811111216.png)

上线成功.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811111446.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811111800.png)

拓补图中橙色的箭头代表着是通过 SMB 方式连接的, 而箭头的方向表明这是一个正向连接, 另外在 external 后会有 `∞∞` 的图标, 显示了与目标 Beacon 的连接状态.

因为 SMB 走的是 TCP 连接, 就不存在什么异步执行, 所以 last 就可以无视掉了, 数值也只是距离上一次操作经过的时间.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811112126.png)

对于 SMB Beacon 有两个命令, link 和 unlink.

unlink 可以暂时断开和目标 Beacon 的连接, 但不会退出进程, 而 link 就又会重新连接回去, 两者都需要在发起连接的 Beacon 上执行.

unlink.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811112438.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811112503.png)

图标会从 `∞∞` 变为 `∞ ∞`, 箭头上显示 DISCONNECTED, 颜色变为红色, 但进程仍在运行.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811112807.png)

我们在另外一台主机上 link.

这台 DC2 没有加入域, 需要手动创建 Token 来通过 SMB 认证.

```
make_toekn DC2\administrator admin7!@#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811113620.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811113651.png)

拓补图中箭头的位置改变了.

也就是说我们可以在任意已有 Beacon 上 link 目标 Beacon, 通过这个父 Beacon 去与目标 Beacon 通讯, 避免了不出网的尴尬. 但同一时间同一 Beacon 只能被 link 一次, 切换父 Beacon 的时候需要在原 Beacon 上先执行一次 unlink 操作, 还得注意凭据能否认证成功.

## Bind TCP Beacon

Bind TCP Beacon 与 SMB Beacon 差不多, 但它可以直接生成载荷在目标机器上执行.

添加 Bind Tcp Beacon Listener. Host 没有实际用处, Port 写死了是 4444, 更改也没有用, 在目标机器上还是会监听 4444 端口的.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811114347.png)

生成 Stageless Payload.

这里说一下 Staged 和 Stageless 的区别. 前者的实际功能只是和 C2 建立连接并接收 Payload, 然后加载执行, 而 Stageless 直接省去了接收 Payload 的步骤. 所以 Stageless 的 Payload 都会比 Staged 类型的要大很多, 而且包含了特征容易被杀软拦截.

不过这里的 Bind TCP Beacon 是正向连接, 而且仅与父 Beacon 通信, 所以就只能使用 Stageless 类型的了.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811114755.png)

执行后要手动去连接, 而 PsExec 方式会直接通过之前选择的 Beacon 上线.

与 SMB Beacon 不同, Bind TCP Beacon 对应的是 connect 和 unlink.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811115504.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811115612.png)

拓补图中的箭头变成绿色的了, 这表明我们是通过 Bind TCP Beacon 连接的.

其余操作与 SMB Beacon 完全相同, 这里就不说了.

但如果在同时 link 和 connect 同一 Beacon 的机器上上执行 unlink, 两者就都会被退掉.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811115931.png)

## Reverse TCP Beacon

反向连接已有 Beacon 上线, 但这个并不能直接在 Listeners 中添加, 需要右键已有 Beacon - Pivoting - Listener 添加.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811120511.png)

指定反向连接的 Listen Host 和 Listen Port. 一般默认即可, 除非机器有多个网卡. 这里意为将该机器作为跳板机, 让上线 Beacon 去连接这台机器, 然后与 C2 通信. 因而内网中每台机器都可以创建一个 Reverse TCP Beacon Listener, 所以溯源时也会有难度.

Reverse TCP Beacon 只能通过 Stageless Payload 上线.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811120911.png)

上线成功.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811120954.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811121024.png)

其中拓补图中箭头的方向变了, 这表明我们是通过反向上线的.

需要注意的是, Reverse 方式是没有 link unlink 一说的, unlink 之后就会直接退出进程, 想重新上线就必须要再次执行 Payload.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811121147.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190811121520.png)