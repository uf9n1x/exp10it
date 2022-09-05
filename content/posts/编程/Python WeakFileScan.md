---
title: "Python WeakFileScan"
date: 2018-05-05T00:00:00+08:00
draft: false
author: "X1r0z"

tags: ['python']
categories: ['编程']

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---

WeakFileScan 是基于 Python 的网站备份检测脚本.

<!--more-->

Python 3.6

```
集成常见的文件名 如 web www wwwroot backup back data
支持多种压缩格式 如 rar zip tar.gz tar.bz2 tar.xz 7z
```

## Usage

```
-u 目标 url (需加 http)
-t 线程数 (默认为 2)
-a 输出详细信息
```

## Output

```
2018-05-05 12:26:05,596 - INFO - GET http://www.xxx.com/www.zip
2018-05-05 12:26:05,757 - INFO - GET http://www.xxx.com/www.tar.gz
2018-05-05 12:26:06,047 - INFO - GET http://www.xxx.com/xxx.rar
2018-05-05 12:26:06,092 - INFO - GET http://www.xxx.com/xxx.zip
2018-05-05 12:26:06,175 - INFO - GET http://www.xxx.com/xxx.tar.gz
2018-05-05 12:26:17,716 - WARNING - FOUND http://www.xxx.com/www.xxx.com.tar.gz
```

## Code

```
from urllib import parse
import threading
import argparse
import requests
import logging
import queue

parser = argparse.ArgumentParser()
parser.add_argument('url',help='Target url')
parser.add_argument('-t',help='Thread number',type=int,default=2)
parser.add_argument('-a',help='Show all message',action='store_const',const=logging.INFO,default=logging.WARNING)
args = parser.parse_args()

logging.basicConfig(level=args.a,format='%(asctime)s - %(levelname)s - %(message)s')

class WeakFileScan(object):
	def __init__(self,url,threads):
		self.url = url
		self.threads = threads
		self.queue = queue.Queue()
		self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36','X-Forwarded-For':'127.0.0.1'}

	def run(self):
		for item in self._dict():
			self.queue.put(item)
		for _ in range(self.threads):
			t = threading.Thread(target=self._request)
			t.start()
		t.join()

	def _request(self):
		while not self.queue.empty():
			url = self.queue.get()
			logging.info('GET {0}'.format(url))
			resp = requests.head(url,headers=self.headers)
			if resp.status_code == 200:
				logging.warning('FOUND {0}'.format(url))

	def _parse(self,url):
		obj = parse.urlparse(url)
		return obj.netloc

	def _join(self,*args):
		obj = parse.urljoin(*args)
		return obj

	def _dict(self):
		url = self._parse(self.url)
		a = ('bak','backup','www','web','wwwroot','beifen','ftp','website','back','backupdata','temp','htdocs','database','data','user','admin','test','conf','config','db','sql','install','w','bf','aaa','0','1','2','3','4','5','6','7','8','9')
		b = (url,url.replace('.',''),url.split('.',1)[1],url.split('.',1)[0],url.split('.')[1],url.split('.')[-1])
		c = ('.rar','.zip','.tar','.tar.gz','.tar.bz2','.tar.xz','.gz','.bz2','.xz','.tgz','.7z','.z')
		for x in a+b:
			for y in c:
				yield self._join(self.url,x+y)

Scanner = WeakFileScan(args.url,args.t)
Scanner.run()
```