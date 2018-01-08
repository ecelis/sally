# -*- coding: utf-8 -*-

# Scrapy settings for sally project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

### Test settings
SHEET_ID='1AxioUWtPJItfnv--JxNg5-oiUUMJgW4uoQopx-JlH00'
SHEET_NAME='testing'
### END test settings

BOT_NAME = 'sally'

### BEGIN Eve settings

API_VERSION = 'v1'
DOMAIN = { 'lightfoot': {}}
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_DBNAME = BOT_NAME + '_' + API_VERSION
#MONGO_USERNAME =
#MONGO_PASSWORD =
ALLOWED_FILTERS = []

### END Eve settings

SPIDER_MODULES = ['sally.spiders']
NEWSPIDER_MODULE = 'sally.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'sally (+http://www.shipkraken.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

FEED_FORMAT = 'jsonlines'
## AttributeError: 'FeedExporter' object has no attribute 'slot'
## https://github.com/scrapy/scrapyd/issues/31

#FEED_URI = 'file:///tmp/sally/%(name)s/%s(time)s.csv'

DEPTH_LIMIT = 1

OUTPUT_PATH = '/tmp/sally/test.json'
# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

REACTOR_THREADPOOL_MAXSIZE = 20

RETRY_ENABLED = False

AJAXCRAWL_ENABLED = True

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'sally.middlewares.SallySpiderMiddleware': 543,
#}
SPIDER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 543,
}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'sally.middlewares.MyCustomDownloaderMiddleware': 543,
#}
DOWNLOADER_MIDDLEWARES = {
    'scrapy.spidermiddlewares.offsite.OffsiteMiddleware': 540,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 543,
}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'sally.pipelines.SallyPipeline': 300,
#}
ITEM_PIPELINES = {
    'sally.pipelines.LightfootPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
