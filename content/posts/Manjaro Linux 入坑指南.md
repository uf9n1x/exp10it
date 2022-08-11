---
title: "Manjaro Linux 入坑指南"
date: 2018-08-10T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['linux','manjaro']
categories: ['linux']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

从 Deepin 换到了 Manjaro, 中间体验过 Ubuntu, 各种 PPA 加上网上零零散散的 deb 包, 找起来挺费事的

去年折腾过 Arch, 安装过程其实很简单, 基本上就是 `分区 -> 挂载 -> chroot -> base 系统安装 -> 各种系统设置 -> grub` 走一遍

没遇到过滚挂的情况, 但用起来总觉得怪怪的

Arch 系的发行版还有 antergos, 据说用户体验不怎么好

<!--more-->

# 特点

**滚动更新** 一个命令就能更新到最新的版本, 不需要像 Ubuntu 跨系统升级那样进行繁琐的操作

**强大的 AUR 软件仓库** 目前 AUR 中的软件数量是最多的

**开箱即用** 省去了安装 Arch Linux 的复杂过程, 内置各种常用工具, 第三方软件基本靠 pacman 或 yaourt 就能搞定

**稳定** Manjaro 的软件仓库的所有分支 unstable testing stable 都比原 Arch 的推迟几天到几星期, 一般不容易滚挂

目前 Manjaro 在 DistroWatch 中排名第一

# 桌面选择

个人还是比较喜欢 KDE, 特效 过渡动画都挺好看, 加上一些 K 系列的软件, Koncolse Kate 什么的, 缺点就是电脑配置太低会卡卡的

XFCE 比 KDE 更轻量了, 低配电脑首选, 自己折腾一会的美观度不比 KDE 差, 不过像我这种手残的就算了吧

GNOME 不怎么喜欢, 大概还需要自己搞一下才能提高日常使用的效率

至于 i3 Awesome 之类的 “轻量级” 桌面, 如果不是那种装逼党的话尽量别用, 好的桌面不是让用户来熟悉的

# 系统配置

## 国内源

Manjaro 中已经内置了国内的镜像源, 使用 `pacman-mirrors` 选择源

```
sudo pacman-mirrors -i -c China -m rank
```

执行中会弹出对话框让你选择软件源, 勾选后记得点击确定

使用国内的 AUR 源

编辑 `/etc/pacman.conf`, 在最后加入内容

```
[archlinuxcn]
Server = http://repo.archlinuxcn.org/$arch
```

保存后执行命令

```
sudo pacman -Syy
sudo pacman -S archlinuxcn-keyring
```

## yaourt

yaourt 是一款和 pacman 类似, 提供了 AUR 支持的包管理器

可从仓库中下载 PKGBUILD 并进行编译安装

```
pacman -S yaourt
```

操作方式几乎与 pacman 一样

```
yaourt -Syyu
yaourt -S INSTALL_PACKAGE_NAME
yaourt INSTALL_PACKAGE_NAME
```

## oh-my-zsh

zsh 是一款比 bash 更强大的 shell

oh-my-zsh 在 Manjaro 源中已提供, 直接安装即可

```
pacman -S zsh oh-my-zsh-git
```

更改主题

`vim ~/.zshrc`

全部主题可在 github 上查看截图, 我用的是 agnoster

```
ZSH_THEME="agnoster"
```

## Konsole

XFCE 的直接跳过, GNOME 你懂的

解决下默认 Konsole 的两个问题

先加上半透明效果

依次点击 `设置 - 配置 Konsole - 配置方案`

选择当前使用的配置方案

点击 `编辑配置方案- 外观`

选择颜色的样式

然后点击 `编辑`

自行更改背景透明度, 还有模糊背景 可选

之后就是默认配置执行 `neofetch` 或 `screenfetch` 出现字符不齐的问题

在选择颜色样式的时候, 在下面点击 `选择字体`

我用的是 `DejaVu Sans Mono` 加上 `Blod`, 总之不是默认的就好

## wine

最新 3.11 的 wine 有点问题, 不能正常运行 qq tim, 目前可用的办法就是降级

从 archive.archlinux.org 上下载旧版本的 wine 安装

```
wget https://archive.archlinux.org/packages/w/wine/wine-3.7-1-x86_64.pkg.tar.xz
sudo pacman -U wine-3.7-1-x86_64.pkg.tar.xz
```

# 日常软件

## QQ/TIM

不得不说 AUR 很强大, 之前在 Ubuntu 上折腾了 QQ 花了不少时间, 而 Manjaro 中 30 秒就搞定了

