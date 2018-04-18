# coding: utf-8
"""
Create on 2018/4/16

@author:hexiaosong
"""

import os
from os.path import dirname

PROJECT_ROOT = dirname(dirname(dirname(os.path.abspath(__file__))).replace('\\', '/')).replace('\\', '/')


if __name__ == '__main__':
    print(PROJECT_ROOT)