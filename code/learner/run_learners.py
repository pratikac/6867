# Terrible hack ... just absolutely awful
import imp
feature_representations = imp.load_source('feature_representations', '../features/feature_representations.py')
from feature_representations import *

import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.decomposition import PCA, KernelPCA
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.tree import DecisionTreeClassifier

from sklearn.cross_validation import cross_val_score
import pdb

def run_svm(X, y, t=None):
    clf = svm.SVC(kernel='rbf',gamma=1.0, C=3)
    clf=clf.fit(X, np.sign(y), sample_weight=np.abs(y))
    
    scores = cross_val_score(clf, X, np.sign(y))
    yp = np.array([clf.predict(x)[0] for x in X])
    success = (yp == np.sign(y)).sum()/float(len(y))
    if t is None: 
        return scores.mean(), success
    else:
        yp = np.array([clf.predict(x)[0] for x in t])
        return scores.mean(), success, yp

def run_decision_tree(X, y, t=None):
    clf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
    yp = np.array([clf.predict(x)[0] for x in X])
    sucess = (yp == np.sign(y)).sum()/float(len(y))
    if t is None: 
        return success
    else:
        yp = np.array([clf.predict(x)[0] for x in t])
        return success, yp

def run_adaboost(X, y, t=None):
    clf = AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), n_estimators=25)
    #clf = AdaBoostClassifier(n_estimators=50)
    clf.fit(X,y)
    
    scores = cross_val_score(clf, X, np.sign(y))
    yp = np.array([clf.predict(x)[0] for x in X])
    success = (yp == np.sign(y)).sum()/float(len(y))
    if t is None: 
        return scores.mean(), success
    else:
        yp = np.array([clf.predict(x)[0] for x in t])
        return scores.mean(), success, yp

def run_pca(X, y, t=None):
    # normalize data
    X = (X-np.mean(X,0))/np.std(X,0)

    pca = PCA(n_components=50)
    X = pca.fit_transform(X)
    
    clf = svm.SVC(kernel='rbf',gamma=1.0, C=3)
    clf=clf.fit(X, np.sign(y), sample_weight=np.abs(y))
    yp = np.array([clf.predict(x)[0] for x in X])
    success = (yp == np.sign(y)).sum()/float(len(y))
    scores = cross_val_score(clf, X, np.sign(y))
    if t is None: 
        return scores.mean(), success
    else:
        yp = np.array([clf.predict(x)[0] for x in t])
        return scores.mean(), success, yp

def run_naive_bayes(X,y,t=None):
    nb = MultinomialNB()
    fitted_nb = nb.fit(X, np.sign(y))
    yp = fitted_nb.predict(X)
    success = (yp == np.sign(y)).sum()/float(len(y))
    scores = cross_val_score(nb, X, np.sign(y))
    if t is None: 
        return scores.mean(), success
    else:
        yp = fitted_nb.predict(t)
        return scores.mean(), success, yp

###################################################################
## Script starts below:
###################################################################

'''
# Import X, y
f = TFIDF(200, -1, 1)
f.readJSON('../process/snippets.jl')
f.get_F()
f.prune_features()
f.gen_f_vectors()

features = f.f_vector
labels = [1 if score > 0 else -1 for score in f.scores]


# Run algorithm
X, y = run_pca(features, labels)
y = np.array(y)
run_svm(X,y)
'''

