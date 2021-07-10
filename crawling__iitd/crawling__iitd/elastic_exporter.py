from logging import warn
from typing import overload
from scrapy.exporters import BaseItemExporter
from elasticsearch import helpers, Elasticsearch
from elasticsearch.helpers import  streaming_bulk,bulk
from multiprocessing import Queue, Process, log_to_stderr
from datetime import datetime
import warnings
import logging


# from crawling__iitd.config import ELASTIC_URI,ELASTIC_INDEX_NAME
from crawling__iitd.mongo_creator import getMongoCollection
from pymongo.mongo_client import MongoClient
from pymongo.collection import Collection

ELASTIC_URI="localhost:9200"
ELASTIC_INDEX_NAME='iitd_sites'
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
        if not self.client.exists(index=ELASTIC_INDEX_NAME, id=response_url):
            self.list.append({"_index":ELASTIC_INDEX_NAME,
                            "_type":"_doc",
                            "_id":response_url,
                            "url":response_url,
                            "title":response_title, 
                            "body":response_body,
                            })

        new_doc=self.mongo_collection.find({"url": response_url})
        #condition to be added

        # print("list length changed to ",len(self.list),"  and RESP_URL SAVED IN ELASTICSEARCH IS: ",response_url,"\n")
        if len(self.list)>=50 :
            # bulk enter data into elastic search
            bulk(self.client,self.list)

            # checking if indexing was successful or not.                
            for data in self.list:    
                if self.client.exists(index=ELASTIC_INDEX_NAME, id=data["url"]):    
                    self.mongo_collection.update_one(
                        {"url": data["url"]},
                        {
                            "$set": {"indexed":True}
                        },
                        upsert=True,
                    )
            self.list=[]


       