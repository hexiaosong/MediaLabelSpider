# coding: utf-8
"""
Create on 2018/3/23

@author:hexiaosong
"""


import time
import codecs
import datetime
from mongoengine import *
from bson import json_util
from MediaLabelSpider.utils import PROJECT_ROOT
from MediaLabelSpider.utils.CommonData import MediaLabelData
from mongoengine import register_connection


MONGODB_DATABASES = dict(
    main_mongo_db={
        'alias': 'MediaLabel',
        'name': 'MediaLabel',
        'username': '',
        'host': 'localhost',
        'password': '',
        'port': 27017,
        'connect': False,
    }
)

for name, data in MONGODB_DATABASES.items():
    register_connection(**data)

class MediaLabelDataStatistics(Document):
    """
    @summary: 媒体资源库
    """
    media_type = StringField(required=False, verbose_name='媒体类型')
    first_cate = StringField(default='', verbose_name='一级类目')
    second_cate = StringField(default='', verbose_name='二级类目')
    number = IntField(required=False, default=0,verbose_name='爬取数量')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='创建时间',
    )

    meta = {
        'db_alias': "MediaLabel",
        'strict': False,
        'index_background': True,
        "collection": "MediaLabelDataStatistics",
        "indexes": [
            "first_cate",
            "second_cate",
            'number',
        ]
    }

    def __unicode__(self):

        return '%s %s %s %s %s' % \
               (self.media_type,
                self.first_cate,
                self.second_cate,
                self.number,
                self.add_time,
                )



def jprint(d):
    print(json_util.dumps(d, ensure_ascii=False, indent=4))



def generate_statics_data():
    """
    生成媒体标签统计数据至mongodb
    :return:
    """
    lines = codecs.open(PROJECT_ROOT + '/web/cate_data.txt','r',encoding='utf8').readlines()
    data = [item.strip() for item in lines]

    result = {}
    for item in data:
        data_split = item.split(':')
        first_cate = data_split[0]
        second_cate_list = data_split[1].split(' ')
        tmp = []
        for second_cate in second_cate_list:
            num = MediaLabelData.objects.filter(first_cate=first_cate, second_cate=second_cate).count()
            tmp.append({second_cate:num})
        result[first_cate] = tmp


    for k, v in result.items():
        for i in v:
            data = MediaLabelDataStatistics.objects.filter(first_cate=k, second_cate=list(i.keys())[0])
            if not data:
                d = {
                    "media_type":"pc",
                    "first_cate":k,
                    "second_cate":list(i.keys())[0],
                    "number":list(i.values())[0]
                }
                media_cate = MediaLabelDataStatistics(**d)
                media_cate.save()
            else:
                old_number = data[0]['number']
                if list(i.values())[0] > old_number:
                    MediaLabelDataStatistics.objects.filter(first_cate=k, second_cate=list(i.keys())[0], number=old_number).delete()
                    d = {
                        "media_type": "pc",
                        "first_cate": k,
                        "second_cate": list(i.keys())[0],
                        "number": list(i.values())[0]
                    }
                    media_cate = MediaLabelDataStatistics(**d)
                    media_cate.save()


def get_today_stamps():
    t = '%s 00:00:00' % datetime.datetime.now().strftime('%Y-%m-%d')
    timeArray = time.strptime(t, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))

    return timeStamp

def get_date(timestamp):

    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp))




if __name__ == '__main__':
    print('App starts: %s' % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    generate_statics_data()
