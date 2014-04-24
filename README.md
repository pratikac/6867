# Sentiment Analysis of Tweets using Machine Learning Algorithms 

This project
deals with sentiment analysis of tweets using various machine learning
techniques.

_Prerequisites_: If you don't already have scrapy installed, get it with
`easy_install -U Scrapy` or `pip install Scrapy`.  Alternate installation
methods available from the [Official Site](scrapy.org/download).

**Quick run**: Just run `make from_scratch`.

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

## Pre-processing the training data
The positive and negative snippets from these various sources are stored in two
different JSON files (.jl format) `positive.jl` and `negative.jl`. Each record
in these files consists of two fields:

1. _'text'_ - containing the text of the post after suitable lemmatization and
   stemming; and

2. _'score'_ - a postive or negative number (depending on the sentiment)
   indicating our confidence in the snippet's classification. 

### Tokenization, Screening and Stemming
In this step we identify the basic lexicon from which feature
vectors may be constructed. A review of a number of sources including [Kang et
al., (2011)](dx.doi.org/10.1016/j.eswa.2011.11.107) and [Pak and Paroubek
(2010)](http://goo.gl/MM7Fe0) have used either only unigrams or a combination
of unigrams and bigrams. We have chosen to follow these authors and have
restricted our lexicon to unigrams and bigrams.
First we remove all non-alphabetical characters from the snippet. Then we
tokenize the snippet to generate two lists: a list of unigrams containing words
with more than three letters, and a list of bigrams (that may contain less than
three letters per word). This is followed by conversion of every word to lower
case. Each word is subjected to lemmatization using Python's [Natural Language
Toolkit](http://www.nltk.org/) lemmatizer drawn from
[WordNet](http://wordnet.princeton.edu/). Unfortunately, this lemmatizer is not
perfect - for instance, it converts the word 'was' into 'wa'. These spurious
stemmations in each word list are subsequently corrected. The two word n-gram
lists are then sorted alphabetically and stored in the _'text'_ field.

### Scoring and confidence estimation
A 'downVote' assigned to a snippet from mylifeisg.com or lmylife.com implies
that (in the opinion of the voter) the author's life is not as 'good' as she
claims. Consequently, we can use a score derived from the numbers of upVotes
and downVotes received by each snippet to represent how positive that snippet
really is. With the snippets from fmylife.com, there is a subtle twist to this
argument. A downVote on this site implies that the voter '... deserve[s] it'.
Snippets that obtain more downVotes than upVotes are typically of the form
where the author confesses to some wrongdoing - such as unprotected sex, or
petty theft. For the sake of simplicity, we will invoke the rather Freudian
argument that such acts of wrongdoing increase the author's happiness (at least
in the short term) and therefore, a snippet from fmylife.com with a negative
score represents a positive sentiment.

The score for each snippet is calculated from the numbers of upvotes and
downvotes received by the snippet (on its source site) using [Evan Miller's
_'Wilson\'s interval score'_
algorithm](http://www.evanmiller.org/how-not-to-sort-by-average-rating.html).
This algorithm calculates the lower bound of one-sided interval within which we
can claim (with a given confidence) that the true value of (positive
votes)/(total votes) lies. One of the key assumptions involved in scoring the snippets this way is that 'value' of one vote is the same across the different source sites. 

The output of this step comprises two JSON files `positive.jl` and `negative.jl` that contain pre-processed positive and negative snippets respectively.

## Feature selection
We have implemented the following methods of feature selection:

1. _Word Frequency_: We select the top `nDim` n-grams that occur the most frequently across all snippets in the training set (with or without an added minimum frequency cutoff `fMin`). Each snippet is then assigned a feature vector with `nDim` elements representing the frequencies of appearences of each of these n-grams.
2. _Word Presence_:  Similar to _Word Frequency_, except that all values of the feature vector are either 0 (n-gram is absent) or 1 (n-gram is present).
3. _Information Gain_: We quantify the amount of information every n-gram contributes towards the classification of the snippets in the training data and choose `nDim` ngrams that contribute the most information (and/or at least `IG_min` information) as our features.
4. _Gain Ratio_: We normalize the information gain per n-gram by the intrinsic entropy of the n-gram in the corpus. We then choose the top `ndim` n-grams that have a gain ratio of at least `IG_min` as our features. As with the _Information Gain_ method, the feature vector counts the frequency of each chosen feature in a given snippet.

