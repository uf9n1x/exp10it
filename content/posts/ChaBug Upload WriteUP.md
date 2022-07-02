---
title: "ChaBug Upload WriteUp"
date: 2018-06-22T00:00:00+08:00
draft: false
tags: ['ctf']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

ChaBug Upload WriteUp

<!--more-->

假上传点, 其实就是个简单的 SQLi.

filename 时间盲注, 能用 BurpSuite 跑.

无提示地过滤了 `and or union` 关键字, 用 `&& ||` 绕过.

[ctf.tar.gz](http://exp10it-1252109039.cossh.myqcloud.com/2018/06/23/1529737472.gz)

源码

index.php

```
<form action="upload.php" method="post" enctype="multipart/form-data">
<input type="file" name="file" />
<input type="hidden" name="filepath" value="upload/" />
<input type="hidden" name="filename" value="<?php echo time().'.jpg';?>" />
<input type="submit" name="submit" value="上传" />
</form>

<?php

$dir = opendir('upload/');
while(($filename=readdir($dir))!==false){
	if(($filename !='.') && ($filename!='..')){
		echo $filename.' ';
	}
}
closedir($dir);

?>
```

upload.php

```
<?php

function waf($str){
	$keyword = array('union','insert','update','delete','where','and','or');
	foreach($keyword as $v){
		while(stripos($str,$v)!==false){
			$str = str_ireplace($v,'',$str);
		}
	}
	return $str;
}

if(isset($_POST['submit'])){
	$filename = time().'.jpg';
	move_uploaded_file($_FILES['file']['tmp_name'],'upload/'.$filename);
	echo 'File saved successfully!';
	echo '<br />';
	echo 'upload/'.$filename;
	echo '<br />';

	$conn = mysqli_connect('localhost','root','root','ctf');
	$name = waf($_POST['filename']);
	$sql = "INSERT INTO logs VALUES('$name')";
	$res = mysqli_query($conn,$sql) or die('saving information error');
	echo 'saved information successfully';
}

?>
```

搅屎脚本

```
import os,sys
import time

str0 = '''
<?php
if(isset($_POST['a'])){
	echo 'hint: union insert update delete where and or';
}
'''

str1 = '''
<html><body><center><form method="POST"><input type="password" name="getpwd"> <input type="submit" value=" O K "></form></center></body></html>
'''

str2 = '''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html">

<title>AUTHENTICATION REQUIRED</title>
<style type="text/css">
body, table, tr, td, div, select, input, textarea, pre, code { font: 100% 'sans-serif',sans-serif; text-decoration: none; }
td, div { max-width: 1024px; }
input, select, textarea { border: 0; padding: 0; }
input, select, textarea { -webkit-box-sizing: border-box; -moz-box-sizing: border-box; box-sizing: border-box; -ms-box-sizing: border-box; }
input::-moz-focus-inner { border: 0;padding: 0; }
body { background-color: #717678; font-family: 'sans-serif',sans-serif !important; font-size: 10px !important; color: #525252;}
*:focus {outline: none;}
.but1, .but2, .but3, .actbut, .but1:active, .but2:active, .but3:active .actbut:active { border: 1px solid #cccccc; margin-left: 1px; text-shadow: 1px 1px 2px #ffffff; vertical-align: middle; }
.but1, .but2, .but3, .actbut { background: #F5F5F5;
filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#F5F5F5', endColorstr='#E0E0E0');
background: -webkit-gradient(linear, left top, left bottom, from(#F5F5F5), to(#E0E0E0));
background: -moz-linear-gradient(top, #F5F5F5, #E0E0E0);
background: -o-linear-gradient(top, #F5F5F5, #E0E0E0);
 }
.but1:hover, .but2:hover, .but3:hover, .actbut:hover { background: #E0E0E0;
filter: progid:DXImageTransform.Microsoft.gradient(startColorstr='#E0E0E0', endColorstr='#F5F5F5');
background: -webkit-gradient(linear, left top, left bottom, from(#E0E0E0), to(#F5F5F5));
background: -moz-linear-gradient(top, #E0E0E0, #F5F5F5);
background: -o-linear-gradient(top, #E0E0E0, #F5F5F5);
 cursor: pointer; }
.but1 { width: 28px; height: 18px; font-size: 10px; font-weight: bold; }
.but2 { color: #4F4F4F; padding: 0 10px 0 10px; height: 20px; font-size: 10px; }
.actbut { color: #4F4F4F; padding: 0 10px 0 10px; height: 18px; font-size: 10px; font-weight: normal; }

.login { background: #F2F2F2; border: 1px solid #777777 ; -moz-box-shadow: #666666 0 0 8px; -webkit-box-shadow: 0 0 8px #666666; box-shadow: 0 0 8px #666666; margin-top: 150px; padding: 10px; text-align: left; }
.login td { padding: 0; }
.login input {  background-color: #FFFFFF; border: 1px solid #CCCCCC; color: #333333; margin: 1px; margin-right: 0; height:20px; width:150px; font-size: 10px; text-shadow: 1px 1px 5px #dddddd; vertical-align: middle; }
.lerror { color: #FF0000; padding-bottom: 10px !important; }

</style>
</head>
<body>
<table cellpadding="0" cellspacing="0" border="0" align="center" class="login">
<tr valign="middle">
<td>
<form method="POST" action=""><table cellpadding="0" cellspacing="0" border="0" align="center">
<tr valign="middle">
<td>
<span style="font-size: 9px; color: #333333; font-weight: bold;">USER&nbsp; </span></td>
<td>
<input type="text" name="zu" value=""></td>
</tr>
<tr valign="middle">
<td>
<span style="font-size: 9px; color: #333333; font-weight: bold;">PASS&nbsp; </span></td>
<td>
<input type="password" name="zp" value=""></td>
</tr>
<tr valign="middle">
<td>
</td>
<td>
<input type="submit" value="Connect" class="but2"></td>
</tr>
</table>
</form></td>
</tr>
</table>
</body></html>
'''

print('[*] 搅屎开始!')

while True:
	dirlist = os.listdir('upload/')
	if 'phpspy.php' in dirlist:
		print('[*] 搅屎完毕!')
		sys.exit()
	if len(dirlist)>=20:
		with open('upload/'+str(int(time.time()))+'.php','w+') as f:
			f.write(str0)
		print('[+] 搅屎x1')
	if len(dirlist)>=30:
		with open('upload/bypass.php','w+') as f:
			f.write(str1)
		print('[+] 搅屎x2')
	if len(dirlist)>=40:
		with open('upload/phpspy.php','w+') as f:
			f.write(str2)
		print('[+] 搅屎x3')
	print('[-] 等待下一波搅屎')
	time.sleep(60)
```