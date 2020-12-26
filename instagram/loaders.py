import scrapy
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from .items import InstaTag, InstaPost


class InstaTagLoader(ItemLoader):
    default_item_class = InstaTag
    default_input_processor = MapCompose
    tag_id_in = ''.join
    tag_id_out = TakeFirst()
    name_in = ''.join
    name_out = TakeFirst()
    count_in = ''.join
    count_out = TakeFirst()
    #profile_pic_url_in = ''.join()
    profile_pic_url_out = TakeFirst()


class InstaPostLoader(ItemLoader):
    default_item_class = InstaPost
    default_input_processor = MapCompose
    #post_id_in = ''.join
    post_id_out = TakeFirst()
    text_in = ' '.join
    text_out = TakeFirst()
    #comments_count_in = ''.join
    taken_at_timestamp_out = TakeFirst()
    #likes_in = ' '.join
    likes_out = TakeFirst()
    #owner_in = ''.join
    owner_out = TakeFirst()
    pictures_in = ', '.join
    pictures_out = TakeFirst()
    accessabolity_caption_in = ' '.join
    accessabolity_caption_out = TakeFirst()
    display_url_in = ' '.join
    display_url_out = TakeFirst()
