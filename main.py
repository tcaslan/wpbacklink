import requests
import bs4
import lxml
from requests import get,post
from bs4 import BeautifulSoup as bs 
import json
import urllib3
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
links = open('links.txt').read().splitlines()
headers = {
    'authority': 'google.cx',
    'cache-control': 'max-age=0',
    'origin': 'https://google.cx',
    'upgrade-insecure-requests': '1',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
    'sec-fetch-dest': 'document',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'referer': 'https://google.cx/',
    'accept-language': 'en-US,en;q=0.9',
}

data = json.load(open('postData.json'))
for link in links:
	print("[+] ID")
	try:
		r = get(link,verify=False)
	except Exception as e:
		print("[-] Link Hata:",link)
		print()
		continue
	if not r:
		print("[-] 404 Link:",link)
		print()
		continue
	soup = bs(r.text,'lxml')
	form = soup.find(id='commentform')
	if not form:
		print("[-] Yorum Formu Bulunamadı")
		print()
		continue
	print("[+] Form Bulundu",link)
	inputs = {inp['name']:inp.get('value','') for inp in form.findAll(attrs={"name":True})}
	for field in ['comment_post_ID','comment_parent','ak_js']:
		if field in inputs:
			data[field] = inputs.get(field,'')
	linkParse = urlparse(link)
	postLink = form.get('action',f"{linkParse.scheme}://{linkParse.netloc}/wp-comments-post.php")
	print("[+] Form Gönderiliyor")
	headers['referer'] = link
	headers['origin'] = f"{linkParse.scheme}://{linkParse.netloc}"
	headers['authority'] = f"{linkParse.netloc}"
	try:
		r = post(postLink,verify=False,data=data,headers=headers)
		print("[+] Form Gönderildi")
	except:
		print("[-] Form Gönderilirken Hata Oluştu")
		print()
		continue
	open('success.txt','a').write(f'{link}\n')
	print()
