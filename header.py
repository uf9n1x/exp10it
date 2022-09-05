import os

doc = os.listdir('.')

for filename in doc:
    if filename == 'header.py':
        break
    with open(filename, 'r', encoding="utf-8") as f:
        content = f.readlines()

    with open(filename, 'w', encoding="utf-8") as f:
        text='''---
{}
{}
draft: false
author: "X1r0z"

{}
{}

hiddenFromHomePage: false
hiddenFromSearch: false

toc:
  enable: true
math:
  enable: false
lightgallery: false
---
{}'''.format(content[1].rstrip('\n'), content[2].rstrip('\n'), content[6].rstrip('\n'), content[7].rstrip('\n'), ''.join(content[33:]))
        f.write(text)