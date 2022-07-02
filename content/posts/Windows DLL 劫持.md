---
title: "Windows DLL 劫持"
date: 2019-08-09T00:00:00+08:00
draft: false
tags: ['windows','dll']
categories: ['漏洞复现']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

项目代码 [X1r0z/DllHijackTest](https://github.com/X1r0z/DllHijackTest)

如有错误, 望指正.

<!--more-->

## 何为 DLL

DLL 全称 Dynamic Link Library, 即动态链接库. DLL 包含了我们所需要的函数或变量, 并通过主程序加载 DLL 来进行调用.

DLL 的好处在于它缩小了主程序的体积, 提供了一种模块化编程的思想, 并且也更易于它人调用, 而无需手动再次实现对应的功能.

## 编写 DLL

至于 DLL 劫持是什么? 怎么做? 暂且不说, 先来讲讲如何编写并调用 DLL 文件.

其中调用 DLL 分为静态调用和动态调用, 前者在程序运行时就进行加载, 后者则适时加载和卸载相应的 DLL.

以下示例代码会编写 Test.dll 文件并通过 DllHijack 程序动态调用 Test 函数弹出窗口.

DllHijack.cpp

```
#include <Windows.h>

int main()
{
	HMODULE hDLL = LoadLibrary(L"Test.dll");
	FARPROC fpFun = GetProcAddress(hDLL, "Test");
	(*fpFun)();
	FreeLibrary(hDLL);
}
```

Test.cpp

```
#include "pch.h"

void Test()
{
    MessageBox(NULL, TEXT("Hello World!"), TEXT("Test"), NULL);
}
```

dllmain.cpp

```
#include "pch.h"

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}
```

Test.def

```
EXPORTS
	Test
```

编译执行.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190808175628.png)

### EXE 做了什么

首先, 我们的程序通过 `LoadLibrary()` 动态加载 Test.Dll 这个文件, 

然后通过 `GetProcAddress()` 获取 DLL 中已被导出的 Test 函数的在内存中的地址并保存在 fpFun 指针中, 最后解引用指针并进行调用, 被调用的 Test 函数通过 `MessageBox()` 弹出窗口.

### DLL 做了什么

当 DLL 被加载时, 首先执行 DllMain 来进行初始化, 其中的 `DLL_PROCESS_ATTACH`, `DLL_THREAD_ATTACH`, `DLL_THREAD_DETACH`, `DLL_PROCESS_DETACH` 分别在程序开始运行时, 创建新线程时, 线程结束运行时, 程序结束运行时进行对应的初始化操作, 这里默认为空.

然后, 当程序调用 Test 函数时, DLL 将会检查对应的函数是否已被导出 (Test.def), 如果已经被导出, 则返回其在内存中的地址, 如果未被导出, 则返回空地址.

这里的是否被导出, 我觉得将它们理解为 Public 和 Private 更合适一些 :)

## DLL 搜索顺序

为什么要提这个呢? 下面我们将 Test.dll 从程序当前目录移动至 C:\Windows\SysWOW64 中, 再次执行程序.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190808175628.png)

执行成功.

但我没有指定 DLL 在 SysWOW64 中, 它是如何找到对应的 Test.dll 文件的? 这里就要引入 DLL 搜索顺序这一概念.

当 `LoadLibrary()` 被调用时, 系统一般会从以下路径里依次查找 DLL.

```
1. 程序所在目录
2. C:\windows\SysWOW64
3. C:\Windows\System32
4. C:\Windows\System
5. 用户当前目录
6. PATH 环境变量中的目录
```

其中 "用户当前目录" 怎么去理解呢?  其实很简单.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190808200604.png)

这里我将 Release 中的 Test.dll 删掉, 但程序还是会成功执行.

显而易见, "用户当前目录" 就是指用户在执行程序时当前所在的目录, 比如再打开文档时, Word 程序可能就会在文档所在目录下查找需要被调用的 DLL 文件.

但要注意, 在 Windows XP SP2 之前的系统中, "用户当前目录" 默认的优先级是高于 System32 的, 而后面的系统中优先级下调是因为默认启用了 SafeDllSearchMode, 位置为 `HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager`

### KnownDLLs

另外说一下 KnownDLLs.

这是一个注册表项, 其具体位置在 `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs` 中.

如果一个 DLL 名在 KnownDLLs 中, 程序在调用 DLL 时则会跳过当前目录, PATH 等, 直接在系统目录下查找, 也就是说, 这些 DLL 只能够在系统目录中被调用.

## DLL 劫持

因为部分 DLL 在当前目录下的查找优先级永远是高于系统目录下的,所以 DLL 劫持的原理就很清晰了.

攻击者利用 DLL 搜索路径中的缺陷, 在程序调用指定系统 DLL 之前提前就把重名的恶意 DLL 放置在程序当前目录中, 达到了劫持的目的.

其中存在于 KnownDLLs 中的 DLL 文件是无法进行 DLL 劫持的, 通过修改注册表能够绕过其限制, 不过需要系统重启后才会生效.

### 针对系统目录的 DLL 劫持

劫持系统目录下的 DLL, 通用性较强, 但大部分 DLL 名都被添加进杀软黑名单中.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190808225242.png)

而且在编写 DLL 时一般会通过 `LoadLibrary(L"\\kernel32.dll")` 这种在 DLL 名称前加上两道反斜杠的方式来直接从系统目录中加载 DLL, 所以直接劫持系统 DLL 的方法现在已经很少见了.

