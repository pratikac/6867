from run_learners import *
import cPickle as pickle 
import sys


# construct algorithms
algorithms = [run_svm, run_pca, run_adaboost, run_naive_bayes]

create_features = 1
features = []

if create_features:
    
    # init features
    wf= WordFrequency(nDim=200)
    ig = InformationGain(nDim=200)
    gr = GainRatio(nDim=200)
    tfidf = TFIDF(200,-1,1)

    # construct features
    features = [wf, ig, gr, tfidf]
    count = 0
    for feature in features:
        feature.readJSON('../process/snippets.jl')
        feature.get_F()
        feature.prune_features()
        feature.gen_f_vectors()
        count += 1
        print count
    pickle.dump(features, open('all_features.pkl','wb'))
else:
    features = pickle.load(open('all_features.pkl','rb'))

def run_all_tests():
    for feature in features:
        X, y = feature.f_vector, feature.scores
        for alg in algorithms:
            print feature.__class__.__name__, alg.__name__, alg(X,y)

def run_one_test(feature, alg):
    for f in feature:
        for a in alg:
            X, y = f.f_vector, f.scores
            print f.__class__.__name__, a.__name__, a(X,y)

run_one_test(features, [algorithms[2]])
#run_all_tests()
