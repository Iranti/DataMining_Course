# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

#class GbParseItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    #pass

class Insta(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    data = scrapy.Field()
    img = scrapy.Field()


class InstaTag(Insta):
    _id = scrapy.Field()
    tag_id = scrapy.Field()
    name = scrapy.Field()
    profile_pic_url = scrapy.Field()
    count = scrapy.Field()


class InstaPost(Insta):
    id = scrapy.Field()
    data = scrapy.Field()
    post_id = scrapy.Field()
    text = scrapy.Field()
    comments_count = scrapy.Field()
    taken_at_timestamp = scrapy.Field()
    display_url = scrapy.Field()
    likes = scrapy.Field()
    owner = scrapy.Field()
    pictures = scrapy.Field()
    accessabolity_caption = scrapy.Field()


class InstaUser(Insta):
    pass


class InstaFollow(scrapy.Item):
    _id = scrapy.Field()
    date_parse = scrapy.Field()
    user_name = scrapy.Field()
    user_id = scrapy.Field()
    follow_name = scrapy.Field()
    follow_id = scrapy.Field()
