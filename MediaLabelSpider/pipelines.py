# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from __future__ import unicode_literals

import requests
from mongoengine import register_connection
from MediaLabelSpider.utils.CommonData import MONGODB_DATABASES, MediaLabelData

class MedialabelspiderPipeline(object):

    def __init__(self):
        super(MedialabelspiderPipeline, self).__init__()
        # 注册数据库连接
        for name, data in MONGODB_DATABASES.items():
            register_connection(**data)

    def process_item(self, item, spider):

        url = item.get('url')

        # try:
        #     res = requests.get(url, timeout=25)
        #     if res.status_code == 200:
        #         item['validated'] = True
        # except Exception as e:
        #     print('链接:%s访问异常' % url)

        if not MediaLabelData.objects.filter(url=url):
            item['media_type'] = 'pc'
            data = MediaLabelData(**item)
            data.save()
            print('Save sucessful: %s' % data)
        else:
            print('此媒体信息已经存在,跳过！！')
        return item
