---
title: "RSA 算法原理"
date: 2018-08-03T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['RSA']
categories: ['算法']

hiddenFromHomePage: false
hiddenFromSearch: false
twemoji: false
lightgallery: true
ruby: true
fraction: true
fontawesome: true
linkToMarkdown: true
rssFullText: false

toc:
  enable: true
  auto: true
code:
  copy: true
  maxShownLines: 50
math:
  enable: false
share:
  enable: true
comment:
  enable: true
---


学习 RSA 算法的相关笔记

<!--more-->

先介绍两个概念, 对称加密算法和非对称加密算法.

**对称加密算法**

使用同一密钥进行加解密. 例如之前介绍的 xor, 也可以算作对称加密算法.

**非对称加密算法**

使用不同密钥进行加解密, 公开的叫公钥, 不公开的叫私钥, 使用公钥加密, 私钥解密.

RSA 是一种典型的非对称加密算法.

# 数论

简单介绍一点数学知识.

**质数**

除了 1 和它本身以外不再有其它因数的自然数.

**最大公因数**

两个或两个以上的数中最大的共有因数.

**最小公倍数**

两个或两个以上的数中最小的共有倍数.

**互质关系**

对于两个数 a b, 如果 a 与 b 的公因数只有 1, 则 a 与 b 互质.

例如 1 和 2 互质, 15 和 23 互质.

**欧拉函数**

对于一个正整数 n, 在不大于 n 的范围中所有与它互质的数的总个数表示为 `φ(n)`.

`φ(n)` 叫做 n 的欧拉函数.

例如 正整数 4, 在 1,2,3,4 中, 4 与 1 互质, 4 与 3 互质, 则 `φ(4) = 2`.

计算欧拉函数分很多种情况, 这里就简单介绍两种, 后面进行加密的时候还会用到.

对于质数 a, 则 `φ(a) = a - 1`.

如果 c 可以分解为两个质数 a b 的乘积, 例如 6 = 2 x 3, 则 `φ(c) = φ(ab) = φ(a)φ(b)`, 又因为 `φ(a) = a - 1`, `φ(b) = b - 1`, 所以 `φ(c) = (a - 1)(b - 1)`.

**模反元素**

对于两个互质的正整数 a b, 总有整数 c, 使 `(ab) -1` 被 c 整除, 或者说 `ab` 被 n 除的余数是 1, c 就叫做 a 的模反元素.

例如 3 和 11 互质, 因为 `(3 x 4) = 12, (12 - 1) ÷ 11 = 1`, 所以 3 的模反元素就为 4.

当然模反元素不止一个, `(3 x 15) = 45, (45 - 1) ÷ 11 = 4`, 这里 15 也是 3 的模反元素.

# 生成密钥

**生成两个不相等的大质数 p q**

举个例子.

`p = 23`, `q = 67`

**计算 p q 的乘积 n**

`n = 23 x 67 = 1541`

**计算 n 的欧拉函数** `φ(n)`

`φ(n) = (p - 1)(q - 1)`

`φ(n) = 22 x 66 = 1452`

这里其实也可以计算出 `lcm(p - 1, q - 1)`, 即 p - 1 和 q - 1 的最小公倍数.

好像只是个范围, 数学系的学姐说这样也能求出 e 和 d 并成功进行信息的加解密.

**随机选择一个整数 e, 必须满足 `1 < e < φ(n)`, 且 e 与 `φ(n)` 互质**

`e = 5`

**计算 e 对于 `φ(n)` 的模反元素 d, 使 `ed - 1` 能被 `φ(n)` 整除, 且 `1 < d < φ(n)`**

`ed = 1 (mod φ(n))`

`d = 581`

**将 n 和 e 封装为公钥, n d 封装为私钥**

`pub = (n, e) = (1541, 5)`

`pri = (n, d) = (1541, 581)`

# 信息加密

假设信息为 m , 其中 m 必须为整数, 且 `m < n`.

`m = ord('A') = 65`

加密公式

`me = c (mod n)`

已知 m e n, 求 c

Python

`c = (m ** e) % n`

计算出 `c = 839`

# 信息解密

解密公式

`cd = m (mod n)`

已经 c d n, 求 m

Python

`m = (c ** d) % n`

计算出 `m = 65 chr(m) = 'A'`

# 实践

Python 实现的简单 RSA

```
#!/usr/bin/python3
import random
import string
import math

def gcd(a, b):
    if a % b == 0:
        return b
    else:
        return gcd(b, a % b)

def lcm(a, b):
    if a * b == 0:
        return 0
    return a * b // gcd(a, b)

def prime(n):
    if n == 2 or n == 3:
        return True
    if n % 6 != 1 and n % 6 != 5:
        return False
    t = int(math.sqrt(n))
    for i in range(5,t + 1):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True

def rnd_pq(size):
    while True:
        p = int(''.join(random.sample(string.digits,size)))
        q = int(''.join(random.sample(string.digits,size)))
        if prime(p) and prime(q):
            if p != q:
                return p, q

def rel_e(l):
    for e in range(2, l):
        if gcd(e, l) == 1:
            return e

def mod_d(e, l):
    for d in range(2, l):
        if  (e * d) % l == 1:
            return d

def encrypt(m, pub):
    n = pub[0]
    e = pub[1]
    c = (m ** e) % n
    return c

def decrypt(m, pri):
    n = pri[0]
    d = pri[1]
    m = (c ** d) % n
    return m

p, q = rnd_pq(2)
n = p * q
l = lcm(p - 1, q - 1)
e = rel_e(l)
d = mod_d(e, l)
pub = (n, e)
pri = (n, d)
m = 65
c = encrypt(m, pub)
cm = decrypt(c, pri)
print(m, c, cm)
```