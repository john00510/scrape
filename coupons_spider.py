#!/usr/bin/python

from datetime import datetime
import sys, os, time
sys.path.append(os.path.abspath('').replace('coupons', 'functions'))
from functions import csv_file, mongo_db, spider_sel, data_cleaner


def scroll_down(driver):
    prev = None
    while True:
        cur = len(driver.find_elements_by_xpath('.//div[@class="pages"]/div[@class="page"]'))
        if cur == prev:
            break
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(10)
        prev = cur

def scraping(driver, fh, coll, url):
    total = driver.find_element_by_xpath('.//div[@class="page"]/div[@class="seg-label title homepage-title title-cat"]/h2').text.split(' ')[0]
    pages = driver.find_elements_by_xpath('.//div[@class="pages"]/div[@class="page"]')
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
                    item['details'] = coupon.find_element_by_xpath('./p[@class="details"]').text.strip().encode('utf8')
                    if len(item['brand']) == 0: continue
                    item['cashback'] = data_cleaner(item['offer'], item['details'])
                    item['source'] = url
                    item['timestamp'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    item['url'] = ''
                    coll.insert(item)
                    line = '"%s","%s","%s","%s","%s","%s",%s\n' % (item['brand'], item['cashback'], item['offer'], item['details'], item['url'],  item['source'], item['timestamp'])
                    fh.write(line)

def main():
    print '...running coupons spider'
    url = 'https://www.coupons.com/coupons/'
    fn = 'coupons'
    header = 'brand,cashback,offer,details,url,source,date_time\n'
    driver = spider_sel(url)
    fh = csv_file(fn, header)
    client, coll = mongo_db()
    scroll_down(driver)
    scraping(driver, fh, coll, url)
    driver.quit()
    fh.close()
    client.close()

main()
