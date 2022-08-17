import scrapy
import time

from ..items import StockScraperItem


class StockSpider(scrapy.Spider):
    name = 'stock'
    allowed_domains = ['goodinfo.tw']
    start_urls = ['http://goodinfo.tw/']
    stockId_list = ['2330', '2454', '2317']  # stock id list

    def start_requests(self):
        for stockId in self.stockId_list:
            time.sleep(3)
            url = f'https://goodinfo.tw/tw/StockDetail.asp?STOCK_ID={stockId}'
            print(f'爬取{stockId}...')
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # initialize item
        stockItem = StockScraperItem()

        # css seletors
        stock_name = response.css("table[class='b1 p4_2 r10'] tr.bg_h0.fw_normal td:nth-child(1) a::text").get()
        date = response.css("table[class='b1 p4_2 r10'] tr.bg_h0.fw_normal td:nth-last-child(1) nobr::text").get()
        table_titles = response.css("table[class='b1 p4_2 r10'] tr.bg_h1.fw_normal nobr::text").getall()
        table_values = response.css("table[class='b1 p4_2 r10'] tr.bg_h1.fw_normal + tr td *::text").getall()

        # collect all data from titles and values in the table, and build a dict
        info = {}
        # ensure the number of title and value in the table match
        if len(table_titles) == len(table_values):
            for i in range(len(table_titles)):
                title = table_titles[i]
                value = table_values[i]
                info[title] = value
        else:
            print('The number of title and value in the table does not match')

        # store data into item
        stockItem['stock_name'] = stock_name
        stockItem['date'] = date
        stockItem['deal_price'] = info.get('成交價')
        stockItem['opening_price'] = info.get('開盤')
        stockItem['closing_price'] = info.get('昨收')
        stockItem['highest_price'] = info.get('最高')
        stockItem['lowest_price'] = info.get('最低')

        yield stockItem

        

        
