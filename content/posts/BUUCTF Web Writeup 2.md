---
title: "BUUCTF Web Writeup 2"
date: 2022-08-22T18:19:41+08:00
lastmod: 2022-08-22T18:19:41+08:00
draft: true
author: "X1r0z"

tags: []
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

## [ACTF2020 新生赛]BackupFile

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221821094.png)

手工试出来 index.php.bak

```php
<?php
include_once "flag.php";

if(isset($_GET['key'])) {
    $key = $_GET['key'];
    if(!is_numeric($key)) {
        exit("Just num!");
    }
    $key = intval($key);
    $str = "123ffwsfwefwf24r2f32ir23jrw923rskfjwtsw54w3";
    if($key == $str) {
        echo $flag;
    }
}
else {
    echo "Try to find out source file!";
}
```

弱类型转换

```
http://dacc2c9f-1fe9-44a7-a79a-6bff32b539cc.node4.buuoj.cn:81/?key=123
```

## [极客大挑战 2019]BuyFlag

右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221833474.png)

访问 pay.php 右键源代码

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221834560.png)

还是弱类型

提交 404aaa 之后提示 `You must be a student from CUIT !!!`

Cookie 把 `user=0` 改成 `user=1`, post 再传入 `money=100000000`

 然后提示数字太长了... 改成 `money[]=100000000` 就行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202208221840904.png)

## [护网杯 2018]easy_tornado