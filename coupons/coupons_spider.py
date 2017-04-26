#!/usr/bin/python

from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pymongo import MongoClient
import time
import csv

def spider(url):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    #driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(5)
    return driver

def scroll_down(driver):
    prev = None
    while True:
        cur = len(driver.find_elements_by_xpath('.//div[@class="pages"]/div[@class="page"]'))
        if cur == prev:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        prev = cur

def csv_file():
    date = datetime.utcnow().strftime('%Y_%m_%d')
    fn = 'coupons_%s.csv' % date
    header = 'brand,offer,details,timestamp\n'
    fh = open(fn, 'w')
    fh.write(header)
    return fh

def mongo_db():
    profile = "mongodb://mongodb0.example.net:27017"
    client = MongoClient()
    db = client.coupons
    coll = db.dataset
    return coll, client

def scraping(driver, fh, coll):
    total = driver.find_element_by_xpath('.//div[@class="page"]/div[@class="seg-label title homepage-title title-cat"]/h2').text.split(' ')[0]
    pages = driver.find_elements_by_xpath('.//div[@class="pages"]/div[@class="page"]')
    items = 0
    d = ','
    for page in pages:
        rows1 = page.find_elements_by_xpath('./div[@class="row"]')
        for row1 in rows1:
            rows2 = row1.find_elements_by_xpath('./div[@class="column grid_1"]')
            for row2 in rows2:
                coupons = row2.find_elements_by_xpath('.//div[@class="pod-info"]')
                for coupon in coupons:
                    item = dict()
                    item['offer'] = coupon.find_element_by_xpath('./h4[@class="summary"]').text.strip().encode('utf8')
                    item['brand'] = coupon.find_element_by_xpath('./h5[@class="brand"]').text.strip().encode('utf8')
                    if len(item['brand']) == 0: continue
                    item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    item['details'] = coupon.find_element_by_xpath('./p[@class="details"]').text.strip().encode('utf8')
                    coll.insert(item)
                    line = '"%s","%s","%s",%s\n' % (item['brand'],item['offer'],item['details'],item['timestamp'])
                    fh.write(line)
                    items += 1
    
    print 'total:', total
    print 'scraped:', items

def main():
    url = 'https://www.coupons.com/coupons/'
    driver = spider(url)
    fh = csv_file()
    coll, client = mongo_db()
    scroll_down(driver)
    scraping(driver, fh, coll)
    driver.quit()
    fh.close()
    client.close()

main()
