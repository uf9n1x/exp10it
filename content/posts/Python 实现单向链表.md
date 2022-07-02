---
title: "Python 实现单向链表"
date: 2018-02-19T00:00:00+08:00
draft: false
tags: ['python']
categories: ['编程']
author: "X1r0z"

# weight: 1  # Top page

# You can also close(false) or open(true) something for this content.
# P.S. comment can only be closed
comment: false
toc: false
autoCollapseToc: false
---

链表是一种物理存储单元上非连续、非顺序的存储结构, 数据元素的逻辑顺序是通过链表中的指针链接次序实现的.

<!--more-->

## 介绍

链表的基本单位为 node

node 存储 data 和 next

data: 数据

next: 指向下一个 node 的指针

插入单位为 n 的数据 时间复杂度为 `O(1)`

查找单位为 n 的数据 时间复杂度为 `O(n)`

## 代码

node

```
class Node(object):
    def __init__(self,data):
        self.data = data
        self.next = None

    def __repr__(self):
        return str(self.data)
```

链表

```
class Link(object):
    def __init__(self,head=None):
        self.head = Node(head)
        if head:
            self.length = 1
        else:
            self.length = 0

    def __len__(self):
        return self.length

    def __str__(self):
        current = 0
        p = self.head
        item = '['
        while current <= self.length:
            item += ' ' + '\'' + str(p) + '\''
            p = p.next
            current += 1
        item += ' ]'
        return item

    def __call__(self):
        current = 0
        p = self.head
        while current <= self.length:
            yield p
            p = p.next
            current += 1
    
    def append(self,data):
        data = Node(data)
        if self.head == None:
            self.head = data
        else:
            p = self.head
            while p.next:
                p = p.next
            p.next,p.next.next = data,None
        self.length += 1

    def pop(self):
        p = self.head
        while p.next:
            p = p.next
            pp = p
        pp = None
        self.length -= 1       
    
    def insert(self,index,data):
        data = Node(data)
        if index == 0:
            p = self.head
            self.head = data
            self.head.next = p
        else:
            current = 0
            p = self.head
            while current <= self.length:
                if current +1 == index:
                    pp = p.next
                    p.next = data
                    p.next.next = pp
                    break
                else:
                    current += 1
                    p = p.next
        self.length += 1
    
    def delete(self,index):
        if index == 0:
            self.head = self.head.next
        else:
            current = 0
            p = self.head
            while current <= self.length:
                if current + 1 == index:
                    pp = p.next.next
                    p.next = pp
                    break
                else:
                    current += 1
                    p = p.next
        self.length -= 1
```