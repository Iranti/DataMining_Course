# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#class GbLes5ParseItem(scrapy.Item):
    # define the fields for your item here like:
    #name = scrapy.Field()
    #pass


class HHVacancyItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    author_url = scrapy.Field()

class HHAuthorItem(scrapy.Item):
    _id = scrapy.Field()
    author = scrapy.Field()
    comp_url = scrapy.Field()
    #industry = scrapy.Field()
    description = scrapy.Field()
    vacancies = scrapy.Field()


