# coding: utf-8
"""
Create on 2018/4/16

@author:hexiaosong
"""
from __future__ import unicode_literals

import re
import scrapy
from lxml import etree
from bson import json_util
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider
from MediaLabelSpider.items import MedialabelspiderItem
from MediaLabelSpider.utils.CommonData import CATE_URL_DICT


class MediaLabelSpider(CrawlSpider):

    name = 'media_label'

    def __init__(self, url_dict=CATE_URL_DICT, cate_item_list=['交通旅游']):
        super(MediaLabelSpider, self).__init__()
        self.index_url = 'http://top.chinaz.com'
        self.base_url = 'http://top.chinaz.com/hangye/index_%s.html'
        self.url_dict = url_dict
        self.crawl_cate = self.crawl_item(cate_item_list)

    def crawl_item(self, cate_list):
        """
        获取指定的行业类别
        :param cate_list:
        :return:
        """
        d = {}
        if not cate_list:
            for k,v in self.url_dict.items():
                d[k] = self.base_url % v
        else:
            for item in cate_list:
                tmp = self.url_dict.get(item,'')
                if tmp:
                    d[item] = self.base_url % tmp

        return d

    @staticmethod
    def jprint(j_data):
        """
        打印dict数据
        :param j_data:
        :return:
        """
        print(json_util.dumps(j_data, ensure_ascii=False, indent=4))

    def start_requests(self):

        for cate, url in self.crawl_cate.items():
            yield scrapy.Request(url, callback=self._parse_index_page, meta={'first_cate':cate})


    def _parse_index_page(self, response):
        """
        解析获取一级类目下的二级类目
        :param response:
        :return:
        """
        first_cate = response.meta.get('first_cate')
        link = response.xpath('//div[@class="HeadFilter clearfix"]/a/@href').extract()
        cate_list = response.xpath('//div[@class="HeadFilter clearfix"]/a/text()').extract()

        for cate, link in zip(cate_list, link):
            print("cate:%s, link:%s" % (cate, link))
            yield scrapy.Request('http://top.chinaz.com/hangye/' + link, callback=self._parse_cate_page,
                                 meta={
                                     'first_cate':first_cate,
                                     'second_cate':cate
                                 })


    def _parse_cate_page(self, response):
        """获取二级类目页面url"""

        kwargs = response.meta

        # 获取该类目下页面总数
        page_num = response.xpath('//div[@class="ListPageWrap"]/a[last()-1]/text()').extract_first()
        cate_url = response.url

        cate_page_url_list = [cate_url]
        for index in range(2, int(page_num)+1):
            next_url = cate_url.replace('.html', '_%s.html' % index)
            cate_page_url_list.append(next_url)

        for page_url in cate_page_url_list:
            yield scrapy.Request(page_url, callback=self._parse_list_page, meta=kwargs)

    def _etree_extract(self, etree, path):
        """
        使用xpath提取etree元素
        :param etree:
        :param path:
        :return:
        """
        result = etree.xpath(path)
        if result:
            return result[0]
        else:
            return ''

    def _parse_list_page(self, response):

        d = response.meta

        # for item in ['download_latency', 'download_slot', 'download_timeout']:
        #     if item in d.keys():
        #         d.pop(item)

        eles = response.xpath('//ul[@class="listCentent"]/li').extract()
        self.logger.info('当前页面:%s, 获取媒体元素%s个.' % (response.url, len(eles)))

        for ele in eles:
            e_tree = etree.HTML(ele)

            d['media_name'] = self._etree_extract(e_tree, '//h3[@class="rightTxtHead"]/a/text()')

            href = self._etree_extract(e_tree, '//h3[@class="rightTxtHead"]/a/@href')
            if href:
                href = self.index_url + href
            else:
                self.logger.info('当前元素: %s 没有获取到链接' % d['media_name'])

            d['desc'] = self._etree_extract(e_tree, '//p[@class="RtCInfo"]/text()')
            score_text = self._etree_extract(e_tree, '//div[@class="RtCRateCent"]/span/text()')
            if score_text:
                score = int(score_text.replace('得分:',''))
            else:
                score = ''
            d['score'] = score

            soup = BeautifulSoup(ele, "lxml")
            text = soup.get_text()
            result = re.search('反链数：(\d+)', text)
            if result:
                link_num = int(result.group(1))
            else:
                link_num = ''
            d['link_num'] = link_num

            yield scrapy.Request(href, callback=self._parse_detail_page, meta=d)


    def _parse_detail_page(self, response):

        d = response.meta

        d['url'] = response.xpath('//p[@class="plink ml5 fl"]/a/@href').extract_first()
        d['website_rank'] = response.xpath("//p[@class='headpoint']/a[contains(@href, 'all')]/text()").extract_first()
        d['province_rank'] = response.xpath("//p[@class='headpoint']/a[contains(@href, 'diqu')]/text()").extract_first()
        d['industry_rank'] = response.xpath("//p[@class='headpoint']/a[contains(@href, 'hangye')]/text()").extract_first()

        d['update_time'] = response.xpath('//span[@class="dateup"]/text()').extract_first().replace('数据更新：','')

        block = response.xpath('//div[@class="Tagone TopMainTag-show"]').extract_first()
        soup = BeautifulSoup(block, "lxml")
        text = soup.get_text().strip()
        res = re.search("网站类型：(?P<type>.*?)所属地区：(?P<web_place>.*)", text)
        if res:
            d.update(res.groupdict())

        weight_src = response.xpath('//img[contains(@src,"/themes/default/images/baidu/")]/@src').extract_first()
        d['baidu_pc_weight'] = weight_src.split('/')[-1].replace('.gif','')

        if '移动网址' in response.text:
            mobile_lable = response.xpath('//dl[@class="TMain03Wrap clearfix"]/dt').extract()
            mobile_value = response.xpath('//dl[@class="TMain03Wrap clearfix"]/dd').extract()
            for label,value in zip(mobile_lable, mobile_value):
                if '百度权重' in label:
                    d['baidu_mobile_weight'] = re.search('(\d+).gif', value).group(1)
                if '移动网址' in label:
                    d['mobile_url'] = re.search('href="(.*?)"', value).group(1)

        if '企业信息' in response.text:
            company_lable = response.xpath('//div[@class="CobaseCon mb30"]/ul/li[1]/span').extract()
            company_value = response.xpath('//div[@class="CobaseCon mb30"]/ul/li[last()]/span').extract()
            for label, value in zip(company_lable, company_value):
                if '公司名称' in label:
                    d['company_name'] = re.search('<span>(.*?)</span>', value).group(1)
                if '法定代表人' in label:
                    d['representative'] = re.search('<span.*?>(.*?)</span>', value).group(1)
                if '注册资本' in label:
                    d['registered_capital'] = re.search('<span>(.*?)</span>', value).group(1)
                if '注册时间' in label:
                    d['registered_date'] = re.search('<span>(.*?)</span>', value).group(1)


        if '备案信息' in response.text:
            # 公司信息
            company_str = response.xpath('//li[@class="TMain06List-Left fl"]').extract_first()
            company_text = BeautifulSoup(company_str, "lxml").get_text()
            res = re.search('单位名称：(?P<company_name>.*?)单位性质：(?P<company_properties>.*?)网站备案', company_text)
            if res:
                d.update(res.groupdict())

            # 服务器
            server_str = response.xpath('//li[@class="TMain06List-Cent fl"]').extract_first()
            server_text = BeautifulSoup(server_str, "lxml").get_text()
            res = re.search('服务器Ip地址：(?P<ip_address>.*?)服务器地址：(?P<server_address>.*?)服务器类型', server_text)
            if res:
                d.update(res.groupdict())

            # 域名
            domain_str = response.xpath('//li[@class="TMain06List-right fl"]').extract_first()
            domain_text = BeautifulSoup(domain_str, "lxml").get_text()
            res = re.search('域名域名：(?P<domain>.*?)域名注册商: (?P<dm_server>.*?)域名服务器：.*创建时间：(?P<dm_create_time>.*?)到期时间: (?P<dm_deadline>.*)', domain_text)
            if res:
                d.update(res.groupdict())

        self.jprint(d)
        for item in ['depth','download_latency','download_slot','download_timeout']:
            if item in d.keys():
                d.pop(item)

        item = MedialabelspiderItem(**d)

        yield item