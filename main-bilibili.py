import threading
from json import loads

import redis
import requests as req

# import time
import tools

# from lxml import etree

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
    (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53'
}

# Redis缓存
R = redis.Redis(
    host='124.223.13.92',
    port=6379,
    password='19260817',
    charset='utf-8',
    decode_responses=True,  # 使结果不为二进制
    db=0
)


# 视频列表
video_list = []
# 封面列表
image_dict = {}


class User:
    def __init__(self, d: dict):
        self.id: int = int(d["mid"])
        self.name: str = d["name"]

    def get_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.id

    # 缓存用户信息
    def download_to_redis(self, r: redis.Redis):
        # 'hmset()'已弃用(悲)
        r.hset(str(self.id), 'name', self.name)


class Video:
    def __init__(self, d: dict):
        self.bv_id: str = str(d["bvid"])
        self.title: str = d["title"]
        self.upper: User = User(d["upper"])
        self.image: str = d["cover"]

    def __str__(self) -> str:
        # 序列化
        return f'{self.upper.get_name()}({self.upper.get_id()}):"{self.title}"[{self.bv_id}]:{self.image}'

    # 返回封面url
    def get_image_url(self) -> str:
        return self.image

    # 返回视频bv
    def get_video_bv(self) -> str:
        return self.bv_id

    # 缓存视频信息到Redis
    def download_to_redis(self, r) -> None:  # TODO
        # 还需添加用户信息的字段 'hmset()'需改为'hset()'
        # r.hmset(str(self.bv_id), {'title': self.title, 'image': self.image})
        r.hsetnx(str(self.bv_id), 'title', self.title)
        r.hsetnx(str(self.bv_id), 'image', self.image)
        self.upper.download_to_redis(r)


def get_images(urls: dict, hds: dict):
    img: tuple = urls.popitem()
    # 下载到指定的文件夹

    # if tools.download_image(img, headers=hds, path="./video_image") != 200:
    #     urls[img[0]] = img[1]

    try:
        tools.download_image(img, headers=hds, path="./video_image")
    except:  # TODO
        urls[img[0]] = img[1]


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    # 获取视频列表
    # 收藏夹最大页数 在html文件中无法获取
    pn = 1
    while True:
        # 目标收藏夹
        favorites_id = "https://space.bilibili.com/430965590/favlist?fid=999903590&ftype=create"
        # 收藏夹视频列表api参数
        payload = {'media_id': f'{favorites_id.split("?")[1].split("&")[0].split("=")[1]}',
                   'pn': str(pn), 'ps': '20', 'keyword': '', 'order': 'mtime',
                   'type': '0', 'tid': '0', 'platform': 'web', 'jsonp': 'jsonp'}
        """
        media_id: 收藏夹id
        pn: 翻页数 第1页等于第0页 超过最大页面返回视频列表为空
        """

        # 向api发起请求 返回一个json 包含视频列表
        res = req.get('https://api.bilibili.com/x/v3/fav/resource/list', params=payload)
        # strict:允许不规范的json
        json_dist = loads(tools.replace(res.text, "\n", ""), strict=False)

        # 视频列表获取完毕 结束循环
        if json_dist['data']['medias'] is None:
            tools.info("video list is loaded!!!")
            break

        # 继续获取下一页视频列表
        pn += 1
        for video in json_dist['data']['medias']:
            v = Video(video)
            # video - redis
            v.download_to_redis(R)

            tools.info(v)
            video_list.append(v)
            del v

    # 提取视频封面url
    for video_img in video_list:
        # 排除掉无效视频
        if video_img.title == '已失效视频':
            continue
        image_dict[video_img.get_video_bv()] = video_img.get_image_url()

    # 下载封面

    # 线程列表
    thread_list = []
    while len(image_dict):
        # 分配任务
        t = threading.Thread(target=get_images, args=(image_dict, headers))
        thread_list.append(t)
        # 启动函数
        t.start()
    for t in thread_list:
        # 等待线程结束
        t.join()
