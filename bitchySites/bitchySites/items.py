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

class LMLSnippet(Item):
    """
        This is a copy of the FMLSnippet class, but I'm too lazy to implement
        inheritance
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

class MLIASnippet(Item):
    """
        This is basically a copy of the MLIGSnippet class, but I'm too lazy to
        implement inheritance
    """
    # define the fields for your item here like:
    # name = Field()
    text = Field()
    snippetID = Field()
    upVotes = Field()
    downVotes = Field()
