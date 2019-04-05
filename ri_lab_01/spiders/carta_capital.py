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
    
    # Urls already visited, which avoids a repeat visits like the same urls
    visited_urls = []

    def __init__(self, *a, **kw):
        super(CartaCapitalSpider, self).__init__(*a, **kw)
        with open('seeds/carta_capital.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        # Gets page's article content.
        if(self.__is_response_article(response) and self.__is_valid_article(response)):
            yield self.__get_articles_data(response)

        # Gets new pages.
        for next_page in response.css('a::attr(href)').getall():
            if self.__is_valid_link(next_page):
                # next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse)
            
            self.visited_urls.append(next_page)

        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)

    def __is_response_article(self, response):
        """
            Returns a boolean indicating whether the page contains an article.
        """
        return response.css('article').get() is not None

    def __is_valid_link(self, link):
        """
            Returns a boolean indicating whether the link is valid for the crawler. That is, it is not
            empty, has not yet been visited and is the link of one of the sections for charter capital:
            Politics, Economy, Justice, Society, World.
        """
        return (link is not None) and (self.visited_urls.count(link) == 0) and self.__is_link_from_section_carta_capital(link)

    def __is_link_from_section_carta_capital(self, link):
        """
            Returns a boolean indicating whether the link of one of the sections for charter capital:
            Politics, Economy, Justice, Society, World.
        """
        is_link_from_section_carta_capital = False
        for section_link in self.start_urls:
            is_link_from_section_carta_capital = is_link_from_section_carta_capital or (section_link.lower() in link.lower())

        return is_link_from_section_carta_capital

    def __get_page_date(self, response):
        """
            Gets the date of publication of the page.
        """
        date_index = 0
        zone_utc_symbol = "+"
        str_response_datetime = response.xpath("//meta[@property='article:published_time']/@content").get().replace("T", " ").split(zone_utc_symbol)[date_index]
        response_datetime = datetime.strptime(str_response_datetime, '%Y-%m-%d %H:%M:%S')

        return response_datetime

    def __is_valid_article(self, page_article):
        """
            Returns a boolean that indicates whether the article is valid, that is, it is an article
            published after the date 01/01/2018.
        """
        article_datetime = self.__get_page_date(page_article)
        articles_year = article_datetime.year
        
        return articles_year >= 2018

    def __get_articles_data(self, response):
        """
            Gets article's data.
        """
        articles_data = {
                'title': self.__get_article_title(response),
                "sub_title": self.__get_article_sub_title(response),
                'author': self.__get_article_author(response),
                'date': self.__get_article_date(response),
                'section': self.__get_article_section(response),
                'text': self.__get_article_text(response),
                'url': self.__get_article_url(response),
            }
        return articles_data

    def __get_article_title(self, response):
        """
            Gets article's title.
        """
        return response.css('h1.eltdf-title-text::text').get()

    def __get_article_sub_title(self, response):
        """
            Gets article's subtitle.
        """
        return response.css('div.wpb_wrapper h3::text').get()

    def __get_article_author(self, response):
        """
            Gets article's author.
        """
        return response.css('div.eltdf-title-post-author-info a::text').get()

    def __get_article_date(self, response):
        """
            Gets article's publication date.
        """
        article_datetime = self.__get_page_date(response)
        formatted_article_datetime = article_datetime.strftime('%d/%m/%Y %H:%M:%S')

        return formatted_article_datetime

    def __get_article_section(self, response):
        """
            Gets article's section.
        """
        return response.css('div.eltdf-post-info-category a::text').get()

    def __get_article_text(self, response):
        """
            Gets article's text.
        """
        return "".join(response.css('article p::text').getall())

    def __get_article_url(self, response):
        """
            Gets article's page url.
        """
        return response.request.url