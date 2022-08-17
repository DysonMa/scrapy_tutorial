import scrapy
from scrapy.shell import inspect_response

from scrapy_selenium import SeleniumRequest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from ..items import YoutubeScraperItem

class YoutubeSpider(scrapy.Spider):
    name = 'youtube'
    allowed_domains = ['www.youtube.com']
    # start_urls = ['http://www.youtube.com/']

    root_url = 'http://www.youtube.com'
    start_url = 'https://www.youtube.com/feed/trending'

    def start_requests(self):
        yield SeleniumRequest(
            url=self.start_url,
            callback=self.parse,
            wait_time=10,   # max waiting time
            wait_until=EC.visibility_of_element_located((By.TAG_NAME, "ytd-video-renderer"))  # If you're use `wait_until`, you must also specify the `wait_time`
        )

    def parse(self, response):
        # For testing
        # inspect_response(response, self)
            
        for video in response.css('ytd-video-renderer'):
            item = YoutubeScraperItem()
            item['title'] = video.css('#title-wrapper #video-title yt-formatted-string::text').get()
            item['link'] = self.root_url + video.css('#title-wrapper #video-title::attr(href)').get()
            item['channel'] = video.css('#metadata #channel-name a::text').get()
            item['view'] = video.css('#metadata-line span:nth-child(1)::text').get()
            item['duration'] = video.css('#metadata-line span:nth-child(2)::text').get()

            yield SeleniumRequest(
                url=item['link'],
                callback=self.__parse_each_video,
                wait_time=10,  # max waiting time 
                wait_until=EC.visibility_of_element_located((By.CSS_SELECTOR, "#below")),  # If you're use `wait_until`, you must also specify the `wait_time`
                cb_kwargs={"item": item}
            )

    def __parse_each_video(self, response, item):
        keywords = response.css('meta[name="keywords"]::attr(content)').get() # "k1, k2, k3,..." -> list

        keywords_list = []
        for keyword in keywords.split(','):
            keywords_list.append(keyword.strip())

        item['keywords'] = keywords_list

        yield item