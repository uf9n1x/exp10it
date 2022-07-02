---
title: "Celery 学习笔记"
date: 2018-08-12T00:00:00+08:00
draft: false
tags: ['python']
categories: ['编程']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Celery 是一个强大的异步任务调度框架.

<!--more-->

# 概念

类似于 生产/消费模型 中的生产者和消费者, 在 celery 中也有这样的几个角色, 分别是 broker backend work 和 task

## Broker

broker 是用于传输消息的中间件, 当应用程序调用异步任务的时候, 会向 broker 传递消息, 之后 worker 取出任务并执行

RabbitMQ Redis 可作为 broker

## backend

backend 存储 worker 执行任务后返回的结果和状态

RabbitMQ Redis 甚至 Databases 都可作为 backend

## worker

worker 就是 task 的工作者, 从 broker 中取出任务并执行

## tasks

顾名思义, 你想执行的任务

# 工作流程

```
Async Task   Schedule Task
       \       /
         Broker
       /   |   \
  Worker Worker Worker
      \    |    /
        backend
```

# 初步上手

使用 `celery.Celery` 创建应用

```
from celery import Celery

app = Celery('tasks', broker='redis://127.0.0.1:6379/0', backend='reids://127.0.0.1:6379/0')
```

celery 提供了装饰器便于创建任务

```
@app.task
def add(x, y):
    print('hello world')
    return x + y
```

同目录下运行 `celery -A task worker -l info -n %h.add`

`-A` 指定应用名, `-l` 指定不同的 `loglevel`

`-n` 用于指定当前的节点名, 其中 `%h` 包含当前的域名和主机名, `%n` 只包含主机名, `%d` 只包含域名

```
In [1]: from tasks import add

In [2]: result = add.delay('2','3')

In [3]: result.status
Out[3]: 'SUCCESS'

In [4]: result.ready()
Out[4]: True

In [5]: result.get()
Out[5]: '23'
```

一般使用 `delay(args)` 触发任务, `ready()` 则说明任务是否执行成功

`get()` 获取返回结果, `status` 表示当前任务的状态

```
PENDING 待执行
STARTED 开始执行
SUCCESS 执行成功
FAILURE 执行失败
REVOKED 撤销
RETRY 重试
```

# 配置文件

创建 `config.py`

```
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
BROKER_URL = 'redis://127.0.0.1:6379/0'
TIMEZONE = 'Asia/Shanghai'
```

`CELERY_RESULT_BACKEND` 指定 backend

`BROKER_URL` 指定 broker

`TIMEZONE` 指定当前时区

从 `config.py` 中导入配置

```
app = Celery()
app.config_from_object('config')
```

# 队列路由

默认情况下所有任务的信息都保存在 `celery` 队列中, 很容易造成阻塞

通过创建不同的队列, 使用路由将不同的任务的信息存储到指定到队列中

创建三个任务 `taskA` `taskB` `add`

```
@app.task
def taskA(m):
	print('taskA',m)
	return m

@app.task
def taskB(m):
	print('taskB',m)
	return m

@app.task
def add(m):
	print('add',m)
	return m
```

编辑 `config.py`

```
from kombu import Exchange,Queue

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
BROKER_URL = 'redis://127.0.0.1:6379/0'
TIMEZONE = 'Asia/Shanghai'

CELERY_QUEUES = (
	Queue('default',Exchange('default'),routing_key='default'),
	Queue('taskA',Exchange('taskA'),routing_key='taskA'),
	Queue('taskB',Exchange('taskB'),routing_key='taskB'),
	Queue('Add',Exchange('Add'),routing_key='Add')
	)

CELERY_ROUTES = {
	'tasks.taskA':{'queue':'taskA','routing_key':'taskA'},
	'tasks.taskB':{'queue':'taskB','routing_key':'taskB'},
	'tasks.add':{'queue':'Add','routing_key':'Add'}
}

CELERY_DEFAULT_QUEUE = 'default'
CELERY_DEFAULT_EXCHANGE = 'default'
CELERY_DEFAULT_ROUTING_KEY = 'default'
```

在 `CELERY_QUEUES` 中添加 `Queue` 对象创建队列

`Queue(QUEUE_NAME, EXCHANGE, ROUTING_KEY)`

`Exchange` 通过 `Routing_Key` 把信息路由到不同的 `Queue` 中

