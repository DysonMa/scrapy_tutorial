import scrapy

class LoginSpider(scrapy.Spider):
    name = 'login_demo'
    start_urls = ['https://pythonscraping.com/pages/files/form.html']

    def parse(self, response):
        return scrapy.FormRequest.from_response(
            response,
            # `name` attribute in the form input tag
            formdata={'firstname': 'Scrapy demo', 'lastname': 'Login'},  
            callback=self.after_login
        )

    def after_login(self, response):
        print(response.text)