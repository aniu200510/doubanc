# -*- coding:utf-8 -*-
import json
import logging
import multiprocessing
import os
import re

import requests
from requests.exceptions import RequestException

from bs4 import BeautifulSoup
from bs4.element import Tag

BASE_URL = 'https://movie.douban.com/top250?start={}&filter='
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}


def append_movies_url(page_url, movies_url_list):
    r = requests.get(page_url, headers=HEADERS)
    r.encoding = r.apparent_encoding
    if not r.status_code == 200:
        logging.warning('Get url {} fail!'.format(page_url))
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    tags = soup.body.ol.children
    for t in tags:
        if isinstance(t, Tag):
            name = t.find('span', class_='title').get_text()
            url = t.find(href=re.compile("subject"))
            url = url.get('href')
            movies_url_list.append(dict(name=name, url=url))


def get_moves_urls():
    # 网站的反爬程序返回状态码418， 需要添加请求header
    with multiprocessing.Manager() as mg:
        movies_urls = mg.list()   # 主进程与子进程共享这个List
        writers = [multiprocessing.Process(
            target=append_movies_url,
            args=(BASE_URL.format(i), movies_urls)) for i in range(0, 250, 25)]

        for w in writers:
            w.start()

        for w in writers:
            w.join()

    return movies_urls


def get_movie_info(url):
    # 连续最多尝试3次请求URL
    count = 0
    while count < 3:
        try:
            r = requests.get(url, headers=HEADERS, timeout=5)
            r.encoding = 'utf8'
        except RequestException as e:
            logging.warning('Get url {0} fail:{1}'.format(url, str(e)))
            count += 1
            continue

        if not r.status_code == 200:
            logging.warning('Get url {} fail!'.format(url))
            count += 1
            continue

        break

    if count >= 3:
        return

    return encap_movie_info(r.text)


def encap_movie_info(text):
    movie = dict()
    soup = BeautifulSoup(text, 'html.parser')
    body = soup.body
    info = body.find('div', id='info').get_text()
    for line in info.split(os.linesep):
        if line.startswith('片长:'):
            movie['mins'] = line.split(':')[-1].strip()
        elif line.startswith('制片国家/地区:'):
            movie['region'] = line.split(':')[-1].strip()
        elif line.startswith('又名:'):
            movie['other'] = line.split(':')[-1].strip()
        elif line.startswith('语言:'):
            movie['language'] = line.split(':')[-1].strip()

    head = soup.head
    s = head.find('script',
                  type="application/ld+json").get_text()
    # json.loads(json_data) 报错json.decoder.JSONDecodeError: Invalid control character at:
    # json默认使用的是严谨格式，当跨语言传递数据时，就容易报出这个错误。
    # 解决方法：加上参数 strict
    s = json.loads(s, encoding='utf8', strict=False)
    movie['name'] = s.get('name', '')
    directors = s.get('director', [])
    movie['director'] = '/'.join([d.get('name', '') for d in directors])
    authors = s.get('author', [])
    movie['author'] = '/'.join([a.get('name', '') for a in authors])
    actors = s.get('actor', [])
    movie['actor'] = '/'.join([a.get('name', '') for a in actors])
    movie['published'] = s.get('datePublished', '')
    movie['genre'] = '/'.join(s.get('genre', []))
    movie['rating'] = s.get('aggregateRating', {}).get('ratingValue', 0)
    movie['best_rating'] = s.get('aggregateRating', {}).get('bestRating', 0)
    movie['worst_rating'] = s.get('aggregateRating', {}).get('worstRating', 0)
    movie['rating_count'] = s.get('aggregateRating', {}).get('ratingCount', 0)
    movie['description'] = s.get('description', '')

    return movie


if __name__ == "__main__":
    data = []
    urls = get_moves_urls()
    for item in urls:
        movie = get_movie_info(item['url'])
        data.append(movie)
        print(movie)

    cur_dir = os.path.abspath('.')
    dst_file = os.path.join(cur_dir, 'data', 'top250_movies.json')
    with open(dst_file, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, indent=4)
