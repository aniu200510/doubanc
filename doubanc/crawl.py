# -*- coding:utf-8 -*-
"""
Crawl is a HTTP module, written in Python, used to crawl douban movie data.
"""
import logging

import requests
from requests.exceptions import RequestException


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}


def get(url):
    # 连续最多尝试3次请求URL
    count = 0
    while count < 3:
        try:
            # 网站的反爬程序返回状态码418， 需要添加请求header
            r = requests.get(url, headers=HEADERS, timeout=5)
            r.encoding = 'utf8'
            if r.status_code != 200:
                raise RequestException('status_code:{}'.format(r.status_code))
        except RequestException as e:
            count += 1
            logging.warning(
                'Get url {0} fail:{1}.\nTry {2} times!'.format(
                    url, str(e), count))
            continue
        break

    if count >= 3:
        logging.error('Get url {} fail!'.format(url))
        return

    return r.text
