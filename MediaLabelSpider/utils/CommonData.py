# coding: utf-8
"""
Create on 2018/4/16

@author:hexiaosong
"""
from __future__ import unicode_literals

import datetime
from mongoengine import Document
from mongoengine.fields import *


# 网站类别链接
CATE_URL_DICT = {
    '新闻媒体':'news',
    '交通旅游':'jiaotonglvyou',
    '医疗健康':'yiliao',
    '体育健身':'tiyu',
    '政府组织': 'gov',
    '购物网站': 'shopping',
    '休闲娱乐': 'yule',
    '网络科技':'wangluo',
    '生活服务':'shenghuo',
    '教育文化':'jiaoyu',
    '行业企业':'qiye',
    '综合其他':'zonghe',
}


MONGODB_DATABASES = dict(
    # 媒体标签库
    main_mongo_db={
        'alias': 'MediaLabel',
        'name': 'MediaLabel',
        'username': '',
        'host': 'localhost',
        'password': '',
        'port': 27017,
        'connect': False,
    },
)


class MediaLabelData(Document):
    """
    @summary: 媒体资源库
    """
    media_type = StringField(required=False, verbose_name='媒体类型')
    first_cate = StringField(default='', verbose_name='一级类目')
    second_cate = StringField(default='', verbose_name='二级类目')
    media_name = StringField(default='', verbose_name='媒体名称')
    url = StringField(default='', verbose_name='网站url')
    web_place = StringField(default='', verbose_name='网站地区')
    type = StringField(default='', verbose_name='网站类型')
    score = IntField(required=False, default=0,verbose_name='综合得分')
    link_num = IntField(required=False, default=0,verbose_name='反链数')
    baidu_pc_weight = IntField(required=False, default=0,verbose_name='百度pc权重')
    baidu_mobile_weight = IntField(required=False, default=0,verbose_name='百度mobile权重')
    desc = StringField(default='', verbose_name='网站简介')
    website_rank = StringField(default='', verbose_name='国内排名')
    province_rank = StringField(default='', verbose_name='省份排名')
    industry_rank = StringField(default='', verbose_name='网站行业类型排名')
    mobile_url = StringField(default='', verbose_name='移动url')
    company_name = StringField(default='', verbose_name='公司名称')
    representative = StringField(default='', verbose_name='法定代表人')
    registered_capital = StringField(default='', verbose_name='公司注册资本')
    registered_date = StringField(default='', verbose_name='注册时间')
    company_properties = StringField(default='', verbose_name='企业性质')
    ip_address = StringField(default='', verbose_name='ip地址')
    server_address = StringField(default='', verbose_name='服务器地址')
    domain = StringField(default='', verbose_name='域名')
    dm_server = StringField(default='', verbose_name='域名服务商')
    dm_create_time = StringField(default='', verbose_name='域名创建时间')
    dm_deadline = StringField(default='', verbose_name='域名到期时间')
    update_time = StringField(default='', verbose_name='数据更新日期')
    validated = BooleanField(default=False, verbose_name='网站验证是否有效')
    add_time = DateTimeField(
        db_field='createtime',
        default=datetime.datetime.now,
        verbose_name='创建时间',
    )

    meta = {
        'db_alias': "MediaLabel",
        'strict': False,
        'index_background': True,
        "collection": "media_label_data",
        "indexes": [
            "first_cate",
            "second_cate",
            'media_name',
        ]
    }

    def __unicode__(self):

        return '%s %s %s %s %s %s' % \
               (self.add_time,
                self.first_cate,
                self.second_cate,
                self.media_name,
                self.url,
                self.desc,
                )

