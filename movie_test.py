#!/usr/bin/python3.10
# -*- coding:utf-8 -*-


import requests
from xml.etree.ElementTree import Element, tostring, fromstring
from lxml import etree
import json
import tools


# parse = lambda html_str, xpath_str: html.xpath(xpath_str)[0].text
"""
def parse(html_str: str, xpath_str: str) -> str:
    return html.xpath(xpath_str)[0].text
"""


headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53'
}

res = requests.get(
    url='https://movie.douban.com/subject/26654184/?from=showing',
    headers=headers
)
print(res.status_code)
html = etree.HTML(res.text)

# movie_info = {'title': html.xpath('//*[@id="content"]/h1/span[1]')[0].text, }  # title

# application/ld+json
result = json.loads(tools.replace(html.xpath('//script[@type="application/ld+json"]/text()')[0], "\n", ""), )  # info

# ensure_ascii=False

print(result)
