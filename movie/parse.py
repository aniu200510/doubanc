import json
import os
import re
import logging

from movie import models

CHINESE_PATTERN = re.compile(r'[\u4e00-\u9fa5]+')


def _parse_m2m(info, model):
    data = dict()
    results = []
    if not info:
        return results

    for item in info.split('/'):
        if not CHINESE_PATTERN.match(item.strip()):
            data['name'] = item.strip()
            continue

        d = item.strip().split(sep=None, maxsplit=1)
        data['name'] = d[0]
        if len(d) > 1:
            data['alias'] = d[-1]

        obj, created = model.objects.get_or_create(**data)
        results.append(obj)

    return results


def _parse_name(info):
    name, alias = '', ''
    names = info.split(sep=None, maxsplit=1)
    if names:
        name, alias = names[0].strip(), names[-1].strip()

    return name, alias


def parse(item):
    data = dict()
    data['name'], data['alias'] = _parse_name(item.get('name', ''))
    data['other'] = item.get('other', '')
    data['published'] = item.get('published') if item.get(
        'published') else '1000-01-01'
    data['rating'] = float(item.get('rating', 0))
    data['best_rating'] = float(item.get('best_rating', 0))
    data['worst_rating'] = float(item.get('worst_rating', 0))
    data['rating_count'] = item.get('rating_count', 0)
    obj, created = models.Movie.objects.get_or_create(**data)

    actors = _parse_m2m(item.get('actor'), models.Actor)
    obj.actors.set([i.id for i in actors])

    authors = _parse_m2m(item.get('author'), models.Author)
    obj.authors.set([i.id for i in authors])

    directors = _parse_m2m(item.get('director'), models.Director)
    obj.directors.set([i.id for i in directors])

    genres = _parse_m2m(item.get('genre'), models.Genre)
    obj.genre.set([i.id for i in genres])

    regions = _parse_m2m(item.get('region', ''), models.Region)
    obj.region.set([i.id for i in regions])

    languages = _parse_m2m(item.get('language'), models.Language)
    obj.language.set([i.id for i in languages])


def save_top250():
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    dst_file = os.path.join(cur_dir, 'data', 'top250.json')
    with open(dst_file) as fp:
        items = json.load(fp)
        for item in items:
            logging.info(str(item))
            try:
                parse(item)
            except Exception as e:
                logging.warning(str(e))
                continue
