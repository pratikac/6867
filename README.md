# Sentiment Analysis of Tweets using Machine Learning Algorithms This project
deals with sentiment analysis of tweets using various machine learning
techniques.

_Prerequisites_: If you don't already have scrapy installed, get it with
`easy_install -U Scrapy` or `pip install Scrapy`.  Alternate installation
methods available from the [Official Site](scrapy.org/download).

**Quick run**: Just run `make fromscratch`.

## Collecting training data

Scrapy permits the creation of spiders to crawl entire domains for specific
information in specific formats. The code for these spiders can be found in
`bitchySites/bitchySites/spiders`.  Running the script `scrapeTrainingData.py`
from inside the folder `bitchySites` will create JSON files with snippets from
[FML](fmylife.com) and [MLIG](mylifeisg.com). 

**Note**: Make sure to screen out duplicate snippets from LML using the
following commands: `sort -u LML.jl > LML_uniq.jl mv LML_uniq.jl LML.jl` This
is already implemented in the makefile.

The number of unique records obtained by running `scrapeTrainingData.py` are as
follows: FML.jl  1287 (100/1900+ pages scraped) LML.jl  654  (as much as
possible from the Way Back Machine) MLIG.jl 599  (all pages) MLIA.jl 990
(100/11000+ pages)

I feel only the first three sites are suitable sources of training data. Almost
all MLIA posts are either about how Harry Potter is awesome and Twilight sucks
(which risks severly biasing any keyword-based Machine Learning algorithm), or
neutral (hence the 'average' in MyLifeIsAverage).  The first 100 pages of FML
provide 1287 _negative_ examples, and the combination of LML and MLIG provide a
total of 1253 _positive_ examples. This is of the same order as the number of
training examples used by [Pang and Lee
(2004)](dx.doi.org/10.3115/1218955.1218990).

The positive and negative snippets from these various sources are stored in two
different JSON files (.jl format) `positive.jl` and `negative.jl`. Each record
in these files consists of two fields:
1. _'text'_ - containing the text of the post after suitable lemmatization and
   stemming; and
2. _'score'_ - a postive or negative number (depending on the sentiment)
   calculated from the numbers of upvotes and downvotes received by the snippet
   using [Evan Miller's _'Wilson\'s interval score'_
   algorithm](http://www.evanmiller.org/how-not-to-sort-by-average-rating.html).

We perform lemmatization using Python's [Natural Language Toolkit](http://www.nltk.org/) lemmatizer drawn from [WordNet](http://wordnet.princeton.edu/).

### Tokenization, Screening and Stemming
**Tokenization** In this step we identify the basic lexicon from which feature
vectors may be constructed. A review of a number of sources including [Kang et
al., (2011)](dx.doi.org/10.1016/j.eswa.2011.11.107) and [Pak and Paroubek
(2010)](http://goo.gl/MM7Fe0) have used either only unigrams or a combination
of unigrams and bigrams. We have chosen to follow these authors and have
restricted our lexicon to unigrams and bigrams.

## Feature selection

