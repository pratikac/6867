"""
    Define here the models for your scraped items
    
    See documentation in:
    http://doc.scrapy.org/en/latest/topics/items.html
"""

from scrapy.item import Item, Field

class FMLSnippet(Item):
    """
        Container to be loaded with data scraped from fmylife.com
    """
    # define the fields for your item here like:
    # name = Field()
    text = Field()
    snippetID = Field()
    upVotes = Field()
    downVotes = Field()


class MLIGSnippet(Item):
    """
        Container to be loaded with data scraped from mlig.com
    """
    # define the fields for your item here like:
    # name = Field()
    text = Field()
    snippetID = Field()
    upVotes = Field()
    downVotes = Field()
