#This function does all the file Handling required for creating the index.

import sys
import bz2
import heapq
import os
import operator
from collections import defaultdict
import threading

class writeParallel(threading.Thread):                                                              #Multi Threading , write multiple field files simultaneously
    
    def __init__(self, field, data, offset, countFinalFile,pathOfFolder):
        threading.Thread.__init__(self)
        self.data=data
        self.field=field
        self.count=countFinalFile
        self.offset=offset
        self.pathOfFolder=pathOfFolder
        
    def run(self):
        filename= self.pathOfFolder+'\\'+self.field+str(self.count)
        with bz2.BZ2File(filename+'.bz2', 'wb', compresslevel=7) as f:
            f.write('\n'.join(self.data))
        with open(filename+'.txt', 'wb') as f:
            f.write('\n'.join(self.data))
        filename= self.pathOfFolder+'\\o'+self.field+str(self.count)+'.txt'
        with open(filename, 'wb') as f:
            f.write('\n'.join(self.offset))
    
def writeFinalIndex(data, countFinalFile, pathOfFolder,offsetSize):                                 #Write index after merging
    title=defaultdict(dict)
    text=defaultdict(dict)
    info=defaultdict(dict)
    category=defaultdict(dict)
    externalLink=defaultdict(dict)
    uniqueWords=[]
    offset=[]

    for key in sorted(data.keys()):
        listOfDoc=data[key]
        temp=[]
        flag=0
        for i in range(0,len(listOfDoc),6):
           word=listOfDoc
           docid=word[i]
           if word[i+1]!='0.0':
               title[key][docid]=float(word[i+1])
               flag=1
           if word[i+2]!='0.0':
               text[key][docid]=float(word[i+2])
               flag=1
           if word[i+3]!='0.0':
               info[key][docid]=float(word[i+3])
               flag=1
           if word[i+4]!='0.0':
               category[key][docid]=float(word[i+4])
               flag=1
           if word[i+5]!='0.0':
               externalLink[key][docid]=float(word[i+5])
               flag=1

        if flag==1:
            string = key+' '+str(countFinalFile)+' '+str(len(listOfDoc)/6)
            uniqueWords.append(string)
            offset.append(str(offsetSize))
            offsetSize=offsetSize+len(string)+1
    

    titleData=[]
    textData=[]
    infoData=[]
    categoryData=[]
    externalLinkData=[]

    titleOffset=[]
    textOffset=[]
    infoOffset=[]
    categoryOffset=[]
    externalLinkOffset=[]

    previousTitle=0
    previousText=0
    previousInfo=0
    previousCategory=0
    previousExternalLink=0

    for key in sorted(data.keys()):                                                                     #create field wise Index
        #print key
        if key in title:
            string=key+' '
            sortedField=title[key]
            sortedField = sorted(sortedField, key = sortedField.get, reverse=True)
            for doc in sortedField:
                string+=doc+' '+str(title[key][doc])+' '
            titleOffset.append(str(previousTitle)+' '+str(len(sortedField)))
            previousTitle = len(string)+1
            titleData.append(string)

        if key in text:
            string=key+' '
            sortedField=text[key]
            sortedField = sorted(sortedField, key = sortedField.get, reverse=True)
            for doc in sortedField:
                string+=doc+' '+str(text[key][doc])+' '
            textOffset.append(str(previousText)+' '+str(len(sortedField)))
            previousText+=len(string)+1
            textData.append(string)       

        if key in info:
            string=''
            string+=key+' '
            sortedField=info[key]
            sortedField = sorted(sortedField, key = sortedField.get, reverse=True)
            for doc in sortedField:
                string+=doc+' '+str(info[key][doc])+' '
            infoOffset.append(str(previousInfo)+' '+str(len(sortedField)))
            previousInfo+=len(string)+1
            infoData.append(string)

        if key in category:
            string=key+' '
            sortedField=category[key]
            sortedField = sorted(sortedField, key = sortedField.get, reverse=True)
            for doc in sortedField:
                string+=(doc+' '+str(category[key][doc])+' ')
            categoryOffset.append(str(previousCategory)+' '+str(len(sortedField)))
            previousCategory+=len(string)+1
            categoryData.append(string)

        if key in externalLink:
            string= key+' '
            sortedField=externalLink[key]
            sortedField = sorted(sortedField, key = sortedField.get, reverse=True)
            for doc in sortedField:
                string+=doc+' '+str(externalLink[key][doc])+' '
            externalLinkOffset.append(str(previousExternalLink)+' '+str(len(sortedField)))
            previousExternalLink+=len(string)+1
            externalLinkData.append(string)

    try:
        if os.path.getsize(pathOfFolder+'\\b'+str(countFinalFile)+'.bz2') > 10485760:
            countFinalFile+=1
    except:
        pass

    thread1 = writeParallel('t', titleData, titleOffset, countFinalFile,pathOfFolder)
    thread2 = writeParallel('b', textData, textOffset, countFinalFile,pathOfFolder)
    thread3 = writeParallel('i', infoData, infoOffset, countFinalFile,pathOfFolder)
    thread4 = writeParallel('c', categoryData, categoryOffset, countFinalFile,pathOfFolder)
    thread5 = writeParallel('e', externalLinkData, externalLinkOffset, countFinalFile,pathOfFolder)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    thread5.join()
     
    with open(pathOfFolder+"\\vocabularyList.txt","ab") as f:
      f.write('\n'.join(uniqueWords))
      
    with open(pathOfFolder+"\\offset.txt","ab") as f:
      f.write('\n'.join(offset))
      
    return countFinalFile, offsetSize
        
        

