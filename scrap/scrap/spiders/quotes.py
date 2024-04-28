import json
from typing import Iterable 
import scrapy 
from urllib.parse import urljoin
import re

class AmazonSearchProductSpider(scrapy.Spider):
    name="amazon_search_product"

    def start_requests(self):
        keyword_list=[
    "apple watch",
    "crocs",
    "airpods",
    "kindle",
    "air fryer",
    "ipad",
    "ps5",
    "ring doorbell",
    "fire stick",
    "portable air conditioners",
    "stanley 40 oz tumbler with handle",
    "iphone 14 pro max case",
    "laptop",
    "apple watch band",
    "nintendo switch",
    "paper towels",
    "ninja creami",
    "iphone charger",
    "desk",
    "tv",
    "iphone 13 case",
    "toilet paper",
    "shower curtain",
    "crocs womens",
    "alexa",
    "mini fridge",
    "protein powder",
    "sol de janeiro",
    "liquid iv",
    "fan",
    "kindle paperwhite 2023",
    "lego",
    "ice maker",
    "school supplies",
    "apple watch series 8",
    "neck fan",
    "office chair",
    "electric bike",
    "gaming chair",
    "led lights",
    "crocs mens",
    "airtag",
    "air purifiers",
    "blink outdoor camera",
    "luggage",
    "portable charger",
    "shoe rack",
    "coffee maker",
    "yeti",
    "highlighters",
    "iphone 14 pro case",
    "car accessories",
    "air conditioner",
    "ring camera",
    "makeup",
    "shower head",
    "gift cards amazon ecard",
    "pencil case",
    "magnesium glycinate",
    "travel essentials",
    "airpods pro 2nd generation",
    "hismile",
    "jansport backpack",
    "party plates",
    "pens",
    "dresser",
    "iphone 13 pro max case",
    "queen bed frame",
    "backpack for school",
    "water shoes",
    "pencil pouch",
    "bluetooth speakers",
    "stanley cup",
    "birkenstock sandals women",
    "aa batteries",
    "dresses for women 2023",
    "laptop computer",
    "iphone",
    "packing cubes",
    "vacuum",
    "monitor",
    "hey dudes for men",
    "playstation 5",
    "gaming pc",
    "backpack",
    "xbox series x",
    "portable fan",
    "jbl bluetooth speaker",
    "cat tree",
    "makeup bag",
    "stanley",
    "pool",
    "beats headphones",
    "fitbit",
    "projector",
    "vanity",
    "ear buds",
    "amazon gift card",
    "iphone 11 case",
    "shower caddy"
]
        for keyword in keyword_list:
            amazon_search_url=f'https://www.amazon.com/s?k={keyword}&page=1'
            yield scrapy.Request(url=amazon_search_url,callback=self.discovery_product_urls,meta={'keyword':keyword,'page':1})

    def discovery_product_urls(self,response):
        page=response.meta['page']
        keyword=response.meta['keyword']        

        search_products = response.css("div.s-result-item[data-component-type=s-search-result]")
        for product in search_products:
            relative_url = product.css("h2>a::attr(href)").get()
            product_url = urljoin('https://www.amazon.com/', relative_url).split("?")[0]
            yield scrapy.Request(url=product_url, callback=self.parse_product_data, meta={'keyword': keyword, 'page': page})

        if page == 1:
            available_pages = response.xpath(
                '//*[contains(@class, "s-pagination-item")][not(has-class("s-pagination-separator"))]/text()'
            ).getall()

            last_page = available_pages[-1]
            for page_num in range(2, int(last_page)):
                amazon_search_url = f'https://www.amazon.com/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.parse_search_results, meta={'keyword': keyword, 'page': page_num})
    


    def parse_product_data(self, response):
        image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        feature_bullets = [bullet.strip() for bullet in response.css("#feature-bullets li ::text").getall()]
        price = response.css('.a-price span[aria-hidden="true"] ::text').get("")
        if not price:
            price = response.css('.a-price .a-offscreen ::text').get("")
        yield {
            "name": response.css("#productTitle::text").get("").strip(),
            "price": price,
            "stars": response.css("i[data-hook=average-star-rating] ::text").get("").strip(),
            "rating_count": response.css("div[data-hook=total-review-count] ::text").get("").strip(),
            "feature_bullets": feature_bullets,
            "images": image_data,
            "variant_data": variant_data,
        }