# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import ArticleItem, CommentItem

from scrapy.exporters import JsonItemExporter
import psycopg2
from . import settings
import requests

class PttScraperPipeline:
    def process_item(self, item, spider):
        """
        Convert `push` from string to integer, in three cases:

        1. Empty string -> 0
        2. "爆" -> 100
        3. Begin with "X" means the number of boo is greater than the number of push
            ex: "X1" represents that the number of boo is 10 more than the number of push -> -10
            ex: "X2" represents that the number of boo is 20 more than the number of push -> -20
            ex: "XX" represents that the number of boo is 100 more than the number of push -> -100
        """
        if isinstance(item, ArticleItem):
            # Empty push
            if item['push'] is None:
                item['push'] = 0
            # "爆"
            elif item['push'] == '爆':
                item['push'] = 100
            # Begin with "X"
            elif 'X' in item['push']:
                boo_cnt = item['push'].split('X')[-1]
                # "X"
                if boo_cnt == '':
                    item['push'] = -10
                # "XX"
                elif boo_cnt == 'X':
                    item['push'] = -100
                # "X2", "X3", "X7"...
                else:
                    item['push'] = -int(boo_cnt)*10
            # Other normal integer-like string such as "12", "23", "36",...
            else:
                item['push'] = int(item['push'])

        return item


# Custom JSON Exporter
class JsonWriterPipeline:
    def open_spider(self, spider):
        self.f = open("ptt-by-JsonItemExporter.json", "wb")    # it must to be binary mode
        self.exporter = JsonItemExporter(self.f, encoding="utf8")  # initialize exporter
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()


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

        # line-notify token
        self.token = 'YOUR_TOKEN'


    def __create_tables_if_not_exist(self):
        try:
            article_sql = """
                CREATE TABLE IF NOT EXISTS article(
                    id SERIAL NOT NULL,
                    article_id TEXT PRIMARY KEY,
                    push INT,
                    title TEXT,
                    "link" TEXT,
                    author TEXT,
                    published_date TEXT,
                    "content" TEXT
                );
                """
            comment_sql = """
                CREATE TABLE IF NOT EXISTS "comment"(
                    id SERIAL NOT NULL,
                    article_id TEXT,
                    push_tag TEXT,
                    push_user_id TEXT,
                    push_content TEXT,
                    push_ipdatetime TEXT,
                    FOREIGN KEY(article_id) REFERENCES article(article_id) ON DELETE CASCADE
                );
            """
            self.cursor.execute(article_sql)
            self.cursor.execute(comment_sql)
            self.connection.commit()  # commit this transaction
            print('Create table successfully')
        except Exception as e:
            self.connection.rollback()  # explicitly rollback this transaction
            print('Failed to create table')
            print(e)


    # Insert data into database
    def process_item(self, item, spider):
        try:
            sql, data = None, None
            if isinstance(item, ArticleItem):
                sql, data = self.__process_article_item(item)
                delete_sql = 'DELETE FROM "comment" WHERE article_id=%s'
                delete_data = (item["article_id"], )   # tuple cantains article_id
                self.cursor.execute(delete_sql, delete_data)
            elif isinstance(item, CommentItem):
                sql, data = self.__process_comment_item(item)
            
            if sql is not None and data is not None:
                self.cursor.execute(sql, data)
                self.connection.commit()  # commit this transaction
        except Exception as e:
            self.connection.rollback()  # explicitly rollback this transaction
            print(e)

        return item   # Don't forget to return the item

    def __process_article_item(self, item):
        sql = """
            INSERT INTO article(
                article_id,
                push, 
                title, 
                "link", 
                author, 
                published_date,
                "content"
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT ON CONSTRAINT article_pkey
            DO UPDATE SET push=EXCLUDED.push, title=EXCLUDED.title, content=EXCLUDED.content;
            """
        data = (item["article_id"], item["push"], item["title"], item["link"], item["author"], item["published_date"], item["content"]) # tuple
        return sql, data

    
    def __process_comment_item(self, item):
        sql = """
            INSERT INTO "comment"(
                article_id,
                push_tag, 
                push_user_id, 
                push_content, 
                push_ipdatetime
            ) 
            VALUES (%s, %s, %s, %s, %s);
            """
        data = (item["article_id"], item["push_tag"], item["push_user_id"], item["push_content"], item["push_ipdatetime"])  # tuple
        return sql, data


    def lineNotifyMessage(self, msg):
        headers = {
            "Authorization": f"Bearer {self.token}", 
            "Content-Type" : "application/x-www-form-urlencoded"
        }

        payload = {'message': msg}
        res = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
        
        if res.status_code != 200:
            print('LINE Notify failed')

    # Close the connection with postgresql
    def close_spider(self, spider):
        # Find the top 10 article title, tweets, links
        self.cursor.execute('SELECT title, push, "link" FROM article ORDER BY push DESC LIMIT 10')
        top10 = self.cursor.fetchall()  # List of tuple

        # build messages
        msg = ''
        for each in top10:
            title, push, link = each
            msg += f'{push} {title} {link}\n'

        # line notify
        self.lineNotifyMessage(msg)

        self.cursor.close()
        self.connection.close()
        print('Closing database...')