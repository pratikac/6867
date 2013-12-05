import json
import numpy as np
from scipy.sparse import coo_matrix

class process_file():
    '''
    separates positive and negative
    '''
    
    def __init__(self, dim=200, fname):
        self.dim = dim
        self.fname = fname
    
    def get_words():
        
        # 1. all_words
        all_words = set()
        num_documents = 0
        with open(self.fname, 'r') as file:
            for line in file:
                snippet = json.loads(line)
                all_words.update(snippet['unigramList'])
                num_documents += 1
        
        num_words = len(all_words)
        self.word_to_int = dict(zip(list(all_words), range(num_words)))
        self.int_to_word = dict(zip(range(num_words),list(all_words)))
    
    def compute_tf_idf():
        # 2. calculate tf, idf
        row,col = [],[]
        count = 0
        lambda_word_to_int = lambda x: self.word_to_int[x]
        with open(self.fname, 'r') as file:
            for line in file:
                snippet = json.loads(line)
                words = map(lambda_word_to_int, snippet['unigramList'])
                col += words
                row += [count for i in xrange(len(words))]
                count += 1
        M = coo_matrix((np.ones(len(row)), (np.array(row),np.array(col))), 
                       shape=(num_documents, num_words), dtype=np.int8).todense()
        
        # is this correct?
        tmp1 = M.sum(axis=0)[0].tolist()[0]   # row-wise sum, i.e, #docs per word
        idf = {w:np.log(float(num_documents)/(1.0+tmp1[w])) for w in self.word_to_int}
        tf = {w:tmp1[w] for w in self.word_to_int}
        self.tf_idf = {w:tf[w]*idf[w] for w in self_word_to_int}
    
    def prune_words():
        best_keys = sorted(tf_idf, key=tf_idf.get, reverse=True)[:self.dim]
        self.words = {w:self.tf_idf[w] for w in best_keys}
        
        num_words = len(self.words)
        word_to_index = dict(zip(self.words.keys(), range(num_words)))
        index_to_word = dict(zip(range(num_words), self.words.keys()))

        lambda_word_to_int = lambda x: self.word_to_int[x]
        with open(self.fname, 'r') as file:
            for line in file:
                snippet = json.loads(line)
                words = map(lambda_word_to_int, snippet['unigramList'])
                


class gaussian_process():
    def __init__(self):
        pos_words = process_file(100, '../process/positive.jl')
        neg_words = process_file(100, '../process/negative.jl')
        
        
    def 
        
        
        



        
