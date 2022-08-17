import scrapy
from scrapy_selenium import SeleniumRequest

# selenium
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException

class YoutubeSeleniumTestSpider(scrapy.Spider):
    name = 'youtube_selenium_test'
    allowed_domains = ['www.youtube.com']

    root_url = 'http://www.youtube.com'
    start_url = 'https://www.youtube.com/watch?v=eZh1mC1vPgw'   # test single youtube page

    def start_requests(self):
        yield SeleniumRequest(
            url=self.start_url,
            callback=self.parse,
            wait_time=10,  # max waiting time 
            wait_until=EC.visibility_of_element_located((By.CSS_SELECTOR, "#below")),  # If you're use `wait_until`, you must also specify the `wait_time`
            script="window.scroll(0, 300)"   # execute javascript to scroll the page, because the button we want to click is invisible now
        )

    def parse(self, response):
        # get `driver` instance from `meta` field provided by `scrapy_selenium`
        driver = response.request.meta['driver']
        try:
            expandBtn = WebDriverWait(driver, timeout=50).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#expand")))   # or #more
            expandBtn.click()

            # gather all description and remove \n, \t
            result = ""
            description = response.css("#description *::text").getall()
            for text in description:
                if text.strip() != "":
                    result = result + text.strip() + "\n"
            print(result)
        except TimeoutException as e:
            print("Reach timeout")
        except NoSuchElementException as e:
            print(e.msg)
        except ElementNotInteractableException as e:
            print(e.msg)
            print(expandBtn.get_attribute("id"))
