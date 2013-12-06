# Terrible hack ... just absolutely awful
import imp
feature_representations = imp.load_source('feature_representations', '../features/feature_representations.py')
from feature_representations import *
from run_learners import *
import cPickle as pickle 
import json

testDataFileName = '../stream/test_data.json'

def test_vector(f):
    ## Feature Vector construction
    t_vector = []
    lat_long = []
    snippetIDs = []
    with open(testDataFileName, 'r') as snippetFile:
        for line in snippetFile:
            snippet = json.loads(line)
            words_in_snippet = snippet['unigramList']
            word_presence = [1 if f.chosen_ngrams[i] in words_in_snippet else 0 for i in range(len(f.chosen_ngrams)) ]
            if all(x == 0 for x in word_presence):
                continue

            t_vector.append(word_presence)
            lat_long.append([snippet['lat'], snippet['long']])
            snippetIDs.append(snippet['ID'])

    return (t_vector, lat_long, snippetIDs)

def write_predicted_sentiment(f, a, yp):
    outputFileName = 'predictions_'+f.__class__.__name__+'_'+a.__name__+'.json'
    with open(outputFileName, 'w') as outFile:
        for point in range(len(yp)):
            outputJSON = {'sentiment': yp[point], 'ID': f.t_data['ID'][point], 'lat': f.t_data['lat_long'][point][0] , 'long': f.t_data['lat_long'][point][1], 't_vector': f.t_data['t_vector'][point]}
            outFile.write(json.dumps(outputJSON)+"\n")


# construct algorithms
algorithms = [run_svm, run_pca, run_adaboost, run_naive_bayes]

create_features = 1
features = []

if create_features:
    
    # init features
    wf = WordFrequency(nDim = 200)
    ig = InformationGain(nDim = 200)
    gr = GainRatio(nDim = 200)
    tfidf = TFIDF(200, -1, 1)

    # construct features
    features = [wf, ig, gr, tfidf]
    count = 0
    for feature in features:
        feature.readJSON('../process/snippets.jl')
        feature.get_F()
        feature.prune_features()
        feature.gen_f_vectors()
        (t_vector, lat_long, snippetIDs) = test_vector(feature)
        feature.t_data = {'t_vector': t_vector, 'lat_long': lat_long, 'ID': snippetIDs}
        
        count += 1
        print count
    pickle.dump(features, open('all_features.pkl','wb'))
else:
    features = pickle.load(open('all_features.pkl','rb'))

def run_all_tests():
    for feature in features:
        X, y, t = feature.f_vector, feature.scores, feature.t_data['t_vector']
        for alg in algorithms:
            results = alg(X,y,t)
            print feature.__class__.__name__, alg.__name__, results[0:2]
            write_predicted_sentiment(feature, result[2])

def run_one_test(feature, alg):
    X, y, t = feature.f_vector, feature.scores, feature.t_data['t_vector']
    results = alg(X, y, t)
    print feature.__class__.__name__, alg.__name__, results[0:2]
    write_predicted_sentiment(feature, alg, results[2])

run_one_test(gr,run_svm)
#run_all_tests()
