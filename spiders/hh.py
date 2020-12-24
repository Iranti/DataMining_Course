# 1Pipeline
#1. название вакансии
#2. оклад (строкой от до или просто сумма)
#3. Описание вакансии
#4. ключевые навыки - в виде списка названий
#5. ссылка на автора вакансии

import scrapy

from gb_les5_parse.loaders import HHVacancyLoader, HHAuthorItemLoader

class HHSpider(scrapy.Spider):
    name = 'HH'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath = {
        'pagination': '//div[@data-qa="pager-block"]//a[@data-qa="pager-page"]/@href',
        'vacancy_urls': '//a[@data-qa="vacancy-serp__vacancy-title"]/@href'
        #'author_urls': '//a[@data-qa="vacancy-serp__vacancy-employer-logo"]/@href'
    }
    vacancy_xpath = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]//text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//span[@data-qa="bloko-tag__text"]/text()',
        "author_url": '//a[@data-qa="vacancy-company-name"]/@href'
    }

    author_xpath = {
        'author': '//h1/span[contains(@class, "company-header-title-name")]/text()',
        'comp_url': '//a[contains(@data-qa, "sidebar-company-site")]/@href',
        'description': '//div[contains(@data-qa, "company-description")]//text()'
    }

    def parse(self, response, **kwargs):
        for pag_page in response.xpath(self._xpath['pagination']):
            yield response.follow(pag_page, callback=self.parse)

        for vacancy in response.xpath(self._xpath['vacancy_urls']):
            yield response.follow(vacancy, callback=self.vacancy_parse)

    def vacancy_parse(self, response, **kwargs):
        loader = HHVacancyLoader(response=response)
        loader.add_value('author_url', response.url)
        for key, value in self.vacancy_xpath.items():
            loader.add_xpath(key, value)

        yield loader.load_item()
        yield response.follow(response.xpath(self.vacancy_xpath['author_url']).get(), callback=self.author_parse)

    def company_parse_B(self, response, **kwargs):
        vacancies = []
        for _ in response.xpath('//div[contains(@class, "company-vacancies-group")]'):
            itm = response.xpath('//a[contains(@data-qa, "vacancy-serp__vacancy-title")]/text()')
            vacancies.append(itm)
        return vacancies

    def author_parse(self, response, **kwargs):
        loader = HHAuthorItemLoader(response=response)
        loader.add_value('comp_url', response.url)
        for key, value in self.author_xpath.items():
            loader.add_xpath(key, value)
        loader.add_value('vacancies', self.company_parse_B(response))

        yield loader.load_item()



