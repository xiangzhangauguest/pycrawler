#! -*- coding: utf8 -*-

import json
import requests
from collections import defaultdict
import re
from operator import itemgetter
import datetime
import time

import jieba
import jieba.analyse
from bosonnlp import BosonNLP

def crawler(s_name, page):
    url = 'https://xueqiu.com/statuses/search.json?count=10&comment=0&symbol={s_name}&hl=0&source=all&sort=time&page={page}&_=1486548896521'.format(s_name=s_name, page=page)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Host': 'xueqiu.com',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://xueqiu.com/S/{s_name}'.format(s_name=s_name),
        'Connection': 'keep-alive',
        'Cookie': 's=5u11qd0x09; xq_a_token=4939ec38314fd03eb90e7d93a689a274dfb6487e; xq_r_token=f9162a16f515c6e1105bb2d2366276607af6e5f0; u=941486551063854; Hm_lvt_1db88642e346389874251b5a1eded6e3=1486551276; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1486551279; __utmt=1; __utma=1.520347875.1486551279.1486551279.1486551279.1; __utmb=1.1.10.1486551279; __utmc=1; __utmz=1.1486551279.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
    }

    html = requests.get(url, headers=headers)
    return html

class Recorder:
    keywords = ''
    target_f = ''
    
    def get_keywords(self, keywords):
        self.keywords = keywords

    def init_rec_file(self, target_f):
        self.target_f = target_f
        with open(target_f, 'wb') as f:
            keywords = [x.encode('GBK') for x in self.keywords] + ['总量'.decode('utf8').encode('GBK')]
            f.write('date,' + ','.join(keywords) + '\n')

    def record(self, content, start_time, end_time):
        with open(self.target_f, 'ab') as f:
            f.write(datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d') + "--" +
                    datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d'))
            for keyword in self.keywords:
                freq = content[keyword]
                f.write(',{freq}'.format(freq=freq))
            f.write(',{total}'.format(total=content['total']))
            f.write("\n")
        
if __name__ == '__main__':
    # get stocks names
    stocks_name = ['WB', 'SOHU', 'NTES']

    # Get now timestamp
    now_time = time.time()

    # Files' name
    dir_res = 'result/'
    dir_debug = 'debug/'
    f_wc_res = 'word_cut_result.csv'
    f_text = 'text.log'
    f_filtered = 'filered_msg.log'

    f_stopwords = 'stopwords.txt'
    f_keywords = 'keywords.txt'

    # get nlp tool instance
    #bosonnlp_token = 'r-RR3P--.12747.KxRTq0OJ_i0S'
    #b_nlp = BosonNLP(bosonnlp_token)

    # get stopwords
    with open(f_stopwords) as f:
        stopwords = f.readlines()
        stopwords = [x.strip('\n') for x in stopwords]

    # Get keywords and give it to jieba
    for s_name in stocks_name:
        t = s_name + "_" + f_keywords
        jieba.load_userdict(t)

    # set filters
    BEGIN_TIME = 1464710400 # 20160601
    invalid_user_id = [-1]
    invalid_source = ['持仓盈亏']

    # Analyse related values
    grain_size = 7 * 24 * 60 * 60 # 7 days

    for s_name in stocks_name:
        #Get stock's keywords
        with open(s_name + "_" + f_keywords) as f:
            keywords = [x.strip("\n").decode('utf8') for x in f.readlines()]

        complete = 0
        page = 0
        fenci_res = defaultdict(int)
        tags_res = []

        # Init a recorder for this stock
        recorder = Recorder()
        recorder.get_keywords(keywords)
        recorder.init_rec_file(dir_res + s_name + "_" + f_wc_res)
        
        start_time = now_time
        end_time = now_time - grain_size

        while not complete:
            # Get html content until content is valid
            try_time = 0
            while True:
                html = crawler(s_name, page)
                if html.status_code == 200:
                    break
                try_time += 1
                if try_time > 10:
                    print "tried 10 times but still not word, exist"
                    break
                print html
                print html.text
                print page
                time.sleep(300)
            page += 1
            if page > 100:
                complete = 1

            json_res = json.loads(html.text)

            with open(dir_res + '{s_name}_{f_text}'.format(s_name=s_name, f_text=f_text), 'ab') as f:

                for msg in json_res['list']:

                    created_at = datetime.datetime.fromtimestamp(msg['created_at'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Rule of stop
                    created_ts = msg['created_at'] / 1000
                    if created_ts < end_time:
                        recorder.record(fenci_res, start_time, end_time)
                        if end_time < BEGIN_TIME:
                            complete = 1
                            break
                        fenci_res = defaultdict(int)
                        start_time = end_time
                        end_time = start_time - grain_size
                    # Filter
                    if msg['user_id'] in invalid_user_id:
                        continue
                    if msg['source'].encode('utf8') in invalid_source:
                        continue

                    text = msg['text']
                    text = re.sub('<.*?>', '', text)
                    text = text.replace('&nbsp', '')
                    #text = text.replace('$', '')
                    text = re.sub('//.*?$', '', text).strip(' ')
                    #f.write(text.encode('utf8') + '\n')
                    
                    # word cut
                    seg = jieba.cut(text, cut_all=False)
                    for word in seg:
                        fenci_res[word] += 1
                    fenci_res['total'] += 1
                    
                    """
                    # tag
                    tags = jieba.analyse.extract_tags(text, topK=5)
                    #tags_res.append(tags)
                    f.write('\n' + '  '.join(tags).encode('utf8') + '\n')

                    # Summary
                    result = b_nlp.summary('', text)
                    f.write('[{time}]: {summary}'.format(time=created_at, summary=result.encode('utf8')))
                    f.write('\n\n')
                    """

