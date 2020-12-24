import re
from scrapy import Request
import requests
import scrapy
import pymongo
import json
import urllib
import urllib.parse


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    ccs_query = {
        'brands': 'div.ColumnItemList_container__5gTrc div.ColumnItemList_column__5gjdt a.blackLink',
        'pagination': '.Paginator_block__2XAPy a.Paginator_button__u1e7D',
        'ads': 'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = pymongo.MongoClient()['Les4_auto_parse']['GB_parse']

    def parse(self, response):
        for brand in response.css(self.ccs_query['brands']):
            yield response.follow(brand.attrib.get('href'), callback=self.brand_page_parse)

    def brand_page_parse(self, response):
        for pag_page in response.css(self.ccs_query['pagination']):
            yield response.follow(pag_page.attrib.get('href'), callback=self.brand_page_parse)

        for ads_page in response.css(self.ccs_query['ads']):
            yield response.follow(ads_page.attrib.get('href'), callback=self.ads_parse)

    def ads_parse(self, response):
        data = {
            'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
            'images': [img.attrib.get('src') for img in response.css('figure.PhotoGallery_photo__36e_r img')],
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').get(),
            'url': response.url,
            'author': self.js_decoder_autor(response),
            'specification': self.get_specifications(response),
            'year production': response.css('.AdvertSpecs_data__xK2Qx a.blackLink::text').get(),
            'tel': self.tel_parse(response)
        }

        self.db.insert_one(data)

    def get_specifications(self, response):
        return {itm.css('.AdvertSpecs_label__2JHnS::text').get(): itm.css(
            '.AdvertSpecs_data__xK2Qx::text').get() or itm.css('a::text').get() for itm in
                response.css('.AdvertSpecs_row__ljPcX')}

    def js_decoder_autor(self, response):
        # script = response.xpath('//script[contains(text(), "window.transitState =")]/text()').get()
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        re_str = re.compile(r"youlaId%22%2C%22([0-9|a-zA-Z]+)%22%2C%22avatar")
        result = re.findall(re_str, script)
        return f'https://youla.ru/user/{result[0]}' if result else None

    def tel_parse(self, response):
        requests.get('https://sslwidget.criteo.com/event?a=31409&v=5.6.2&p0=e%3Dce%26m%3D%255B%255D&p1=e%3Dexd%26site_type%3Dd&p2=e%3Dvc%26id%3Dcriteo_transaction_show_phone%26p%3D%255Bi%25253D29a02748e1ee8e9e%252526pr%25253D8300000%252526q%25253D1%255D&p3=e%3Ddis&adce=1&bundle=2fConV9adFFjeUlNU3FBQ0E0bSUyQnkwamFNNiUyQjNCT040TGdpZW9QV0dYdVlpcXFYaHclMkZaUE0lMkZESkREWnF0NU1LcWdXb1hoMENjbGlvbXJVbzVvM1VNZiUyRnYzbXlObE1UTVFWaE4zQnRZekI1REV1bWI1d3pyYjRHVWVpSzRCQmRoWlFhZmpGRDJ1dlNHT28wTUQlMkJvS1JjbUp5U0ElM0QlM0Q&tld=youla.ru&dtycbr=40976')
        script = response.css('script:contains("window.transitState = decodeURIComponent")::text').get()
        #script = response.css('div.Popup_block__2-Er4')
        #res = script.split('phones')
        #res_str = re.findall(res[1], script)
        #script_decode = urllib.parse.unquote(str(script))
        res_str = re.findall(r'\+[0-9]\([0-9]{3}\)[0-9]{3}-[0-9]{2}-[0-9]{2}', script)
        #result = urllib.parse.unquote(str(res_str))
        return  f'{res_str}'


    #def get_mobile(self, response):
        #css-селектор .PopupPhoneNumber_number__1hybY
        #script = response.xpath('//script[contains("span.PopupPhoneNumber_number__1hybY")]/text()').get()
        #+7(495) 136 - 83 - 37

