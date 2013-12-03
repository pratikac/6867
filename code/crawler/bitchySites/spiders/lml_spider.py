"""
    This script pulls snippets from lmylife.com
    This site is now defunct, but it can be recovered from the Way Back Machine
"""
from scrapy.spider import BaseSpider
from scrapy.selector import Selector

from bitchySites.items import LMLSnippet

class LMLSpider(BaseSpider):
    name = "LML"
    allowed_domains = ["web.archive.org"]
    urlPrefixes = ["https://web.archive.org/web/20110104112408/http://www.lmylife.com/?page=",
            "https://web.archive.org/web/20110104112408/http://www.lmylife.com/?sort=agree&page=",
            "https://web.archive.org/web/20110104112408/http://www.lmylife.com/?sort=disagree&page=",
            "https://web.archive.org/web/20110104112408/http://www.lmylife.com/?sort=random&page="]
    maxPages = 43 # 1-indexed page numbers. Max no. of pages = 43
    start_urls = [urlPrefix + str(PageNo+1) for PageNo in range(maxPages) for urlPrefix in urlPrefixes]

    def parse(self, response):
        sel = Selector(response)
        snippetDivs = sel.xpath('//div[@class="item_box"]')
        snippetList = []
        for snippetNo, snippet in enumerate(snippetDivs):
            newSnippet = LMLSnippet()
            snippetText = snippetDivs[snippetNo].xpath('.//p/a/text()').extract()[0]
            newSnippet['text'] = snippetText.strip()
            newSnippet['snippetID'] = int(snippetDivs[snippetNo].xpath('.//p/a/@href').extract()[0].split('=')[-1])
            snippetVotes = snippetDivs[snippetNo].xpath('.//span[@class="item_info"]//td')[0].re(r'\([ ]*[0-9]+[ ]*\)')
            newSnippet['upVotes'] =  int(snippetVotes[0].strip('\(\)'))
            newSnippet['downVotes'] =  int(snippetVotes[1].strip('\(\)'))
            snippetList.append(newSnippet)
        return snippetList
