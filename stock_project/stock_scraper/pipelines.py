# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
from . import settings
from datetime import datetime


class StockScraperPipeline:
    def process_item(self, item, spider):
        if spider.name == 'stock':
            # parse date, ex: "資料日期: 06/20" -> "2022-06-20"
            if '資料日期: ' in item['date']:
                date = item['date'].split('資料日期: ')[-1]  # 06/20
                year = str(datetime.now().year)
                item['date'] = datetime.strptime(year+"/"+date, "%Y/%m/%d").strftime("%Y-%m-%d")  # '2022-06-20'
                
            item['deal_price'] = float(item['deal_price']) if item['deal_price'] is not None else None
            item['opening_price'] = float(item['opening_price']) if item['opening_price'] is not None else None
            item['closing_price'] = float(item['closing_price']) if item['closing_price'] is not None else None
            item['highest_price'] = float(item['highest_price']) if item['highest_price'] is not None else None
            item['lowest_price'] = float(item['lowest_price']) if item['lowest_price'] is not None else None
                
        elif spider.name == 'stock-dividend':
            item['rank'] = int(item['rank']) if item['rank'] is not None else None
            item['dividend_distribution_year'] = int(item['dividend_distribution_year']) if item['dividend_distribution_year'] is not None else None
            item['EPS'] = float(item['EPS']) if item['EPS'] is not None else None
            item['cash_dividend'] = float(item['cash_dividend']) if item['cash_dividend'] is not None else None
            item['stock_dividend'] = float(item['stock_dividend']) if item['stock_dividend'] is not None else None
            item['cash_yield'] = float(item['cash_yield']) if item['cash_yield'] is not None else None
            item['stock_yield'] = float(item['stock_yield']) if item['stock_yield'] is not None else None
            # parse date format, ex: "22'07/28" -> "2022-07-28"
            if item['cash_dividend_distribution_date'] is not None:
                item['cash_dividend_distribution_date'] = datetime.strptime(item['cash_dividend_distribution_date'], "%y'%m/%d").strftime("%Y-%m-%d")   # %y: year without century as a zero padded decimal number
        return item


class DatabasePipeline:
    def open_spider(self, spider):
        # Create connection with postgresql
        self.connection = psycopg2.connect(
            host=settings.POSTGRESQL_HOST,
            database=settings.POSTGRESQL_DATABASE,
            user=settings.POSTGRESQL_USERNAME,
            password=settings.POSTGRESQL_PASSWORD
        )
        print('Connecting to database...')

        # Create cursor
        self.cursor = self.connection.cursor()

        # Create tables
        self.__create_tables_if_not_exist()

    def __create_tables_if_not_exist(self):
        try:
            stock_price_sql = """
                CREATE TABLE IF NOT EXISTS stock_price(
                    stock_name TEXT,
                    date DATE,
                    deal_price FLOAT,
                    opening_price FLOAT,
                    closing_price FLOAT,
                    highest_price FLOAT,
                    lowest_price FLOAT
                );
            """
            stock_dividend_sql = """
                CREATE TABLE IF NOT EXISTS stock_dividend(
                    rank INT,
                    code TEXT,
                    name TEXT,
                    dividend_distribution_year INT,
                    EPS FLOAT,
                    cash_dividend FLOAT,
                    stock_dividend FLOAT,
                    cash_yield FLOAT,
                    stock_yield FLOAT,
                    cash_dividend_distribution_date DATE
                );
            """
            self.cursor.execute(stock_price_sql)
            self.cursor.execute(stock_dividend_sql)
            self.connection.commit()  # commit this transaction
            print('Create table successfully')
        except Exception as e:
            self.connection.rollback()  # explicitly rollback this transaction
            print('Failed to create table')


    # Insert data into database
    def process_item(self, item, spider):
        try:
            sql, data = None, None
            if spider.name == 'stock':
                sql, data = self.__process_stock_price_item(item)
            elif spider.name == 'stock-dividend':
                sql, data = self.__process_stock_dividend_item(item)
            
            if sql is not None and data is not None:
                self.cursor.execute(sql, data)
                self.connection.commit()  # commit this transaction
        except Exception as e:
            self.connection.rollback()  # explicitly rollback this transaction

        return item   # Don't forget to return the item

    def __process_stock_price_item(self, item):
        sql = """
            INSERT INTO stock_price(
                stock_name,
                date,
                deal_price,
                opening_price,
                closing_price,
                highest_price,
                lowest_price
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        data = (item["stock_name"], item["date"], item["deal_price"], item["opening_price"], item["closing_price"], item["highest_price"], item["lowest_price"]) # tuple
        return sql, data

    
    def __process_stock_dividend_item(self, item):
        sql = """
            INSERT INTO stock_dividend(
                rank,
                code,
                name,
                dividend_distribution_year,
                EPS,
                cash_dividend,
                stock_dividend,
                cash_yield,
                stock_yield,
                cash_dividend_distribution_date
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
        data = (
            item["rank"], 
            item["code"], 
            item["name"], 
            item["dividend_distribution_year"], 
            item["EPS"],
            item["cash_dividend"],
            item["stock_dividend"],
            item["cash_yield"],
            item["stock_yield"],
            item["cash_dividend_distribution_date"],
        )  # tuple
        return sql, data

    # Close the connection with postgresql
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
        print('Closing database...')

