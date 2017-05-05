#!/bin/sh

import sys, os
sys.path.append(os.path.abspath('functions'))

path = os.path.abspath('spiders')

execfile(path+'/ebates_spider.py')
execfile(path+'/coupons_spider.py')
execfile(path+'/retailmenot_spider.py')
