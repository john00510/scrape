import requests
from pymongo import MongoClient
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

def spider(url):
    r = requests.get(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0', 'referer': 'https://www.ebates.com/index.htm'}
    )
    return r

def sel_spider(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver.get(url)
    time.sleep(5)
    return driver

def double_cash_back(collection):
    url = 'https://www.ebates.com/athleisure-deals.htm'
    response = spider(url)
    data = html.fromstring(response.text)
    for e in  data.xpath('.//ul/li/a[@class="bblk nohover"]'):
        item = dict()
        item['url'] = e.xpath('./@href')[0].strip('/')
        item['cashback'] = e.xpath('./span/text()')[1].strip().split(' ')[0]
        collection.insert(item)
        print item

def hot_deals(collection):
    url = 'https://www.ebates.com/deals.htm'
    response = spider(url)
    data = html.fromstring(response.text)
    for e in data.xpath('.//div[@id="coupons"]/div[@class="coupon-blk logo-blk blk border-b pad-30"]'):
        item = dict()
        item['url'] = e.xpath('./div[@class="merchlogo flt"]/a/@href')[0].strip('/')
        item['cashback'] = e.xpath('./ul/li/span/text()')[1].split('Cash')[0].strip().strip('+').strip()
        collection.insert(item)
        print item

def luxury(collection):
    url = 'https://www.ebates.com/luxury/all-stores.htm'
    driver = sel_spider(url)
    for e in driver.find_elements_by_xpath('.//ul[@class="store-sort"]/li'):
        item = dict()
        url = e.find_element_by_xpath('./a').get_attribute('href').split('/')
        if 'mytheresa-com' in url: item['url'] = 'mytheresa.com' 
        else: item['url'] =  e.find_element_by_xpath('./a').get_attribute('href').split('/')[-1]
        item['cashback'] = e.find_elements_by_xpath('./a/span')[1].text.split(' ')[0].strip()
        collection.insert(item)
        print item

def in_store(collection):
    url = 'https://www.ebates.com/in-store.htm'
    driver = sel_spider(url)
    for e in driver.find_elements_by_xpath('.//div[@id="clo-offers-cont"]/div'):
        item = dict()
        item['url'] = e.find_element_by_xpath('./img').get_attribute('title')
        item['cashback'] = e.find_elements_by_xpath('./div')[0].text.split(' ')[0]
        collection.insert(item)
        print item

    driver.quit()

def main():
    profile = "mongodb://mongodb0.example.net:27017"
    client = MongoClient()
    db = client.ebates
    coll = db.dataset

    double_cash_back(coll)
    time.sleep(5)
    hot_deals(coll)
    time.sleep(5)
    luxury(coll)
    time.sleep(5)
    in_store(coll)

    client.close()

main()
