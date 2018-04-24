# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
from __future__ import unicode_literals

import scrapy


class MedialabelspiderItem(scrapy.Item):
    media_type = scrapy.Field()         # 媒体类型
    first_cate = scrapy.Field()         # 一级类目
    second_cate = scrapy.Field()        # 二级类目
    media_name = scrapy.Field()         # 媒体名称
    url = scrapy.Field()                # 网站url
    web_place = scrapy.Field()          # 网站地区
    type = scrapy.Field()               # 网站类型
    score = scrapy.Field()              # 综合得分
    link_num = scrapy.Field()           # 反链数
    baidu_pc_weight = scrapy.Field()    # 百度pc权重
    baidu_mobile_weight = scrapy.Field()# 百度mobile权重
    keywords_baidu = scrapy.Field()     # 百度关键词
    keywords_360 = scrapy.Field()       # 360关键词
    pv_str = scrapy.Field()             # pv访问量
    ip_str = scrapy.Field()             # ip访问量
    pv_list_str = scrapy.Field()        # pv访问量数字串
    ip_list_str = scrapy.Field()        # ip访问量数字串
    desc = scrapy.Field()               # 网站简介
    website_rank = scrapy.Field()       # 国内排名
    province_rank = scrapy.Field()      # 省份排名
    industry_rank = scrapy.Field()      # 网站行业类型排名
    mobile_url = scrapy.Field()         # 移动url
    company_name = scrapy.Field()       # 公司名称
    representative = scrapy.Field()     # 法定代表人
    registered_capital = scrapy.Field() # 公司注册资本
    registered_date = scrapy.Field()    # 注册时间
    company_properties = scrapy.Field() # 企业性质
    ip_address = scrapy.Field()         # ip地址
    server_address = scrapy.Field()     # 服务器地址
    domain = scrapy.Field()             # 域名
    dm_server = scrapy.Field()          # 域名服务商
    dm_create_time = scrapy.Field()     # 域名创建时间
    dm_deadline = scrapy.Field()        # 域名到期时间
    update_time = scrapy.Field()        # 数据更新日期
    validated = scrapy.Field()          # 网站访问是否有效