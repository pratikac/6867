from organize_training_data import *


def process_twitter():
    posfname = 'positive.jl'
    negfname = 'negative.jl'
    scrapedfile = '../twitter/training.txt'
    
    with open(posfname, 'a') as posf:
        with open(negfname, 'a') as negf:
           
            with open(scrapedfile,'r') as scrapef:
                count = 0
                for line in scrapef:
                    ls = line.split('\t')
                    unigram,bigram = process_text(ls[1])

                    if len(unigram) == 0:
                        continue

                    score = int(ls[0])
                    if score == 0:
                        score = -1
                    snippet_data = {'unigramList': unigram, 'bigramList': bigram, 'score': score,
                            'ID': str(count)}
                    if score > 0:
                        posf.write(json.dumps(snippet_data)+"\n")
                    else:
                        negf.write(json.dumps(snippet_data)+"\n")
                    
                    #pdb.set_trace()
                    count += 1
                    if count % 100 == 0:
                        print count

if __name__ == "__main__":
    process_twitter()
