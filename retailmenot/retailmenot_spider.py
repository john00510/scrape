#!/usr/bin/python

from lxml import html
from datetime import datetime
import sys, os
sys.path.append(os.path.abspath('').replace('retailmenot', 'functions'))
from functions import data_cleaner, spider, csv_file, mongo_db


def scraping1(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//div[@class="js-recommended-merchant recommended-merchant"]')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('./div/img/@alt')[0].replace('Coupons', '').strip()
        item['offer'] = e.xpath('./div')[1].text.replace('\n', ' ').strip()
        item['details'] = ''
        item['url'] = ''
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        item['cashback'] = data_cleaner(item['offer'], item['details']) 
        coll.insert(item)
        line = '"%s","%s","%s","%s","%s",%s\n' % (item['brand'], item['cashback'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def scraping2(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//ul[@class="coupon-list js-offers"]/li')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('.//div[contains(@class, "offer-merchant-name")]/text()')[0].strip().encode('utf8')
        item['offer'] = e.xpath('.//a[contains(@class, "offer-title")]/text()')[0].strip().encode('utf8')
        item['details'] = e.xpath('.//div[@class="offer-description"]/text()')[0].replace('\n', ' ').strip().encode('utf8')
        item['url'] = e.xpath('.//a/img/@data-merchant-name')[0]
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        item['cashback'] = data_cleaner(item['offer'], item['details'])
        coll.insert(item)
        line = '"%s","%s","%s","%s","%s",%s\n' % (item['brand'], item['cashback'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def scraping3(response, fh, coll):
    data = html.fromstring(response.text)
    elements = data.xpath('.//div[@class="carousel-slide js-carousel-slide js-triggers-outclick"]')
    for e in elements:
        item = dict()
        item['brand'] = e.xpath('./@data-site-title')[0].strip().encode('utf8')
        item['offer'] = e.xpath('./a/img/@alt')[0].strip().encode('utf8')
        item['details'] = e.xpath('./a/div/div/p/text()')[0].replace('\n', ' ').strip().encode('utf8')
        item['url'] = e.xpath('./@data-merchant-name')[0]
        item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        item['cashback'] = data_cleaner(item['offer'], item['details'])
        coll.insert(item)
        line = '"%s","%s","%s","%s","%s",%s\n' % (item['brand'], item['cashback'], item['offer'], item['details'], item['url'], item['timestamp'])
        fh.write(line)

def main():
    url = 'https://www.retailmenot.com/'
    fn = 'retailmenot'
    response = spider(url)
    fh = csv_file(fn)
    client, coll = mongo_db()
    scraping1(response, fh, coll)
    scraping2(response, fh, coll)
    scraping3(response, fh, coll)
    fh.close()
    client.close()

main()
