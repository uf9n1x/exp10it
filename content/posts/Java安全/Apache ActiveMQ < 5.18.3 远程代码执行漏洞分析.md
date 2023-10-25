---
title: "Apache ActiveMQ (版本 < 5.18.3) RCE 分析"
date: 2023-10-25T20:06:27+08:00
lastmod: 2023-10-25T20:06:27+08:00
draft: false
author: "X1r0z"

tags: []
categories: []

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Apache ActiveMQ (版本 < 5.18.3) RCE 分析

<!--more-->

参考:

https://github.com/apache/activemq/commit/958330df26cf3d5cdb63905dc2c6882e98781d8f

https://github.com/apache/activemq/blob/1d0a6d647e468334132161942c1442eed7708ad2/activemq-openwire-legacy/src/main/java/org/apache/activemq/openwire/v4/ExceptionResponseMarshaller.java

复现完后有点困先睡会, 明天起床再写