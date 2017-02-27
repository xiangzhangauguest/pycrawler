#! -*- coding: utf8 -*-

import json
import requests
from collections import defaultdict
import re
import time
import datetime
import operator

from crawler import crawler

if __name__ == '__main__':
    # Files' name
    dir_res = 'result/'
    f_res = 'daily_msg_count.csv'
    f_res2 = 'daily_msg_count2.csv'

    dir_backup = 'backup/'
    f_backup = 'backup.log'
    
    dir_last_timestamp = 'last_timestamp/'
    f_last_timestamp = 'last_timestamp.log'

    f_stocks = 'stocks_list.txt'

    # Set end date = last midnight
    yesterday_midnight = datetime.date.today().strftime("%s")

    # get stocks names
    with open(f_stocks) as f:
        stocks_name = f.readlines()
        stocks_name = [x.strip('\n') for x in stocks_name]

    try:
        with open(dir_res + f_res, 'rb'):
            pass
    except IOError:
        t = [x.replace(',', '|') for x in stocks_name]
        with open(dir_res + f_res, 'wb') as f:
            f.write('日期,' + ','.join(t) + '\n')

    try:
        with open(dir_res + f_res2, 'rb'):
            pass
    except IOError:
        with open(dir_res + f_res2, 'wb'):
            f.write('日期,' + 'ticker,' + '总量\n')

    # set filters
    invalid_user_id = [-1]
    invalid_source = ['持仓盈亏']

    grain_size = 1 * 24 * 60 * 60

    msg_count = defaultdict(dict)
    date_list = []

    for str_s_name in stocks_name:
        list_s_name = str_s_name.split(',')
        for s_name in list_s_name:
            # Get last timestamp
            try:
                with open(dir_last_timestamp + s_name + '_' + f_last_timestamp, 'rb') as f:
                    last_timestamp = int(f.readlines()[-1].strip('\n'))
            except IOError:
                last_timestamp = 1
            write_last_timestamp = False
            # Content backup buffer
            # Model is: created_time\tuser_id\ttext\n
            content_buffer = []

            complete = 0
            page = 0

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
                        print "tried 10 times, exist"
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
                    # Start and end conditions
                    create_time = msg['created_at'] / 1000
                    if create_time >= yesterday_midnight:
                        continue
                    if not write_last_timestamp:
                        with open(dir_last_timestamp + s_name + '_' + f_last_timestamp, 'ab') as f:
                            f.write("{0}".format(create_time))
                        write_last_timestamp = True
                    if create_time < last_timestamp:
                        complete = 1
                        break

                    # Backup
                    content_buffer.append(
                        {
                            'user_id': msg['user_id'],
                            'created_time': create_time,
                            'text': msg['text']
                        }
                    )

                    # Count msg
                    date = datetime.datetime.fromtimestamp(create_time).strftime('%Y%m%d')
                    date_list.append(date)
                    try:
                        msg_count[date][str_s_name] += 1
                    except:
                        msg_count[date][str_s_name] = 1
            with open(dir_backup + s_name + '_' + f_backup, 'ab') as f:
                while content_buffer:
                    rec = content_buffer.pop()
                    f.write("{0}\t{1}\t{2}\n".format(
                            rec['created_time'], rec['user_id'], rec['text'].encode('utf8'))
                    )
                
    with open(dir_res + f_res, 'ab') as f:
        for date in date_list:
            if date < '20160101':
                continue
            f.write(date[:4] + '/' + date[4:6] + '/' + date[6:])
            for stock in stocks_name:
                try:
                    count = msg_count[date][stock]
                except KeyError:
                    count = 0
                f.write(',{0}'.format(count))
            f.write('\n')

    with open(dir_res + f_res2, 'ab') as f:
        for date in msg_count:
            if date < '20160101':
                continue
            for stock in msg_count[date]:
                f.write('{0},{1},{2}'.format(
                        date[:4] + '/' + date[4:6] + '/' + date[6:], stock.replace(',', '|'), msg_count[date][stock])
                )
