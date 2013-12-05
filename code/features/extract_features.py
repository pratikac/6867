"""
    This script performs feature extraction on positive and negative corpora. 
"""
import feature_representations
import sys

snippet_file_name = '../process/snippets.jl'
feature_file_name = 'training_data.jl'

# Word frequency method 
if sys.argv[1] == 'WordFrequency':
    featureExtractor = feature_representations.WordFrequency()

# Word presence method 
if sys.argv[1] == 'WordPresence':
    featureExtractor = feature_representations.WordPresence()

# Word frequency based on information gain
if sys.argv[1] == 'InformationGain':
    featureExtractor = feature_representations.InformationGain()

# Word frequency based on gain ratio
if sys.argv[1] == 'GainRatio':
    featureExtractor = feature_representations.GainRatio()

# Word frequency based on gain ratio
if sys.argv[1] == 'TFIDF':
    featureExtractor = feature_representations.TFIDF()

featureExtractor.readJSON(snippet_file_name)
featureExtractor.get_F()
featureExtractor.prune_features()
featureExtractor.gen_f_vectors()
featureExtractor.write_f_vectors(feature_file_name)

