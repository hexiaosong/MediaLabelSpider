# coding: utf-8
"""
Create on 2018/4/16

@author:hexiaosong
"""
from scrapy import cmdline
from scrapy.cmdline import execute




if __name__ == '__main__':

    cmdline.execute("scrapy crawl media_label".split())