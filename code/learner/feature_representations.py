"""
    Class definitions for feature extractors
"""
import json, pdb
import operator
from math import copysign
from math import log
from collections import Counter

def plog2p(x):
    if x <= 0:
        return 0
    else:
        return x*log(x, 2)

def uniqify(seq, idfun=None):
    #order preserving uniqifier
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

'''
class WordFrequency:
    def __init__(self, nDim=200, fMin=4, includeBigrams=False):
        self.snippetFileName = ''
        self.nGramList = []
        self.nGramDictionary = {}
        self.nDim = nDim
        self.fMin = fMin
        self.includeBigrams = includeBigrams
        self.maxFeatures = 0

    def readJSON(self, snippetFileName):
        self.snippetFileName = snippetFileName

    def generate_nGram_list(self):
        big_list = []
        with open(self.snippetFileName, 'r') as snippetFile:
            for line in snippetFile:
                snippet = json.loads(line)
                print snippet['unigramList']
                pdb.set_trace()
                big_list + snippet['unigramList']
                if self.includeBigrams:
                    big_list + snippet['bigramList']

        # Check unigrams with nGramList
        nGram_dictionary = Counter(big_list)
                
        # Prune nGramList
        self.nGramDictionary = nGram_dictionary.copy()
        self.maxFeatures = len(self.nGramDictionary.keys())

        pruned_dictionary = { k:v for k, v in self.nGramDictionary.items() if v > self.fMin}
        self.nGramList = [pair[0] for pair in sorted(pruned_dictionary.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.nDim]]
            
            
    def gen_f_vectors(self, featureFileName):
        self.generate_nGram_list()

        with open(self.snippetFileName, 'r') as snippetFile, open(featureFileName, 'w') as outFile:
            for line in snippetFile:
                snippet = json.loads(line)
                fVectorData = {'ID':snippet['ID'], 'score':snippet['score']}
                f_vector = [0.0] * self.nDim

                # Check nGrams from nGramList
                for index, nGram in enumerate(self.nGramList):
                    if nGram in snippet['unigramList'] + snippet['bigramList']:
                        f_vector[index] += 1

                fVectorData['f_vector'] = f_vector
                outFile.write(json.dumps(fVectorData)+"\n")
'''
class word_freq():
    def __init__(self, dim=200):
        self.dim = dim
        self.snippet_name = ''
    
    def read_json(snippet_name):
        self.snippet_name = snippet_name

    def get_ngrams(self):
        


class WordPresence(WordFrequency):
    """
        Count just the presence or absence of the most frequently appearing 
        words in each document.
    """
    def gen_f_vectors(self, featureFileName):
        self.generate_nGram_list()

        with open(self.snippetFileName, 'r') as snippetFile, open(featureFileName, 'w') as outFile:
            for line in snippetFile:
                snippet = json.loads(line)
                fVectorData = {'ID':snippet['ID'], 'score':snippet['score']}
                f_vector = [0.0] * self.nDim

                # Check nGrams from nGramList
                for index, nGram in enumerate(self.nGramList):
                    if nGram in snippet['unigramList'] + snippet['bigramList']:
                        f_vector[index] = 1

                fVectorData['f_vector'] = f_vector
                outFile.write(json.dumps(fVectorData)+"\n")


