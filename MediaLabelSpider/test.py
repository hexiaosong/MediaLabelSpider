# coding: utf-8
"""
Create on 2018/4/21

@author:hexiaosong
"""
from __future__ import unicode_literals

import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from mongoengine import register_connection
from MediaLabelSpider.utils.CommonData import MONGODB_DATABASES,MediaLabelData


class ElasticObj:
    def __init__(self, index_name="medialabel",index_type="media_label_data",ip ="127.0.0.1"):
        '''

        :param index_name: 索引名称
        :param index_type: 索引类型
        '''
        # 无用户名密码状态
        #self.es = Elasticsearch([ip])
        #用户名密码状态
        self.index_name = index_name
        self.index_type = index_type
        self.es = Elasticsearch([ip],port=9200)

    def Index_Data_mongo(self):
        '''
        从mongodb中读取数据，并存储到es中
        :param csvfile: csv文件，包括完整路径
        :return:
        '''
        data_list = MediaLabelData.objects.all()
        count = 0
        doc = {}
        for item in data_list:
            doc['first_cate'] = item['first_cate']
            doc['second_cate'] = item['second_cate']
            doc['media_name'] = item['media_name']
            doc['url'] = item['url']
            doc['web_place'] = item['web_place']
            doc['type'] = item['type']
            doc['desc'] = item['desc']
            res = self.es.index(index=self.index_name, doc_type=self.index_type, body=doc)
            time.sleep(0.5)
            count += 1
            print('COUNT: %s' % count)
            print(res['created'])

    def bulk_Index_Data(self):
        '''
        用bulk将批量数据存储到es
        :return:
        '''
        list = [
            {"date": "2017-09-13",
             "source": "慧聪网",
             "link": "http://info.broadcast.hc360.com/2017/09/130859749974.shtml",
             "keyword": "电视",
             "title": "付费 电视 行业面临的转型和挑战"
             },
            {"date": "2017-09-13",
             "source": "中国文明网",
             "link": "http://www.wenming.cn/xj_pd/yw/201709/t20170913_4421323.shtml",
             "keyword": "电视",
             "title": "电视 专题片《巡视利剑》广获好评：铁腕反腐凝聚党心民心"
             },
            {"date": "2017-09-13",
             "source": "人民电视",
             "link": "http://tv.people.com.cn/BIG5/n1/2017/0913/c67816-29533981.html",
             "keyword": "电视",
             "title": "中国第21批赴刚果（金）维和部隊启程--人民 电视 --人民网"
             },
            {"date": "2017-09-13",
             "source": "站长之家",
             "link": "http://www.chinaz.com/news/2017/0913/804263.shtml",
             "keyword": "电视",
             "title": "电视 盒子 哪个牌子好？ 吐血奉献三大选购秘笈"
             }
        ]
        ACTIONS = []
        i = 1
        for line in list:
            action = {
                "_index": self.index_name,
                "_type": self.index_type,
                "_id": i, #_id 也可以默认生成，不赋值
                "_source": {
                    "date": line['date'],
                    "source": line['source'].decode('utf8'),
                    "link": line['link'],
                    "keyword": line['keyword'].decode('utf8'),
                    "title": line['title'].decode('utf8')}
            }
            i += 1
            ACTIONS.append(action)
            # 批量处理
        success, _ = bulk(self.es, ACTIONS, index=self.index_name, raise_on_error=True)
        print('Performed %d actions' % success)

    def Delete_Index_Data(self,id):
        '''
        删除索引中的一条
        :param id:
        :return:
        '''
        res = self.es.delete(index=self.index_name, doc_type=self.index_type, id=id)
        print res

    def Get_Data_Id(self,id):

        res = self.es.get(index=self.index_name, doc_type=self.index_type,id=id)
        print(res['_source'])

        print '------------------------------------------------------------------'
        #
        # # 输出查询到的结果
        for hit in res['hits']['hits']:
            # print hit['_source']
            print hit['_source']['date'],hit['_source']['source'],hit['_source']['link'],hit['_source']['keyword'],hit['_source']['title']

    def Get_Data_By_Body(self):
        # doc = {'query': {'match_all': {}}}
        doc = {
            "query": {
                "match": {
                    "keyword": "电视"
                }
            }
        }
        _searched = self.es.search(index=self.index_name, doc_type=self.index_type, body=doc)

        for hit in _searched['hits']['hits']:
            # print hit['_source']
            print hit['_source']['date'], hit['_source']['source'], hit['_source']['link'], hit['_source']['keyword'], \
            hit['_source']['title']

if __name__ == '__main__':
    for name, data in MONGODB_DATABASES.items():
        register_connection(**data)
    obj = ElasticObj()
    obj.Index_Data_mongo()
    print('Sucess !!')


