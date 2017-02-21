#! -*- coding: utf8 -*-

import json
import requests
from collections import defaultdict
import re
from operator import itemgetter
import datetime
import time
import operator

import jieba
import jieba.posseg as pseg
import jieba.analyse
from bosonnlp import BosonNLP

from crawler import crawler

class Recorder:
    keywords = ''
    target_f = ''
    
    def get_keywords(self, keywords):
        self.keywords = keywords

    def init_rec_file(self, target_f):
        self.target_f = target_f
        with open(target_f, 'wb') as f:
            pass

    def record(self, s_name, content):
        with open(self.target_f, 'ab') as f:
            if ',' in s_name:
                s_name = s_name.replace(',', '|')
            f.write(s_name)
            sorted_content = sorted(content.items(), key=operator.itemgetter(1), reverse=True)
            words = sorted_content[0:30]
            for word, freq in words:
                if word == 'total':
                    continue
                f.write(',{word}'.format(word=word.encode('GBK')))
            f.write(',总量'.decode('utf8').encode('GBK') + '\n')
            for word, freq in words:
                if word == 'total':
                    continue
                f.write(',{freq}'.format(freq=freq))
            f.write(',{total}'.format(total=content['total']))
            f.write("\n")
            total = content['total']
            for word, freq in words:
                if word == 'total':
                    continue
                f.write(',{percent:.2f}%'.format(percent=(100 * freq / total)))
            f.write("\n")
        
if __name__ == '__main__':
    # Get now timestamp
    now_time = time.time()

    # Files' name
    dir_res = 'result/'
    dir_debug = 'debug/'
    f_wc_res = 'word_cut_result.csv'
    f_text = 'text.log'
    f_filtered = 'filered_msg.log'

    f_stocks = 'stocks_list.txt'
    
    f_stopwords = 'stopwords.txt'
    f_keywords = 'keywords.txt'

    f_user_defined_dict = 'user_defined_dict.txt'

    # Use user defined dictionary.
    jieba.load_userdict(f_user_defined_dict)

    # get stocks names
    with open(f_stocks) as f:
        stocks_name = f.readlines()
        stocks_name = [x.strip('\n') for x in stocks_name]

    # get nlp tool instance
    #bosonnlp_token = 'r-RR3P--.12747.KxRTq0OJ_i0S'
    #b_nlp = BosonNLP(bosonnlp_token)

    # get stopwords
    with open(f_stopwords) as f:
        stopwords = f.readlines()
        stopwords = [x.strip('\n').decode('utf8') for x in stopwords]

    """
    # Get keywords and give it to jieba
    for s_name in stocks_name:
        t = s_name + "_" + f_keywords
        jieba.load_userdict(t)
    """

    # set filters
    BEGIN_TIME = 1464710400 # 20160601
    invalid_user_id = [-1]
    invalid_source = ['持仓盈亏']

    # Analyse related values
    grain_size = 7 * 24 * 60 * 60 # 7 days

    # Init a recorder for this stock
    recorder = Recorder()
    #recorder.get_keywords(keywords)
    recorder.init_rec_file(dir_res + f_wc_res)
        
    for str_s_name in stocks_name:
        fenci_res = defaultdict(int)
        tags_res = []
        
        list_s_name = str_s_name.split(',')
        for s_name in list_s_name:
            """
            #Get stock's keywords
            with open(s_name + "_" + f_keywords) as f:
                keywords = [x.strip("\n").decode('utf8') for x in f.readlines()]
            """

            complete = 0
            page = 0

            start_time = now_time
            end_time = now_time - grain_size
            
            while not complete:
                # Get html content until content is valid
                try_time = 0
                while True:
                    time.sleep(2.1)
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

                for msg in json_res['list']:
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
                    #seg = jieba.cut(text, cut_all=False)
                    seg = pseg.cut(text)
                    showed_words = []
                    for word, flag in seg:
                        if word in stopwords:
                            continue
                        # Longer than 2 chinese characters.
                        if len(word) < 2:
                            continue
                        # Must be noun.
                        if 'n' not in flag:
                            continue
                        # Remove duplicate.
                        if word in showed_words:
                            continue
                        fenci_res[word] += 1
                        showed_words.append(word)
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
        recorder.record(str_s_name, fenci_res)

