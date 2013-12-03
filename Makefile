# This makefile runs all the codes needed for this project
# 

PROJECT = sentiment_analysis
TRAINING_DATA = FML.jl LML.jl MLIA.jl MLIG.jl

$(TRAINING_DATA): 
	cd bitchySites/ &&\
	echo `pwd` &&\
	python scrapeTrainingData.py &&\
	sort -u LML.jl > LML_uniq.jl &&\
	mv LML_uniq.jl LML.jl 


all: $(PROJECT)


$(PROJECT): $(TRAINING_DATA) 


clean:
	rm -f bitchySites/*.jl 

fromscratch: clean all
