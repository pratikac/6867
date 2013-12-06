from topsy import *
import time
import datetime

def date_to_unix(d):
    return int(time.mktime(datetime.datetime.strptime(d, "%d/%m/%Y %H:%M").timetuple()))

THANKSGIVING_START = date_to_unix("29/11/2013 10:00")
THANKSGIVING_END = date_to_unix("29/11/2013 23:00")

USA_CODE = 225

t = Topsy()
RESOURCE = 'content/bulktweets'

query_terms = { 'limit': 1, 
                'mintime' : THANKSGIVING_START,
                'maxtime' : THANKSGIVING_END,
                'region' : USA_CODE,
                'latlong' : 1,
                'allow_lang' : 'en', 
                'tweet_types' : 'tweet' }

results = t._get(RESOURCE, **query_terms)
