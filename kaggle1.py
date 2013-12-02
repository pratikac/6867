import numpy as np
from math import log
import cPickle as pickle 
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from nltk.stem.wordnet import WordNetLemmatizer
import nltk
import os, re

author_words={}
words_authors={}
edges={}
train={}
test={}
id_author={} #index is the new author id
word_ids={} #index is the new word id
word_id_freq={} #freq of word in all documents combined
coauthors={}

features=[]
labels=[]

def read_features(fname):
    lmtzr=WordNetLemmatizer()
    count = 0
    for line in open(fname,"rb"):
            count += 1
            if count % 1000 == 0:
                print count
            line = line.rstrip('\n').split(', ')
            author_name = line[0][0:-1]
            id = len(id_author.keys())
            id_author[author_name] = id
            if not id in author_words:
                author_words[id] = set()
            
            for item in line[1:]:
                wfreq = item.split(':')
                #print wfreq
                #raw_input()
                freq = int(wfreq[-1])
                unclean_word = wfreq[0][1:-1]
                clean_word = re.sub('[^A-Za-z0-9]+', '', unclean_word).lower()
                keyword = clean_word
                #keyword = lmtzr.lemmatize(clean_word)
                #if keyword in nltk.corpus.stopwords.words('english'):
                #    continue
                
                if not keyword in word_ids:
                    word_id = len(word_ids.keys())
                    word_ids[keyword] = word_id
                    word_id_freq[word_id] = 0
                keyword_frequency = freq
                word_id_freq[word_id] += keyword_frequency
                author_words[id].add(word_id)

                if not word_id in words_authors:
                    words_authors[word_id]=[]
                words_authors[word_id].append(id)
    print "finished"
    raw_input()

def read_edges(fname):
    edat = np.loadtxt(fname,delimiter=',',dtype=np.str, skiprows=1)
    for e in edat:
        edges[int(e[0])]=(id_author[e[1].replace(' ','')],id_author[e[2].replace(' ','')])

def read_train(fname):
    tdat = np.loadtxt(fname, delimiter=',',dtype=np.int, skiprows=1)
    for t in tdat:
        eid = t[0]
        train[eid] = t[1]
        a1,a2= edges[eid]
        if not a1 in coauthors:
            coauthors[a1]=[]
        if not a2 in coauthors:
            coauthors[a2]=[]
        if t[1] > 0:
            coauthors[a1].append(a2)
            coauthors[a2].append(a1)

def read_test(fname):
    tedat = np.loadtxt(fname, delimiter=' , ', dtype=np.int, usecols=(0,), skiprows=1)
    for t in tedat:
        test[t] = None

def write_submission(fname, predict):
    fp=open(fname,'w')
    fp.write('id , coauthors\n')
    for key in predict:
        fp.write(str(key)+' , '+str(predict[key])+'\n')
    fp.close()

def create_feature_vector(eid):
    a1,a2=edges[eid]
    w1,w2=set(author_words[a1]),set(author_words[a2])
    c1,c2=set(),set()

    if a1 in coauthors:
        c1=set(coauthors[a1])
    if a2 in coauthors:
        c2=set(coauthors[a2])

    w1iw2=w1.intersection(w2)
    w1uw2=w1.union(w2)
    c1ic2=c1.intersection(c2)

    lw1,lw2,lw1iw2,lw1uw2=len(w1),len(w2),len(w1iw2),len(w1uw2)
    lc1,lc2,lc1ic2=len(c1),len(c2),len(c1ic2)

    tf1=0
    tf2=0
    idf=0
    tfidf1=0
    tfidf2=0
    metric=0
    avg_c=0
    for w in w1iw2:
        tf1=author_words[a1].count(w)/float(len(author_words[a1]))
        tf2=author_words[a2].count(w)/float(len(author_words[a2]))
        idf=len(id_author)/float(word_id_freq[w])
        tfidf1=tf1*idf
        tfidf2=tf2*idf
        metric+=(tfidf1*tfidf2)/float(tfidf1+tfidf2)
        avg_c+=len(words_authors[w])
    if lw1iw2 > 0:
        avg_c=avg_c/float(lw1iw2)
    if lw1uw2 == 0:
        jaccard=1
    else:
        jaccard=lw1iw2/float(lw1uw2)

    return [lw1, lw2, lc1, lc2, jaccard, metric, avg_c, lw1iw2, lc1ic2]

def preprocess():
    for eid in train:
        key=create_feature_vector(eid)
        features.append(key)
        labels.append(train[eid])

def run_train(clf):
    true_positive=0
    false_positive=0
    errors=0
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
    predictions={}
    for eid in test:
        key=create_feature_vector(eid)
        pred=clf.predict(key)[0]
        predictions[eid]=pred
    return predictions

def run_svm():
    clf = svm.SVC(kernel='rbf',gamma=1.0, C=1.5)
    return clf

#os.nice(-10)
if 0:
    read_features('features.txt')
    print "Finished reading features"
    read_edges('edge_names.csv')
    print "Finished reading edge_names"
    read_train('train.csv')
    print "Finished reading training data"
    
    backup=(features,labels,author_words,words_authors,edges,train, \
            test,id_author, word_ids,word_id_freq,coauthors)
    pickle.dump(backup,open('read_data.pkl','wb'))
else:
    features,labels,author_words,words_authors,edges,train, \
            test,id_author, word_ids,word_id_freq,coauthors = pickle.load(open('read_data.pkl','rb'))
print "Finished reading"

if 0:
    preprocess()
    backup=(features,labels,author_words,words_authors,edges,train, \
            test,id_author, word_ids,word_id_freq,coauthors)
    pickle.dump(backup,open('preprocess.pkl','wb'))
    print "Finished pickling"
else:
    features,labels,author_words,words_authors,edges,train, \
            test,id_author,word_ids,word_id_freq,coauthors=pickle.load(open('preprocess.pkl','rb'))

clf=run_svm()
clf=clf.fit(features,labels)
run_train(clf)
predictions=run_test(clf)
write_submission('mypredict.csv',predictions)
