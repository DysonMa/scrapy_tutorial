import scrapy
import re
from ..items import ArticleItem, CommentItem

class PttSpider(scrapy.Spider):
    # Custom class attributes
    ROOT_URL = 'https://www.ptt.cc'
    PAGE_LIMIT = 10  # TODO: This depends on your use case 
    current_page = 1
    board = 'Soft_Job' # try Gossiping

    name = 'ptt'
    allowed_domains = ['www.ptt.cc']
    start_urls = [f'https://www.ptt.cc/bbs/{board}/index.html']

    # Built-in requests method
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies={'over18':'1'})  
            # You can add argument `cookies={key:value}` to send request with cookies. 
            # In this example, add `cookies={'over18':'1'}` for Gossiping board

    def parse(self, response):
        print(f'Scraping the page {self.current_page}...')
        # Crawl the current page
        yield from self.__parse_article_list(response)
        # Crawl the next page
        if self.current_page < self.PAGE_LIMIT:
            yield from self.__parse_next_page(response)


    # Crawl the article list and all article information and comments on the next page
    def __parse_next_page(self, response):
        # Get all buttons listed on the page, if no matching seletor is found, `getall` will return an empty list
        buttons = response.css('a.btn.wide::text').getall()

        # Get the next page button
        if buttons != [] and buttons[1] == '‹ 上頁':
            next_page_url = self.ROOT_URL + response.css('a.wide::attr(href)').getall()[1]
            self.current_page += 1
            yield scrapy.Request(url=next_page_url, callback=self.parse)   # Recursively call parse method

    # Crawl the list of articles, including the article id, title, link, push, author, published date of each article
    def __parse_article_list(self, response):
        for each in response.css('.r-ent'):
            # Check if the article is deleted, if there's no link, `get()` will return None
            link = each.css("div.title > a::attr(href)").get()
            if link is None:
                continue
            
            # Extract articl_id from url, ex: /bbs/Soft_Job/M.1648133083.A.BAA.html --> M.1648133083.A.BAA
            # Regex pattern: https://regex101.com/r/HcUgEn/1
            # `r` prefix means "raw", i.e. backslashed are taken literally, so concatenate board with regex string without using f-string
            regex_pattern = r"^\/bbs\/" + self.board + r"\/(?P<id>[a-zA-Z]{1}\.[0-9]+\.[a-zA-Z]{1}\.[a-zA-Z0-9]+)\.html$"
            _res = re.match(regex_pattern, link)
            if _res is not None:
                article_id = _res.groupdict()['id']  # `_res.groupdict()` will return `{'id': 'M.1648133083.A.BAA'}`
            # nothing matched
            else:
                continue
            
            # Crawl other article fields
            push = each.css("div.nrec > span::text").get()
            title = each.css("div.title > a::text").get()
            link = self.ROOT_URL + link
            author = each.css("div.meta > div.author::text").get()
            published_date = each.css("div.meta > div.date::text").get()

            self.logger.debug("爬取文章中...")
            articleItem = ArticleItem()
            articleItem['article_id'] = article_id
            articleItem['push'] = push
            articleItem['title'] = title
            articleItem['link'] = link
            articleItem['author'] = author
            articleItem['published_date'] = published_date

            # Crawl each article
            yield scrapy.Request(url=link, callback=self.__parse_each_article, cb_kwargs={'article_id': article_id, 'articleItem': articleItem})

    # Crawl the content of each article and push tag, push user id, push content, push ipdatetime of each comment
    def __parse_each_article(self, response, article_id, articleItem):
        # Crawl article content
        content = response.css('#main-content::text').get()
        if content is not None:
            content = content.strip()

        self.logger.debug('爬取內文中...')
        articleItem['content'] = content
        yield articleItem

        # Crawl comment
        for comment in response.css('.push'):
            push_tag = comment.css('.push-tag::text').get()
            push_user_id = comment.css('.push-userid::text').get()
            push_content = comment.css('.push-content::text').get()
            push_ipdatetime = comment.css('.push-ipdatetime::text').get()

            self.logger.debug("爬取留言中...")
            commentItem = CommentItem()
            commentItem['article_id'] = article_id
            commentItem['push_tag'] = push_tag
            commentItem['push_user_id'] = push_user_id
            commentItem['push_content'] = push_content
            commentItem['push_ipdatetime'] = push_ipdatetime
            yield commentItem