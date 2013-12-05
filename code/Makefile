# This makefile runs all the codes needed for this project
# 

PROJECT = sentiment_analysis
# The feature selection method could be one of:
# 	WordFrequency
# 	WordPresence
# 	GainRatio
# 	InformationGain
# 	TFIDF
FEATURE_SELECTION = TFIDF

TRAINING_DATA = features/training_data.jl
POSITIVE_SITES = crawler/LML.jl crawler/MLIG.jl
NEGATIVE_SITES = crawler/FML.jl
SCRAPED_SNIPPETS = crawler/FML.jl crawler/LML.jl crawler/MLIA.jl crawler/MLIG.jl

all: $(PROJECT)

features: $(TRAINING_DATA)

$(PROJECT): $(TRAINING_DATA)

$(TRAINING_DATA): process/snippets.jl
	cd features &&\
	python extract_features.py $(FEATURE_SELECTION)

process/snippets.jl: process/positive.jl process/negative.jl
	add_twitter
	cat $? >> process/snippets.jl &&\
	sort -u process/snippets.jl > process/snippets_uniq.jl &&\
	mv process/snippets_uniq.jl process/snippets.jl

add_twitter:
	cd process/ &&\
	python process_twitter.py

process/positive.jl: $(POSITIVE_SITES)
	cd process/ &&\
	python organize_training_data.py $(subst crawler/,,$(subst .jl,,$?)) &&\
	sort -u positive.jl > positive_uniq.jl &&\
	mv positive_uniq.jl positive.jl
	
process/negative.jl: $(NEGATIVE_SITES)
	cd process/ &&\
	python organize_training_data.py $(subst crawler/,,$(subst .jl,,$?)) &&\
	sort -u negative.jl > negative_uniq.jl &&\
	mv negative_uniq.jl negative.jl

crawler/LML.jl: 
	cd crawler/ &&\
	scrapy crawl LML &&\
	sort -u LML.jl > LML_uniq.jl &&\
	mv LML_uniq.jl LML.jl 

crawler/FML.jl: 
	cd crawler/ &&\
	scrapy crawl FML

crawler/MLIA.jl: 
	cd crawler/ &&\
	scrapy crawl MLIA

crawler/MLIG.jl: 
	cd crawler/ &&\
	scrapy crawl MLIG

scrape_all: 
	cd crawler/ &&\
	python scrapeTrainingData.py &&\
	sort -u LML.jl > LML_uniq.jl &&\
	mv LML_uniq.jl LML.jl 

clean_training_data:
	rm -f $(TRAINING_DATA)
	rm -f crawler/*.jl 

clean_snippets:
	rm -f process/*.jl

clean_all: clean_snippets clean_training_data

from_scratch: clean_all all
