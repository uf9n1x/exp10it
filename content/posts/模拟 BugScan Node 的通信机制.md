---
title: "模拟 BugScan Node 的通信机制"
date: 2018-08-24T00:00:00+08:00
draft: false
tags: ["python"]
categories: ["web","编程"]
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

大多数扫描器都是基于 B/S 或 C/S 架构, 但执行任务都是在 server 端进行, 像 bugscan 这样挂载节点执行扫描, server 只负责与节点通信的结构让人眼前一亮.

<!--more-->

![20220701204932](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701204932.png)

![20220701204949](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701204949.png)

挂载节点命令格式

`python2 -c"exec(__import__('urllib').urlopen('http://old.bugscan.net/u/HASH').read())"`

动态加载 urllib 并通过 exec 执行 response 中的内容

用户无需安装第三方库, 全部由 python 自带库完成操作

![20220701205011](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701205011.png)

# 动态加载

一般的动态加载, 首先文件要存在, 其次才能通过 `__import__` 或者 `imp` 库加载模块

bugscan 网传源码中的加载函数

```
def preload_module(chunk, modulename):
    m = imp.new_module(modulename)
    exec chunk in m.__dict__
    sys.modules[modulename] = m
    return m
```
使用 `imp.new_module` 创建一个空模块, 然后用 `exec chunk in m.__dict__` 加载 chunk 的内容

`__dict__` 为 python 中模块 函数 类 对象属性的映射, 相当于 namespace

python 的 namespace 是可以动态变化的, 通过更改 `__dict__` 来进行属性的添加 删除

```
>>> m = imp.new_module('a')

>>> def a():
        print 'a'

>>> m.__dict__['a'] = a

>>> m.a()
a

>> m.b = 'b'

>> m.b
'b'
```

这种方法在后面 patch 模块的时候还会用到

同理, `exec chunk in m.__dict__` 会把 `exec chunk` 放到 m 的 namespace 中执行, 这样就不会影响到 `__main__` 中的 namespace

```
import util
import hackhttp
import miniCurl

m.util = util
m.curl = miniCurl.Curl()
m.hackhttp = hackhttp.hackhttp()
```

# Hook

插件中输出信息使用 security_hole security_warning security_info security_note 四个函数

由于是节点扫描, 在终端商直接输出漏洞信息是没有多大用的

需要实现调用函数后将插件名称和 hash 及输出信息存储到字典中并放到指定的列表内这个功能

这就需要重写输出函数, 但插件名称和 hash 是不会传递的

但在 namespace 中存放类的方法, 该 namespace 的模块还能调用类的其它方法

把加载的模块包装成一个类, 放入四个 report 方法并执行 hook 操作, 在实例化的时候传入插件名称和 hash, 这样在调用输出的时候既能保持原有参数不变, 又能获取到插件信息并向服务端发送报告

```
class A(object):
    def __init__(self):
        self.b = 'b'
    def c(self):
        print self.b

>>> m = imp.new_module('m')

>>> a = A()

>>> m.__dict__['c'] = a.c

>>> m.c()
b
```

# 原理

bugscan 节点的三个核心 object

```
Service: rpc client, 负责与 server 通信, 获取任务\插件 发送报告等操作
Task_Manager: 任务管理器, 执行添加 删除任务的操作
Task: 获取插件 执行任务 输出报告
```

# 执行流程

```
 <-----------------循环------------------
   |                                      |
 service  -------> Task_Manager -------> Task
获取任务列表  发送     添加/删除      调用   执行/停止
```

```
无限循环 -> service 获取任务列表 -> 是否有待执行的任务 -> 发送至 task_manager -> 添加任务 -> 调用 task -> task 执行任务 -> service 设置任务状态 -> 是否返回报告 -> service 发送报告 -> 是否有待停止的任务 -> 发送至 task_manager -> 删除任务 -> 调用 task -> task 停止任务 -> service 设置任务状态 -> 无限循环
```

## Service

实现的方法: login get_task_list get_plugin_list set_task_status send_vuln_info delete_cur_node

