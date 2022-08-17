import scrapy
from scrapy_selenium import SeleniumRequest
from ..items import KkdayScraperItem

from scrapy.shell import inspect_response

class KkdaySpider(scrapy.Spider):
    name = 'kkday'
    allowed_domains = ['www.kkday.com']
    # start_urls = ['http://www.kkday.com/']

    url = "https://www.kkday.com/zh-tw/city/taichung/"
    categories = ['attractions-and-tickets', 'outdoor-activities', 'accommodation']

    def start_requests(self):
        yield SeleniumRequest(
            url=self.url+self.categories[0],
            wait_time=5,
            callback=self.parse
        )

    def parse(self, response):
        # test for scrapy shell
        # inspect_response(response, self)	

        # for category in self.categories:
        print(f"Scraping {self.url+self.categories[0]}...")

        for card in response.css(".product-card"):
            item = KkdayScraperItem()

            title = card.css(".product-card__title::text").get()
            link = card.css("a::attr(href)").get()
            tag = [tag.strip() for tag in card.css(".product-card__tag  span::text").getall()]  # List
            rate = card.css(".product-card__info-score::text").get()
            vote_number = card.css(".product-card__info-number::text").get()
            order_number = card.css(".product-card__info-order-number::text").get()
            price = card.css(".currency::text").get() + card.css(".price::text").get()


            item["title"] = title.strip() if title is not None else title
            item["link"] = link
            item["tag"] = tag
            item["rate"] = rate.strip() if rate is not None else rate
            item["vote_number"] = vote_number.strip() if vote_number is not None else vote_number
            item["order_number"] = order_number.strip() if order_number is not None else order_number
            item["price"] = price.strip() if price is not None else price

            yield SeleniumRequest(
                url=item["link"],
                wait_time=5,
                callback=self.__parse_each_card, 
                cb_kwargs={"item": item}
            )


    def __parse_each_card(self, response, item):
        print(f"Scraping {response.url}...")

        product_info = "\n".join([info.strip() for info in response.css("div#prodInfo *::text").getall()])
        item["product_info"] = product_info
        
        item["options"] = []
        for option in response.css(".option-item"):
            option_content = "".join(option.css(".option-content *::text").getall())
            product_price = option.css(".product-pricing > h4::text").get()
            original_price = option.css(".product-pricing > .origin-price::text").get()
            earliest_available_date = option.css(".tip.text-blue::text").get()

            item["options"].append({
                "option_content": option_content.strip() if option_content is not None else option_content,
                "product_price": product_price.strip() if product_price is not None else product_price,
                "original_price": original_price.strip() if original_price is not None else original_price,
                "earliest_available_date": earliest_available_date.strip() if earliest_available_date is not None else earliest_available_date,
            })

        yield item