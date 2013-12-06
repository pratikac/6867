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
            if randf() < prob:
                b_pos_features.append(z[0])
                b_pos_labels.append(z[1])
        
        for z in zip(self.neg_features, self.neg_labels):
            if randf() < prob:
                b_neg_features.append(z[0])
                b_neg_labels.append(z[1])
        return b_pos_features, b_neg_features, b_pos_labels, b_neg_labels 

    def predict(self, z):
        C = 1e-1
        gamma = 1e-1
        theta = 1.25
        hamming_dist = lambda x,y : np.sum(np.abs(x-y))
        
        #pf,nf,pl,nl = self.bootstrap(0.3)
        pf,nf,pl,nl = self.pos_features, self.neg_features, self.pos_labels, self.neg_labels
        ztile = np.tile(z, (len(pf), 1))
        p_pos = np.sum(np.exp(-C*gamma*np.sum(np.abs(ztile - np.array(pf)), axis=1)))
        ztile = np.tile(z, (len(nf), 1))
        p_neg = np.sum(np.exp(-C*gamma*np.sum(np.abs(ztile - np.array(nf)), axis=1)))
        
        #pdb.set_trace()
        #print p_pos_array.tolist()
        #pdb.set_trace()
        #print p_pos, p_neg
        if p_pos<1e-10:
            return -1
        elif p_neg <1e-10:
            return  1
        else:
            ratio  = p_pos/p_neg
            if ratio > theta:
                return 1
            else:
                return -1

def test():
    gp = gaussian_process(100, -1, 1)
    predictions = []
    pf,nf,pl,nl = gp.bootstrap(0.1)
    print len(pf), len(nf)
    for fv in pf:
        t1 = gp.predict(fv)
        predictions.append(t1)
    tmp1 = np.array(predictions)
    print 'pos_success: ', np.sum(tmp1[np.where(tmp1 > 0)])/float(len(predictions))
    
    predictions = []
    for fv in nf:
        t1 = gp.predict(fv)
        predictions.append(t1)
    tmp1 = np.array(predictions)
    print 'neg_success: ', np.sum(tmp1[np.where(tmp1 < 0)])/float(len(predictions))
