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
            self.f_vector.append(np.array(self.F[documentNo, :].todense())[0].tolist())

    def write_f_vectors(self, featureFileName):
        with open(featureFileName, 'w') as outFile:
            for documentNo in range(self.num_documents):
                fVectorData = {'ID':self.IDs[documentNo], 'score':self.scores[documentNo], 'f_vector': self.f_vector[documentNo]}

                outFile.write(json.dumps(fVectorData)+"\n")


class WordFrequency(BaseFeatureExtractor):
    def __init__(self, nDim=10000, fMin=4, includeBigrams=False):
        self.nDim = nDim
        self.fMin = fMin
        self.includeBigrams = includeBigrams
        self.pruned_dictionary = {}
        super(WordFrequency, self).__init__()

    def prune_features(self):
        self.word_frequencies = { k:v for k, v in self.word_frequencies.items() if v > self.fMin}

        self.F = self.F.tocsc()
        for col in [self.word_to_int[w] for w in self.word_frequencies]:
            self.F.data[self.F.indptr[col]:self.F.indptr[col+1]] = 0

        self.F = self.F.tocoo()
            

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
    def __init__(self, nDim=10000, IG_min=0.1, includeBigrams=False):
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

        IG = (-1)      * ( plog2p(P_pos)       + plog2p(P_neg)       ) \
             + P_w     * ( plog2p(P_pos_w)     + plog2p(P_neg_w)     ) \
             + P_w_bar * ( plog2p(P_pos_w_bar) + plog2p(P_neg_w_bar) )

        return IG

    def prune_features(self):
        self.nTotal = self.num_documents
        self.nPositive = sum([1 for x in self.scores if x > 0])
        self.P_positive = self.nPositive/self.nTotal
        self.nNegative = sum([1 for x in self.scores if x < 0])
        self.P_negative = self.nNegative/self.nTotal

        self.P = self.F.copy()
        self.P = self.P.tocsr()
        self.N = self.P.copy()

        for row in range(self.num_documents):
            if self.scores[row] > 0:
                self.N.data[self.N.indptr[row]:self.N.indptr[row+1]] = 0
            elif self.scores[row] < 0:
                self.P.data[self.P.indptr[row]:self.P.indptr[row+1]] = 0

        self.F = self.F.tocsc()
        self.P = self.P.tocsc()
        self.N = self.N.tocsc()
        self.P_w = {w: float(sum(self.F.data[self.F.indptr[self.word_to_int[w]]:self.F.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}
        self.P_pos_w = {w: float(sum(self.P.data[self.P.indptr[self.word_to_int[w]]:self.P.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}
        self.P_neg_w = {w: float(sum(self.N.data[self.N.indptr[self.word_to_int[w]]:self.N.indptr[self.word_to_int[w]+1]]))/self.nTotal for w in self.word_frequencies}


        # Calculate information gain
        self.IG = {w: self.calculate_IG(w) for w in self.word_frequencies}

        self.word_frequencies = { k:v for k, v in self.word_frequencies.items() if v > self.IG_min}

        self.F = self.F.tocsc()
        for col in [self.word_to_int[w] for w in self.word_frequencies]:
            self.F.data[self.F.indptr[col]:self.F.indptr[col+1]] = 0

        self.F = self.F.tocoo()


    def gen_f_vectors(self):
        super(InformationGain, self).gen_f_vectors()
        for documentNo in range(self.num_documents):
            self.f_vector[documentNo] = [int(x != 0) for x in self.f_vector[documentNo]]

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
    def __init__(self, dim = 200, freq=4, tfidf=0.5):
        super(TFIDF, self).__init__()
        self.snippetFileName = None
        self.dim = dim
        self.freq = freq
        self.tfidf = tfidf
        

    def prune_features(self):
        '''
            get top highest dims or threshold by freq
        '''
        # tf is already calculated in word_frequencies

        M = self.F.todense()
        M = M.sum(axis=0)[0].tolist()[0]   # row-wise sum, i.e, #docs per word
        
        #pdb.set_trace()
        idf = {w:np.log(float(self.num_documents)/(1.0+M[self.word_to_int[w]])) for w in self.word_frequencies}
        tfidf = {w:self.word_frequencies[w]*idf[w] for w in self.word_frequencies}
        
        def create_sorted_word_frequencies(which_dict):
            best_keys = sorted(which_dict, key=which_dict.get, reverse=True)[:self.dim]
            return {w:self.word_frequencies[w] for w in best_keys}
        
        if self.tfidf < 0:
            if self.dim > 0:
                self.word_frequencies = create_sorted_word_frequencies(self.word_frequencies)
            elif self.freq > 0:
                self.word_frequencies = {w:f for w, f in self.word_frequencies.iteritems() if f>self.freq}
        else:
            self.word_frequencies = create_sorted_word_frequencies(tfidf)

        #is_chosen_word = lambda w: w in self.word_frequencies 
        #for dp in self.data:
        #    dp[0] = [w for w in dp[0] if is_chosen_word(w)]
        #    if dp[1] > 0:
        #        dp[1] = +1
        #    else:
        #        dp[1] = -1

        # Efficient pruning using CSC format - just set the relevant columns to zero
        self.F = self.F.tocsc()
        for col in [self.word_to_int[w] for w in self.word_frequencies]:
            self.F.data[self.F.indptr[col]:self.F.indptr[col+1]] = 0

        self.F = self.F.tocoo()

    def gen_f_vectors(self):
        self.f_vector = []

        #self.word_frequencies = pd.word_frequencies
        #num_words = len(word_freq)
        #word_to_index = dict(zip(word_freq.keys(), range(num_words)))
        #index_to_word = dict(zip(range(num_words), word_freq.keys()))
        #for index in range(num_words):
        #    self.int_to_eng_words[index] = pd.int_to_word[index_to_word[index]]

        #def get_bitmap(word_array):
        #    #z = [0 for i in range(num_words)]
        #    z = [0]*self.num_words
        #    for w in word_array:
        #        z[self.word_to_int[w]] = self.word_frequencies[w]
        #    return z

        #for dp in pd.data:
        #    self.features.append(get_bitmap(dp[0]))
        #    self.labels.append(dp[1])
        self.F = self.F.tocsr()
        for documentNo in range(self.num_documents):
            self.f_vector.append(np.array(self.F[documentNo, :].todense())[0].tolist())

    def get_word_array_from_bitmap(self, bit_array):
        l = len(bit_array)
        which = [i for i in xrange(l) if bit_array[i] > 0]
        return [self.int_to_word[wi] for wi in which]


class process_data():
    '''
        creates a more malleable representation of data
    '''
    def __init__(self, dim=200, freq=4, tfidf=0.5):
        self.dim = dim
        self.freq = freq
        self.tfidf = tfidf
        self.word_frequencies = {}
        
        self.word_to_int = {}
        self.int_to_word = {}

        #   words : set of words, written as ints (which are keys in int_to_word)
        #   score, id : score, id
        self.data = []
        
        self.get_all_words()
        self.prune_words()

    def get_all_words(self):
        fnames = ['../process/positive.jl', '../process/negative.jl']
        
        # 1. create set of all words, all_words is a dict with key = word, value = int
        all_words = set()
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    all_words.update(snippet['unigramList'])
        
        num_words = len(all_words)
        self.word_to_int = dict(zip(list(all_words), range(num_words)))
        self.int_to_word = dict(zip(range(num_words),list(all_words)))

        # 2. convert to better data format
        # we also count the frequency of words while doing this
        list_all_words = []
        get_word_key = lambda x: self.word_to_int[x]
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    mapped_words = map(get_word_key, snippet['unigramList'])
                    data_point = [mapped_words, snippet['score'], snippet['ID']]
                    self.data.append(data_point)
                    list_all_words.append(mapped_words)
        
        flattend_list = [item for sublist in list_all_words for item in sublist]
        self.word_frequencies = Counter(flattend_list)
    
    def prune_words(self):
        '''
            get top highest dims or threshold by freq
        '''
        
        # tf is already calculated in word_frequencies
        num_documents = len(self.data)
        num_words = len(self.word_frequencies)
        row = []
        col = []
        count = 0
        for dp in self.data:
            col += dp[0]
            row += [count for i in xrange(len(dp[0]))]
            count +=1
        M = coo_matrix((np.ones(len(row)), (np.array(row),np.array(col))), shape=(num_documents, num_words), dtype=np.int8).todense()
        M = M.sum(axis=0)[0].tolist()[0]   # row-wise sum, i.e, #docs per word
        
        #pdb.set_trace()
        idf = {w:np.log(float(num_documents)/(1.0+M[w])) for w in self.word_frequencies}
        tfidf = {w:self.word_frequencies[w]*idf[w] for w in self.word_frequencies}
        
        def create_sorted_word_frequencies(which_dict):
            best_keys = sorted(which_dict, key=which_dict.get, reverse=True)[:self.dim]
            return {w:self.word_frequencies[w] for w in best_keys}
        
        if self.tfidf < 0:
            if self.dim > 0:
                self.word_frequencies = create_sorted_word_frequencies(self.word_frequencies)
            elif self.freq > 0:
                self.word_frequencies = {w:f for w,f in self.word_frequencies.iteritems() if f>self.freq}
        else:
            self.word_frequencies = create_sorted_word_frequencies(tfidf)

        is_chosen_word = lambda w: w in self.word_frequencies 
        for dp in self.data:
            dp[0] = filter(is_chosen_word, dp[0])
            if dp[1] > 0:
                dp[1] = +1
            else:
                dp[1] = -1
                        

class feature_vector():
    '''
    constructs a feature vector from word_freq data
    '''
    def __init__(self, dim, freq, tfidf):
        pd = process_data(dim, freq, tfidf)
        
        self.features = []
        self.labels = []
        self.int_to_eng_words = {}

        word_freq = pd.word_frequencies
        num_words = len(word_freq)
        word_to_index = dict(zip(word_freq.keys(), range(num_words)))
        index_to_word = dict(zip(range(num_words), word_freq.keys()))
        for index in range(num_words):
            self.int_to_eng_words[index] = pd.int_to_word[index_to_word[index]]

        def get_bitmap(word_array):
            z = [0 for i in range(num_words)]
            for w in word_array:
                z[word_to_index[w]] = word_freq[w]
            return z

        for dp in pd.data:
            self.features.append(get_bitmap(dp[0]))
            self.labels.append(dp[1])

        def get_word_array_from_bitmap(bit_array):
            l = len(bit_array)
            which = [i for i in xrange(l) if bit_array[i] > 0]
            return [self.int_to_eng_words[wi] for wi in which]

#fv = feature_vector(200,-1, 1)

