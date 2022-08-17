import scrapy
from ..items import StockDividendItem

class StockDividendSpider(scrapy.Spider):
    name = 'stock-dividend'
    allowed_domains = ['goodinfo.tw']
    start_urls = ['https://goodinfo.tw/tw/StockList.asp?RPT_TIME=&MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E8%82%A1%E7%A5%A8%E8%82%A1%E5%88%A9+%28%E6%9C%80%E6%96%B0%E5%B9%B4%E5%BA%A6%29%40%40%E8%82%A1%E7%A5%A8%E8%82%A1%E5%88%A9%40%40%E6%9C%80%E6%96%B0%E5%B9%B4%E5%BA%A6']

    def parse(self, response):
        try:
            # collect table headers
            titles = []
            for each in response.css('#tblStockList > .bg_h2 > th'):        
                title = ''.join(each.css('* ::text').getall())
                titles.append(title)

            # collect data in table
            for each in response.css('#tblStockList tr'):
                # find each tr has id starts with "row"
                rows = []
                for td in each.css('tr[id^="row"] td'):
                    row = td.css('*::text').get()
                    rows.append(row)

                # build stock dividend dict
                if rows == []:
                    continue
                stock_dividend = dict(zip(titles, rows))
                
                # build item
                stockDividendItem = StockDividendItem()
                stockDividendItem['rank'] = stock_dividend.get('排名')
                stockDividendItem['code'] = stock_dividend.get('代號')
                stockDividendItem['name'] = stock_dividend.get('名稱')
                stockDividendItem['dividend_distribution_year'] = stock_dividend.get('股利發放年度')
                stockDividendItem['EPS'] = stock_dividend.get('所屬EPS')
                stockDividendItem['cash_dividend'] = stock_dividend.get('現金股利')
                stockDividendItem['stock_dividend'] = stock_dividend.get('股票股利')
                stockDividendItem['cash_yield'] = stock_dividend.get('現金殖利率')
                stockDividendItem['stock_yield'] = stock_dividend.get('股票殖利率')
                stockDividendItem['cash_dividend_distribution_date'] = stock_dividend.get('現金股利發放日')

                yield stockDividendItem
                    
        except Exception as e:
            self.logger.error(e)

        

