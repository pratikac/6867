from get_features import *


class gaussian_process(): 
    
    def __init__(self, dim, freq, tfidf):
        pd = process_data(dim, freq, tfidf)
        
        self.features = []
        self.labels = []
        self.int_to_eng_words = {}

        self.pos_features, self.neg_features = [], []
        self.pos_labels, self.neg_labels = [], []

        self.word_freq = pd.word_frequencies
        self.num_words = len(self.word_freq)
        self.word_to_index = dict(zip(self.word_freq.keys(), range(self.num_words)))
        self.index_to_word = dict(zip(range(self.num_words), self.word_freq.keys()))
        for index in range(self.num_words):
            self.int_to_eng_words[index] = pd.int_to_word[self.index_to_word[index]]

        for dp in pd.data:
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

    def predict(self, z):
        C = 1
        gamma = 1
        theta = 1
        hamming_dist = lambda x,y : np.sum(np.abs(x-y))
        p_pos = sum(np.array([np.exp(-C*gamma*hamming_dist(z,fv)) for fv in self.pos_features]))
        p_neg = sum(np.array([np.exp(-C*gamma*hamming_dist(z,fv)) for fv in self.neg_features]))
        
        if p_neg <1e-10:
            return 1
        ratio  = p_pos/p_neg
        if ratio > theta:
            return 1
        else:
            return -1

gp = gaussian_process(200, -1, 1)
predictions = []
for fv in gp.neg_features:
    t1 = gp.predict(fv)
    predictions.append(t1)
    print t1

tmp1 = np.array(predictions)
print np.sum(np.where(tmp1 > 0))/float(len(predictions)) 
