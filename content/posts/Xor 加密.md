---
title: "Xor 加密"
date: 2018-07-30T00:00:00+08:00
draft: false
tags: ['xor']
categories: ['算法']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

xor 异或运算表示两个操作数的位中, 相同则为0, 不同则为1.

<!--more-->

xor 的运算符一般为 `^` 或者 `XOR`, 例如 `110^011` 表示对 110 和 011 两个二进制数进行异或运算.

```
111^101 010
110^110 000
101^010 111
```

xor 有个很神奇的特点, 对于两个二进制数 a b, 如果 `a^b = c`, 那必有 `c^b = a`.

```
010^101 111
000^110 110
111^010 101
```

基于这种特性, 就衍生出了 xor 加密.

`message XOR key //cipher`

`cipher XOR key //message`

注意在加解密前后, key 的长度必须大于等于 message 或者 cipher 的长度.

python 的 xor 加密实现

```
message = 'Hello World'
key = 'exp10itexp10itexp10it'

cipher = ''
for i,j in zip(message,key):
    cipher += chr(ord(i)^ord(j))
```

`cipher: '-\x1d\x1c]_I#\n\n\x1cU'`

解密同理

```
cipher = '-\x1d\x1c]_I#\n\n\x1cU'
key = 'exp10itexp10itexp10it'

message = ''
for i,j in zip(cipher,key):
    message += chr(ord(i)^ord(j))
```

`message: Hello World`