# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Rule
from scrapy import Request
from scrapy.linkextractors import LinkExtractor
from ..spidy import RedisCrawlSpider
from ..spidy import RedisSpider
from urllib.parse import urlparse

#redis-cli lpush am:start_urls https://www.cnn.com

class AmSpider(RedisCrawlSpider):
    name = "am"
    redis_key = 'am:start_urls'

    rules = (
        Rule(LinkExtractor(allow='www.audiomack.com/trending-now'), callback='parse_trending', follow=False, process_request='process_req'),
        Rule(LinkExtractor(allow=[r'[\w\-]+/song/[\w\-]+']), callback='parse_song', follow=False)
    )

    def process_req(self, req, res):
        req.meta['scrollyes'] = True;
        return req;

    def parse_song(self, response):
        response;
        pass;

    def parse_trending(self, response):
        items = response.xpath("//*[contains(@class, 'music-detail__link')]/@href");
        for item in items:
            link = item.get();
            #yield Request(link, meta={'render': True}, dont_filter=True);

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