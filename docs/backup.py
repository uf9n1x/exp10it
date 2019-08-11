import requests
import time
import json
import sys
import os

reload(sys)
sys.setdefaultencoding('utf8')

folder = 'posts/'

if not os.path.exists(folder):
	os.mkdir(folder)

token = 'c#c8d8b28cd9f7cda349#d0818fc56b9955d3c03a#0'

url = 'https://api.github.com/repos/X1r0z/exp10it/issues'

headers = {
	'Accept': 'application/vnd.github.v3+json',
	'Authorization': token.replace('#', '')
}

p = 1

while True:
	params = {
	'filter': 'created',
	'page': p
	}
	response = requests.get(url, params=params, headers=headers)
	data = json.loads(response.text)
	if not data:
		break
	for item in data:
		title, rawdate = item['title'].split(' #')
		body = item['body']
		date = time.strftime('%Y-%m-%d', time.strptime(rawdate, '%b %d, %Y'))
		with open (folder + date + ' ' + title + '.md', 'w+') as f:
			f.write(body)
		print title,'OK'
	p += 1