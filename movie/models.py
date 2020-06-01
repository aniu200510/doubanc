from django.db import models


class Actor(models.Model):
    name = models.CharField('名称', max_length=128)
    alias = models.CharField('别名', max_length=128, default=None)

    class Meta:
        unique_together = ("name", "ename")

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField('名称', max_length=128)
    alias = models.CharField('别名', max_length=128, default=None)

    class Meta:
        unique_together = ("name", "ename")

    def __str__(self):
        return self.name


class Author(models.Model):
    name = models.CharField('名称', max_length=128)
    alias = models.CharField('别名', max_length=128, default=None)

    class Meta:
        unique_together = ("name", "ename")

    def __str__(self):
        return self.name


class Genre(models.Model):
    genre = models.CharField('类型', max_length=128)

    def __str__(self):
        return self.genre


class Movie(models.Model):
    name = models.CharField('电影名', max_length=128, unique=True)
    alias = models.CharField('别名', max_length=128, default=None)
    other = models.CharField('又名', max_length=256, default=None)
    region = models.CharField('制片国家/地区', max_length=128, default=None)
    language = models.CharField('语言', max_length=64, default=None)
    directors = models.ManyToManyField(Director, default=None, blank=True)
    authors = models.ManyToManyField(Author, default=None, blank=True)
    actors = models.ManyToManyField(Actor, default=None, blank=True)
    genre = models.ManyToManyField(Genre, default=None, blank=True)
    published = models.DateField('上映日期', default=None)
    rating = models.FloatField('评分', default=None)
    best_rating = models.FloatField('最高分', default=None)
    worst_rating = models.FloatField('最低分', default=None)
    rating_count = models.IntegerField('评论数', default=None)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.name
