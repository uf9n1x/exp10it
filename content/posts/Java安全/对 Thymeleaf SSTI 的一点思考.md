---
title: "对 Thymeleaf SSTI 的一点思考"
date: 2023-02-15T13:35:48+08:00
lastmod: 2023-02-15T13:35:48+08:00
draft: false
author: "X1r0z"

tags: ['ssti', 'thymeleaf']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

尝试写点网上没有的东西

<!--more-->

## 基本原理

这个不多说了

[https://xz.aliyun.com/t/10514](https://xz.aliyun.com/t/10514)

[https://xz.aliyun.com/t/9826](https://xz.aliyun.com/t/9826)

[https://www.anquanke.com/post/id/254519](https://www.anquanke.com/post/id/254519)

[https://www.cnpanda.net/sec/1063.html](https://www.cnpanda.net/sec/1063.html)

## 回显原理

首先说明一下, 这种回显的本质其实是 throw 某个会包含表达式执行结果的异常, 而在低版本的 springboot (<= 2.2) 中, `server.error.include-message` 的默认值为 `always`, 这使得默认的 500 页面会显示异常信息

但是在高版本的 springboot (>= 2.3) 中, 上述选项的默认值变成了 `never`, 那么 500 页面就不会显示任何异常信息

所以这种回显形式还是会有一定的局限性

先来看常规的 payload, 无法回显

```
__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("whoami").getInputStream()).next()%7d__::
```

![image-20230215120652323](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151206407.png)

但是在 `::` 后面加上东西就能够回显了

```
__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("whoami").getInputStream()).next()%7d__::xx
```

![image-20230215120720598](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151207633.png)

其实这两种 payload 最终抛出的异常是不一样的, 调试的流程也会有所差别

下面具体分析一下, 环境为 springboot 2.2.0 + thymeleaf 3.0.11

首先是没有回显的 payload

![image-20230215121920679](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151219788.png)

经过了一次 preprocess 之后得到命令执行的结果, 然后再走一遍 parse 的流程

![image-20230215122018191](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151220297.png)

![image-20230215135135371](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151351487.png)

但是再次 parse 的时候返回的 expression 为 null, 所以最终会抛出 IllegalArgumentException 异常, 携带的异常信息只包含了我们输入的内容, 并没有命令的回显

而使用了回显 payload 之后, expression 的值会变成 FragmentExpression

![image-20230215122446741](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151224852.png)

之后返回到 renderFragment 方法, 往下会将表达式执行结果作为 templateName, 并提取出 `::` 后面的内容作为 selector

然后调用 `viewTemplateEngine.process()`

![image-20230215122723457](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151227564.png)

![image-20230215122906499](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151229609.png)

跟进 `resolveTemplate()`

![image-20230215123009149](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151230262.png)

templateResolver 负责在 classpath (prefix) 下依据 template (name) 和 suffix 寻找对应的模板文件

![image-20230215123204456](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151232569.png)

当然这里肯定是找不到的, 所以会抛出 TemplateInputException 异常, 但是这个异常会带出 tempate 名称并最终显示在 500 页面中, 因此达到了回显的效果

![image-20230215123049689](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151230787.png)

另外这里也解释了为什么以下这种可控点无法拿到回显的结果

```java
@Controller
public class IndexController {
    @GetMapping({"/"})
    public String index(@RequestParam String page) {
        return "welcome ::" + page;
    }
}
```

虽然能够通过预处理表达式提前执行命令, 但是 page 其实位于 selector 的位置, 根据上面的代码可以知道最终抛出 TemplateInputException 异常的时候携带的是 template, 也就是 `::` 前面的内容 , 并没有带出 selector, 所以最终 500 页面显示的只有 welcome

![image-20230215125528665](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151255698.png)

那为什么不往 `::` 后面加内容反而不会抛出 TemplateInputException? 即为什么原来的 payload 第二次 parse 的时候得到的 expression 会是 null, 而不是 FragmentExpression

一路跟进 parse 流程, 来到 `FragmentExpression#parseFragmentExpressionContent` 方法

![image-20230215124231718](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151242820.png)

![image-20230215123942908](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151239013.png)

先判断有没有 `::`, 然后将 `::` 左右分隔成两部分, 即 templateNameStr 和 fragmentSpecStr, 如果 fragmentSpecStr 为空则返回 null

这样一层一层往上, 最终得到的 expression 就会是 null, 导致提前抛出了 TemplateProcessingException, 无法拿到回显

## 预处理表达式

预处理表达式保证了表达式执行的最高优先级, 是否需要预处理表达式的关键在于 return 语句是否完全可控

看下面一个例子

```java
return page;
return "aa/" + page;
return "aa :: bb" + page;
```

如果是第一种完全可控的情况, 那么用不用预处理表达式都是无所谓的

如果是第二种或第三种情况, 使用不含预处理表达式的 payload 会执行失败

例如

```
aa$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("calc").getInputStream()).next()%7d::xx

aa::bb$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("calc").getInputStream()).next()%7d 
```

更改为预处理表达式的形式后, 执行成功

```
aa__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("whoami").getInputStream()).next()%7d__::xx

aa::bb__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("calc").getInputStream()).next()%7d__
```

原因在于第一组 payload 开头并不符合表达式的形式, parse 后的 templateName (或 fragmentSelector) 会变成 TextLiteralExpression, 而这个 expression 并不会走 spel 表达式解析的流程

![image-20230215131016896](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151310000.png)

如果删除了开头的 aa, 则 templateName (或 fragmentSelector) 会被解析成 VariableExpression, 该 expression 会被作为 spel 表达式执行

![image-20230215131348816](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151313926.png)

对于预处理表达式, thymeleaf 会将 `__${...}__` 中的内容用正则提取出来, 然后再 parse 一遍, 因为这个内容我们完全可控, 所以最终会返回 VariableExpression, 这个过程不会受到任何限制

![image-20230215131733856](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151317963.png)

## 2.x 版本

看到一些文章说 thymeleaf ssti 的原因在于片段表达式 `~{ }`, 这个特性是在 3.0 版本引入的, 所以 2.x 版本不存在 ssti

但实际上这种说法并不准确, 因为整个 ssti 的利用过程都与片段表达式没有任何关系, 其实 2.x 版本也能触发漏洞

下面以 springboot 1.4.1 + thymeleaf 2.1.5 为例

跟进 renderFragment 方法

![image-20230215132649275](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151326385.png)

这里调用的方法名与 3.x 版本有一点区别

跟进 computeStandardFragmentSpec 方法

![image-20230215132728075](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151327185.png)

![image-20230215132815896](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151328009.png)

同样存在 preprocess 方法来处理预处理表达式

![image-20230215132843519](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151328622.png)

parse 得到 VariableExpression, 然后调用 execute 执行表达式

对于不含预处理表达式的 payload, 同样能够执行, 只是位置不太一样

![image-20230215133112621](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202302151331731.png)

上文所述的回显原理以及预处理表达式的相关问题同样适用于 2.x 版本
