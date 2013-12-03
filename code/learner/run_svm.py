from get_features import *

from sklearn import svm
import pdb

def run_svm():
    fv = feature_vector()

    clf = svm.SVC(kernel='rbf',gamma=1.0, C=1.5)
    clf=clf.fit(fv.features,fv.labels)
    print clf.support_vectors_    

run_svm()
