---
title: "DREAD 风险评估"
date: 2018-06-15T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['note']
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


微软的 DREAD 模型.

<!--more-->

高危: 12-15分, 中危: 8-11分, 低危: 0-7分.

**等级**|**高(3)**|**中(2)**|**低(1)**
|----|----|----|----|
Damage Potential|获取完全验证权限; 执行管理员操作; 非法上传文件|泄露敏感信息	|泄露其他信息
Reproducibility|攻击者可以随意再次攻击|攻击者可以重复攻击, 但有时间限制|攻击者很难重复攻击
Exploitability|初学者在短期内能掌握攻击方法|熟练的攻击者才能完成这次攻击	|漏洞利用条件非常苛刻
Affected users|所有用户, 默认配置, 关键用户|部分用户, 非默认配置|极少数用户, 匿名用户
Discoverability|漏洞很明显, 攻击条件很容易获得|在私有区域, 部分人能看到, 需要深入挖掘漏洞|发现该漏洞极其困难

举个例子

```
SQL 注入: D(3) + R(3) + E(3) + A(3) + D(3) = 15 高危

XSS 攻击: D(2) + R(2) + E(2) + A(2) + D(2) = 10 中危

钓鱼欺骗: D(3) + R(1) + E(2) + A(1) + D(1) = 8 中危

铁锤砸机: D(1) + R(1) + E(1) + A(1) + D(1) = 5 低危
```