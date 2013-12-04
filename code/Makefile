# This makefile runs all the codes needed for this project
# 

PROJECT = sentiment_analysis
# The feature selection method could be one of:
# 	WordFrequency
# 	WordPresence
# 	GainRatio
# 	InformationGain
FEATURE_SELECTION = WordFrequency

TRAINING_DATA = training_data.jl
POSITIVE_SITES = crawler/LML.jl crawler/MLIG.jl
NEGATIVE_SITES = crawler/FML.jl
SCRAPED_SNIPPETS = crawler/FML.jl crawler/LML.jl crawler/MLIA.jl crawler/MLIG.jl

all: $(PROJECT)

$(PROJECT): $(TRAINING_DATA)

$(TRAINING_DATA): snippets.jl
	python process/extract_features.py $(FEATURE_SELECTION)

snippets.jl: positive.jl negative.jl
	cat $? >> process/snippets.jl &&\
	sort -u process/snippets.jl > process/snippets_uniq.jl &&\
	mv process/snippets_uniq.jl process/snippets.jl

positive.jl: $(POSITIVE_SITES)
	python process/organize_training_data.py $(subst crawler/,,$(subst .jl,,$?)) &&\
	sort -u process/positive.jl > process/positive_uniq.jl &&\
	mv process/positive_uniq.jl process/positive.jl
	
negative.jl: $(NEGATIVE_SITES)
	python process/organize_training_data.py $(subst crawler/,,$(subst .jl,,$?)) &&\
	sort -u process/negative.jl > process/negative_uniq.jl &&\
	mv process/negative_uniq.jl process/negative.jl

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
	echo `pwd` &&\
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