### 针对程序目录的 DLL 劫持

劫持程序目录下的 DLL, 利用方式与一般的 DLL 劫持不同, 它是通过用重名恶意 DLL 替换程序目录下正常 DLL 来达到另外一种 "劫持" 的效果的. 稳定性较强, 基本上大部分 DLL 都能够被劫持, 同时对于系统目录中的 DLL 劫持一般也能这样做.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190808225524.png)

### 针对文件关联的 DLL 劫持

主要是针对 Adobe, Office 等软件在双击打开文档后在文档所在目录进行查找时的 DLL 劫持.

网上资料比较少, 通常情况下也并不隐蔽, 因为文档会伴随着 DLL 出现.

在此不做演示.

### 查找可劫持的 DLL

方法是将可能存在劫持的 DLL 依次替换成为恶意 DLL, 然后重新启动应用程序, 并检测 Payload 是否被执行.

这里需要解决的是如何查询程序加载的 DLL 文件, 以及如何把这个过程自动化.

如果是针对程序目录的 DLL 劫持, 个人还是建议通过手动的方式来测试.

#### Process Explorer & Process Monitor

[SysinternalsSuite](https://docs.microsoft.com/zh-cn/sysinternals/downloads/sysinternals-suite)

查看和监控进程所加载的 DLL 名称和路径.

Process Explorer. 总览进程 DLL.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809101240.png)

Process Moniter. 监控指定进程的详细操作.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809101843.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809101954.png)

#### Rattler

[sensepost/rattler](https://github.com/sensepost/rattler)

原理是通过不断启动应用程序来检测测试 DLL 是否被执行, 但漏报误报较多, 也只能检测系统自带的 DLL.

#### dll_hijack_detect

[adamkramer/dll_hijack_detect](https://github.com/adamkramer/dll_hijack_detect)

枚举所有进程, 依次检测其正在加载的系统 DLL 是否可以劫持, 缺点是输出较长,可以自己修改源码.

### 对于恶意 DLL 的修改

DLL 劫持是通过使用恶意 DLL 来替代程序对正常 DLL 的加载的. 但就会有一个问题: 如何确保在 DLL 劫持成功之后, 程序能正常运行?

需要明确一点, 多半进行 DLL 劫持的目的是在于权限维持而不是提权, 所以我们需要确保 DLL 的稳定性与隐蔽性, 而且要能够正常的执行被劫持 DLL 的功能.

#### AHeadLib

[PEDIY](https://bbs.pediy.com/thread-224408.htm)

软件的本质是通过读取导出的函数名和内联汇编代码来 "转发" DLL.

如果在加载 DLL 时出错就说明位数有问题, 需要运行 x64 的 AHeadLib.

这里以微信的 WeChatWin.dll 为例.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809160233.png)

注意两个点: 转发选项和原始 DLL 名称.

当前者为 "直接转发函数" 时, 则直接转发整个 DLL, 代码中仅有 DllMain. 如果选择 "即时调用函数", 就会细分至 DLL 的每一个函数, 在调用不同函数时依次进行转发. 例如在接受文档时触发 Payload, 或是在程序崩溃时触发 Payload, 高度自定义, 没有需要的话默认即可.

"原始 DLL 名" 指的是被劫持 DLL 修改后的名称. 工具只是帮你把指定函数转发到对应的 DLL 上, 并不是直接反编译出内容, 所以需要通过恶意 DLL 来调用被劫持 DLL 的相关函数, 如果勾选 "系统路径" 则说明被劫持的 DLL 为系统 DLL.

生成后在 Visual Studio 新建动态链接库项目, 然后在 dllmain 中粘贴代码.

这里我们在 `DLL_PROCESS_ATTACH` 中加入启动进程的代码.

```
STARTUPINFO si = { sizeof(si) };
PROCESS_INFORMATION pi;
CreateProcess(TEXT("C:\\Windows\\System32\\calc.exe"), NULL, NULL, NULL, false, 0, NULL, NULL, &si, &pi);
```

选择对应位数编译 (如果是 64 位的 DLL 需要在项目中添加之前生成的 .obj 文件).

复制 DLL, 并修改被劫持 DLL 的名称为之前指定的 "原始 DLL 名".

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809161204.png)

打开微信程序.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809154108.png)

#### SuperDllHijack

[anhkgg/SuperDllHijack](https://github.com/anhkgg/SuperDllHijack)

一种通用的 DLL 劫持方法, 直接更改 `LoadLibrary()` 返回的 DLL 地址, 优点是通用性强, 不需要手动导出 DLL 函数.

以之前的程序为例.

修改 Test.dll 为 .Test.dll, 并在 dllmain.cpp 中更改被劫持 DLL 的名称 (如果管理员是傻子可以尝试将 DLL 设为隐藏).

```
PathAppend(tszDllPath, TEXT(".Test.Dll"));
```

加入启动进程的代码.

```
STARTUPINFO si = { sizeof(si) };
PROCESS_INFORMATION pi;
CreateProcess(TEXT("C:\\Windows\\System32\\calc.exe"), NULL, NULL, NULL, false, 0, NULL, NULL, &si, &pi);
DllHijack1(hModule);
```

编译执行.

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20190809163622.png)

## 其它

实测中发现如果是 x64 的系统, DllHijack 只会从 SysWOW64 中加载 DLL, 而不是 System32.