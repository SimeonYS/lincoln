import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import LincolnItem
from itemloaders.processors import TakeFirst
from scrapy.http import FormRequest
pattern = r'(\xa0)?'

class LincolnSpider(scrapy.Spider):
	name = 'lincoln'
	start_urls = ['https://www.mylsb.com/blog/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="li-img"]/a[@class="inner"]/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//li[@class="page-next"]/a').get()
		if next_page:
			yield FormRequest.from_response(response, formdata={"__EVENTTARGET":'ctl00$cph_main_content$uclBlogList$pgPaging$btnNext'}, callback=self.parse)

	def parse_post(self, response):
		date = response.xpath('//p[@class="author"]/strong/following-sibling::text()').get().split('in')[0].strip()
		title = response.xpath('//h1/text()').get().strip()
		content = response.xpath('//div[@class="content"]//text()[not (ancestor::h1 or ancestor::p[@class="author"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=LincolnItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
