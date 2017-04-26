from scrapy import Spider
from scrapy.selector import Selector

from highside.items import HighsideItem

import logging

class HighsideSpider(Spider):
    name = "highside"
    allowed_domains = ["ebates.com"]
    start_urls = [
        "http://www.ebates.com",
    ]

    def parse(self, response):

        logging.log(logging.DEBUG, " ***  in parse with response = {} ".format(response))
        questions = Selector(response).xpath('//span[@class="now_rebate"]')
        logging.log(logging.DEBUG, " *** in parse with questions = {}".format(questions))

        for question in questions:            
            logging.log(logging.DEBUG, " ***  in parse with question = {} ".format(question))
            item = HighsideItem()
            item['title'] = question.xpath(
                'a[@class="question-hyperlink"]/text()').extract()[0]
            item['url'] = question.xpath(
                'a[@class="question-hyperlink"]/@href').extract()[0]
            yield item
