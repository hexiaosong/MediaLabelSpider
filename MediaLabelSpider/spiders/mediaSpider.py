# coding: utf-8
"""
Create on 2018/4/16

@author:hexiaosong
"""
from __future__ import unicode_literals

import re
import json
import time
import random
import scrapy
import requests
import demjson
from lxml import etree
from bson import json_util
from bs4 import BeautifulSoup
from scrapy.spiders import CrawlSpider
from mongoengine import register_connection
from MediaLabelSpider.items import MedialabelspiderItem
from MediaLabelSpider.utils.CommonData import VistitedUrl, MONGODB_DATABASES
from MediaLabelSpider.utils.CommonData import CATE_URL_DICT


class MediaLabelSpider(CrawlSpider):

    name = 'media_label'

    def __init__(self, url_dict=CATE_URL_DICT, cate_item_list=[]):
        super(MediaLabelSpider, self).__init__()
        self.index_url = 'http://top.chinaz.com'
        self.base_url = 'http://top.chinaz.com/hangye/index_%s.html'
        self.url_dict = url_dict
        self.flag_first_page = 0
        self.crawl_cate = self.crawl_item(cate_item_list)
        self.conn_mongodb()

    def conn_mongodb(self):
        for name, data in MONGODB_DATABASES.items():
            register_connection(**data)

    @staticmethod
    def jprint(j_data):
        """
        打印dict数据
        :param j_data:
        :return:
        """
        print(json_util.dumps(j_data, ensure_ascii=False, indent=4))


    def crawl_chinaz_api(self, website_domain=None, is_ip=False, is_pv=False):
        """
        爬取日均ip和日均pv
        :param is_ip: 查询网站的域名
        :param is_ip: 是否查询ip
        :param is_pv: 是否查询pv
        :return:
        """
        if (not is_ip and not is_pv) or (is_ip and is_pv):
            self.logger.error('is_ip 或 is_pv有且仅有一个为True!!')
            return
        ip_url = 'http://alexa.chinaz.com/Handlers/GetAlexaIpNumHandler.ashx'
        pv_url = 'http://alexa.chinaz.com/Handlers/GetAlexaPvNumHandler.ashx'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,mt;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': 'UM_distinctid=162d79915bb1175-060f8f30740179-33697b04-fa000-162d79915bc37d; Hm_lvt_aecc9715b0f5d5f7f34fba48a3c511d6=1524128056; Hm_lpvt_aecc9715b0f5d5f7f34fba48a3c511d6=1524128056; ASP.NET_SessionId=dkberwb5y10nmtfcfa2srnto;__lnkrntdmcvrd=-1;CNZZDATA5082702=cnzz_eid%3D1324617910-1524449648-null%26ntime%3D1524531168;qHistory=aHR0cDovL3Nlby5jaGluYXouY29tK1NFT+e7vOWQiOafpeivonxodHRwOi8vdG9vbC5jaGluYXouY29tK+ermemVv+W3peWFt3xodHRwOi8vcmFuay5jaGluYXouY29tK+eZvuW6puadg+mHjeafpeivonxodHRwOi8vcmFuay5jaGluYXouY29tL3JhbmthbGwvK+adg+mHjee7vOWQiOafpeivonxodHRwOi8vdG9vbC5jaGluYXouY29tL2xpbmtzLyvmrbvpk77mjqXmo4DmtYsv5YWo56uZUFLmn6Xor6I=',
            'Host': 'alexa.chinaz.com',
            'Origin': 'http://alexa.chinaz.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }
        data = {'url': website_domain}

        if is_ip:
            url = ip_url
        if is_pv:
            url = pv_url
        res = requests.post(url, headers=headers, data=data)
        html = res.text
        try:
            json_data = demjson.decode(html)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(html)
            json_data = None

        # self.jprint(json_data)
        time.sleep(random.uniform(0, 1.5))
        return json_data

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
        links = response.xpath('//div[@class="HeadFilter clearfix"]/a/@href').extract()
        cate_list = response.xpath('//div[@class="HeadFilter clearfix"]/a/text()').extract()

        for cate, link in zip(cate_list, links):
            print("cate:%s, link:%s" % (cate, link))
            yield scrapy.Request('http://top.chinaz.com/hangye/' + link, callback=self._parse_cate_page,
                                 meta={
                                     'first_cate':first_cate,
                                     'second_cate':cate
                                 })


    def _parse_cate_page(self, response):
        """获取二级类目页面url"""

        kwargs = response.meta
        kwargs['first_page_html'] = response.text

        # 获取该类目下页面总数
        page_num = response.xpath('//div[@class="ListPageWrap"]/a[last()-1]/text()').extract_first()
        cate_url = response.url

        cate_page_url_list = []
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

        if 'first_page_html' in d.keys():
            if self.flag_first_page==0:
                first_page = d.pop('first_page_html')
                first_page_tree = etree.HTML(first_page)
                first_page_eles = first_page_tree.xpath('//ul[@class="listCentent"]/li')
                first_page_str_eles = [etree.tostring(item) for item in first_page_eles]
                eles.extend(first_page_str_eles)
                self.flag_first_page = 1
            else:
                d.pop('first_page_html')

        for ele in eles:
            e_tree = etree.HTML(ele)

            d['media_name'] = self._etree_extract(e_tree, '//h3[@class="rightTxtHead"]/a/text()')

            href = self._etree_extract(e_tree, '//h3[@class="rightTxtHead"]/a/@href')
            if href:
                href = self.index_url + href
                if VistitedUrl.objects.filter(url=href):
                    self.logger.info('此详情页链接已访问，跳过！！ %s' % href)
                    continue
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

        # 将已经访问的详情页链接保存, 防止重复访问
        href = response.url
        url_obj = VistitedUrl(**{"url": href})
        url_obj.save()

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

        if '主要关键词' in response.text:
            baidu_text_list = response.xpath('//div[@class="TPageCent-TMainmob fl"]/ul/li/span[@class="Lnone"]/text()').extract()
            if '百度关键词' in baidu_text_list:
                baidu_text_list.remove('百度关键词')
            d['keywords_baidu'] = ','.join(baidu_text_list)

            _360_text_list = response.xpath('//div[@class="TPageCent-TMainmob fr"]/ul/li/span[@class="Lnone"]/text()').extract()
            if '360关键词' in _360_text_list:
                _360_text_list.remove('360关键词')
            d['keywords_360'] = ','.join(_360_text_list)

        # 获取网站的ip, pv量信息
        website_domain = d['url'].replace('http://','')
        pv_data = self.crawl_chinaz_api(website_domain,is_pv=True)
        ip_data = self.crawl_chinaz_api(website_domain, is_ip=True)
        if pv_data and ip_data:
            d['pv_str'] = json.dumps(pv_data)
            d['ip_str'] = json.dumps(ip_data)

            pv_num_list = [str(int(item['data']['PvNum'])/float(10000)) for item in pv_data]
            ip_num_list = [str(int(item['data']['IpNum'])/float(10000)) for item in ip_data]
            d['pv_list_str'] = ','.join(list(reversed(pv_num_list)))
            d['ip_list_str'] = ','.join(list(reversed(ip_num_list)))

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
        for item in ['depth','download_latency','download_slot','download_timeout','retry_times']:
            if item in d.keys():
                d.pop(item)

        item = MedialabelspiderItem(**d)

        yield item