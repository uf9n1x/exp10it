---
title: "Python AsyncIO 学习笔记"
date: 2018-06-26T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['python','note']
categories: ['编程']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

asyncio 是在 Python 3.4 中引入的异步 IO 标准库.

<!--more-->

简单介绍一下什么是同步 IO / 异步 IO.

```
同步 IO: 你和女朋友去约会, 你需要一直等着她来, 之后你才能和她吃饭.
异步 IO: 你和女朋友去约会, 在她来的路上你不用一直等着, 可以去买礼物什么的.
```

## async/await/future

*Python 3.5 引出的语法糖*

async 创建协程, await 当协程阻塞时将其挂起并让步操作给其它协程, future 包装协程.

通过 `asyncio.sleep()` 模拟 IO 操作.

```
import asyncio

async def hello(s):
	print('Waiting '+str(s))
	await asyncio.sleep(s)
	print('Done '+str(s))
	return 'Res '+str(s)

tasks = [
	asyncio.ensure_future(hello(1)),
	asyncio.ensure_future(hello(2)),
	asyncio.ensure_future(hello(3))
]

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
for task in tasks:
	print(task.result())
```

输出

```
Waiting 1
Waiting 2
Waiting 3
Done 1
Done 2
Done 3
Res 1
Res 2
Res 3
```

## callback

当协程执行完毕时调用 callback

```
import asyncio

async def hello():
	print('Hello World')

def callback(future):
	print('Done')

coro = asyncio.ensure_future(hello())
coro.add_done_callback(callback)
loop = asyncio.get_event_loop()
loop.run_until_complete(coro)
```

输出

```
Hello World
Done
```

## aiohttp

aiohttp 是基于 asyncio 的 HTTP 框架.

`aiohttp.request` 用于发起 HTTP 请求.

```
import asyncio
import aiohttp

async def req(s):
	print('Requesting '+str(s))
	async with aiohttp.request('GET',s) as response:
		res = await response.read()
		print('Receiving from '+str(s))

urls = ['http://www.baidu.com/','http://www.qq.com','http://www.163.com/']
tasks = []

for url in urls:
	coro = asyncio.ensure_future(req(url))
	tasks.append(coro)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
```

输出

```
Requesting http://www.baidu.com/
Requesting http://www.qq.com
Requesting http://www.163.com/
Receiving from http://www.baidu.com/
Receiving from http://www.qq.com
Receiving from http://www.163.com/
```

`aiohttp.ClientSession` 同样也能发起 HTTP 请求.

```
import asyncio
import aiohttp

async def req(s):
	print('Requesting '+str(s))
	async with aiohttp.ClientSession() as session:
		async with session.get(s) as response:
			res = await response.read()
			print('Receiving from '+str(s))

urls = ['http://www.baidu.com/','http://www.qq.com','http://www.163.com/']
tasks = []

for url in urls:
	coro = asyncio.ensure_future(req(url))
	tasks.append(coro)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
```

输出

```
Requesting http://www.baidu.com/
Requesting http://www.qq.com
Requesting http://www.163.com/
Receiving from http://www.baidu.com/
Receiving from http://www.qq.com
Receiving from http://www.163.com/
```