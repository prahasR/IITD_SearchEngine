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
            doc = self.mongo_collection.find_one_and_update({"url": url}, {"$setOnInsert": {
                "crawl_details": {},
                "scraped": False}
                }, upsert=True, return_document=ReturnDocument.AFTER)
        
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
            request.meta["mongo_doc"] = self.mongo_collection.find_one_and_update({"url": request.url},{"$setOnInsert": {
                "crawl_details": {},
                "scraped": False}
                },upsert=True,return_document=ReturnDocument.AFTER)

        #Drop this request if it has already been crawled
        # if len(request.meta["mongo_doc"]["crawl_details"]) != 0:
        if request.meta["mongo_doc"]["scraped"]!=False:
            return None
        
        return request
    
    # def parse_item(self, response):
    #     self.logger.info('Hello World Checking this function')
    #     item = {
    #         "request": response.request,
    #         "elastic_doc": {
    #             'url': response.url,
    #             'status': response.status,
    #             'title': response.xpath("//title").get(),
    #             'body': response.xpath("//body").get(),
    #             'link_text': response.meta['link_text'],
    #         },
    #     }

    #     return item

    def parse_item(self,response) :
        if response.status==200:
            self.logger.info(f'Scraping Page with url {response.url}')
            body=self.extract_body(response)

            links=response.css('a')
            links_url=links.css('::attr(href)').extract()
            links_text=links.css('::text').extract()
            remove='\n \t \f \r \b'
            for text in links_text:
                text=text.lstrip(remove)
                text=text.rstrip(remove)

            item = {
                "url":response.url,    
                "status":response.status,
                "title":response.css('title::text').get(),
                "meta_data":response.css('meta').extract(),
                "body":body,
                "crawled_on":datetime.datetime.now(),
                "links_url":links_url,
                "links_text":links_text,
            }
            # doc = self.mongo_collection.find_one_and_update({"url": response.url},{"$setOnInsert": {"crawl_details": item,"crawled_on": datetime.datetime.now()}},upsert=True,return_document=ReturnDocument.AFTER)
            myquery = { 'url': response.url }
            newvalues = { "$set": { 'crawl_details' : item, 'scraped':True } }
            self.mongo_collection.update_one(myquery, newvalues)
            
            yield item 
        else:
            yield None

    def extract_body(self,response):
        # all text data in heading, para, a, b tags is extracted
        body=[]
        # cheking for paragraphs
        paras=response.css('p::text').extract()
        for str in paras :
            if(self.check_string(str)==-1):
                paras.remove(str)
        body+=paras

        # checking for headings <h2>
        headings=response.css('h2::text').extract()
        for str in headings:
            if(self.check_string(str)==-1):
                headings.remove(str)
        body+=headings
        
        # checking for bolds tags
        bolds=response.css('b::text').extract()
        for str in bolds:
            if(self.check_string(str)==-1):
                bolds.remove(str)
        body+=bolds

        # checking for all headings
        headings1=response.css('h1::text').extract()
        for str in headings1:
            if(self.check_string(str)==-1):
                headings1.remove(str)
        body+=headings1

        headings3=response.css('h3::text').extract()
        for str in headings3:
            if(self.check_string(str)==-1):
                headings3.remove(str)
        body+=headings3

        headings4=response.css('h4::text').extract()
        for str in headings4:
            if(self.check_string(str)==-1):
                headings4.remove(str)
        body+=headings4

        headings5=response.css('h5::text').extract()
        for str in headings5:
            if(self.check_string(str)==-1):
                headings5.remove(str)
        body+=headings5

        # checking for link texts
        links=response.css('a::text').extract()
        for str in links:
            if(self.check_string(str)==-1):
                links.remove(str)
        body+=links


        return body

    def check_string(self,str):
        remove="\n \t \f \r \b  "
        str=str.lstrip(remove)
        str=str.rstrip(remove)
        if(len(str)<=2):
            return -1
        else:
            return 1
