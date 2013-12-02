import numpy as np
from math import log, sqrt
import cPickle as pickle
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.cross_validation import cross_val_score
from sklearn import cross_validation

user_groups = {}
group_users = {}
edges = {}
train = {}
test = {}
neighbors = {}

features = []
labels = []

def read_edges(fname):
    edat = np.loadtxt(fname, delimiter=',', dtype=np.int, skiprows=1)
    for e in edat:
        edges[e[0]] = (e[1], e[2])

def read_groups(fname):
    for line in open(fname):
        line = line.rstrip('\n').split(', ')
        id = int(line[0])
        groups = []
        if len(line) > 1:
            groups= map(lambda x: int(x[1:-1]), line[1:])
        user_groups[id] = groups
        
        if len(groups) > 0:
            for g in groups:
                if not g in group_users:
                    group_users[g] = []
                group_users[g].append(id)

def read_train(fname):
    tdat = np.loadtxt(fname, delimiter=',', dtype=np.int, skiprows=1)
    for t in tdat:
        eid = t[0]
        train[eid] = t[1]
        u1,u2 = edges[eid]
        if not u1 in neighbors:
            neighbors[u1] = []
        if not u2 in neighbors:
            neighbors[u2] = []
        if t[1] > 0:
            neighbors[u1].append(u2)
            neighbors[u2].append(u1)

def read_test(fname):
    tedat = np.loadtxt(fname, delimiter=' , ', dtype=np.int, usecols=(0,), skiprows=1)
    for t in tedat:
        test[t] = None

def write_submission(fname, predict):
    fp = open(fname, 'w')
    fp.write('id , friends\n')
    for key in predict:
        fp.write(str(key) + ' , ' + str(predict[key]) +'\n') 
    fp.close()


def create_feature_vector(eid):
    '''
    build feature vectors based on group similarity and neighbor similarity 
    '''
    u1,u2 = edges[eid]
    g1,g2 = set(user_groups[u1]), set(user_groups[u2])
    n1, n2 = set(), set()
    if u1 in neighbors:
        n1 = set(neighbors[u1])
    if u2 in neighbors:
        n2 = set(neighbors[u2])

    g1ig2 = g1.intersection(g2)
    g1ug2 = g1.union(g2)
    n1in2 = n1.intersection(n2)
    n1un2 = n1.union(n2)

    gnu1 = g1
    for nu1 in n1:
        gnu1.intersection(gnu1, user_groups[nu1])
    gnu2 = g2
    for nu2 in n2:
        gnu2.intersection(gnu2, user_groups[nu2])
    lgnu1ignu2 = len(gnu1.intersection(gnu2))
    lgnu1, lgnu2 = len(gnu1), len(gnu2)

    lg1, lg2, lg1ig2, lg1ug2 = len(g1), len(g2), len(g1ig2), len(g1ug2)
    ln1, ln2, ln1in2, ln1un2 = len(n1), len(n2), len(n1in2), len(n1un2)
    ngroups = len(group_users.keys())
    nusers = len(user_groups.keys())

    if (not lg1 == 0) and (not lg2 == 0):
        prod = lg1*lg2
    else:
        prod = -1000

    ad_ad_s = 0
    avg_s = 0
    for g in g1ig2:
        ad_ad_s += 1/float(len(group_users[g]))
        avg_s += len(group_users[g])
    if lg1ig2 > 0:
        avg_s = avg_s/float(len(g1ig2))
    
    if lg1ug2 == 0:
        jaccardg = 1
    else:
        jaccardg = lg1ig2/float(lg1ug2)
    
    if ln1un2 == 0:
        jaccardn = 1
    else:
        jaccardn = ln1in2/float(ln1un2)
    
    alpha = 0.5
    return [(lg1 + alpha*lgnu1)/float(ngroups), (lg2 + alpha*lgnu2)/float(ngroups), (ln1+ln2)/float(nusers), 
            prod/float(ngroups*ngroups), lg1ig2/float(ngroups), \
            lgnu1ignu2/float(ngroups), ln1in2/float(nusers), jaccardg, jaccardn, ad_ad_s]

def preprocess():
    for eid in train:
        key = create_feature_vector(eid)
        features.append(key)
        labels.append(train[eid])
        
def run_train(clf):
    true_positive = 0
    false_positive = 0
    errors = 0
    for eid in train:
        key = create_feature_vector(eid)
        label = train[eid]
        pred = clf.predict(key)[0]
        if not label == pred:
            errors += 1
        if label and pred:
            true_positive += 1
        if (not label) and pred:
            false_positive += 1

    print "total: ", len(train.keys()), " tpos: ", true_positive, " fpos: ", \
            false_positive, " errors: ", errors

def run_test(clf):
    predictions = {}
    for eid in test:
        key = create_feature_vector(eid)
        pred = clf.predict(key)[0]
        predictions[eid] = pred
    return predictions

def run_cross_validation(clf):
    for i in xrange(5):
        X_train, X_test, y_train, y_test = \
                cross_validation.train_test_split(features, labels, test_size=0.5, random_state=3)
        clf.fit(X_train, y_train)
        print clf.score(X_test, y_test)
    
if 0:
    read_edges('edge_names.csv')
    read_groups('features.txt')
    read_train('train.csv')
    read_test('test.csv')
    preprocess()
    pickle.dump((user_groups, group_users, edges, neighbors, features, labels, train, test), open('preprocess.pkl','wb'))
else:
    user_groups, group_users, edges, neighbors, features, labels, train, test = pickle.load(open('preprocess.pkl','rb'))
    

def run_svm():
    clf = svm.SVC(kernel='rbf', gamma=5, C=200)
    return clf

def run_boosting():
    clf = RandomForestClassifier(n_estimators=20)
    #clf = AdaBoostClassifier(n_estimators=10)
    return clf

clf1 = run_svm()
clf2 = run_boosting()
if 0:
    run_cross_validation(clf)
else:
    #run_train(clf)
    clf1.fit(features, labels)
    clf2.fit(features, labels)
    print "Finished training"

    predictions1 = run_test(clf1)
    predictions2 = run_test(clf2)
    predictions = {}
    for k in predictions1:
        p1 = predictions1[k]
        p2 = predictions2[k]
        if p1*p2 > 0:
            predictions[k] = p1
        else:
            predictions[k] = int((0.3*p1 + 0.7*p2) > 0.5)
    print "Finished predictions"
    write_submission('mypredict.csv', predictions)