def writeIntoFile(pathOfFolder, index, dict_Id, countFile, titleOffset):                                        
    data=[]                                                                             #write the primary index
    previousTitleOffset=titleOffset
    
    for key in index:
        string= str(key)+' '
        temp=index[key]
        string+=' '.join(temp)
        data.append(string)

    filename=pathOfFolder+'\index'+str(countFile)+'.txt.bz2'                            #compress and write into file
    with bz2.BZ2File(filename, 'wb', compresslevel=9) as f:
        f.write('\n'.join(data))
        
    data=[]
    dataOffset=[]
    for key in dict_Id:
        data.append(str(key)+' '+dict_Id[key])
        dataOffset.append(str(previousTitleOffset))
        previousTitleOffset+=len(str(key)+' '+dict_Id[key])
        
    filename=pathOfFolder+'\\title.txt'
    with open(filename,'ab') as f:
        f.write('\n'.join(data))

    '''filename=pathOfFolder+'\\titleoffset.txt'
    with open(filename,'ab') as f:
        f.write('\n'.join(dataOffset))'''

    return  previousTitleOffset

def mergeFiles(pathOfFolder, countFile):                                                 #merge multiple primary indexes
    listOfWords={}
    indexFile={}
    topOfFile={}
    flag=[0]*countFile
    data=defaultdict(list)
    heap=[]
    countFinalFile=0
    offsetSize = 0
    for i in xrange(countFile):
        fileName = pathOfFolder+'\index'+str(i)+'.txt.bz2'
        indexFile[i]= bz2.BZ2File(fileName, 'rb')
        flag[i]=1
        topOfFile[i]=indexFile[i].readline().strip()
        listOfWords[i] = topOfFile[i].split(' ')
        if listOfWords[i][0] not in heap:
            heapq.heappush(heap, listOfWords[i][0])        

    count=0        
    while any(flag)==1:
        temp = heapq.heappop(heap)
        count+=1
        for i in xrange(countFile):
            if flag[i]:
                if listOfWords[i][0]==temp:
                    data[temp].extend(listOfWords[i][1:])
                    if count==1000000:
                        oldCountFile=countFinalFile
                        countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)
                        if oldCountFile!=  countFinalFile:
                            data=defaultdict(list)
                        
                    topOfFile[i]=indexFile[i].readline().strip()   
                    if topOfFile[i]=='':
                            flag[i]=0
                            indexFile[i].close()
                            os.remove(pathOfFolder+'\index'+str(i)+'.txt.bz2')
                    else:
                        listOfWords[i] = topOfFile[i].split(' ')
                        if listOfWords[i][0] not in heap:
                            heapq.heappush(heap, listOfWords[i][0])
    countFinalFile, offsetSize = writeFinalIndex(data, countFinalFile, pathOfFolder, offsetSize)
   
                
            
            
                    
                
        

