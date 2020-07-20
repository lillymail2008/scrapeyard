# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from itemadapter import is_item, ItemAdapter
import websockets
from scrapy.http import HtmlResponse
from logging import getLogger
import asyncio
import pyppeteer
import logging
from concurrent.futures._base import TimeoutError

pyppeteer_level = logging.WARNING
logging.getLogger('websockets.protocol').setLevel(pyppeteer_level)
logging.getLogger('pyppeteer').setLevel(pyppeteer_level)

# useful for handling different item types with a single interface

class CrawlSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class CrawlDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class PyppeteerMiddleware():
    def __init__(self, **args):
        """
        init logger, loop, browser
        :param args:
        """
        self.logger = getLogger(__name__)
        self.loop = asyncio.get_event_loop()
        self.browser = self.loop.run_until_complete(
            pyppeteer.launch(headless=True))
        self.args = args

    def __del__(self):
        """
        close loop
        :return:
        """
        self.loop.close()

    def render(self, url, retries=1, script=None, wait=0.3, scrolldown=False, sleep=0,
               timeout=8.0, keep_page=False):
        """
        render page with pyppeteer
        :param url: page url
        :param retries: max retry times
        :param script: js script to evaluate
        :param wait: number of seconds to wait before loading the page, preventing timeouts
        :param scrolldown: how many times to page down
        :param sleep: how many long to sleep after initial render
        :param timeout: the longest wait time, otherwise raise timeout error
        :param keep_page: keep page not to be closed, browser object needed
        :param browser: pyppetter browser object
        :param with_result: return with js evaluation result
        :return: content, [result]
        """

        # define async render
        async def async_render(url, script, scrolldown, sleep, wait, timeout, keep_page):
            try:
                # basic render
                page = await self.browser.newPage()
                await asyncio.sleep(wait)
                response = await page.goto(url, options={'timeout': int(timeout * 1000)})
                if response.status != 200:
                    return None, None, response.status
                result = None
                # evaluate with script
                if script:
                    result = await page.evaluate(script)

                # scroll down for {scrolldown} times
                if scrolldown:
                    for _ in range(scrolldown):
                        await page._keyboard.down('PageDown')
                        await asyncio.sleep(sleep)
                else:
                    await asyncio.sleep(sleep)
                if scrolldown:
                    await page._keyboard.up('PageDown')

                # get html of page
                content = await page.content()

                print(content);
                return content, result, response.status
            except TimeoutError:
                return None, None, 500
            finally:
                # if keep page, do not close it
                if not keep_page:
                    await page.close()

        content, result, status = [None] * 3

        # retry for {retries} times
        for i in range(retries):
            if not content:
                content, result, status = self.loop.run_until_complete(
                    async_render(url=url, script=script, sleep=sleep, wait=wait,
                                 scrolldown=scrolldown, timeout=timeout, keep_page=keep_page))
            else:
                break

        # if need to return js evaluation result
        return content, result, status

    def process_request(self, request, spider):
        """
        :param request: request object
        :param spider: spider object
        :return: HtmlResponse
        """
        if request.meta.get('render'):
            try:
                self.logger.debug('rendering %s', request.url)
                html, result, status = self.render(request.url)
                return HtmlResponse(url=request.url, body=html, request=request, encoding='utf-8',
                                    status=status)
            except websockets.exceptions.ConnectionClosed:
                pass

    @classmethod
    def from_crawler(cls, crawler):
        return cls(**crawler.settings.get('PYPPETEER_ARGS', {}))