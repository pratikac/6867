# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from bitchySites.spiders.mlig_spider import MLIGSpider
from bitchySites.spiders.mlia_spider import MLIASpider
from bitchySites.spiders.fml_spider import FMLSpider
from bitchySites.spiders.lml_spider import LMLSpider

import subprocess

class JsonWriter(object):

    def __init__(self):
        print "Spiders started!"

    def open_spider(self, spider):
        if isinstance(spider, MLIGSpider):
            print "Currently crawling: MLIG"
            self.file_mlig = open('MLIG.jl', 'wb')
        elif isinstance(spider, MLIASpider):
            print "Currently crawling: MLIA"
            self.file_mlia = open('MLIA.jl', 'wb')
        elif isinstance(spider, FMLSpider):
            print "Currently crawling: FML"
            self.file_fml = open('FML.jl', 'wb')
        elif isinstance(spider, LMLSpider):
            print "Currently crawling: LML"
            self.file_lml = open('LML.jl', 'wb')
        else:
            print "Unidentified spider!"

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"

        if isinstance(spider, MLIGSpider):
            self.file_mlig.write(line)
        elif isinstance(spider, MLIASpider):
            self.file_mlia.write(line)
        elif isinstance(spider, FMLSpider):
            self.file_fml.write(line)
        elif isinstance(spider, LMLSpider):
            self.file_lml.write(line)

        return item

#    def close_spider(self, spider):
#        if isinstance(spider, LMLSpider):
#            subprocess.call("sort -u LML.jl > LML_uniq.jl", shell=True)
#            subprocess.call("mv LML_uniq.jl LML.jl", shell=True)