如果不能运行先参考之前降级 wine 的步骤

```
yaourt -S deepin-wine-qq
yaourt -S deepin-wine-tim
```

## 网易云音乐

不需要 root 权限就能运行, 也可以保存登录信息

```
yaourt -S netease-cloud-music
```

## 搜狗输入法

还是习惯搜狗, 当然也有谷歌拼音

```
yaourt -S fcitx fcitx-sogoupinyin fcitx-im kcm-fcitx
```

在 ~/.Xprofile 中添加以下内容

```
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XMODIFIERS="@im=fcitx"
```

重启后就可以使用了

## 坚果云

良心同步云盘, 国内 Dropbox

```
yaourt -S nutstore
```

## Sublime Text

代码编辑器, 但官方的版本不能输入中文, AUR 中有修复的软件包, 但是太老了

```
yaourt -S sublime-text-dev
```

## Chrome

Chrome 浏览器, Firefox 已内置

```
sudo pacman -S google-chrome
```

## 科学梯子

图形化界面, qt5 版本的只支持酸酸

```
yaourt -S electron-ssr

yaourt -S shadowsocks-qt5-git
```

## Enpass

```
yaourt -S enpass-bin
```

## PlayOnLinux

相当于免费版的 crossover, 玩玩还是可以的

```
sudo pacman -S playonlinux
```

## WPS

国内版 office, Manjaro 中已经内置了 LibreOffice

```
yaourt -S wps-office
```

## Pamac

听说 Manjaro 用的是这款图形化包管理器, 后来安装的时候已经换成 Octopi 了, 看个人喜好吧

```
sudo pacman -S pamac
```

## 迅雷

种子, 磁力链接下载神器, 之前在 deepin 用的时候发现已经不限速了

```
yaourt -S deepin-wine-thunderspeed
```

## Telegram

电报, 匿名的安全聊天软件, 需要科学梯子

```
sudo pacman -S telegram-desktop
```

## Wireshark

网络分析, 抓包工具, 做 CTF 中的流量分析类题目特别好用

```
sudo pacman -S wireshark-qt
```

# 滚挂

Arch 会滚挂, Manjaro 也会滚挂, 列出一些滚挂后的措施

日常准备 Manjaro 启动盘 liveCD , 便于进行回滚

滚挂一般都是 pacman 执行更新操作, 但某些包出现兼容性问题而导致的, `/var/log/pacman.log` 日志文件很重要

滚挂不一定是无法进入系统, 也可能是某个软件无法运行, 或者类似于桌面特效没有了

如果能判断是那个包导致滚挂的可到 archive.archlinux.org 上下载旧版软件包, 在 liveCD 中 chroot 然后 `pacman -U INSTALL_PACKAGE`

桌面滚挂的话键盘上 `Ctrl + Alt + F2` 切换至 tty 登录, 然后跟上面一样

一些比较重要的包如果可能导致滚挂, 官方会在博客上提前说明 [Manjaro.Org](https://manjaro.org/)

可向社区求助或百度, 也许不止有你一个人出现过这种问题

# 定期备份

`tar cvpjf backup.tar.bz2 --exclude-from=excl /`

excl 文件存放排除的目录

```
/proc/*
/dev/*
/sys/*
/tmp/*
/mnt/*
/media/*
/run/*
/var/lock/*
/var/run/*
/var/lib/pacman/*
/var/cache/pacman/pkg/*
/lost+found
```

# 还原备份

启动盘先进入 liveCD

挂载系统分区

```
mount /dev/sda1 /mnt
```

如果备份文件是在系统分区里面的, 直接移出来

不然就要再挂载一遍备份的分区

```
mkdir /backup
mount /dev/sda2 /backup
```

解压备份包

```
cd /mnt
tar xvpjf /backup/backup.tar.bz2
```

重新生成 fstab

```
genfstab -U -p /mnt >> /mnt/etc/fstab
```

安装 `mhwd-chroot`

```
pacman -S mhwd-chroot
```

chroot 系统分区

```
mhwd-chroot /mnt /bin/bash
```

重新配置引导

```
grub-mkconfig -o /boot/grub/grub.cfg
```

退出

```
exit
umount -R /mnt
reboot
```

# 社区

`Manjaro-Linux QQ 交流群: 478058928`

[Manjaro 吧](https://tieba.baidu.com/f?kw=manjaro)

[Arch 衍生板块](https://bbs.archlinuxcn.org/viewforum.php?id=26)

[Manjaro 中文论坛](https://www.manjaro.cn/bbs)