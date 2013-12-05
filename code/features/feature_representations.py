import json
from math import log
from collections import Counter, defaultdict

import numpy as np
from scipy.sparse import coo_matrix, lil_matrix

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
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


class BaseFeatureExtractor(object):
    def __init__(self):
        self.snippetFileName = None
        
        self.scores = []
        self.IDs = []
        self.F = None
        self.chosen_ngrams = []
        self.chosen_columns = []
        self.f_vector = None
        self.word_frequencies = None
        self.word_to_int = None
        self.int_to_word = None
        self.num_documents = 0
        self.num_words = 0
        self.includeBigrams = False

    def readJSON(self, snippetFileName):
        self.snippetFileName = snippetFileName

    def get_F(self):
        """ 
            Our first function creates F - matrix of entries F_ij : number of times document i contains word j
            
            Inputs: snippets file
            Output: scipy sparse matrix F
        """
        self.word_frequencies = defaultdict( int )
        # 1. create set of all words, word_frequencies is a dict with key = word, value = int (frequency in corpus)
        self.num_documents = 0
        with open(self.snippetFileName, 'r') as snippetFile:
            for document in snippetFile:
                snippet = json.loads(document)
                self.num_documents = self.num_documents + 1
                self.scores.append(snippet['score'])
                self.IDs.append(snippet['ID'])
                for unigram in snippet['unigramList']:
                    self.word_frequencies[unigram] += 1
                if self.includeBigrams:
                    for bigram in snippet['bigramList']:
                        self.word_frequencies[bigram] += 1

        self.num_words = len(self.word_frequencies)

        self.word_to_int = dict(zip(list(self.word_frequencies), range(self.num_words)))
        self.int_to_word = dict(zip(range(self.num_words), list(self.word_frequencies)))

        
        F = lil_matrix((self.num_documents, self.num_words), dtype=np.int8) # Linked list for rapid row modification
        with open (self.snippetFileName, 'r') as snippetFile: 
            for documentNo, document in enumerate(snippetFile):
                snippet = json.loads(document)
                if not snippet['unigramList'] and not snippet['bigramList']:
                    continue
                mapped_words = [self.word_to_int[x] for x in snippet['unigramList']+snippet['bigramList']] # list comprehension faster than map
                wordList = Counter(mapped_words)
                F[documentNo, wordList.keys()] = wordList.values()

        self.F =  F.tocoo()

    def gen_f_vectors(self):
        self.f_vector = []

        self.F = self.F.tocsr()
        for documentNo in range(self.num_documents):
            self.f_vector.append(np.array(self.F[documentNo, self.chosen_columns].todense()).tolist()[0])

        self.F = self.F.tocoo()

    def write_f_vectors(self, featureFileName):
        with open(featureFileName, 'w') as outFile:
            for documentNo in range(self.num_documents):
                fVectorData = {'ID':self.IDs[documentNo], 'score':self.scores[documentNo], 'f_vector': self.f_vector[documentNo]}
                outFile.write(json.dumps(fVectorData)+"\n")


class WordFrequency(BaseFeatureExtractor):
    def __init__(self, nDim=100, fMin=4, includeBigrams=False):
        self.nDim = nDim
        self.fMin = fMin
        self.includeBigrams = includeBigrams
        self.pruned_dictionary = {}
        super(WordFrequency, self).__init__()

    def prune_features(self):
        self.word_frequencies = { k:v for k, v in self.word_frequencies.items() if v > self.fMin}

        def create_sorted_word_frequencies(which_dict):
            best_keys = sorted(which_dict, key=which_dict.get, reverse=True)[:self.nDim]
            return best_keys

        self.chosen_ngrams = create_sorted_word_frequencies(self.word_frequencies)
        #print self.chosen_ngrams
        self.chosen_columns = [self.word_to_int[x] for x in self.chosen_ngrams]
        self.pruned_word_frequencies = {w:self.word_frequencies[w] for w in self.chosen_ngrams}
            
class WordPresence(WordFrequency):
    """
        Count just the presence or absence of the most frequently appearing 
        words in each document.
    """
    def gen_f_vectors(self):
        super(WordPresence, self).gen_f_vectors()
        for documentNo in range(self.num_documents):
            self.f_vector[documentNo] = [int(x != 0) for x in self.f_vector[documentNo]]
        

