import requests

def crawler(s_name, page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={s_name}&hl=0&source=all&sort=time&page={page}'.format(s_name=s_name, page=page)
    headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Host': 'xueqiu.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://xueqiu.com/S/{s_name}'.format(s_name=s_name),
            'Cookie': 'aliyungf_tc=AQAAADP11j6lnAQAgpiHPQ9Z+A27Vh/e; u=221487852825437; u.sig=t3pefeJ2YP9C-iEVEs5cT9e6oL4; xq_a_token=280dee5696661da23161c033e7ce7facef8af94d; xq_a_token.sig=jvgfBt0IPrEBGqhhWZCXMCzIcMo; xq_r_token=184a2c0e20d72c3b3f23c2a1587bae0798adf96d; xq_r_token.sig=ptgAVJkPu7bY-y_cplgoXV79bQo; s=7a13jdw08u; __utmt=1; Hm_lvt_1db88642e346389874251b5a1eded6e3=1487852826; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1487852863; __utma=1.400462993.1487852833.1487852833.1487852833.1; __utmb=1.2.10.1487852833; __utmc=1; __utmz=1.1487852833.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
    }

    html = requests.get(url, headers=headers)
    return html

