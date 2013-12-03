""" 
    This script runs scrapy from within python.
"""
from twisted.internet import reactor
from scrapy import log, signals
from scrapy.crawler import Crawler, CrawlerProcess
from scrapy.settings import Settings
from scrapy.xlib.pydispatch import dispatcher
from scrapy.utils.project import get_project_settings

# Custom spiders 
from bitchySites.spiders.mlig_spider import MLIGSpider
from bitchySites.spiders.mlia_spider import MLIASpider
from bitchySites.spiders.fml_spider import FMLSpider
from bitchySites.spiders.lml_spider import LMLSpider

# Get project settings
def scrapeTrainingData():
    settings = get_project_settings()
    
    # Set up MLIG crawler
    mlig_spider = MLIGSpider()
    mlig_crawler = Crawler(settings)
    mlig_crawler.configure()
    mlig_crawler.crawl(mlig_spider)
    mlig_crawler.start()
    
    # Set up MLIA crawler
    mlia_spider = MLIASpider()
    mlia_crawler = Crawler(settings)
    mlia_crawler.configure()
    mlia_crawler.crawl(mlia_spider)
    mlia_crawler.start()
    
    # Set up FML crawler
    fml_spider = FMLSpider()
    fml_crawler = Crawler(settings)
    #fml_crawler.signals.connect(reactor.stop, signal=signals.spider_closed) # Send stop signal only when FML is done. FML will take the most time
    fml_crawler.configure()
    fml_crawler.crawl(fml_spider)
    fml_crawler.start()
    
    # Set up LML crawler
    lml_spider = LMLSpider()
    lml_crawler = Crawler(settings)
    lml_crawler.signals.connect(reactor.stop, signal=signals.spider_closed) # Send stop signal only when LML is done. LML will take the most time
    lml_crawler.configure()
    lml_crawler.crawl(lml_spider)
    lml_crawler.start()
    
    # Start the reactor (i.e., unleash both spiders)
    log.start()
    log.msg('Running reactor...')
    reactor.run()  # the script will block here until the spider is closed
    log.msg('Reactor stopped.')

if __name__ == '__main__':
    scrapeTrainingData()
