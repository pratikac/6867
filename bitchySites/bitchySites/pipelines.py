# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from bitchySites.spiders.mlig_spider import MLIGSpider
from bitchySites.spiders.fml_spider import FMLSpider

class JsonWriter(object):

    def __init__(self):
        print "Spiders started!"

    def open_spider(self, spider):
        if isinstance(spider, MLIGSpider):
            print "Currently crawling: MLIG"
            self.file_mlig = open('MLIG.jl', 'wb')
        elif isinstance(spider, FMLSpider):
            print "Currently crawling: FML"
            self.file_fml = open('FML.jl', 'wb')
        else:
            print "Unidentified spider!"

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"

        if isinstance(spider, MLIGSpider):
            self.file_mlig.write(line)
        elif isinstance(spider, FMLSpider):
            self.file_fml.write(line)

        return item
