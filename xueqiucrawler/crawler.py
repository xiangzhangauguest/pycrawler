import json
import requests
from collections import defaultdict
import re
from operator import itemgetter

import jieba

def crawler(page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=WB&hl=0&source=all&sort=time&page={page}&_=1483939336621'.format(page=page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Host': 'xueqiu.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://xueqiu.com/S/WB',
        'Cookie': 's=5r11gm4726; xq_r_token=e386c2c5442603d86294a718b13da436909b3f07; u=341483007204349; _sid=qaxE4GIPGdismx6xBWl5EHgKDa1WXh; xq_a_token=fa4b993b49cc434e60f8eed7fd93599969c092c1; xq_is_login=1; bid=f7e919156871e526c88cc617624b4f25_ixa9haoo; webp=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1483007469,1483009225,1483083745,1483094424; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1483939336; __utmt=1; __utma=1.755614866.1482394030.1483934576.1483939336.9; __utmb=1.1.10.1483939336; __utmc=1; __utmz=1.1483083745.5.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic'
    }

    html = requests.get(url, headers=headers)
    print html
    return html

if __name__ == '__main__':
    BEGIN_TIME = 1480521600
    complete = 0
    page = 1
    fenci_res = defaultdict(int)
    while True:
        print page
        html = crawler(page)

        json_res = json.loads(html.text)

        with open('text.log', 'ab') as f:
            for msg in json_res['list']:
                if (msg['created_at'] / 1000) < BEGIN_TIME:
                    complete = 1
                    break
                text = msg['text'].encode('utf8')
                f.write(text + '\n')
                text = re.sub('<a.*?</a>', '', text)
                text = re.sub('<img.*?/>', '', text)
                text = re.sub('//.*?$', '', text).strip(' ')
                f.write(text + '\n')
                seg = jieba.cut(text, cut_all=False)
                for word in seg:
                    fenci_res[word] += 1
                    f.write(word.encode('utf8') + ' ')
                f.write('\n' + '\n')

        if complete:
            sorted_fenci_res = sorted(fenci_res.iteritems(), key=itemgetter(1), reverse=True)
            with open('fenci_result.log', 'wb') as f:
                for word, freq in sorted_fenci_res:
                    #print type(word)
                    f.write('{word}: {freq}\n'.format(word=word.encode('utf8'), freq=freq))
            break
        else:
            page += 1
