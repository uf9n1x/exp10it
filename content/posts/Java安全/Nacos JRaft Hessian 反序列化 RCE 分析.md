---
title: "Nacos JRaft Hessian 反序列化 RCE 分析"
date: 2023-06-08T11:49:07+08:00
lastmod: 2023-06-08T11:49:07+08:00
draft: false
author: "X1r0z"

tags: ['nacos', 'jraft', 'hessian']
categories: ['Java安全']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

期末周了, 先占个坑 (

<!--more-->

参考链接

[https://github.com/alibaba/nacos/releases/tag/2.2.3](https://github.com/alibaba/nacos/releases/tag/2.2.3)

[https://github.com/alibaba/nacos/pull/10542/commits](https://github.com/alibaba/nacos/pull/10542/commits)

[https://www.sofastack.tech/projects/sofa-jraft/jraft-user-guide/](https://www.sofastack.tech/projects/sofa-jraft/jraft-user-guide/)

[https://www.cnblogs.com/kingbridge/articles/16717030.html](https://www.cnblogs.com/kingbridge/articles/16717030.html)

[http://www.bmth666.cn/bmth_blog/2023/02/07/0CTF-TCTF-2022-hessian-onlyJdk](http://www.bmth666.cn/bmth_blog/2023/02/07/0CTF-TCTF-2022-hessian-onlyJdk)