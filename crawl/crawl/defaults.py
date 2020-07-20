import redis


# For standalone use.
DUPEFILTER_KEY = 'dupefilter:%(timestamp)s'
PIPELINE_KEY = '%(spider)s:items'
REDIS_CLS = redis.StrictRedis
REDIS_ENCODING = 'utf-8'

REDIS_PARAMS = {
    'socket_timeout': 30,
    'socket_connect_timeout': 30,
    'retry_on_timeout': True,
    'encoding': REDIS_ENCODING,
}

SCHEDULER_QUEUE_KEY = '%(spider)s:requests'
SCHEDULER_QUEUE_CLASS = 'crawl.queue.PriorityQueue'
SCHEDULER_DUPEFILTER_KEY = '%(spider)s:dupefilter'
SCHEDULER_DUPEFILTER_CLASS = 'crawl.dupefilter.RedisDupeFilter'

START_URLS_KEY = '%(name)s:start_urls'
START_URLS_AS_SET = False
START_URLS_AS_ZSET = False
