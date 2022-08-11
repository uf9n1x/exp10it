---
title: "BurpSuite 攻击模式"
date: 2018-07-06T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['burpsuite']
categories: ['web']

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


BurpSuite Intruder 支持4种攻击模式.

`Sniper` 狙击手, `Battering ram` 攻城锤, `Pitchfork` 干草叉 和 `Cluster bomb` 集束炸弹.

<!--more-->

## Sniper

狙击手将 payload 依次替换至每一个 position.

没有替换的 position 将用标注时默认的内容替代.

仅支持设置1个载荷集合.

```
username=§1§&password=§2§

payload1: admin test guest
```

result

```
admin 2
test 2
guest 2

1 admin
1 test
1 guest
```

## Battering ram

攻城锤将 payload 依次替换至所有的 position.

即每次发包时 position 里的 payload 都是相同的.

仅支持设置1个载荷集合.

```
username=§1§&password=§2§

payload1: admin test guest
```

result

```
admin admin
test test
guest guest
```

## Pitchfork

干草叉将不同载荷集合中的 payload 按顺序替换至对应的 position.

有多少 position 就设置多少载荷集合.

最多支持5个 position (载荷集合).

```
username=§1§&password=§2§

payload1: admin test guest
payload2: 123 456 789
```

result

```
admin 123
test 456
guest 789
```

## Cluster bomb

集束炸弹将不同载荷集合中的 payload 依次替换至每一个 position.

有多少 position 就设置多少载荷集合.

发包的数量为所有载荷集合中 payload 的乘积.

```
username=§1§&password=§2§

payload1: admin test guest
payload2: 123 456 789
```

result

```
admin 123
admin 456
admin 789

test 123
test 456
test 789

guest 123
guest 456
guest 789
```