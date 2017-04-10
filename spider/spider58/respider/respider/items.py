# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class RespiderItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    zone = scrapy.Field()
    location = scrapy.Field()
    room = scrapy.Field()
    price = scrapy.Field()
    last_post = scrapy.Field()
    detail = scrapy.Field()
    fine = scrapy.Field()
    duplication = scrapy.Field()
    img_cnt = scrapy.Field()
