"""
    Class definitions for feature extractors
"""
import json
import operator

class WordFrequency:
    def __init__(self, nDim=10000, fMin=4, includeBigrams=False):
        self.snippetFileName = ''
        self.nGramList = []
        self.nGramDictionary = {}
        self.nDim = nDim
        self.fMin = fMin
        self.includeBigrams = includeBigrams
        self.maxFeatures = 0

    def readJSON(self, snippetFileName):
        self.snippetFileName = snippetFileName

    def generate_nGram_list(self):
        nGram_dictionary = {}

        with open(self.snippetFileName, 'r') as snippetFile:
            for line in snippetFile:
                snippet = json.loads(line)


                # Check unigrams with nGramList
                for unigram in snippet['unigramList']:
                    if unigram in nGram_dictionary.keys():
                        nGram_dictionary[unigram] += 1
                    else:
                        nGram_dictionary[unigram] = 1
                
                # Check bigrams with nGramList
                if self.includeBigrams:
                    for bigram in snippet['bigramList']:
                        if bigram in nGram_dictionary.keys():
                            nGram_dictionary[bigram] += 1
                        else:
                            nGram_dictionary[bigram] = 1
            
        # Prune nGramList
        self.nGramDictionary = nGram_dictionary.copy()
        self.maxFeatures = len(self.nGramDictionary.keys())

        pruned_dictionary = { k:v for k, v in self.nGramDictionary.items() if v > self.fMin}
        self.nGramList = [pair[0] for pair in sorted(pruned_dictionary.iteritems(), key=operator.itemgetter(1), reverse=True)[:self.nDim]]
            
            
    def gen_f_vectors(self, featureFileName):
        self.generate_nGram_list()

        with open(self.snippetFileName, 'r') as snippetFile, open(featureFileName, 'w') as outFile:
            for line in snippetFile:
                snippet = json.loads(line)
                fVectorData = {'ID':snippet['ID'], 'score':snippet['score']}
                f_vector = [0.0] * self.nDim

                # Check nGrams from nGramList
                for index, nGram in enumerate(self.nGramList):
                    if nGram in snippet['unigramList'] + snippet['bigramList']:
                        f_vector[index] += 1

                fVectorData['f_vector'] = f_vector
                outFile.write(json.dumps(fVectorData)+"\n")
                

class WordPresence(WordFrequency):
    """
        Count just the presence or absence of the most frequently appearing 
        words in each document.
    """
    def gen_f_vectors(self, featureFileName):
        self.generate_nGram_list()

        with open(self.snippetFileName, 'r') as snippetFile, open(featureFileName, 'w') as outFile:
            for line in snippetFile:
                snippet = json.loads(line)
                fVectorData = {'ID':snippet['ID'], 'score':snippet['score']}
                f_vector = [0.0] * self.nDim

                # Check nGrams from nGramList
                for index, nGram in enumerate(self.nGramList):
                    if nGram in snippet['unigramList'] + snippet['bigramList']:
                        f_vector[index] = 1

                fVectorData['f_vector'] = f_vector
                outFile.write(json.dumps(fVectorData)+"\n")


