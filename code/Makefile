# This makefile runs all the codes needed for this project
# 

PROJECT = sentiment_analysis
TRAINING_DATA = snippets.jl
POSITIVE_SITES = bitchySites/LML.jl bitchySites/MLIG.jl
NEGATIVE_SITES = bitchySites/FML.jl
SCRAPED_SNIPPETS = bitchySites/FML.jl bitchySites/LML.jl bitchySites/MLIA.jl bitchySites/MLIG.jl

all: $(PROJECT)

$(PROJECT): $(TRAINING_DATA)

snippets: snippets.jl

snippets.jl: positive.jl negative.jl
	cat $? >> snippets.jl &&\
	sort -u positive.jl > positive_uniq.jl &&\
	mv positive_uniq.jl positive.jl

positive.jl: $(POSITIVE_SITES)
	python organize_training_data.py $(subst bitchySites/,,$(subst .jl,,$?)) &&\
	sort -u positive.jl > positive_uniq.jl &&\
	mv positive_uniq.jl positive.jl
	
negative.jl: $(NEGATIVE_SITES)
	python organize_training_data.py $(subst bitchySites/,,$(subst .jl,,$?)) &&\
	sort -u negative.jl > negative_uniq.jl &&\
	mv negative_uniq.jl negative.jl

bitchySites/LML.jl: 
	cd bitchySites/ &&\
	scrapy crawl LML &&\
	sort -u LML.jl > LML_uniq.jl &&\
	mv LML_uniq.jl LML.jl 

bitchySites/FML.jl: 
	cd bitchySites/ &&\
	scrapy crawl FML

bitchySites/MLIA.jl: 
	cd bitchySites/ &&\
	scrapy crawl MLIA

bitchySites/MLIG.jl: 
	cd bitchySites/ &&\
	scrapy crawl MLIG

scrape_all: 
	cd bitchySites/ &&\
	echo `pwd` &&\
	python scrapeTrainingData.py &&\
	sort -u LML.jl > LML_uniq.jl &&\
	mv LML_uniq.jl LML.jl 

clean_snippets:
	rm -f bitchySites/*.jl 

clean_training_data:
	rm -f $(TRAINING_DATA)

clean_all: clean_snippets clean_training_data

from_scratch: clean_all all
