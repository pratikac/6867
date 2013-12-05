from get_features import *
from gaussian_process import *


def create_cloud(gp):
    data = gp.pd.data

    pos_text, neg_text='',''
    for dp in data:
        words = [gp.pd.int_to_word[w] for w in dp[0]]
        if dp[1] > 0:
            pos_text += ' '.join(words) + ' '
        else:
            neg_text += ' '.join(words) + ' '
        
    pdb.set_trace()
    
gp = gaussian_process(200, -1, 1)
create_cloud(gp)
