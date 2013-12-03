"""
    This script uses the .jl JSON files generated by scraping FML etc. to
    generate consolidated corpora of positive and negative training data with
    scores post lemmatization
"""

import simplejson as json
from math import sqrt
from nltk.tokenize import RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer

lmtzr = WordNetLemmatizer()

# One sided confidence interval that the 'actual' score will be above the calcualted score
CONFIDENCE = 1.645        # use 1.0 for a confidence of 85%, 1.645 for 95%

def calculate_score(upVotes, downVotes, confidence):
    nVotes = upVotes + downVotes
    if nVotes == 0:
        return 0

    P_hat = float(upVotes)/nVotes
    return (P_hat+confidence*confidence/(2*nVotes)-confidence*sqrt((P_hat*(1-P_hat)+confidence*confidence/(4*nVotes))/nVotes))/(1+confidence*confidence/nVotes)


def process_text(text):
    # Tokenize ONLY alphabetic sequences 
    wordTokenizer = RegexpTokenizer('\w+')
    longWordTokenizer = RegexpTokenizer('\w{3,}')   # words with > 2 letters 

    # Lemmatize words in the word list 
    wordList = [lmtzr.lemmatize(word.lower()) for word in wordTokenizer.tokenize(text)]
    longWordList = [lmtzr.lemmatize(word.lower()) for word in longWordTokenizer.tokenize(text)]

    # Clean up after lemmatization - is there a more efficient way? 
    for wordNo, word in enumerate(wordList):
        # 'was' becomes 'wa' after lemmatization
        if word == 'wa':
            wordList[wordNo] = 'was'

    for wordNo, word in enumerate(longWordList):
        # 'was' becomes 'wa' after lemmatization
        if word == 'wa':
            longWordList[wordNo] = 'was'

    # Generate unigram  and bigram lists
    unigram_list = longWordList

    bigram_list = []
    for wordNo in range(len(wordList[:-1])):
        bigram_list.append(wordList[wordNo]+' '+wordList[wordNo+1])

    return (sorted(unigram_list), sorted(bigram_list))


FML_file = 'bitchySites/FML.jl'
MLIG_file = 'bitchySites/MLIG.jl'
LML_file = 'bitchySites/LML.jl'
MLIA_file = 'bitchySites/MLIA.jl'

positive_file = 'positive.jl'
negative_file = 'negative.jl'

positiveSources = ['LML', 'MLIG']
negativeSources = ['FML']

# Process NEGATIVE sources
with open(negative_file, 'w') as outFile:
    for sourceName in negativeSources:
        scrapedFile = 'bitchySites/' + sourceName + '.jl' 
        print "Processing snippets from " + sourceName
        with open(scrapedFile, 'r') as jsonFile:
            for line in jsonFile:
                snippet = json.loads(line)

                # Snippet processing
                unigramList, bigramList = process_text(snippet['text'])
                # Assign a NEGATIVE score
                score = (-1) * calculate_score(snippet['upVotes'], snippet['downVotes'], CONFIDENCE) 
                snippetData = {'unigramList': unigramList, 'bigramList': bigramList, 'score': score, 'ID': sourceName+'_'+str(snippet['snippetID'])}
                outFile.write(json.dumps(snippetData)+"\n")


# Process POSITIVE sources
with open(positive_file, 'w') as outFile:
    for sourceName in positiveSources:
        scrapedFile = 'bitchySites/' + sourceName + '.jl' 
        print "Processing snippets from " + sourceName
        with open(scrapedFile, 'r') as jsonFile:
            for line in jsonFile:
                snippet = json.loads(line)

                # Snippet processing
                unigramList, bigramList = process_text(snippet['text'])
                # Assign a POSITIVE score
                score = (1) * calculate_score(snippet['upVotes'], snippet['downVotes'], CONFIDENCE) 
                snippetData = {'unigramList': unigramList, 'bigramList': bigramList, 'score': score, 'ID': sourceName+'_'+str(snippet['snippetID'])}
                outFile.write(json.dumps(snippetData)+"\n")


print "Done!"