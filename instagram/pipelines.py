# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
import pymongo
import requests


class GbParsePipeline:
    collection_name = 'Instagram_items'

    def __init__(self,  mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('Parse_Insta', 'insta_items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

class GbImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        media_item = item.get('pictures', [])
        for img in media_item:
            img_url = img['src']
            yield Request(img_url)

    def item_completed(self, results, item, info):
        item['pictures'] = [itm[1] for itm in results]
        return item

    #def image_save(self, item, url):
        #item =
        #response = requests.get(url)
        #with open(f'{url}.png', 'wb') as file:
            #file.write(response.content)
