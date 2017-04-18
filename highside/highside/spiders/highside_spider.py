from scrapy import Spider
from scrapy.selector import Selector

from highside.items import HighsideItem

import logging

class HighsideSpider(Spider):
    name = "highside"
    allowed_domains = ["stackoverflow.com"]
    start_urls = [
        "http://stackoverflow.com/questions?pagesize=50&sort=newest",
    ]

    def parse(self, response):

        logging.log(logging.DEBUG, " ***  in parse with response = {} ".format(response))
        questions = Selector(response).xpath('//div[@class="summary"]/h3')

        for question in questions:            
            logging.log(logging.DEBUG, " ***  in parse with question = {} ".format(question))
            item = HighsideItem()
            item['title'] = question.xpath(
                'a[@class="question-hyperlink"]/text()').extract()[0]
            item['url'] = question.xpath(
                'a[@class="question-hyperlink"]/@href').extract()[0]
            yield item
