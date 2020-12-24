from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_les5_parse.spiders.hh import HHSpider

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('gb_les5_parse.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    crawl_proc.crawl(HHSpider)
    crawl_proc.start()