实例化的参数: uhash rpc_url

### init

设置用户的 uhash 用于后面操作时的认证

rpc_url 指定 server 的地址

### login

传递当前的 uhash 以及本机的 ip hostname platform 等信息

server 端接受信息后判断 uhash 的有效性并生成 nodeid, 返回 json

相同主机的 nodeid 最好是唯一的, 例如 uhash+hostname 并通过 md5 或者 sha1 加密, 返回前 16 个字符

### get_task_list

传递 uhash nodeid 获取当前用户的任务列表

返回的 json 为 list, 每个 list 应包含 target 和 policy, policy 中包含扫描速度 超时时间 cookie useragent 调用的插件 hash 任务 hash 等信息

### get_plugin_list

传递 uhash nodeid 和 task policy 中的插件 hash 获取插件的详细信息

每个插件 list 包含 name hash service body 等信息

### set_task_status

传递 uhash nodeid thash 和要设置的任务 status 更改任务状态

### send_vuln_info

传递 uhash nodeid 和任务的 report 发送扫描报告

### delete_cur_node

传递 uhash nodeid 从 server 中删除当前节点

在 ctrl c 后调用

## Task_Manager

实现的方法: push kill

实例化的参数: 无

### init

创建列表 tasks 和字典 pool, tasks 存放任务的 hash, pool 则通过 hash 获取到 task 实例

### push

传递 thash policy 添加任务, 创建后台线程防止阻塞并实例化 task 类执行任务

执行前先在 tasks pool 中放入对应任务的 hash 和 task 实例

### kill

传递 thash 删除任务, 并从 pool 中获取 task 实例执行 kill 方法

最后在 tasks pool 中删除对应的 hash 实例

## Task

![20220701205532](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701205532.png)

实现的方法: run kill audit report load_module patch_module security_hole security_warning security_info security_note

实例化的参数: thash policy

### init

获取 thash, 并从 policy 获取 target plugins speed timeout cookie useragent 等信息

创建 taskqueue threadpool doc vulnerabilities 和 varlist, 设置 socket 的超时时间

### run

依次从 plugins 中获取数据, 执行 load_module 和 patch_module 操作, 将插件信息和动态加载后返回的对象存储在 taskinfo 字典中并 put 到 taskqueue

根据扫描速度创建线程, join 等待线程执行完毕, 最后根据 vulnerabilities 的内容生成报告, 添加到全局变量 report 中

### kill

停止线程

### audit

创建线程时指定的 target, 不断从 taskqueue 中获取数据, 将插件名称和 hash 临时存到 varlist 中, 调用 module.audit 方法并捕获 socket.timeout 异常, 最后清空 varlist

### report

在 doc 中添加任务 hash target 和 vulnerabilities

### load_module

传递 name chunk, 通过 imp 创建空模块并将在其命名空间内执行 chunk 的内容

### patch_module

传递 name phash m, 在 m 的命名空间中添加 util curl hackhttp 以及 security_hole security_warning security_info security_note 等函数

### security_hole

传递 m, 并输出信息

从 varlist 中获取插件名称和 hash, 将其与输出信息和 level 存储在 vuln 字典中, 并将 vuln 添加到 vulnerabilities 列表内

### security_warning

传递 m, 并输出信息

从 varlist 中获取插件名称和 hash, 将其与输出信息和 level 存储在 vuln 字典中, 并将 vuln 添加到 vulnerabilities 列表内

### security_info

传递 m, 并输出信息

从 varlist 中获取插件名称和 hash, 将其与输出信息和 level 存储在 vuln 字典中, 并将 vuln 添加到 vulnerabilities 列表内

### security_note

传递 m, 并输出信息

从 varlist 中获取插件名称和 hash, 将其与输出信息和 level 存储在 vuln 字典中, 并将 vuln 添加到 vulnerabilities 列表内

# 代码

提供代码? 不存在的. 自己动手写吧

![20220701205703](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701205703.png)

![20220701205713](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220701205713.png)