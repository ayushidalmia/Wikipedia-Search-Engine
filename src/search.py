#This file enables search on Wikipedia corpus. It takes as input the query and returns the top ten links.

from textProcessing import tokenise,stopWords,stemmer
from collections import defaultdict
import threading
import sys
import bz2
import re
import math

offset=[]

def ranking(results, documentFreq, numberOfFiles):                                                      #rank the results obtained

    listOfDocuments=defaultdict(float)
    
    for key in documentFreq:
        documentFreq[key]= math.log((float(documentFreq[key])/float(numberOfFiles-1)))
        
    for word in results:
        fieldWisePostingList= results[word]
        for key in fieldWisePostingList:
            if len(key)>0:
                field=key
                postingList=fieldWisePostingList[key]
                if key=='t':
                    factor=0.3
                if key=='b':
                    factor=0.3
                if key=='i':
                    factor=0.2
                if key=='c':
                    factor=0.1
                if key=='e':
                    factor=0.1
                for i in range(0,len(postingList),2):
                    listOfDocuments[postingList[i]]+=float(postingList[i+1])
                
    return listOfDocuments

def findFileNumber(low,high,offset,pathOfFolder,word,f):                                                    #Binary Search on offset
    while low<high:
        mid=(low+high)/2
        f.seek(offset[mid])
        testWord = f.readline().strip().split(' ')
        if word==testWord[0]:
            return testWord[1:], mid  
        elif word>testWord[0]:
            low=mid+1
        else:
            high=mid-1
    return [],-1

def findFileList(fileName,fileNumber,field,pathOfFolder,word,fieldFile):                                    #Find posting list
    fieldOffset=[]
    tempdf= [] 
    offsetFileName=pathOfFolder+'\\o'+field+fileNumber+'.txt'
    with open(offsetFileName,'rb') as fieldOffsetFile:
        for line in fieldOffsetFile:
            offset, docfreq = line.strip().split(' ')
            fieldOffset.append(int(offset))
            tempdf.append(int(docfreq))
    fileList, mid = findFileNumber(0,len(fieldOffset),fieldOffset,pathOfFolder,word,fieldFile)
    return fileList, tempdf[mid]

def queryMultifield(queryWords, listOfFields,pathOfFolder,fVocabulary):                                         #Deal with multifield query
    fileList=defaultdict(dict)
    df={}
    for i in range(len(queryWords)):
        word=queryWords[i]
        key=listOfFields[i]
        returnedList, mid= findFileNumber(0,len(offset),offset,sys.argv[1],queryWords[0],fVocabulary)
        if len(returnedList)>0:
            fileNumber = returnedList[0]
            fileName= pathOfFolder+'\\'+key+str(fileNumber)+'.bz2'
            fieldFile=bz2.BZ2File(fileName,'rb')
            returnedList, docfreq= findFileList(fileName,fileNumber,key,pathOfFolder,word,fieldFile)
            fileList[word][key] = returnedList
            df[word]=docfreq
    return fileList,df
            
    
def querySimple(queryWords, pathOfFolder, fVocabulary):                                                         #Deal with single word query
    fileList=defaultdict(dict)
    df={}
    listOfField=['t','b','i','c','e']
    for word in queryWords:
        returnedList, _= findFileNumber(0,len(offset),offset,sys.argv[1],word,fVocabulary)
        if len( returnedList)>0:
            fileNumber = returnedList[0]
            df[word] = returnedList[1]
            for key in listOfField:
                fileName= pathOfFolder+'\\\\'+key+str(fileNumber[0])+'.bz2'
                fieldFile=bz2.BZ2File(fileName,'rb')
                returnedList, _ = findFileList(fileName,fileNumber[0],key,pathOfFolder,word,fieldFile)
                fileList[word][key] = returnedList
    return fileList,df

def main():

    
    if len(sys.argv)!= 2:                                             #check arguments
        print "Usage :: python wikiIndexer.py pathOfFolder"
        sys.exit(0)
     
   
    with open(sys.argv[1]+'\\offset.txt','rb') as f:
        for line in f:
            offset.append(int(line.strip()))
            
    titleOffset=[]
    with open(sys.argv[1]+'\\titleoffset.txt','rb') as f:
        for line in f:
            titleOffset.append(int(line.strip()))
    
    while True:
        query=raw_input()                                                               #Take raw query
        flag=0
        fVocabulary = open(sys.argv[1]+'\\vocabularyList.txt','r')
        if re.search(r'[t|b|c|e|i]:',query[:2]):
            flag=1
            queryWords=query.strip().split(' ')
            listOfFields=[]
            temp=[]
            for key in queryWords:
                listOfFields.append(key[:1])
                temp.append(key[2:])
            key=stopWords(temp)
            temp=stemmer(key)
            results, documentFrequency = queryMultifield(temp, listOfFields, sys.argv[1],fVocabulary)
        else:
            queryWords=tokenise(query)
            queryWords=stopWords(queryWords)
            queryWords=stemmer(queryWords)
            results, documentFrequency = querySimple(queryWords, sys.argv[1],fVocabulary)
            
        f=open(sys.argv[1]+'\\numberOfFiles.txt','r')
        numberOfFiles=int(f.read().strip())
        f.close()

        results = ranking(results, documentFrequency,numberOfFiles)
        titleFile=open(sys.argv[1]+'\\title.txt','rb')
        dict_Title={}

        for key in sorted(results.keys()):                                                                  #find top ten links
            title, _ = findFileNumber(0,len(titleOffset),titleOffset,sys.argv[1],key,titleFile)
            dict_Title[key] = ' '.join(title)
        
        if len(results)>0:
            results = sorted(results, key=results.get, reverse=True)
            if len(results)>10:
                results=results[:10]
            print results[0]
            for key in results:
                print dict_Title[key]
        else:
            print "Phrase Not Found"
      
    
if __name__ == "__main__":                                            #main
    main()
    
   
