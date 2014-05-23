#This module takes as input the xml file and returns the posting list for the same.
#The index file generated is used by search.py for querying

import xml.sax.handler                                                  #modules
from textProcessing import processText,processTitle
from fileHandling import writeIntoFile, mergeFiles
from collections import defaultdict
import sys
import timeit

index=defaultdict(list)
count = 0
countFile=0
dict_Id={}
offset = 0

class WikiHandler(xml.sax.handler.ContentHandler):                     #SAX Parser
  
  flag=0
  
  def createIndex(self, title, text, infoBox, category, externalLink):    #add tokens generated to index

    global index
    global dict_Id
    global countFile
    global offset
    global count
    
    vocabularyList= list(set(title.keys()+text.keys()+infoBox.keys()+category.keys()+externalLink.keys()))
    t=float(len(title))
    b=float(len(text))
    i=float(len(infoBox))
    c=float(len(category))
    e=float(len(externalLink))
    for key in vocabularyList:
      string= str(count)+' '
      try:
        string+=str(round(title[key]/t,4))+' '
      except ZeroDivisionError:
        string+='0.0 '
      try:
        string+=str(round(text[key]/b,4))+' '
      except ZeroDivisionError:
        string+='0.0 '
      try:
        string+=str(round(infoBox[key]/i,4))+' '
      except ZeroDivisionError:
        string+='0.0 '
      try:
        string+=str(round(category[key]/c,4))+' '
      except ZeroDivisionError:
        string+='0.0 '
      try:
        string+=str(round(externalLink[key]/e,4))
      except ZeroDivisionError:
        string+='0.0'
      index[key].append(string)       

    count+=1
    if count%5000==0:
      print count
      offset = writeIntoFile(sys.argv[2], index, dict_Id, countFile,offset)
      index=defaultdict(list)
      dict_Id={}
      countFile+=1
      
  def __init__(self):                                                 #initialisation          
    self.inTitle = 0
    self.inId=0
    self.inText=0
 
  def startElement(self, name, attributes):                           #Start Tag
    if name == "id" and WikiHandler.flag==0:                          #Start Tag: Id
      self.bufferId = ""
      self.inId = 1        
      WikiHandler.flag=1
    elif name == "title":                                             #Start Tag: Title
      self.bufferTitle = ""
      self.inTitle = 1
    elif name =="text":                                               #Start Tag:Body Text
      self.bufferText = ""
      self.inText = 1
        
  def characters(self, data):                                         #Read Text
    global count
    global dict_Id
    if self.inId and WikiHandler.flag==1:                             #Read Text: Id
        self.bufferId += data
    elif self.inTitle:                                                #Read Text: Title
        self.bufferTitle += data
        dict_Id[count]=data.encode('utf-8')
    elif self.inText:                                                 #Read Text: Body Text
        self.bufferText += data 
        
  def endElement(self, name):                                         #End Tag
    if name == "title":                                               #End Tag: Title
      WikiHandler.titleWords=processTitle(self.bufferTitle)           #Parse Title
      self.inTitle = 0
        
    elif name == "text":                                              #End Tag: Body Text
      WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords=processText(self.bufferText)              #Parse Body Text
      WikiHandler.createIndex(self, WikiHandler.titleWords, WikiHandler.textWords, WikiHandler.infoBoxWords, WikiHandler.categoryWords, WikiHandler.externalLinkWords)
      self.inText = 0
        
    elif name == "id":                                                #End Tag: Id
      self.inId = 0
        
    elif name == "page":                                              #End Tag: Page
      WikiHandler.flag=0
    

def main():

    global offset
    global countFile
    if len(sys.argv)!= 3:                                             #check arguments
        print "Usage :: python wikiIndexer.py sample.xml /output"
        sys.exit(0)
  
    parser = xml.sax.make_parser(  )                                  #SAX Parser
    handler = WikiHandler(  )
    parser.setContentHandler(handler)
    parser.parse(sys.argv[1])
    with open(sys.argv[2]+'//numberOfFiles.txt','wb') as f:
      f.write(str(count))
    
    offset = writeIntoFile(sys.argv[2], index, dict_Id, countFile,offset)
    countFile+=1
    mergeFiles(sys.argv[2], countFile)

    titleOffset=[]
    with open(sys.argv[2]+'//title.txt','rb') as f:
      titleOffset.append('0')
      for line in f:
        titleOffset.append(str(len(line)))
    titleOffset = titleOffset[:-1]

    with open(sys.argv[2]+'//titleoffset.txt','wb') as f:
      f.write('\n'.join(titleOffset))
    
if __name__ == "__main__":                                            #main
    start = timeit.default_timer()
    main()
    stop = timeit.default_timer()
    print stop - start