class InformationGain:
    """
        Implements feature selection using information gain
        Similar data structures as those of WordFrequency, except that the
        'counts' represent the number of documents with a given n-gram.
    """
    def __init__(self, nDim=10000, IG_min=0.1, includeBigrams=False):
        self.snippetFileName = ''
        self.includeBigrams = includeBigrams
        self.nDim = nDim
        self.IG_min = IG_min
        
        self.nGramList = []
        self.nGramTotalDictionary = {}
        self.nGramPositiveDictionary = {}
        self.nGramNegativeDictionary = {}

        self.nTotal = 0
        self.nPositive = 0
        self.nNegative = 0

        self.P_positive = {}
        self.P_negative = {}
        self.P_ngrams = {}
        self.P_positive_given_ngrams = {}
        self.P_negative_given_ngrams = {}

        self.IG = {}

        self.maxFeatures = 0

    def readJSON(self, snippetFileName):
        self.snippetFileName = snippetFileName

    def calculate_IG(self, nGram):
        P_pos = self.P_positive
        P_neg = self.P_negative
        P_w   = self.P_ngrams[nGram]
        P_w_bar = 1 - P_w
        P_pos_w = self.P_positive_given_ngrams[nGram]
        P_neg_w = self.P_negative_given_ngrams[nGram]
        P_pos_w_bar = (P_pos - (P_pos_w * P_w))/(1 - P_w)
        P_neg_w_bar = (P_neg - (P_neg_w * P_w))/(1 - P_w)

        IG = (-1)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        return IG

    def generate_nGram_list(self):
        with open(self.snippetFileName, 'r') as snippetFile:
            for line in snippetFile:
                snippet = json.loads(line)

                category = copysign(1, snippet['score'])     # returns +/- 1
                self.nTotal += 1
                if (category == 1):
                    self.nPositive += 1
                elif (category == -1):
                    self.nNegative += 1

                # Check unigrams with nGramList
                for unigram in uniqify(snippet['unigramList']):
                    if unigram in self.nGramTotalDictionary.keys():
                        self.nGramTotalDictionary[unigram] += 1
                        if (category == 1):
                            self.nGramPositiveDictionary[unigram] += 1
                            self.nGramNegativeDictionary[unigram] += 0
                        elif (category == -1):
                            self.nGramPositiveDictionary[unigram] += 0
                            self.nGramNegativeDictionary[unigram] += 1
                    else:
                        self.nGramTotalDictionary[unigram] = 1
                        if (category == 1):
                            self.nGramPositiveDictionary[unigram] = 1
                            self.nGramNegativeDictionary[unigram] = 0
                        elif (category == -1):
                            self.nGramPositiveDictionary[unigram] = 0
                            self.nGramNegativeDictionary[unigram] = 1

                # Check bigrams with nGramList
                if self.includeBigrams:
                    for bigram in uniqify(snippet['bigramList']):
                        if bigram in self.nGramTotalDictionary.keys():
                            self.nGramTotalDictionary[bigram] += 1
                            if (category == 1):
                                self.nGramPositiveDictionary[bigram] += 1
                                self.nGramNegativeDictionary[bigram] += 0
                            elif (category == -1):
                                self.nGramPositiveDictionary[bigram] += 0
                                self.nGramNegativeDictionary[bigram] += 1
                        else:
                            self.nGramTotalDictionary[bigram] = 1
                            if (category == 1):
                                self.nGramPositiveDictionary[bigram] = 1
                                self.nGramNegativeDictionary[bigram] = 0
                            elif (category == -1):
                                self.nGramPositiveDictionary[bigram] = 0
                                self.nGramNegativeDictionary[bigram] = 1
                
        self.maxFeatures = len(self.nGramTotalDictionary.keys())

        # Calculate incidence probabilities
        self.P_positive = float(self.nPositive)/self.nTotal     # P(+)
        self.P_negative = float(self.nNegative)/self.nTotal     # P(-)
        self.P_ngrams = { k: float(v)/self.nTotal for k, v in self.nGramTotalDictionary.items()}    # P(w)
        self.P_positive_given_ngrams = { k: float(v)/self.nGramTotalDictionary[k] for k, v in self.nGramPositiveDictionary.items()}     # P(+|w)
        self.P_negative_given_ngrams = { k: float(v)/self.nGramTotalDictionary[k] for k, v in self.nGramNegativeDictionary.items()}     # P(-|w)

        # Calculate information gain
        self.IG = { k: self.calculate_IG(k) for k in self.nGramTotalDictionary.keys()}
        pruned_IGs = {k : v for k, v in self.IG.items() if v > self.IG_min}
        self.nGramList = [pair[0] for pair in sorted(pruned_IGs.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.nDim]]


    def gen_f_vectors(self, featureFileName):
        self.generate_nGram_list()

        with open(self.snippetFileName, 'r') as snippetFile, open(featureFileName, 'w') as outFile:
            for line in snippetFile:
                snippet = json.loads(line)
                fVectorData = {'ID':snippet['ID'], 'score':snippet['score']}
                f_vector = [0.0] * self.nDim

                # Check nGrams from nGramList
                for index, nGram in enumerate(self.nGramList):
                    if nGram in snippet['unigramList'] + snippet['bigramList']:
                        f_vector[index] = 1

                fVectorData['f_vector'] = f_vector
                outFile.write(json.dumps(fVectorData)+"\n")


class GainRatio(InformationGain):
    """
        Implements feature selection using gain ratio. Differs from
        InformationGain only in that the information gain of a given n-gram is
        normalized by the entropy of the n-gram
    """
    def calculate_IG(self, nGram):
        P_pos = self.P_positive
        P_neg = self.P_negative
        P_w   = self.P_ngrams[nGram]
        P_w_bar = 1 - P_w
        P_pos_w = self.P_positive_given_ngrams[nGram]
        P_neg_w = self.P_negative_given_ngrams[nGram]
        P_pos_w_bar = (P_pos - (P_pos_w * P_w))/(1 - P_w)
        P_neg_w_bar = (P_neg - (P_neg_w * P_w))/(1 - P_w)

        # Entropy of the n-gram
        H =  (-1)      * ( plog2p(P_w)         + plog2p(P_w_bar)     )

        # Information gain of the n-gram
        IG = (-1)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        # Calculate gain ratio
        GR = float(IG)/H

        return GR
