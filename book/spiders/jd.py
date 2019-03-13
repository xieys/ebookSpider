# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy
import json
from book.items import BookItem


class JdSpider(scrapy.Spider):
    name = 'ebook_jd'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://e.jd.com/']

    def parse(self, response):
        menu_pattern = re.compile("menu:(\[{.*}\]).*?submenu:", re.S)
        result = menu_pattern.findall(response.text)
        pattern = re.compile("NAME: '(.*?)',URL: '(.*?)',id: '\d+',children:")
        cata_list = pattern.findall(result[0])
        for cata in cata_list[1:]:
            item = BookItem()
            item['cata_title'] = cata[0]
            item['cata_url'] = cata[1]
            if not item['cata_url'].startswith('//list'):
                num_pattern = re.compile(".*/(\d+)-(\d+)-(\d+).html")
                result = num_pattern.findall(item['cata_url'])[0]
                item['cata_url'] = '//list.jd.com/list.html?cat={},{}&tid={}'.format(result[0], result[1], result[2])
            item['cata_url'] = 'https:' + item['cata_url']
            # print(item)
            yield scrapy.Request(
                item['cata_url'],
                callback=self.parse_list,
                meta={'item': deepcopy(item)}
            )

    def parse_list(self, response):
        item = response.meta['item']
        item['book_list_url'] = response.url
        book_list = response.xpath('//ul[@class="gl-warp clearfix"]/li')
        for book in book_list:
            item['book_detail_url'] = book.xpath('.//div[@class="p-name"]/a/@href').extract_first()
            item['book_img'] = book.xpath('.//div[@class="p-img"]/a/img/@src').extract_first()
            if item['book_img'] is None:
                item['book_img'] = book.xpath('.//div[@class="p-img"]/a/img/@data-lazy-img').extract_first()
            item['book_name'] = book.xpath('.//div[@class="p-name"]/a/em/text()').extract_first()
            item['book_author'] = book.xpath('.//span[@class="author_type_1"]/a/text()').extract_first()
            item['book_store'] = book.xpath('.//span[@class="p-bi-store"]/a/text()').extract_first()
            item['book_date'] = book.xpath('.//span[@class="p-bi-date"]/text()').extract_first()
            item['data_sku'] = book.xpath('./div[@class="gl-i-wrap j-sku-item"]/@data-sku').extract_first()

            yield scrapy.Request(
                'https://p.3.cn/prices/mgets?skuIds=J_{}'.format(item['data_sku']),
                callback=self.parse_price,
                meta={'item': deepcopy(item)}
            )

        next_page = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(
                'https://list.jd.com' + next_page,
                callback=self.parse_list,
                meta={'item': response.meta['item']}
            )

    def parse_price(self, response):
        item = response.meta['item']
        item['book_price'] = json.loads(response.body.decode())[0]['op']
        yield item
