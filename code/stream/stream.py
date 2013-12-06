from twython import Twython, TwythonStreamer
import sys
import argparse

APP_KEY='O44I8yRaaJlkUos1m1Moxw'
APP_SECRET='q0kkv8guwFm4PwttMM8grSALpQYXHNE9a91nRz8'

OAUTH_TOKEN= '58444328-XX0bXZO3Nb0SJ0oC651o50SmVfyZXqbf5AFaGJNLS'
OAUTH_TOKEN_SECRET= 'joqKKhvpUA9Dgl6wMCrlMhpvks7xLOaZl0SD7VwAQPxlD'

class MyStreamer(TwythonStreamer):
    def on_success(self, data):
        if 'text' in data:
            print data['text'].encode('utf-8')
        # Want to disconnect after the first result?
        # self.disconnect()

    def on_error(self, status_code, data):
        print status_code, data
        

'''
twitter = Twython(APP_KEY, APP_SECRET)
auth = twitter.get_authentication_tokens()
OAUTH_TOKEN = auth['oauth_token']
OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
import json
#print(json.dumps(twitter.get_user_timeline(screen_name='jonatascd')[0], indent=2))
'''


if __name__ == '__main__':
        
    parser = argparse.ArgumentParser(prefix_chars='@')
    parser.add_argument("@r", nargs = 4, metavar = ('longMin', 'latMin', 'longMax', 'latMax'),
                        help = 'coordinates of rectangular region', type=float,
                        default = None)
    argList = parser.parse_args()
            
    # Requires Authentication as of Twitter API v1.1
    stream = MyStreamer(APP_KEY, APP_SECRET,
                        OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
                        
    usa = [-118.665162,28.304381,-66.546021,49.325122]
    boston = [-71.288323,42.17714,-70.918908,42.531326]
    
    #stream.statuses.filter(track='sachin, tendulkar, cricket, retire')
    locationRectangle = argList.r
    print locationRectangle
    stream.statuses.filter(locations=locationRectangle, languages=['en'])    
    





