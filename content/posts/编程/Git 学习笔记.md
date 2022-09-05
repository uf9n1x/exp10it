---
title: "Git 学习笔记"
date: 2017-12-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['note']
categories: ['编程']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

Git 学习笔记

<!--more-->

# 基本操作

初始化仓库

`git init`

添加文件到暂存区

`git add file`

提交到版本库

`git commit -m 'text'`

比较文件

`git diff file`

# 日志

查看工作区状态

`git status`

查看当前commit记录

`git log`

查看所有commit记录

`git reflog`

# 版本回退

回退指定版本

`git reset --hard HEAD^`

`git reset --hard HEAD~n`

`git reset --hard commit id`

撤销暂存区文件

`git reset HEAD file`

撤销工作区文件

`git checkout -- file`

删除版本库文件

`git rm file`

# 远程库

添加远程库

`git remote add origin`

删除远程库

`git remote rm origin`

推送

`git push -u origin master`

`git push origin master`

拉取

`git pull remote master`

克隆

`git clone`

# 分支

创建并切换分支

`git checkout -b name`

创建分支

`git branch name`

切换分支

`git checkout name`

查看当前分支

`git branch`

合并分支

`git merge name`

删除分支

`git branch -d name`

# 标签

添加标签

`git tag`

指定添加标签

`git tag commit id`

查看标签commit内容

`git show tag name`

删除标签

`git tag -d name`

推送标签

`git push remote tag name`