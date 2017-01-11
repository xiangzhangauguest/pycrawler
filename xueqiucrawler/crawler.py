#! -*- coding: utf8 -*-

import json
import requests
from collections import defaultdict
import re
from operator import itemgetter

import jieba
import jieba.analyse

def crawler(s_name, page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={s_name}&hl=0&source=all&sort=time&page={page}&_=1483939336621'.format(s_name=s_name, page=page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Host': 'xueqiu.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://xueqiu.com/S/{s_name}'.format(s_name=s_name),
        'Cookie': 's=5r11gm4726; xq_r_token=e386c2c5442603d86294a718b13da436909b3f07; u=341483007204349; _sid=qaxE4GIPGdismx6xBWl5EHgKDa1WXh; xq_a_token=fa4b993b49cc434e60f8eed7fd93599969c092c1; xq_is_login=1; bid=f7e919156871e526c88cc617624b4f25_ixa9haoo; webp=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1483007469,1483009225,1483083745,1483094424; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1483939336; __utmt=1; __utma=1.755614866.1482394030.1483934576.1483939336.9; __utmb=1.1.10.1483939336; __utmc=1; __utmz=1.1483083745.5.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic'
    }

    html = requests.get(url, headers=headers)
    return html

def crawlerZNH(page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol=ZNH&hl=0&source=all&sort=time&page={page}&_=1484102611941'.format(page=page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Host': 'xueqiu.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://xueqiu.com/S/ZNH',
        'Cookie': 's=5r11gm4726; xq_r_token=e386c2c5442603d86294a718b13da436909b3f07; u=341483007204349; _sid=qaxE4GIPGdismx6xBWl5EHgKDa1WXh; xq_a_token=fa4b993b49cc434e60f8eed7fd93599969c092c1; xq_is_login=1; bid=f7e919156871e526c88cc617624b4f25_ixa9haoo; webp=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1483007469,1483009225,1483083745,1483094424; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1483939336; __utmt=1; __utma=1.755614866.1482394030.1483934576.1483939336.9; __utmb=1.1.10.1483939336; __utmc=1; __utmz=1.1483083745.5.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic'
    }

    html = requests.get(url, headers=headers)
    return html

if __name__ == '__main__':
    stop_words = [
	' ',
	' ',
        '，',
        '。',
        '、',
        '？',
        '（',
        '）',
        '：',
        '%',
        '“',
        '”',
        '；',
        '—',
        '...',
        '-',
        '.',
        '/',
        '——',
        '！',
        '，：',
        ';',
        ',',
        ':',
        '：',
        '(',
        ')',
        '【',
        '】',
        '+',
        '《',
        '》',
        '!',
        '他',
        '她',
        '的',
        '了',
        '是',
        '和',
        '在',
        '我',
        '都',
        '也',
        '这'
    ]
    stocks_name = ['WB', 'ZNH']
    for s_name in stocks_name:
        BEGIN_TIME = 1480521600
        complete = 0
        page = 1
        fenci_res = defaultdict(int)
        tags_res = []
        while True:
            html = crawler(s_name, page)

            json_res = json.loads(html.text)

            with open('text_{s_name}.log'.format(s_name=s_name), 'ab') as f:
                for msg in json_res['list']:
                    if (msg['created_at'] / 1000) < BEGIN_TIME:
                        complete = 1
                        break
                    text = msg['text'].encode('utf8')
                    f.write(text + '\n')
                    text = re.sub('<a.*?</a>', '', text)
                    text = re.sub('<img.*?>', '', text)
                    text = re.sub('<.*?>', '', text)
                    text = text.replace('&nbsp', '')
                    text = re.sub('//.*?$', '', text).strip(' ')
                    f.write(text + '\n')
            
                    # word cut
                    seg = jieba.cut(text, cut_all=False)
                    for word in seg:
                        fenci_res[word] += 1
                        f.write(word.encode('utf8') + ' ')
                    
                    # tag
                    tags = jieba.analyse.extract_tags(text, topK=5)
                    #tags_res.append(tags)
                    f.write('\n' + '  '.join(tags).encode('utf8') + '\n')
                    f.write('\n')

            if complete:
                sorted_fenci_res = sorted(fenci_res.iteritems(), key=itemgetter(1), reverse=True)
                with open('fenci_result_{s_name}.csv'.format(s_name=s_name), 'wb') as f:
                    for word, freq in sorted_fenci_res:
                        #print type(word)
                        word = word.encode('utf8')
                        if word not in stop_words:
                            try:
                                word = word.decode('utf8').encode('GBK')
                            except:
                                pass
                            f.write('{word},{freq}\n'.format(word=word, freq=freq))
                break
            else:
                page += 1
