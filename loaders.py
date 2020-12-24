import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from .items import HHVacancyItem, HHAuthorItem


class HHVacancyLoader(ItemLoader):
    default_item_class = HHVacancyItem
    default_input_processor = MapCompose
    title_in = ''.join
    title_out = TakeFirst()
    author_url_in = ''.join
    author_url_out = TakeFirst()
    description_in = ''.join
    description_out = TakeFirst()
    salary_in = ''.join
    salary_out = TakeFirst()
    skills_in = ', '.join
    skills_out = TakeFirst()

class HHAuthorItemLoader(ItemLoader):
    default_item_class = HHAuthorItem
    author_in = ''.join
    author_out = TakeFirst()
    comp_url_in = ''.join
    comp_url_out = TakeFirst()
    #industry_in = ''.join
    #industry_out = TakeFirst()
    description_in = ' '.join
    description_out = TakeFirst()
    vacancies_in = ', '.join
    vacancies_out = TakeFirst()