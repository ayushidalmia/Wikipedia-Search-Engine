Wikipedia-Search-Engine
========================

This repository consists of the mini project done as part of the course Information Retrieval and Extraction - Spring 2014. The course was instructed by [Dr. Vasudeva Varma](http://faculty.iiit.ac.in/~vv/Home.html). 

##Requirement
Python 2.6 or above

Python libraries:

* Porter Stemmer
* XML Parser

##Problem
The mini project involves building a search engine on the Wikipedia Data Dump without using any external index. For this project we use the data dump of 2013 of size 43 GB. The search results returns in real time. Multi word and multi field search on Wikipedia Corpus is implemented. SAX Parser is used to parse the XML Corpus. After parsing the following morphological operations are implemented:

* Casefolding: Casefolding is easily done.
* Tokenisation: Tokenisation is done using regular expressions.
* Stop Word Removal: Stop words are removed by referring a stop word list.
* Stemming: Using an externalFor stemming, a python library PyStemmer is used.

The index, consisting of stemmed words and posting list is build for the corpus after performing the above operations along with the title and the unique mapping I have used for each document. Thus the document id of the wikipedia page is ignored. This helps in reducing the size as the document id do not begin with single digit number in the corpus. Since the size of the corpus will not fit into the main memory several index files are generated. Next, these index files are merged using K-Way Merge along with creating field based indices files.

For example, index0.txt, index1.txt, index2.txt are generated. These files may contain the same word. Hence, K Way Merge is applied and field based files are generated along with their respective offsets. These field based files are generated using multi-threading. This helps in doing multiple I/O simultaneously. Along with this the vocabulary file is also generated.

Along with these I have also stored the offsets of each of the field files. This reduces the search time to O(logm * logn) where m is the number of words in the vocabulary file and m is the number of words in the largest field file.

The src folder contains the following files:

###Main Functions:

* wikiIndexer.py
This function takes as input the corpus and creates the entire index in field separated manner. Along with the field files, it also creates the offsets for the same. It also creates a map for the title and the document id along with its offset. Apart from this it also creates the vocabulary List

In order to run this code run the following:
**python wikiIndexer.py ./sampleText ./outputFolderPath**

* search.py
This function takes as input the query and returns the top ten results from the Wikipedia corpus.

In order to run this code run the following:
**python search.py ./outputFolderPath**

###Helper Functions:

* textProcessing.py 
This helper function does all the preprocessing. It acts as helper for search.py, wikiIndexer.py

* fileHandler.py
This function does all the file preprocessing. It acts as helper for wikiIndexer.py