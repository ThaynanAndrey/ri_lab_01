# coding: utf-8
import scrapy
import json

from ri_lab_01.items import RiLab01Item
from ri_lab_01.items import RiLab01CommentItem


class CartaCapitalSpider(scrapy.Spider):
    name = 'carta_capital'
    allowed_domains = ['cartacapital.com.br']
    start_urls = []
    
    # urls já visitadas, o que evita uma recursão.
    visited_urls = []

    def __init__(self, *a, **kw):
        super(CartaCapitalSpider, self).__init__(*a, **kw)
        with open('seeds/carta_capital.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        # Obtém conteúdos dos artigos de cada página
        if(response.css('article').get() is not None):
            yield {
                'title': response.css('h1.eltdf-title-text::text').get(),
                'author': response.css('div.eltdf-post-info-author a::text').get(),
            }

        # Obtém novas páginas
        for next_page in response.css('a::attr(href)').getAll():
            if self.__isValidLink(next_page):
                self.visited_urls.append(next_page)
                # next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def __isValidLink(self, link):
        return (link is not None) and (self.visited_urls.count(link) == 0) and (link in 'https://www.cartacapital.com.br/economia')