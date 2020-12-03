import os
import time
import datetime as dt
import requests
import bs4
import pymongo
import dotenv
from urllib.parse import urljoin
from dotenv import load_dotenv
from pymongo import MongoClient

dotenv.load_dotenv('.env')

MONTHS = {
    "янв": 1,
    "фев": 2,
    "мар": 3,
    "апр": 4,
    "май": 5,
    "мая": 5,
    "июн": 6,
    "июл": 7,
    "авг": 8,
    "сен": 9,
    "окт": 10,
    "ноя": 11,
    "дек": 12,
}


class MagnitParse:
    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"
    }

    def __init__(self, start_url):
        self.start_url = start_url
        client = MongoClient(os.getenv('mongodb://localhost:27017/'))
        self.db = client['Les2']

    @staticmethod
    def _get(*args, **kwargs):
        while True:
            try:
                response = requests.get(*args, **kwargs)
                print(response)
                if response.status_code != 200:
                    raise Exception
                return response
            except Exception:
                time.sleep(0.5)

    def soup(self, url) -> bs4.BeautifulSoup:
        response = self._get(url, headers=self.headers)
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        soup = self.soup(self.start_url)
        for product in self.parse(soup):
            self.save(product)

    def parse(self, soup):
        catalog = soup.find('div', attrs={'class': 'сatalogue__main'})

        for product in catalog.find_all('a', recursive=False):
            try:
                pr_data = self.get_product(product)
            except AttributeError:
                continue
            yield pr_data

    def get_product(self, product_soup):
        dt_parser = self.date_parse(product_soup.find('div', attrs={'class': 'card-sale__date'}).text)

        product_template = {
            'url': lambda soup: urljoin(self.start_url, soup.get('href')),
            'promo_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda soup: soup.find('div', attrs={'class': 'card-sale__title'}).text,
            'image_url': lambda soup: urljoin(self.start_url, soup.find('img').get('data-src')),
            'old_price': lambda soups:
            float('.'.join(itm for itm in soups.find('div', attrs={'class': 'label__price_old'}).text.split())),
            # <div class="label__price label__price_old">
            # <span>'class="label__price-integer">29</span>
            # <span> 'class="label__price-decimal">99</span>
            'new_price': lambda soups:
            float('.'.join(itm for itm in soups.find('div', attrs={'class': 'label__price_new'}).text.split())),
            # "date_from": "DATETIME",
            # <div class="card-sale__date">
            # <p>с 02 декабря</p>
            # <p>до 08 декабря</p>
            # </div>
            'date_from': lambda _: next(dt_parser),
            'date_to': lambda _: next(dt_parser),
        }

        result = {}
        for key, value in product_template.items():
            try:
                result[key] = value(product_soup)
            except (AttributeError, ValueError, StopIteration):
                continue
        return result

    #def save(self, product):
        #collection = self.db['magnit_case']
        #collection.insert_one(product)

    @staticmethod
    def date_parse(date_string: str):
        date_list = date_string.replace('с ', '', 1).replace('\n', '').split('до')
        for date in date_list:
            temp_date = date.split()
            yield dt.datetime(year=dt.datetime.now().year, day=int(temp_date[0]), month=MONTHS[temp_date[1][:3]])

    def save(self, data: dict):
        collection = self.db['magnit_case']
        collection.insert_one(data)


if __name__ == '__main__':
    parser = MagnitParse('https://magnit.ru/promo/?geo=moskva')
    parser.run()