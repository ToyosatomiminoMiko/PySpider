#!/usr/bin/python3.10
# -*- coding:utf-8 -*-

"""
多线程爬虫
1. 爬取豆瓣上的电影
2. 保存数据到MySQL
"""
import time

import requests
# from xml.etree.ElementTree import Element, tostring, fromstring
import threading
from lxml import etree
import tools
from json import loads

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53'
}

# 需要获取的电影列表
movie_list = []
# 电影信息保存
movie_info = {}


# 数据清洗
def parse(object_: object, obj_list: list) -> list:
    """
    :param object_: 指定数据结构
    :param obj_list: 待清洗的列表
    :return: 已清洗的数据列表
    """
    rl = []
    for obj in obj_list:
        rl.append(object_(obj))  # 解析对应的数据结构
    return rl


# 电影的评分
class AggregateRating:
    """
    电影评分
    """
    def __init__(self, d: dict):
        self.rating_count: int = int(d['ratingCount'])  # 评分数
        self.best_rating: int = int(d['bestRating'])  # 最高分
        self.worst_rating: int = int(d['worstRating'])  # 最低分
        try:
            self.rating_value: float = float(d['ratingValue'])  # 评定值
        except ValueError:
            self.rating_value: float = 0.0
        self.id: int = d['id']

    def __str__(self) -> str:
        return f"{self.__ne__}/movie_id:{self.id}"


class Person:
    """
    人物
    """
    def __init__(self, d: dict):
        self.name: str = d['name']  # 姓名
        self.id: int = int(d['url'].split('/')[2])

    def __str__(self) -> str:
        return f'{self.__ne__}/{self.id}:"{self.name}"'

    def save_data(self, name: str):
        self.name = name


class Movie:
    """
    这是单个的电影
    通过id获取v其信息
    """
    def __init__(self, m_id: str):
        self.movie_info = {}  # from get_data
        self.id: int = int(m_id)
        self.title: str = ''  # 标题
        self.image_url: str = ''  # 封面路径
        self.director: list = []  # 导演
        self.author: list = []  # 编剧
        self.actor: list = []  # 演员
        self.date_published: str = ''  # 上映时间
        self.genre: str = ''  # 类别
        self.duration: str = ''  # 时长
        self.description: str = ''  # 简介
        self.aggregate_rating: object = AggregateRating  # 评分

    def get_data(self, hds):
        # print(f'https://movie.douban.com/subject/{self.id}/?from=showing')

        r = requests.get(
            url=f'https://movie.douban.com/subject/{self.id}/?from=showing',
            headers=hds
        )
        tools.info(f"[{self.id}]status code: {r.status_code}")
        movie_html = etree.HTML(r.text)

        # info
        self.movie_info = loads(tools.replace(movie_html.xpath('//script[@type="application/ld+json"]/text()')[0], "\n", ""), )
        del r, movie_html
        tools.info(self.movie_info)

    def save_data(self):
        self.title = self.movie_info['name']
        print("title:", self.title)

        self.id = int(self.movie_info['url'].split("/")[2])
        print("id:", self.id)

        self.image_url = self.movie_info['image']
        print("image_url:", self.image_url)

        self.director = parse(Person, self.movie_info['director'])
        print("director:", self.director)

        self.author = parse(Person, self.movie_info['author'])
        print("author:", self.author)

        self.actor = parse(Person, self.movie_info['actor'])
        # print('actor:', self.actor[0])
        print('actor:', self.actor)

        self.movie_info['aggregateRating']['id'] = self.id  # 在评分中标注电影的id
        self.aggregate_rating = parse(AggregateRating, [self.movie_info['aggregateRating']])
        # print('aggregate_rating:', self.aggregate_rating[0])
        print('aggregate_rating:', self.aggregate_rating)

        self.date_published = self.movie_info['datePublished']
        print("date_published:", self.date_published)

        self.genre = self.movie_info['genre']
        print("genre:", self.genre)

        self.duration = self.movie_info['duration']
        print("duration:", self.duration)

        self.description = self.movie_info['description']
        print("description:", self.description)


# 获取每个电影的信息 (多线程实现)
def get_movie(link: list, hds: dict):
    """
    :param link: 链接列表 movie_list
    :param hds: 请求头 headers
    :return: --
    """
    m = Movie(link.pop())
    m.get_data(hds)
    m.save_data()
    del m


if __name__ == '__main__':
    # 获取电影列表
    res = requests.get(
        url='https://movie.douban.com/',
        headers=headers
    )
    print(res.status_code)
    html = etree.HTML(res.text)
    # 定位到电影到电影列表
    result = html.xpath('//*[@id="screening"]/div[2]/ul/li/ul/li[1]/a/@href')
    # print(result)

    for url in result:
        movie_list.append(url.split('/')[4])
        # print(url.split('/')[4])
    # 清除垃圾
    del res, html, result
    # 获取到的电影列表
    tools.info(f"all movie:{movie_list}")

    # 线程列表
    thread_list = []
    # for i in range(8):
    while len(thread_list) < 8:
        # 分配任务
        t = threading.Thread(target=get_movie, args=(movie_list, headers))
        thread_list.append(t)
        # 启动函数
        t.start()
    else:
        time.sleep(1)
    for t in thread_list:
        # 等待线程结束
        t.join()
