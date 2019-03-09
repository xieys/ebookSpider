# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com']
    start_urls = ['https://e.jd.com/']

    def parse(self, response):
        menu_pattern = re.compile("menu:(\[{.*}\]).*?submenu:", re.S)
        result = menu_pattern.findall(response.text)
        pattern = re.compile("NAME: '(.*?)',URL: '(.*?)',id: '\d+',children:")
        cata_list = pattern.findall(result[0])
        # print(cata_list)
        for cata in cata_list[1:]:
            item = {}
            item['cata_title'] = cata[0]
            item['cata_url'] = cata[1]
            if not item['cata_url'].startswith('//list'):
                num_pattern = re.compile(".*/(\d+)-(\d+)-(\d+).html")
                result = num_pattern.findall(item['cata_url'])[0]
                item['cata_url'] = '//list.jd.com/list.html?cat={},{}&tid={}'.format(result[0], result[1], result[2])
            item['cata_url'] = 'https:' + item['cata_url']
            print(item)
            yield scrapy.Request(
                item['cata_url'],
                callback=self.parse_list,
                meta={'item': deepcopy(item)}
            )

    def parse_list(self, response):
        item = response.meta['item']
        book_list = response.xpath('//ul[@class="gl-warp clearfix"]/li')
        # print('book', book_list)
        for book in book_list:
            item['book_img'] = book.xpath('.//div[@class="p-img"]/a/@href').extract_first()
            item['book_price'] = book.xpath('.//div[@class="p-price"]/strong[1]/i/text()').extract_first()
            item['book_name'] = book.xpath('.//div[@class="p-name"]/a/em/text()').extract_first()
            item['book_author'] = book.xpath('.//span[@class="author_type_1"]/a/text()').extract_first()
            item['book_store'] = book.xpath('.//span[@class="p-bi-store"]/a/text()').extract_first()
            item['book_date'] = book.xpath('.//span[@class="p-bi-date"]/text()').extract_first()
            print(item)

        next_page = response.xpath('//a[@class="pn-next"]/@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(
                'https://list.jd.com' + next_page,
                callback=self.parse_list,
                meta={'item': response.meta['item']}
            )
