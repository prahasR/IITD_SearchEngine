# IITD_SearchEngine
This repository contains a search engine for domain "iitd.ac.in"


As of 28th November 2021

Branch storing_files has the latest working code

python modules required
-scrapy
-elasticsearch
-textract
-datetime

to start frontend - commands to be executed in search_frontend directory
-npm install react-scripts@3.0.1 -g
-npm ci
-npm run start

to start the crawler
-run the main.py file in crawling_iitd


elastic_search index = iitd_sites

Crawler limit - 110 pages
(limit is set to 110 pages but it is printing 100 pages on terminal, has to be corrected)

Functionality enabled to limit the no. of requests made to iitd.ac.in per second
