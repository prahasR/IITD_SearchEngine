import datetime
from scrapy import signals
from scrapy.http import Request, Response
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from pymongo.collection import Collection, ReturnDocument
from crawling__iitd.seeder import Seeder
from crawling__iitd.mongo_creator import getMongoCollection

class IITDSpider(CrawlSpider):
    name = "iitd"

    allowed_domains = [
        'iitd.ac.in',
        'iitd.ernet.in'
    ]

    rules = [
        Rule(LinkExtractor(), follow=True, callback="parse_item",process_request="process_request")
    ]

    start_urls = [
        'https://home.iitd.ac.in/',
    ]

    #start_request generates request for all links
    def start_requests(self):
        self.mongo_collection: Collection = getMongoCollection()
        for url in self.start_urls:
            doc = self.mongo_collection.find_one_and_update({"url": url}, {"$setOnInsert": {"crawl_details": [], "crawled_on": datetime.datetime.now()}}, upsert=True, return_document=ReturnDocument.AFTER)
        
        #seeder returns the crawl_info collection...so that Request could be yielded for priviosly crawled links(doc).
        #initially crawl_info does not contain any data ...
        for doc in Seeder(self.mongo_collection).seed():
            url = doc['url']
            self.logger.info(f"Got {url} from seeder")
            yield Request(url, meta={"mongo_doc": doc})


    def process_request(self, request: Request, response: Response):
        self.logger.debug('Processing request')
        
        #newly visited links would not have mongo_doc in request.meta....so saving them in crawl_info ...once saved ...Request would be created for them and hence mongo_doc will then be present in request.meta
        if "mongo_doc" not in request.meta:
            request.meta["mongo_doc"] = self.mongo_collection.find_one_and_update({"url": request.url},{"$setOnInsert": {"crawl_details": [],"crawled_on": datetime.datetime.now()}},upsert=True,return_document=ReturnDocument.AFTER)

        #Drop this request if it has already been crawled
        if len(request.meta["mongo_doc"]["crawl_details"]) != 0:
            return None
        
        return request
    
    def parse_item(self, response):
        self.logger.info(f'Visited URL {response.url}')
        item = {
            "request": response.request,
            "elastic_doc": {
                'url': response.url,
                'status': response.status,
                'title': response.xpath("//title").get(),
                'body': response.xpath("//body").get(),
                'link_text': response.meta['link_text'],
            },
        }

        return item