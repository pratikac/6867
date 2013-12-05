import json, pdb

def create_cloud():
    pos_text, neg_text = '', ''

    fname = 'snippets_no_twitter.jl'
    with open(fname, 'r') as fp:
        for line in fp:
            snippet = json.loads(line)
            score = snippet['score']
            words = snippet['unigramList']
            if score > 0:
                pos_text += ' '.join(words) + ' '
            else:
                neg_text += ' '.join(words) + ' '

    print neg_text

create_cloud()

        
