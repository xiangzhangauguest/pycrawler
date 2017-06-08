# -*- coding: utf-8 -*-

import requests
import re
from collections import defaultdict
import operator
import datetime

import jieba


def get_section_info(content):
    result = dict()

    section_pattern = re.compile("<div class=\"tags-section  fn-left\">(.*?)</div>", re.M | re.S)
    section_result = section_pattern.findall(content)

    section_name_pattern = re.compile("<h4.*?</a>(.*?)</h4>")

    subsection_pattern = re.compile("<a.*?href='(.*?)'.*?title='(.*?)'")

    for section in section_result:
        section_name = section_name_pattern.search(section)
        if section_name is not None:
            section_name = section_name.group(1).decode("GBK")
            result[section_name] = dict()

        subsection_result = subsection_pattern.findall(section)
        for subsection_url, subsection_name in subsection_result:
            result[section_name][subsection_name.decode("GBK")] = subsection_url

    return result


def get_items_url(content):
    result = []

    item_pattern = re.compile("<div class=\"item\">(.*?)</div>", re.S)
    url_pattern = re.compile("a href='(.*?)'.*?title=")

    while True:
        try:
            items = item_pattern.findall(content)
        except TypeError as e:
            print e
            break

        for item in items:
            urls = url_pattern.findall(item)
            result += urls

        content = get_next_page_items(content)
        if content is None:
            break

    return result


def get_next_page_items(content):
    result = None

    next_page_pattern1 = re.compile("<div class='paging'>(.*?)</div>")
    next_page_pattern2 = re.compile("<a.*?class='next' href='(.*?)'>")

    next_page_code_block = next_page_pattern1.search(content)
    if next_page_code_block is not None:
        next_page_code_block = next_page_code_block.group(1)
        next_page_url = next_page_pattern2.search(next_page_code_block)
        if next_page_url is not None:
            next_page_url = next_page_url.group(1)
            result = requests.get(next_page_url)
            if result.status_code == 200:
                result = result.content

    return result


def get_article_keywords(url, output_dict):
    try:
        html = requests.get(url)
        if html.status_code == 200:
            article_content = get_valid_content(html.content)
            article_content = article_content.decode("GBK")
            words = jieba.cut_for_search(article_content)
            stopwords = get_stop_words()
            for word in words:
                if word not in stopwords:
                    output_dict[word] += 1
    except UnicodeDecodeError as e:
        print e
    except Exception as e:
        print e


def get_stop_words():
    input_file = "stopwords.txt"
    with open(input_file, "rb") as f:
        result = f.readlines()
        result = [x.strip('\n').decode('utf8') for x in result]
    return result


def get_valid_content(content):
    result = ''

    content_pattern = re.compile("<div class=\"article-content\" id=\"articleContent\">(.*?)</div>", re.S)

    while True:
        valid_content = content_pattern.search(content)
        if valid_content is not None:
            result += valid_content.group(1)

        content = get_next_page_content(content)
        if content is None:
            break

    tool = Tool()
    result = tool.replace(result)

    return result


def get_next_page_content(content):
    result = None

    next_page_pattern1 = re.compile("<div class=\"page\">(.*?)</div>")
    next_page_pattern2 = re.compile(".*</a><a target=\"_self\" href=\"(.*?)\" class=\"page-item-next\">")

    next_page_code_block = next_page_pattern1.search(content)
    if next_page_code_block is not None:
        next_page_code_block = next_page_code_block.group(1)
        next_page_relative_url = next_page_pattern2.search(next_page_code_block)
        if next_page_relative_url is not None:
            next_page_relative_url = next_page_relative_url.group(1)
            next_page_url = "http://www.autohome.com.cn" + next_page_relative_url
            result = requests.get(next_page_url)
            if result.status_code == 200:
                result = result.content

    return result


class Tool:
    # remove 图片
    remove_img = re.compile("<img.*?>")
    # remove 超链接
    remove_addr = re.compile("<a.*?>|</a>")
    # repalce 段落开头 ＝》 两个空格
    replace_para = re.compile("<p.*?>")
    # replace 换行 ＝》 \n
    replace_line = re.compile("<tr>|<div.*?>|</div>|</p>|&nbsp;|\n")
    # replace 换行符 ＝》 \n
    replace_br = re.compile("<br.*?>")
    # remove 其他标签
    remove_extra_tag = re.compile("<.*?>")
    # remove 空格
    remove_space = re.compile("\s")

    def replace(self, content):
        content = re.sub(self.remove_img, '', content)
        content = re.sub(self.remove_addr, '', content)
        content = re.sub(self.replace_line, '', content)
        content = re.sub(self.replace_para, '', content)
        content = re.sub(self.replace_br, '', content)
        content = re.sub(self.remove_extra_tag, '', content)
        content = re.sub(self.remove_space, '', content)
        return content.strip()

if __name__ == "__main__":
    output_file = "autohome_tags.csv"

    start_url = "http://www.autohome.com.cn/channel2/union/list.html"

    try:
        keywords_dict = dict()

        start_html = requests.get(start_url)

        tags_info = get_section_info(start_html.content)

        with open(output_file, 'wb') as f:
            for tag in tags_info:
                f.write("大标签: ".decode("utf8").encode("GBK") + tag.encode("GBK") + '\n')
                keywords_dict[tag] = dict()
                print tag
                for subtag in tags_info[tag]:
                    f.write("小标签: ".decode("utf8").encode("GBK") + subtag.encode("GBK") + ': ,')
                    print subtag
                    keywords_dict[tag][subtag] = defaultdict(int)
                    subtag_url = tags_info[tag][subtag]
                    subtag_html = requests.get(subtag_url)
                    if subtag_html.status_code != 200:
                        print subtag_url
                        continue
                    articles_url = get_items_url(subtag_html.content)
                    print datetime.datetime.now()
                    print len(articles_url)
                    for article_url in articles_url:
                        get_article_keywords(article_url, keywords_dict[tag][subtag])
                    sorted_keywords = sorted(keywords_dict[tag][subtag].items(), key=operator.itemgetter(1), reverse=True)
                    for sorted_keyword, freq in sorted_keywords:
                        if freq < 10:
                            break
                        f.write("{}: {},".format(sorted_keyword.encode("GBK"), freq))
                    f.write('\n')
                f.write('\n')
    except Exception as e:
        raise
        print e
