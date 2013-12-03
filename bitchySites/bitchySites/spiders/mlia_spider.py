"""
    This script pulls snippets from mlia.com
"""
from scrapy.spider import BaseSpider
from scrapy.selector import Selector

from bitchySites.items import MLIASnippet

class MLIASpider(BaseSpider):
    name = "mlia"
    allowed_domains = ["mylifeisaverage.com"]
    urlPrefix = "http://mylifeisaverage.com/"
    maxPages = 99 # Arbitrary (1-indexed) page number at MLIA < 11081
    start_urls = [urlPrefix + str(PageNo+1) for PageNo in range(maxPages)]

    def parse(self, response):
        sel = Selector(response)
        snippetDivs = sel.xpath('//div[contains(@class, "story")]')
        snippetList = []
        for snippetNo, snippet in enumerate(snippetDivs):
            newSnippet = MLIASnippet()
            snippetText = snippetDivs[snippetNo].xpath('.//div[contains(@class, "sc")]/text()').extract()
            newSnippet['text'] = snippetText[0].strip()
            newSnippet['snippetID'] = int(snippetDivs[snippetNo].xpath('@id').extract()[0].split('_')[-1])
            newSnippet['upVotes'] =  int(snippetDivs[snippetNo].xpath('.//span[contains(@class, "v_pos")]/text()').extract()[0])
            newSnippet['downVotes'] =  int(snippetDivs[snippetNo].xpath('.//span[contains(@class, "v_neg")]/text()').extract()[0])
            snippetList.append(newSnippet)
        return snippetList
