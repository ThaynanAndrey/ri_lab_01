# coding: utf-8
import scrapy
import json

from datetime import datetime

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
        if(self.__is_response_article(response) and self.__is_valid_article(response)):
            yield {
                'title': self.__get_article_title(response),
                'author': self.__get_article_author(response),
                'date': self.__get_article_date(response),
                'section': self.__get_article_section(response),
                'url': self.__get_article_url(response),
            }

        # Obtém novas páginas
        for next_page in response.css('a::attr(href)').getall():
            if self.__is_valid_link(next_page):
                self.visited_urls.append(next_page)
                # next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def __is_response_article(self, response):
        return response.css('article').get() is not None

    def __is_valid_article(self, page_article):
        string_date = page_article.css('div.eltdf-post-info-date a::text').get()
        year = int(string_date.split(" de ")[2])
        return year == 2019

    def __is_valid_link(self, link):
        return (link is not None) and (self.visited_urls.count(link) == 0) and ('https://www.cartacapital.com.br/economia' in link or 'https://www.cartacapital.com.br/sociedade' in link or 'https://www.cartacapital.com.br/politica' in link or 'https://www.cartacapital.com.br/justica' in link or 'https://www.cartacapital.com.br/mundo' in link)

    def __get_article_title(self, response):
        return response.css('h1.eltdf-title-text::text').get()

    def __get_article_author(self, response):
        return response.css('div.eltdf-title-post-author-info a::text').get()

    def __get_article_date(self, response):
        '''monthes = {"janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04", "maio": "05"}
        string_date = response.css('div.eltdf-post-info-date a::text').get()

        list_date_details = string_date.split(" de ")

        day = list_date_details[0]
        month = monthes[list_date_details[1]]
        year = list_date_details[2]
        formatted_date = "/".join([day, month, year])

        article_date = datetime.strptime(formatted_date, '%d/%m/%Y')
        print article_date
        print type(article_date)'''
        return response.css('div.eltdf-post-info-date a::text').get()

    def __get_article_section(self, response):
        return response.css('div.eltdf-post-info-category a::text').get()

    def __get_article_url(self, response):
        return response.request.url