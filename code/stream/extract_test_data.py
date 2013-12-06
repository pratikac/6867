import json

import imp
organize_training_data = imp.load_source('organize_training_data', '../process/organize_training_data.py')
from organize_training_data import *

with open('topsy.json', 'r') as jsonFile:
    with open('test_data.json', 'w') as outputFile:
        for lineNo, line in enumerate(jsonFile):
            tweet = json.loads(line)
            unigramList, bigramList = process_text(tweet['text'])
            latLong = tweet['coordinates']['coordinates']
            longitude = latLong[0]
            lattitude = latLong[1]
            snippetData = {'unigramList': unigramList, 'bigramList': bigramList, 'lat': lattitude, 'long': longitude, 'ID': lineNo}
            outputFile.write(json.dumps(snippetData)+"\n")

