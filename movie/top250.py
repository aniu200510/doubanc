# -*- coding:utf-8 -*-
import json
import multiprocessing
import os
import re

from bs4 import BeautifulSoup
from bs4.element import Tag
from movie.crawl import get

BASE_URL = 'https://movie.douban.com/top250?start={}&filter='
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:76.0) Gecko/20100101 Firefox/76.0'}


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


def append_movies_url(page_url, movies_url_list):
    print('page_url:', page_url)
    text = get(page_url)
    if not text:
        return

    soup = BeautifulSoup(text, 'html.parser')
    tags = soup.body.ol.children
    for t in tags:
        movie_url = dict()
        if isinstance(t, Tag):
            movie_url['name'] = t.find('span', class_='title').get_text()
            url = t.find(href=re.compile("subject"))
            movie_url['url'] = url.get('href')
            movies_url_list.append(movie_url)


def get_top250_moves_urls():
    with multiprocessing.Manager():
        movies_urls = multiprocessing.Manager().list()   # 主进程与子进程共享这个List
        writers = [multiprocessing.Process(
            target=append_movies_url,
            args=(BASE_URL.format(i), movies_urls)) for i in range(0, 250, 25)]

        for w in writers:
            w.start()

        for w in writers:
            w.join()

    return movies_urls


def get_movie_info(url):
    info = dict()
    text = get(url)
    if text:
        info = encap_movie_info(text)
        info['url'] = url

    return info


def get_top250_movies():
    movies = []
    urls = get_top250_moves_urls()
    for item in urls:
        movie = get_movie_info(item['url'])
        movies.append(movie)

    return movies


def save_top250_movies():
    movies = get_top250_movies()
    cur_dir = os.path.abspath('.')
    dst_file = os.path.join(cur_dir, 'data', 'top250.json')
    with open(dst_file, 'w', encoding='utf-8') as fp:
        json.dump(movies, fp, indent=4)
