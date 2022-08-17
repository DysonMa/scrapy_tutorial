# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StockScraperItem(scrapy.Item):
    stock_name = scrapy.Field()     # 股價
    date = scrapy.Field()           # 日期
    deal_price = scrapy.Field()     # 成交價
    opening_price = scrapy.Field()  # 開盤價
    closing_price = scrapy.Field()  # 收盤價
    highest_price = scrapy.Field()  # 最高價
    lowest_price = scrapy.Field()   # 最低價

class StockDividendItem(scrapy.Item):
    rank = scrapy.Field()                             # 排名
    code = scrapy.Field()                             # 代號
    name = scrapy.Field()                             # 名稱
    dividend_distribution_year = scrapy.Field()       # 股利發放年度
    EPS = scrapy.Field()                              # 所屬EPS
    cash_dividend = scrapy.Field()                    # 現金股利
    stock_dividend = scrapy.Field()                   # 股票股利
    cash_yield = scrapy.Field()                       # 現金殖利率
    stock_yield = scrapy.Field()                      # 股票殖利率
    cash_dividend_distribution_date = scrapy.Field()  # 現金股利發放日
