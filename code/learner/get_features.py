import json, pdb
from collections import Counter, namedtuple

class word_freq:
    def __init__(self, dim=200):
        self.dim = dim
        self.words = set()

        #   words : set of words
        #   score, id : score, id
        self.data_point_t = namedtuple('data', ['words', 'score', 'id'])
        self.data = []

    def get_all_words(self):
        fnames = ['../process/positive.jl', '../process/negative.jl']
        
        # 1. create set of all words, all_words is a dict with key = word, value = int
        all_words = set()
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    all_words.update(snippet['unigramList'])
        
        word_to_int = dict(zip(list(all_words), range(len(all_words))))
        int_to_word = dict(zip(range(len(all_words)),list(all_words)))

        # 2. convert to better data format
        get_word_key = lambda x: word_to_int[x]
        for fn in fnames:
            with open(fn, 'r') as file:
                for line in file:
                    snippet = json.loads(line)
                    data_point = self.data_point_t(map(get_word_key, snippet['unigramList']), snippet['score'], snippet['ID'])
                    self.data.append(data_point)
        
        pdb.set_trace()
        
        # 3. create counts all for data-points
        
        

wf = word_freq()
wf.get_all_words()

