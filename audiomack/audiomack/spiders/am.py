# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from ..spidy import RedisCrawlSpider
from ..spidy import RedisSpider
from urllib.parse import urlparse

#redis-cli lpush am:start_urls https://www.cnn.com

def my_request_processor(req, res):
    req.meta['render'] = True
    return req;

class AmSpider(RedisCrawlSpider):
    name = "am"
    redis_key = 'am:start_urls'

    rules = (
        Rule(LinkExtractor(), callback='parse_page', follow=True,  process_request=my_request_processor),
        Rule(LinkExtractor(allow='/trending-now'), callback='parse_trending', follow=True, process_request=my_request_processor)
    )

#/html/body/div/div[3]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div/a/h2
#/html/body/div/div[3]/div/div/div/div[2]/div/div/div/div[1]/div[1]/div/a/h2
    def parse_trending(self, response):
        item = response.xpath("//*[contains(@class, 'music__heading--artist')]").get()
        pass;


    '''
    def parse(self, response):
        if not self.allowed_domains:
            parsed_uri = urlparse(response.url);
            domain = '{uri.netloc}'.format(uri=parsed_uri)
            self.allowed_domains.append(domain);
        self.parse(response);
        return;
    '''


    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        #domain = kwargs.pop('domain', '')
        #self.allowed_domains = filter(None, domain.split(','))
        super(AmSpider, self).__init__(*args, **kwargs)

    def parse_page(self, response):
        return {
            'name': response.css('title::text').extract_first(),
            'url': response.url
        }