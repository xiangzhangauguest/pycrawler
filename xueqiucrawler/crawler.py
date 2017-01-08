import requests

url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=WB&hl=0&source=all&sort=alpha&page=1&_=1483888712749'
headers = {
	'User-Agent': '"Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0"',
	'Host': 'xueqiu.com',
	'Accept': 'application/json, text/javascript, */*; q=0.01',
	'Referer': 'https://xueqiu.com/S/WB',
	'Cookie': 'Hm_lvt_1db88642e346389874251b5a1eded6e3=1483793124,1483844385,1483878869,1483878874; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1483889168; s=7i17flg74n; xq_a_token=660255dff38226bba32536d4e308cdbc3399aafe; xq_r_token=9d1de96fdd5ebd54732f300ef44f779ca6e5716f; u=71483868100216; __utma=1.675574121.1483878872.1483884676.1483887568.4; __utmc=1; __utmz=1.1483878872.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utmb=1.15.10.1483887568; __utmt=1'
}

html = requests.get(url, headers=headers)
with open('result.log', 'wb') as f:
	f.write(html.text.encode('utf8'))
print html
