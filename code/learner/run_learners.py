from get_features import *

import numpy as np
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.decomposition import PCA, KernelPCA

from sklearn.cross_validation import cross_val_score
import pdb

def run_svm(X, y):
    clf = svm.SVC(kernel='rbf',gamma=1.0, C=1.5)
    clf=clf.fit(X, y)
    scores = cross_val_score(clf, X, np.array(y))
    #print clf.support_vectors_    
    print scores.mean()

def run_decision_tree(X, y):
    clf = RandomForestClassifier(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
    scores = cross_val_score(clf, X, np.array(y))
    print scores.mean()

def run_adaboost(X, y):
    clf = AdaBoostClassifier(n_estimators=100)
    scores = cross_val_score(clf, X, np.array(y))
    print scores.mean()

def run_pca(X, y):
    #kpca = KernelPCA(kernel='rbf', fit_inverse_transform=True, gamma=10)
    pca = PCA(n_components=10)
    X = pca.fit_transform(X)
    return X, y

fv = feature_vector(200, -1)
features, labels = fv.features, fv.labels

X,y = run_pca(features,labels)
#run_svm(X, y)
#run_decision_tree(X,y)
run_adaboost(X,y)
