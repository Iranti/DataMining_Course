import datetime as dt
import json
import scrapy
from instagram_les.instagram.items import InstaTag, InstaPost, Insta, InstaUser
from instagram_les.instagram.loaders import InstaPostLoader, InstaTagLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'tag_posts': "9b498c08113f1e09617a1703c22b2f32",
    }

    def __init__(self, login, enc_password, *args, **kwargs):
        self.tags = ['python', 'PS5']
        #self.users = ['teslamotors', ]
        self.login = login
        self.enc_passwd = enc_password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method='POST',
                callback=self.parse,
                formdata={
                    'username': self.login,
                    'enc_password': self.enc_passwd,
                },
                headers={'X-CSRFToken': js_data['config']['csrf_token']}
            )
        except AttributeError as e:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)

    def tag_parse(self, response):
        tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        #yield InstaTag(
            #date_parse=dt.datetime.utcnow(),
            #data={
                #'tag_id': tag['id'],
                #'name': tag['name'],
                #'profile_pic_url': tag['profile_pic_url'],
                #'count': tag['edge_hashtag_to_media']['count']
            #}
        #)

        loader = InstaTagLoader(response=response)
        loader.add_value('profile_pic_url', tag['profile_pic_url'])
        loader.add_value('tag_id', tag['id'])
        loader.add_value('name', tag['name'])
        loader.add_value('count', str(tag['edge_hashtag_to_media']['count']))
        loader.add_value('date_parse', dt.datetime.utcnow())

        yield loader.load_item()
        #yield response.follow(response.xpath(self.vacancy_xpath['author_url']).get(), callback=self.author_parse)
        yield from self.get_tag_posts(tag, response)

    def tag_api_parse(self, response):
        yield from self.get_tag_posts(response.json()['data']['hashtag'], response)

    def get_tag_posts(self, tag, response):
        if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            variables = {
                'tag_name': tag['name'],
                'first': 100,
                'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            }
            url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
            yield response.follow(url, callback=self.tag_api_parse)

        yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    @staticmethod
    def get_post_item(edges):
        for node in edges:
            yield InstaPost(
                date_parse=dt.datetime.utcnow(),
                data=node['node'],
                pictures=node['node']['thumbnail_resources']
            )

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])
