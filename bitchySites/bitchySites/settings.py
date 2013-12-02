# Scrapy settings for bitchySites project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'bitchySites'

SPIDER_MODULES = ['bitchySites.spiders']
NEWSPIDER_MODULE = 'bitchySites.spiders'

# Pipelines for the output
# JsonWriter - 800 (done last, all other pipelines must have orders < 800)
ITEM_PIPELINES = {'bitchySites.pipelines.JsonWriter':800}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'bitchySites (+http://www.yourdomain.com)'
