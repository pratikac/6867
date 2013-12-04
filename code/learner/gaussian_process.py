from get_features import *


class gaussian_process(): 
    
    def __init__(self, dim, freq, tfidf):
        pd = process_data(dim, freq, tfidf)
        
        self.features = []
        self.labels = []
        self.int_to_eng_words = {}

        self.pos_features, self.neg_feature = [], []
        self.pos_labels, self.neg_labels = []

        word_freq = pd.word_frequencies
        num_words = len(word_freq)
        word_to_index = dict(zip(word_freq.keys(), range(num_words)))
        index_to_word = dict(zip(range(num_words), word_freq.keys()))
        for index in range(num_words):
            self.int_to_eng_words[index] = pd.int_to_word[index_to_word[index]]

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

    def get_bitmap(word_array):
        z = [0 for i in range(num_words)]
        for w in word_array:
            z[word_to_index[w]] = word_freq[w]
        return np.array(z)

    def predict(word_array):
        z = self.get_bitmap(word_array)
        

