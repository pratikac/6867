import json
import pylab as plt
from mpl_toolkits.basemap import Basemap
from numpy.random import rand



inputDataFile = 'predictions_GainRatio_run_svm.json'

sentiment = []
lattitude = []
longitude = []

with open(inputDataFile, 'r') as inputData:
    for line in inputData:
        data_point = json.loads(line)
        sentiment.append(data_point['sentiment'])
        lattitude.append(data_point['lat'])
        longitude.append(data_point['long'])

def colorFromSentiment(sentiment):
    if sentiment > 0:
        return 'g'
    else:
        return 'r'

m = Basemap(llcrnrlon = -119, llcrnrlat=22, urcrnrlon=-64, urcrnrlat=49,
        projection='lcc', lat_1 = 33, lat_2=45, lon_0 = -95, resolution ='c')
m.drawcoastlines()
m.drawstates()
m.drawcountries()

numOriginals = len(sentiment)
numDuplicates = 5
duplicationRadius = 0.2
latScale = 27/5.5
longScale = 55/9.0
lattitudeRange = max(lattitude) - min(lattitude)
predictionAccuracy  = 0.9           # From scores obtained from cross-validation
longitudeScaling = ()

for dataPoint in xrange(numOriginals):
    for i in xrange(numDuplicates):
        newY = lattitude[dataPoint] + 2.0*(0.5 - rand())*duplicationRadius*longScale
        newX = longitude[dataPoint] + 2.0*(0.5 - rand())*duplicationRadius*latScale
        newSentiment = 2.0*(0.5 -int(rand() - predictionAccuracy > 0))*sentiment[dataPoint]

        sentiment.append(newSentiment)
        lattitude.append(newY)
        longitude.append(newX)
        
print sentiment
print len(lattitude)
print len(sentiment)

for dataPoint in xrange(len(sentiment)):
    x, y = m(longitude[dataPoint], lattitude[dataPoint])
    m.scatter(x, y, 10, marker='o', color=colorFromSentiment(sentiment[dataPoint]))

plt.savefig('map.pdf')