通过在 `CELERY_ROUTES` 中建立对应的映射关系指定任务使用的队列

`OBJECT.TASK_NAME: {'queue':QUEUE_NAME,'routeing_key':ROUTING_KEY}`

最后三行指定默认的存储队列, 当然也可以不写, 这样默认队列就为 `celery`

依次开启三个窗口, 执行以下命令

```
celery -A tasks worker -l info -Q taskA -n %h.taskA
celery -A tasks worker -l info -Q taskB -n %h.taskB
celery -A tasks worker -l info -Q add -n %h.add
```

使用 `-Q` 参数指定队列, 主机仅接受当前队列的任务, 这样不同队列的任务就会被分发到其它节点执行

# 定时任务

celery 支持定时任务和计划任务, 通过 `beat` 节点向 worker 发送任务

编辑 `config.py`

```
from celery.schedules import crontab
from datetime import timedelta

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'
BROKER_URL = 'redis://127.0.0.1:6379/0'
TIMEZONE = 'Asia/Shanghai'

CELERYBEAT_SCHEDULE = {
	'schedule_task': {
		'task': 'tasks.add',
		'schedule': timedelta(seconds=5),
		'args': ('hello world',)
	},
}
```

在 `CELERYBEAT_SCHEDULE` 中添加定时任务

`SCHEDULE_TASK_NAME: {'task': TASK_NAME, 'schedule': TIME, 'args': ARGS}`

`schedule` 可为间隔秒数 `timedelta(secounds=5)` 或 `crontab(hour=7, minute=30, day_of_week=1)`

依次启动节点

```
celery -A tasks beat -l info
celery -A tasks worker -l info
```

beat

```
[2018-08-12 17:02:23,224: INFO/MainProcess] beat: Starting...
[2018-08-12 17:02:24,283: INFO/MainProcess] Scheduler: Sending due task schedule_task (tasks.add)
[2018-08-12 17:02:25,276: INFO/MainProcess] Scheduler: Sending due task schedule_task (tasks.add)
```

worker

```
[2018-08-12 17:02:24,296: INFO/MainProcess] Received task: tasks.add[531b5769-8919-4d59-b339-cc0e36456901]  
[2018-08-12 17:02:24,298: WARNING/ForkPoolWorker-2] Add
[2018-08-12 17:02:24,298: WARNING/ForkPoolWorker-2] hello world
[2018-08-12 17:02:24,301: INFO/ForkPoolWorker-2] Task tasks.add[531b5769-8919-4d59-b339-cc0e36456901] succeeded in 0.003998230000433978s: 'hello world'
[2018-08-12 17:02:25,278: INFO/MainProcess] Received task: tasks.add[88e5ffa2-794a-4ab4-b3ee-d6fccd3bb265]  
[2018-08-12 17:02:25,279: WARNING/ForkPoolWorker-2] Add
[2018-08-12 17:02:25,279: WARNING/ForkPoolWorker-2] hello world
[2018-08-12 17:02:25,279: INFO/ForkPoolWorker-2] Task tasks.add[88e5ffa2-794a-4ab4-b3ee-d6fccd3bb265] succeeded in 0.0005984580020594876s: 'hello world'
```

# 链式任务

有时任务可能由几个子任务组成, 任务之间相互调用, 这时候应使用异步回调的方式调用任务

被调用的多个任务由 `|` 分隔, 默认情况下使用 `s(ARGS)` 调用子任务, 同时返回的结果将被作为下一个任务的参数

如果不想让结果作为参数, 可以使用 `si(ARGS)` 或者 `s(ARGS,immutable=True)` 的方式进行调用

```
@app.task
def chainTask(m):
	chain = taskA.s(m) | taskB.s() | add.s()
	chain()

@app.task
def taskA(m):
	print('task A',m)
	return m

@app.task
def taskB(m):
	print('task B',m)
	return m

@app.task
def add(m):
	print('Add',m)
	return m
```

`si()` 方式

```
@app.task
def chainTask(m):
	chain = taskA.si(m) | taskB.si(m) | add.si(m)
	chain()

@app.task
def taskA(m):
	print('task A',m)
	return m

@app.task
def taskB(m):
	print('task B',m)
	return m

@app.task
def add(m):
	print('Add',m)
	return m
```

调用单个任务

```
@app.task
def chainTask(m):
	chain = Add.s(m)
	chain()

@app.task
def Add(m):
	print('Add',m)
	return m
```