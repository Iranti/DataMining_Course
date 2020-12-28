import datetime as dt
import json
import scrapy
from instagram_les.instagram.items import InstaTag, InstaPost, Insta, InstaUser, InstaFollow, InstaFollowedBy, InstaMutualFriends
#from instagram_les.instagram.loaders import InstaPostLoader, InstaTagLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    api_url = '/graphql/query/'
    query_hash = {
        'posts': '56a7068fea504063273cc2120ffd54f3',
        'tag_posts': "9b498c08113f1e09617a1703c22b2f32",
        'follow': 'd04b0a864b4b54837c0d870b0e77e076',
        'followers': 'c76146de99bb02f6415203be841dd25a'
    }
    follow_friends_list = []
    followed_by_friends_list = []
    mutual_follow_list = []

    def __init__(self, login, enc_password, *args, **kwargs):
        #self.tags = ['python', 'PS5']
        self.users = ['irina.v.antonova', ]
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
                #for tag in self.tags:
                    #yield response.follow(f'/explore/tags/{tag}/', callback=self.tag_parse)
                for user in self.users:
                    yield response.follow(f'/{user}/', callback=self.user_page_parse)


    #def tag_parse(self, response):
        #tag = self.js_data_extract(response)['entry_data']['TagPage'][0]['graphql']['hashtag']

        #yield InstaTag(
            #date_parse=dt.datetime.utcnow(),
            #data={
                #'tag_id': tag['id'],
                #'name': tag['name'],
                #'profile_pic_url': tag['profile_pic_url'],
                #'count': tag['edge_hashtag_to_media']['count']
            #}
        #)

        #loader = InstaTagLoader(response=response)
        #loader.add_value('profile_pic_url', tag['profile_pic_url'])
        #loader.add_value('tag_id', tag['id'])
        #loader.add_value('name', tag['name'])
        #loader.add_value('count', str(tag['edge_hashtag_to_media']['count']))
        #loader.add_value('date_parse', dt.datetime.utcnow())

        #yield loader.load_item()
        #yield response.follow(response.xpath(self.vacancy_xpath['author_url']).get(), callback=self.author_parse)
        #yield from self.get_tag_posts(tag, response)

    #def tag_api_parse(self, response):
        #yield from self.get_tag_posts(response.json()['data']['hashtag'], response)

    #def get_tag_posts(self, tag, response):
        #if tag['edge_hashtag_to_media']['page_info']['has_next_page']:
            #variables = {
                #'tag_name': tag['name'],
                #'first': 100,
                #'after': tag['edge_hashtag_to_media']['page_info']['end_cursor'],
            #}
            #url = f'{self.api_url}?query_hash={self.query_hash["tag_posts"]}&variables={json.dumps(variables)}'
            #yield response.follow(url, callback=self.tag_api_parse)

        #yield from self.get_post_item(tag['edge_hashtag_to_media']['edges'])

    #@staticmethod
    #def get_post_item(edges):
        #for node in edges:
            #yield InstaPost(
                #date_parse=dt.datetime.utcnow(),
                #data=node['node'],
                #pictures=node['node']['thumbnail_resources']
            #)

    @staticmethod
    def js_data_extract(response):
        script = response.xpath('//script[contains(text(), "window._sharedData =")]/text()').get()
        return json.loads(script.replace("window._sharedData =", '')[:-1])

    def user_page_parse(self, response):
        user_data = self.js_data_extract(response)['entry_data']['ProfilePage'][0]['graphql']['user']
        yield InstaUser(
            date_parse=dt.datetime.utcnow(),
            data=user_data
        )

        yield from self.get_api_follow_request(response, user_data)
        yield from self.get_api_followed_by_request(response, user_data)

    def mutual_friends_identifier(self, follow_friends_list, followed_by_friends_list):
        for i in follow_friends_list:
            for y in followed_by_friends_list:
                if i == y:
                    self.mutual_follow_list.append(i)
        return self.mutual_follow_list


    def get_api_follow_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["follow"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_follow, cb_kwargs={'user_data': user_data})

    def get_api_followed_by_request(self, response, user_data, variables=None):
        if not variables:
            variables = {
                'id': user_data['id'],
                'first': 100,
            }
        url = f'{self.api_url}?query_hash={self.query_hash["followers"]}&variables={json.dumps(variables)}'
        yield response.follow(url, callback=self.get_api_followed_by, cb_kwargs={'user_data': user_data})

    def get_api_follow(self, response, user_data):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield from self.get_follow_item(user_data, data['data']['user']['edge_follow']['edges'])
            if data['data']['user']['edge_follow']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_follow']['page_info']['end_cursor'],
                }
                yield from self.get_api_follow_request(response, user_data, variables)


    def get_api_followed_by(self, response, user_data):
        if b'application/json' in response.headers['Content-Type']:
            data = response.json()
            yield from self.get_followed_by_item(user_data, data['data']['user']['edge_followed_by']['edges'])
            if data['data']['user']['edge_followed_by']['page_info']['has_next_page']:
                variables = {
                    'id': user_data['id'],
                    'first': 100,
                    'after': data['data']['user']['edge_followed_by']['page_info']['end_cursor'],
                }
                yield from self.get_api_followed_by_request(response, user_data, variables)

    def get_follow_item(self, user_data, follow_users_data):
        #global follow_friends_list
        #follow_friends_list = []
        for user in follow_users_data:
            yield InstaFollow(
                user_id=user_data['id'],
                user_name=user_data['username'],
                follow_id=user['node']['id'],
                follow_name=user['node']['username']
            )

            #yield InstaUser(
                #date_parse=dt.datetime.utcnow(),
                #data=user['node']
            #)
            self.follow_friends_list.append(user['node']['id'])
        print('List', self.follow_friends_list)
        #print(f'Follow List {followed_by_friends_list}')
        #return follow_friends_list

    def get_followed_by_item(self, user_data, followed_by_users_data):
        #global followed_by_friends_list
        #followed_by_friends_list = []
        for user in followed_by_users_data:
            yield InstaFollowedBy(
                user_id=user_data['id'],
                user_name=user_data['username'],
                followed_by_id=user['node']['id'],
                followed_by_name=user['node']['username'],
                #mutual_friend=self.mutual_friends_assess(self, InstaFollow('follow_id'), InstaFollowedBy('followed_by_id'))
            )
            #yield InstaUser(
                #date_parse=dt.datetime.utcnow(),
                #data=user['node']
            #)
            self.followed_by_friends_list.append(user['node']['id'])
        #print(f'Followed_by List {followed_by_friends_list}')
        #return followed_by_friends_list
        print('Friends', set(self.mutual_friends_identifier(self.follow_friends_list, self.followed_by_friends_list)))

    def mutual_friends_assess(self, InstaFollow, InstaFollowedBy):
        for followed_by in InstaFollowedBy['followed_by_id']:
            for follower in InstaFollow['follow_id']:
                if followed_by == follower:
                    return True
                else: return False

