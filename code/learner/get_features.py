import json, pdb
from collections import Counter
import numpy as np
from scipy.sparse import coo_matrix

class process_data():
    '''
    creates a more malleable representation of data
    '''
    def __init__(self, dim=200, freq=4, tfidf=0.5):
        self.dim = dim
        self.freq= freq
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
