# encoding=utf8

import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import datetime
from pymongo import MongoClient
import time, os

def data_cleaner(offer, details):
    data1 = offer.split(' ')
    data2 = details.split(' ')
    try:
        cashback = [x for x in data1 if '%' in x or '$' in x or '¢' in x or '.0' in x][0]
    except:
        try:
            cashback = [x for x in data2 if '%' in x or '$' in x or '¢' in x or '.0' in x][0]
        except:
            cashback = ''
    cashback = cashback.strip('.').strip(')').strip('+').strip('!').strip('*')
    return cashback

def url_cleaner(url):
    if 'yves-saint-laurent' in url:
        return 'yves-saint-laurent.com'
    else:
        return url.split('/')[-1]

def spider(url):
    r = requests.get(
        url,
        headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0) Gecko/20100101 Firefox/39.0'},
    )
    return r

def spider_sel(url):
    log_path = os.path.abspath('logs') + '/phantomjs.log'
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")
    driver = webdriver.PhantomJS(desired_capabilities=dcap, service_log_path=log_path)
    #driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(5)
    return driver

def csv_file(fn, header):
    path = '/'.join(os.path.abspath('').split('/')[:-1])
    filename = path + '/scrape/output/' + fn
    date = datetime.utcnow().strftime('%Y_%m_%d')
    fn = '%s_%s.csv' % (filename, date)
    fh = open(fn, 'w')
    fh.write(header)
    return fh

def csv_file2(header, dt, dh):
    path = '/'.join(os.path.abspath('').split('/')[:-1])
    fn = path + '/scrape/output/%s_%s.csv' % (dh, dt)
    fh = open(fn, 'w')
    fh.write(header)
    return fh

def mongo_db():
    profile = "mongodb://mongodb0.example.net:27017"
    client = MongoClient()
    db = client.coupons
    coll = db.dataset
    return client, coll

def diff(row, number):
    def cell_proc1(cell): # %
        cel = cell.replace('%', '')
        if '-' in cel: 
            cel = cel.split('-')[1]
        cel = float(cel.strip())
        return cel
   
    def cell_proc2(cell): # $
        cel = cell.replace('$', '')
        if '-' in cel:
            cel = cel.split('-')[1]
        cel = float(cel.strip())
        return cel

    if '%' in row['cashback_x']:
        cashback_t = cell_proc1(row['cashback_x'])
        cashback_h = cell_proc1(row['cashback_y'])
        dif = cashback_t - cashback_h
        if dif >= number:
            row['diff'] = str(dif) + '%'
        else:
            row['diff'] = None

    if '$' in row['cashback_x']:
        cashback_t = cell_proc2(row['cashback_x'])
        cashback_h = cell_proc2(row['cashback_y'])
        dif = cashback_t/(cashback_h/100) - 100
        if dif >= number:
            row['diff'] = str(dif) + '%'
        else:
            row['diff'] = None

    return row





