# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

import scrapy
import feedparser
import logging

logger = logging.getLogger('root')

class atom2Spider(scrapy.spiders.Spider):
	# identify for this spider
	name = "atom2"
	allowed_dmains = ["zhihu.com"]
	start_urls = ["http://zhihu.com/rss"]
	
	def parse(self, response):
		logger.debug("Start parse...")
		fparser = feedparser.parse(response.body)
		
		logger.debug("%s: %s"%(fparser.feed.title, fparser.feed.description)) 
		logger.debug("entries count :%d" % (len(fparser.entries)))
		
		count = 1
		for e in fparser.entries:
			logger.debug("entry %d:%s",(count),e.title)
			count = count + 1
		