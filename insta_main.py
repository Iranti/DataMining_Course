import os
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instagram_les.instagram.spiders.insta_spider import InstagramSpider
import dotenv

dotenv.load_dotenv('../venv/.env')

if __name__ == '__main__':
    crawl_settings = Settings()
    crawl_settings.setmodule('instagram_les.instagram.settings')
    crawl_proc = CrawlerProcess(settings=crawl_settings)
    password=os.getenv('PASSWORD')
    login = os.getenv('LOGIN')
    crawl_proc.crawl(InstagramSpider, login, password)
    crawl_proc.start()
