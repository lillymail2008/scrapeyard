import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urljoin

class CurspaceSpider(CrawlSpider):
    name="audiomack"
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.name = 'audiomack'
        self.allowed_domains = ['audiomack.com']
        self.start_urls = ['https://www.audiomack.com']

    rules = (
        # Extract links matching 'category.php' (but not matching 'subsection.php')
        # and follow links from them (since no callback means follow=True by default).
        Rule(LinkExtractor()),
    );

    def parse(self, response):
        self.logger.info('Parent : %s', response.url)
        for href in response.xpath('//a/@href').getall():
            self.logger.info('Child : %s', href)
            yield scrapy.Request(urljoin(response.url, href), self.parse, meta={"pyppeteer": True});

    def parse_item(self, response):
        self.logger.info('Url : %s', response.url)
        item = scrapy.Item()
        return item