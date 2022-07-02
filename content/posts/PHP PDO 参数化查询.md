---
title: "PHP PDO 参数化查询"
date: 2018-05-12T00:00:00+08:00
draft: false
tags: ['sqli','php']
categories: ['编程']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

PHP 数据对象 (PDO) 扩展为 PHP 访问数据库定义了一个轻量级的一致接口.

<!--more-->

```
mysql> PREPARE statement FROM 'SELECT * FROM user WHERE username = ?';
Query OK, 0 rows affected (0.00 sec)
Statement prepared
mysql> SET @username = 'admin';
Query OK, 0 rows affected (0.00 sec)
mysql> EXECUTE statement USING @username;
+----------+----------+
| username | password |
+----------+----------+
| admin    | 123456   |
+----------+----------+
1 row in set (0.00 sec)
```

我们暂时不讨论如何用 PDO 预防 SQL 注入.

先来看看 MYSQL 的预处理与参数化.

## MySQL


mysql 的预处理语句暂且可以理解为 模板.

创建了 SQL 语句之后, 后面再次进行查询, 只需要将相应的参数重新赋值即可, 不需要再重写一遍语句.

**这一切都是在 mysql 服务器中进行的**

也就是说, 什么引号之类的, 在 PHP 中不用管, 直接拼接即可, 将后续的转义、过滤操作全部交给 mysql.

由于 `SET @variable = param` 不能像 where 一样在后面跟上运算符 `(= < > like between)`, 所以也就避免了 SQL 注入.

预处理语句的创建:

```
PREPARE [NAME] FROM [SQL Query];
SET @variable = [param];
EXECUTE [NAME] USING @variable;
```

其中在 PREPARE 中的参数要替换为 `?`

即将 `SELECT * FROM user WHERE username = 'admin';` 替换为 `SELECT * FROM user WHERE username = ?';`

EXECUTE 中 USING 后面的变量与语句中的 `?` 一一对应.

## PDO

在 PDO 中提供了 prepare() 方法用于实现参数化查询.

```
$pdo = new PDO('mysql:host=127.0.0.1;dbname=test','root','root');
$sql = 'SELECT * FROM user WHERE username=:username';
$statement = $pdo->prepare($sql);
$statement->bindParam(":username", $username);
$statement->execute();
$row = $statement->fetch();
```

和 mysql 不同的是, `?` 变成了 `:variable`, 以便后面用 bindParam 添加参数.

需要注意的是, PDO 默认在本地模拟拼接 SQL 语句, 最终到 mysql 上时只有一条查询.

通过 $`pdo->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);` 让 PDO 将语句转到 mysql 拼接.

本地测试了一下, windows 无效, linux 有效, 即使不设置 `ATTR_EMULATE_PREPARES` 也能避免注入.