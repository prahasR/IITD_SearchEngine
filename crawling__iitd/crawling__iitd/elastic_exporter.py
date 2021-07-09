from logging import warn
from typing import overload
from scrapy.exporters import BaseItemExporter
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import  streaming_bulk
from multiprocessing import Queue, Process, log_to_stderr
from datetime import datetime
import warnings
import logging

#from crawler.config import ELASTIC_URI, ELASTIC_INDEX_NAME, mongo_collection
from crawling__iitd.mongo_creator import getMongoCollection
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection


ELASTIC_URI ="localhost:9200"
ELASTIC_INDEX_NAME = "iit"
class ElasticExporter(BaseItemExporter):
    
    def __init__(self, _, **kwargs) -> None:
        super().__init__(dont_fail=True, **kwargs)


    def start_exporting(self):
        self.client = Elasticsearch([ELASTIC_URI])
        self.mongo_collection: Collection = getMongoCollection()
        if not self.client.indices.exists(ELASTIC_INDEX_NAME):
            self.client.indices.create(ELASTIC_INDEX_NAME)
        
        #for bulk export to ES
        self.list=[]
    
    def finish_exporting(self):
        print("exporting process ended")
        
    
    def export_item(self, item):
        response_url = item["url"]
        response_title=item["title"]
        response_body=item["body"]
        
        #for bulk export
        self.list.append({"index":'iitd_sites',"type":'_doc',"id":response_url,"body":'hello'})
        
        
        new_doc=self.mongo_collection.find({"url": response_url})
       
        #condition to be added
        self.client.index(index='iit',doc_type='_doc',body={'url':response_url,'title':response_title, "body":response_body})
        print("list lenth changed to ",len(self.list),"  and RESP_URL SAVED IN ELASTICSEARCH IS: ",response_url,"\n")
      
        
        self.mongo_collection.update_one(
            {"url": response_url},
            {
                "$set": {"indexed":True}
            },
            upsert=True,
        )

       