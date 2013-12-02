# Sentiment Analysis of Tweets using Machine Learning Algorithms
This project deals with sentiment analysis of tweets using various machine learning techniques.

## Collecting training data
If you don't already have scrapy installed, get it with `easy_install -U Scrapy` or `pip install Scrapy`. Alternate installation methods available from the [Official Site](scrapy.org/download).
Scrapy permits the creation of spiders to crawl entire domains for specific information in specific formats. These code for these spiders can be found in `bitchySites/bitchySites/spiders`. 
Running the script `scrapeTrainingData.py` will create JSON files with snippets from [FML](fmylife.com) and [MLIG](mylifeisg.com).
