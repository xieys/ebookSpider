# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BookItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cata_title = scrapy.Field()
    cata_url = scrapy.Field()
    book_detail_url = scrapy.Field()
    book_img = scrapy.Field()
    book_name = scrapy.Field()
    book_author = scrapy.Field()
    book_store = scrapy.Field()
    book_date = scrapy.Field()
    data_sku = scrapy.Field()
    book_price = scrapy.Field()
    book_list_url = scrapy.Field()
