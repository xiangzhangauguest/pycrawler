import requests

def crawler(s_name, page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={s_name}&hl=0&source=all&sort=time&page={page}'.format(s_name=s_name, page=page)
    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
            'Host': 'xueqiu.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://xueqiu.com/S/{s_name}'.format(s_name=s_name),
            'Cookie': 's=7w127rvp9d; xq_a_token=4939ec38314fd03eb90e7d93a689a274dfb6487e; xq_r_token=f9162a16f515c6e1105bb2d2366276607af6e5f0; u=651486551502810; Hm_lvt_1db88642e346389874251b5a1eded6e3=1486551618; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1486551626; __utma=1.1328674304.1486551628.1486551628.1486551628.1; __utmb=1.1.10.1486551628; __utmc=1; __utmz=1.1486551628.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1'
    }

    html = requests.get(url, headers=headers)
    return html