class InformationGain(BaseFeatureExtractor):
    """
        Implements feature selection using information gain
        Similar data structures as those of WordFrequency, except that the
        'counts' represent the number of documents with a given n-gram.
    """
    def __init__(self, nDim=100, IG_min=-100, includeBigrams=False):
        super(InformationGain, self).__init__()
        
        self.nDim = nDim
        self.IG_min = IG_min
        self.includeBigrams = includeBigrams
        self.nGramList = []
        self.nGramTotalDictionary = {}
        self.nGramPositiveDictionary = {}
        self.nGramNegativeDictionary = {}

        self.nTotal = 0
        self.nPositive = 0
        self.nNegative = 0

        self.P = None
        self.N = None
        self.P_positive = {}
        self.P_negative = {}
        self.P_w = {}
        self.P_pos_w = {}
        self.P_neg_w = {}

        self.IG = {}


    def calculate_IG(self, nGram):
        P_pos = self.P_positive
        P_neg = self.P_negative
        P_w   = self.P_w[nGram]
        P_w_bar = 1 - P_w
        P_pos_w = self.P_pos_w[nGram]/P_w
        P_neg_w = self.P_neg_w[nGram]/P_w
        P_pos_w_bar = (P_pos - (P_pos_w * P_w))/(1 - P_w)
        P_neg_w_bar = (P_neg - (P_neg_w * P_w))/(1 - P_w)

        IG = (-1.0)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        return IG

    def prune_features(self):
        self.nTotal = self.num_documents
        self.nPositive = sum([1 if x > 0 else 0 for x in self.scores])
        self.P_positive = float(self.nPositive)/self.nTotal
        self.nNegative = sum([1 if x < 0 else 0 for x in self.scores])
        self.P_negative = float(self.nNegative)/self.nTotal

        self.P = self.F.tocsr()
        self.N = self.F.tocsr()

        for row in range(self.num_documents):
            if self.scores[row] >= 0:
                self.N.data[self.N.indptr[row]:self.N.indptr[row+1]] = 0
            elif self.scores[row] <= 0:
                self.P.data[self.P.indptr[row]:self.P.indptr[row+1]] = 0

        self.P.eliminate_zeros()
        self.N.eliminate_zeros()

        self.F = self.F.tocsc()
        self.P = self.P.tocsc()
        self.N = self.N.tocsc()
        self.P_w =     {w: float(sum(self.F.data[self.F.indptr[self.word_to_int[w]]:self.F.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}
        self.P_pos_w = {w: float(sum(self.P.data[self.P.indptr[self.word_to_int[w]]:self.P.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}
        self.P_neg_w = {w: float(sum(self.N.data[self.N.indptr[self.word_to_int[w]]:self.N.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}


        # Calculate information gain
        self.IG = {w: self.calculate_IG(w) for w in self.word_frequencies}

        # remove some words based on IG
        self.word_frequencies = { k:v for k, v in self.IG.items() if v > self.IG_min}

        def create_sorted_word_frequencies(which_dict):
            best_keys = sorted(which_dict, key=which_dict.get, reverse=True)[:self.nDim]
            return best_keys

        self.chosen_ngrams = create_sorted_word_frequencies(self.IG)
        #print self.chosen_ngrams
        #print [self.IG[x] for x in self.chosen_ngrams]
        self.chosen_columns = [self.word_to_int[x] for x in self.chosen_ngrams]
        self.pruned_word_frequencies = {w:self.word_frequencies[w] for w in self.chosen_ngrams}


class GainRatio(InformationGain):
    """
        Implements feature selection using gain ratio. Differs from
        InformationGain only in that the information gain of a given n-gram is
        normalized by the entropy of the n-gram
    """
    def calculate_IG(self, nGram):
        P_pos = self.P_positive
        P_neg = self.P_negative
        P_w   = self.P_w[nGram]
        P_w_bar = 1 - P_w
        P_pos_w = self.P_pos_w[nGram]/P_w
        P_neg_w = self.P_neg_w[nGram]/P_w
        P_pos_w_bar = (P_pos - (P_pos_w * P_w))/(1 - P_w)
        P_neg_w_bar = (P_neg - (P_neg_w * P_w))/(1 - P_w)

        IG = (-1)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        # Entropy of the n-gram
        H =  (-1)      * ( plog2p(P_w)         + plog2p(P_w_bar)     )

        # Information gain of the n-gram
        IG = (-1)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        # Calculate gain ratio
        GR = float(IG)/H

        return GR


class TFIDF(BaseFeatureExtractor):
    def __init__(self, nDim = 200, freq=4, tfidf=0.5):
        super(TFIDF, self).__init__()
        self.snippetFileName = None
        self.nDim = nDim
        self.freq = freq
        self.tfidf = tfidf
        
    def prune_features(self):
        '''
            get top highest dims or threshold by freq
        '''
        # tf is already calculated in word_frequencies

        M = self.F.todense()
        M = M.sum(axis=0)[0].tolist()[0]   # row-wise sum, i.e, #docs per word
        
        self.idf_array = {w:np.log(float(self.num_documents)/(1.0+M[self.word_to_int[w]])) for w in self.word_frequencies}
        self.tfidf_array = {w:self.word_frequencies[w]*self.idf_array[w] for w in self.word_frequencies}
        
        def create_sorted_word_frequencies(which_dict):
            best_keys = sorted(which_dict, key=which_dict.get, reverse=True)[:self.nDim]
            return best_keys
        
        if self.tfidf < 0:
            if self.dim > 0:
                self.chosen_ngrams = create_sorted_word_frequencies(self.word_frequencies)
            elif self.freq > 0:
                self.chosen_ngrams = [w for w, f in self.word_frequencies.iteritems() if f>self.freq]
        else:
            self.chosen_ngrams = create_sorted_word_frequencies(self.tfidf_array)

        #print self.chosen_ngrams
        #print [self.tfidf_array[x] for x in self.chosen_ngrams]
        self.chosen_columns = [self.word_to_int[x] for x in self.chosen_ngrams]
        self.pruned_word_frequencies = {w:self.word_frequencies[w] for w in self.chosen_ngrams}

    def gen_f_vectors(self):
        self.f_vector = []

        self.F = self.F.tocsr()
        frequencyList = [self.word_frequencies[w] for w in self.chosen_ngrams]
        for documentNo in range(self.num_documents):
            self.f_vector.append(np.multiply(np.array(self.F[documentNo, self.chosen_columns].todense())[0], frequencyList).tolist())

        self.F = self.F.tocoo()
