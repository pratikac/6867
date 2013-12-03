"""
    This script pulls snippets from fmylife.com
"""
from scrapy.spider import BaseSpider
from scrapy.selector import Selector

from bitchySites.items import FMLSnippet

class FMLSpider(BaseSpider):
    name = "FML"
    allowed_domains = ["fmylife.com"]
    urlPrefix = "http://fmylife.com/tops/top?page="
    maxPages = 99 # Page numbers start with 0 at FML, 99 chosen arbitrarily
    start_urls = [urlPrefix + str(PageNo) for PageNo in range(maxPages)]

    def parse(self, response):
        sel = Selector(response)
        snippetDivs = sel.xpath('//div[contains(@class, "post article")]')
        snippetList = []
        for snippetNo, snippet in enumerate(snippetDivs):
            newSnippet = FMLSnippet()
            snippetText = snippetDivs[snippetNo].xpath('.//a[contains(@class, "fmllink")]/text()').extract()
            newSnippet['text'] = ''.join(snippetText)
            newSnippet['snippetID'] = int(snippetDivs[snippetNo].xpath('@id').extract()[0])
            newSnippet['upVotes'] =  int(snippetDivs[snippetNo].xpath('.//span[contains(@class, "dyn-vote-j-data")]/text()').extract()[0])
            newSnippet['downVotes'] =  int(snippetDivs[snippetNo].xpath('.//span[contains(@class, "dyn-vote-t-data")]/text()').extract()[0])
            snippetList.append(newSnippet)
        return snippetList
