import json, pdb
from collections import Counter, namedtuple

class process_data():
    '''
    creates a more malleable representation of data
    '''
    def __init__(self, dim=200, freq=4):
        self.dim = dim
        self.freq= freq
        self.all_words = set()
        self.num_words = 0
        self.word_frequencies = {}
        self.word_to_int = {}
        self.int_to_word = {}

        #   words : set of words, written as ints (which are keys in int_to_word)
        #   score, id : score, id
        self.data_point_t = namedtuple('data', ['words', 'score', 'id'])
        self.data = []
        
        self.get_all_words()
        self.prune_words()

    def get_all_words(self):
        fnames = ['../process/positive.jl', '../process/negative.jl']
        
        # 1. create set of all words, all_words is a dict with key = word, value = int
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    self.all_words.update(snippet['unigramList'])
        
        self.num_words = len(self.all_words)
        self.word_to_int = dict(zip(list(self.all_words), range(self.num_words)))
        self.int_to_word = dict(zip(range(self.num_words),list(self.all_words)))

        # 2. convert to better data format
        # we also count the frequency of words while doing this
        list_all_words = []
        get_word_key = lambda x: self.word_to_int[x]
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    mapped_words = map(get_word_key, snippet['unigramList'])
                    data_point = self.data_point_t(mapped_words, snippet['score'], snippet['ID'])
                    self.data.append(data_point)
                    list_all_words.append(mapped_words)
        
        flattend_list = [item for sublist in list_all_words for item in sublist]
        self.word_frequencies = Counter(flattend_list)
    
    def prune_words(self):
        '''
            get top highest dims or threshold by freq
        '''
        if self.dim > 0:
            best_keys = sorted(self.word_frequencies, key=self.word_frequencies.get, reverse=True)[:self.dim]
            self.word_frequencies = {w:self.word_frequencies[w] for w in best_keys}
            pdb.set_trace()
        elif self.freq > 0:
            self.word_frequencies = {w:f for w,f in self.word_frequencies.iteritems() if f>self.freq}

class feature_vector():
    '''
    constructs a feature vector from word_freq data
    '''
    def __init__(self):
        pd = process_data(200, -4)

fv = feature_vector()
