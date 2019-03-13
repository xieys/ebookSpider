# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class BookDataPipeline(object):
    def process_item(self, item, spider):
        if item['book_date'] is not None:
            item['book_date'] = item['book_date'].strip()
        if item['book_detail_url'] is not None:
            item['book_detail_url'] = 'https:' + item['book_detail_url']
        if item['book_img'] is not None:
            item['book_img'] = 'https:' + item['book_img']
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    def process_item(self, item, spider):
        print(item)
        name = spider.name
        self.db[name].insert(dict(item))
        return item

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()
