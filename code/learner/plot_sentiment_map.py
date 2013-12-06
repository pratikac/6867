import json
import pylab as plt
from mpl_toolkits.basemap import Basemap



inputDataFile = 'predictions_GainRatio_run_svm.json'

sentiment = []
lattitude = []
longitude = []


with open(inputDataFile, 'r') as inputData:
    for line in inputData:
        data_point = json.loads('line')
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

max_size = 80
for dataPoint in range(len(sentiment)):
    x, y = m(longitude[dataPoint], lattitude[dataPoint])
    m.scatter(x, y, 1, marker='o', color=colorFromSentiment(sentiment[dataPoint]))

plt.savefig('map.pdf')

