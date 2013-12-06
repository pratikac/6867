from get_features import *


class gaussian_process(): 
    
    def __init__(self, dim, freq, tfidf):
        self.pd = process_data(dim, freq, tfidf)
        
        self.features = []
        self.labels = []
        self.int_to_eng_words = {}

        self.pos_features, self.neg_features = [], []
        self.pos_labels, self.neg_labels = [], []

        self.word_freq = self.pd.word_frequencies
        self.num_words = len(self.word_freq)
        self.word_to_index = dict(zip(self.word_freq.keys(), range(self.num_words)))
        self.index_to_word = dict(zip(range(self.num_words), self.word_freq.keys()))
        for index in range(self.num_words):
            self.int_to_eng_words[index] = self.pd.int_to_word[self.index_to_word[index]]

        for dp in self.pd.data:
            z = self.get_bitmap(dp[0])
            self.features.append(z)
            self.labels.append(dp[1])
            if dp[1] > 0:
                self.pos_labels.append(dp[1])
                self.pos_features.append(z)
            else:
                self.neg_labels.append(dp[1])
                self.neg_features.append(z)

    def get_bitmap(self, word_array):
        z = [0 for i in range(self.num_words)]
        for w in word_array:
            z[self.word_to_index[w]] = self.word_freq[w]
        return np.array(z)

    def bootstrap(self, prob):
        randf = np.random.random
        b_pos_features, b_neg_features = [],[]
        b_pos_labels, b_neg_labels = [],[]
        
        for z in zip(self.pos_features, self.pos_labels):
            if randf() > prob:
                b_pos_features.append(z[0])
                b_pos_labels.append(z[1])
        
        for z in zip(self.neg_features, self.neg_labels):
            if randf() > prob:
                b_neg_features.append(z[0])
                b_neg_labels.append(z[1])
        return b_pos_features, b_neg_features, b_pos_labels, b_neg_labels 

    def predict(self, Z):
        C = 1
        gamma = 1
        theta = 1.25
        hamming_dist = lambda x,y : np.sum(np.abs(x-y))
        
        #pf,nf,pl,nl = self.bootstrap(0.3)
        pf,nf,pl,nl = self.pos_features, self.neg_features, self.pos_labels, self.neg_labels
        yp = np.zeros(len(Z))
        for i in xrange(len(Z)):
            z = Z[i] 
            p_pos_array = np.array([np.exp(-C*gamma*hamming_dist(z,fv)) for fv in pf])
            p_neg_array = np.array([np.exp(-C*gamma*hamming_dist(z,fv)) for fv in nf])
            p_pos = np.dot(p_pos_array, np.abs(pl))
            p_neg = np.dot(p_neg_array, np.abs(nl))
            
            pdb.set_trace()
            if p_neg <1e-10:
                yp[i] = 1
            ratio  = p_pos/p_neg
            if ratio > theta:
                yp[i] = 1
            else:
                yp[i] = -1
        return yp

def test():
    gp = gaussian_process(100, -1, 1)
    predictions = []
    for fv in gp.pos_features:
        t1 = gp.predict(fv)
        predictions += t1
        print t1
    tmp1 = np.array(predictions)
    print 'pos_success: ', np.sum(np.where(tmp1 > 0))/float(len(predictions))
    
    predictions = []
    for fv in gp.neg_features:
        t1 = gp.predict(fv)
        predictions += t1
    tmp1 = np.array(predictions)
    print 'neg_success: ', np.sum(np.where(tmp1 < 0))/float(len(predictions))
