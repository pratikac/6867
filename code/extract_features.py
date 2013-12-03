"""
    This script performs feature extraction on positive and negative corpora. 
"""
import feature_representations
import sys

snippet_file_name = 'snippets.jl'
feature_file_name = 'training_data.jl'

# Word frequency method 
if sys.argv[1] == 'WordFrequency':
    featureExtractor = feature_representations.WordFrequency()
    featureExtractor.readJSON(snippet_file_name)
    featureExtractor.gen_f_vectors(feature_file_name)

# Word presence method 
if sys.argv[1] == 'WordPresence':
    featureExtractor = feature_representations.WordPresence()
    featureExtractor.readJSON(snippet_file_name)
    featureExtractor.gen_f_vectors(feature_file_name)

