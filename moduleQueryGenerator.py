"""
Created on Tue May 23 17:34:14 2017

@author: Ali Emami
"""


import glob
import pickle
import numpy as np
import nltk
from nltk import *
from corenlp_xml_reader import AnnotatedText as A
import copy
from corenlp import *

from simplejson import loads
import re
from nltk.corpus import wordnet
from itertools import chain

from PyDictionary import PyDictionary
dictionary=PyDictionary()




def main():
	
	#Winograd sentences parsed by CoreNLP, stored as XML files, loaded.an
	listOfXmlFiles=glob.glob('winogradXML/*xml')
	listOfXmlFiles.sort()
	listOfXmlFiles=listOfXmlFiles
	numberOfXmlFiles= len(listOfXmlFiles)
	    
	allSentences=[]

	allSentences=[]

	numberOfXmlFiles= len(listOfXmlFiles) 
	scheme=[0 for _ in range(numberOfXmlFiles)]
	lexicalScheme=[0 for _ in range(numberOfXmlFiles)]
	entityOneArray=['' for _ in range(numberOfXmlFiles)]
	entityOneWholeWord=['' for _ in range(numberOfXmlFiles)]
	verbComponent1=[set() for _ in range(numberOfXmlFiles)]
	verbComponent2=[set() for _ in range(numberOfXmlFiles)]
	component1Sentence=[set() for _ in range(numberOfXmlFiles)]
	component2Sentence=[set() for _ in range(numberOfXmlFiles)]
	synonymsComponent1=[{} for _ in range(numberOfXmlFiles)]
	synonymsComponent2=[{} for _ in range(numberOfXmlFiles)]
	f2=open("winogradSolutions.txt")
	lines=f2.readlines()    

	listOfAuxVerbs=["is","get","gets","was","were","can","could","did","does","have","may","might","should","will","would","had","are","has","been","being", "must", "ought to", "shall", "do","having", "be","got"]

	whichModel=0

	if sys.argv[1]=='standard':
		whichModel=0
	elif sys.argv[1]=='synonym':
		whichModel=1

	#Go through each XML File, and extract Q and C
	for f in range(0, numberOfXmlFiles):
		firstINindex=0
	
		print f
		text=lines[f*5]
		xml = open(listOfXmlFiles[f]).read()
		annotated_text = A(xml)
		allSentences+=annotated_text.sentences

		firstVerbOccurence=0
		firstEntityOccurence=0
		positionOfFirstEntity=-1
		positionOfSecondEntity=-1
		startedComponent2=0
		sentenceSample=''
		positionOfStop=0

		#Check if PronounQ before or after PredQ (basically see if class is Class A.1 or Class A.2)
		snippet=lines[f*10+2].split(': ')[1]
		text = word_tokenize(snippet)
		tagged=nltk.pos_tag(text)
		prpEncounteredFinal=0
		for pos in range(0,len(tagged)):
			prpEncounteredFinal=0
			if (tagged[pos][1]=='PRP' and pos==len(tagged)-1) or (tagged[pos][1]=='PRP' and pos==len(tagged)-2 and tagged[pos+1][1]=='.'):
				prpEncounteredFinal=1
				break
			elif tagged[pos][1]=='PRP':
				prpEncounteredFinal=0
				break
			
	   
		if prpEncounteredFinal==0:
			scheme[f]=0
		else:
			scheme[f]=1
	
		
		#Determine first entity and second entity
		entityOne=lines[f*10+4].split()
		entityTwo=lines[f*10+5].split()
		entityOneArray[f]=entityOne[len(entityOne)-1]

		#Which Syntactic Structure
		entityOneSpecific=entityOne[-1]
		entityTwoSpecific=entityTwo[-1]
		verbBetweenEntities=0
		entityOneEncountered=0
		entityTwoEncountered=0
		theSentence=lines[f*10+0]
		text = word_tokenize(theSentence)
		tagged=nltk.pos_tag(text)
		for pos in range(0,len(tagged)):
			if tagged[pos][0].lower()==entityOneSpecific.lower():
				entityOneEncountered=1
			elif tagged[pos][0].lower()==entityTwoSpecific.lower():
				entityTwoEncountered=1
				break	
			if entityOneEncountered==1 and entityTwoEncountered==0 and (tagged[pos][1].find('V')==0 or tagged[pos][1].find('JJ')==0):
				verbBetweenEntities=1
				break
		#Check to see if class A or class B
		if verbBetweenEntities==1:
			lexicalScheme[f]=0
		else:
			lexicalScheme[f]=1
	
		for i in range(0,len(annotated_text.sentences[0]['tokens'])):
			sentenceSample+=annotated_text.sentences[0]['tokens'][i]['word']+' '
			if annotated_text.sentences[0]['tokens'][i]['pos'].find('V')==0 or annotated_text.sentences[0]['tokens'][i]['pos'].find('JJ')==0:
				verbComponent1[f].add(annotated_text.sentences[0]['tokens'][i]['word'])

			if annotated_text.sentences[0]['tokens'][i]['word'].lower()==entityOne[len(entityOne)-1].lower():
				positionOfFirstEntity=i
			if len(entityTwo)>0:
				if annotated_text.sentences[0]['tokens'][i]['word'].lower()==entityTwo[len(entityTwo)-1].lower():
					positionOfSecondEntity=i-(len(entityTwo)-1)
			if i>positionOfFirstEntity and i>positionOfSecondEntity and positionOfFirstEntity!=-1 and positionOfSecondEntity!=-1 and (annotated_text.sentences[0]['tokens'][i]['pos']=='IN' or annotated_text.sentences[0]['tokens'][i]['pos']=='CC' or annotated_text.sentences[0]['tokens'][i]['word']=='.' or annotated_text.sentences[0]['tokens'][i]['pos']=='PRP' or annotated_text.sentences[0]['tokens'][i]['pos']=='PRP$'):
				positionOfStop=i
				break

		sentence=""
		for i in range(positionOfFirstEntity,positionOfSecondEntity+1):
			sentence+=annotated_text.sentences[0]['tokens'][i]['word'] +' '
				
		entityOneString=''
		for p in range(0,len(entityOne)):
			if p!=len(entityOne)-1:
				entityOneString+=entityOne[p]+' '
			else:
				entityOneString+=entityOne[p]
			
		entityTwoString=''
		for p in range(0,len(entityTwo)):
			if p!=len(entityTwo)-1:
				entityTwoString+=entityTwo[p]+' '
			else:
				entityTwoString+=entityTwo[p]


		counter=0

		#Add in verb phrases for set C
		temp=sentence.lower().replace(entityOne[len(entityOne)-1].lower(),"").strip()
		if temp.lower().rsplit(' ', 1)[0] not in listOfAuxVerbs:
			component1Sentence[f].add(temp.lower().rsplit(' ', 1)[0])

		#Add in synonyms of verb for set C
		for verb in verbComponent1[f]:
			if verb not in listOfAuxVerbs:
				component1Sentence[f].add(verb)
				synonymSet=[]
				if len(wordnet.synsets(verb,wordnet.VERB))>0:
					synonyms = wordnet.synsets(verb,wordnet.VERB)[0]
					synonymSet = synonyms.lemma_names()

					synonymsComponent1[f]=synonymSet

				try:
					for synonym in synonymsComponent1[f]:
						synonym=synonym.replace("_"," ")
						if whichModel==1:
							component1Sentence[f].add(synonym)
						if len(component1Sentence[f])>=5:
							break
					if len(component1Sentence[f])>=5:
						break
				except:
					break


		component1Sentence[f] = map(lambda foo: foo.replace(' n\'t', 'n\'t'), component1Sentence[f])



		#Similar process to find set Q
		lastINindex=len(annotated_text.sentences[0]['tokens'])

		for i in range(positionOfSecondEntity+1,len(annotated_text.sentences[0]['tokens'])):
			if firstINindex==0 and  i>=positionOfSecondEntity+len(entityTwo) and (annotated_text.sentences[0]['tokens'][i]['pos']=='IN' or annotated_text.sentences[0]['tokens'][i]['pos']=='CC' or annotated_text.sentences[0]['tokens'][i]['word']=='.' or annotated_text.sentences[0]['tokens'][i]['word']==',' )   and annotated_text.sentences[0]['tokens'][i]['word']!='on':
				if annotated_text.sentences[0]['tokens'][i]['word']!=',' and annotated_text.sentences[0]['tokens'][i]['word']!=',':
					firstINindex=i
					break
				else:
					firstINindex=i+1
					break

		for i in range(firstINindex+1,len(annotated_text.sentences[0]['tokens'])):
			if (annotated_text.sentences[0]['tokens'][i]['pos']=='IN' or annotated_text.sentences[0]['tokens'][i]['pos']=='CC' or annotated_text.sentences[0]['tokens'][i]['pos']=='TO'):
				lastINindex=i
				break


			pronounReplaced=0

		sentence=""
		isAdj=0

		for k in range(firstINindex,len(annotated_text.sentences[0]['tokens'])):
			if annotated_text.sentences[0]['tokens'][k]['pos'].find('V')==0 or annotated_text.sentences[0]['tokens'][k]['pos'].find('JJ')==0 or (annotated_text.sentences[0]['tokens'][k]['pos'].find('NN')==0 and annotated_text.sentences[0]['tokens'][k-1]['pos'].find('IN')==0) :
				verbComponent2[f].add(annotated_text.sentences[0]['tokens'][k]['word'])
				if annotated_text.sentences[0]['tokens'][k]['pos'].find('JJ')==0:
					isAdj=1

			if annotated_text.sentences[0]['tokens'][k]['pos'].find('PRP')!=0 and annotated_text.sentences[0]['tokens'][k]['pos']!='.' : 					
				if k!=firstINindex:
					sentence+=annotated_text.sentences[0]['tokens'][k]['word']+' '
	
			elif annotated_text.sentences[0]['tokens'][k]['pos'].find('PRP')==0:
				if annotated_text.sentences[0]['tokens'][k]['pos']=='PRP':
					sentence+=''
					pronounReplaced=1
				elif pronounReplaced==1:
					sentence+=annotated_text.sentences[0]['tokens'][k]['word']+' '	
						
	
		if sentence.strip() not in listOfAuxVerbs:				
			component2Sentence[f].add(sentence.strip())
	
		for verb in verbComponent2[f]:
			if verb not in listOfAuxVerbs: 
				component2Sentence[f].add(verb)
				synonymSet=[]
				if len(wordnet.synsets(verb,wordnet.VERB))>0 or (isAdj==1 and len(wordnet.synsets(verb,wordnet.ADJ))>0):
					if len(wordnet.synsets(verb,wordnet.VERB))>0:				
						synonyms = wordnet.synsets(verb,wordnet.VERB)[0]
					else:
						synonyms = wordnet.synsets(verb,wordnet.ADJ)[0]
					synonymSet = synonyms.lemma_names()

					synonymsComponent2[f]=synonymSet
				try:
					for synonym in synonymsComponent2[f]:
						synonym=synonym.replace("_"," ")
						if whichModel==1:
							component2Sentence[f].add(synonym)
						if len(component2Sentence[f])>=5:
							break
					if len(component2Sentence[f])>=5:
						break
				except:
					break
		component2Sentence[f] = map(lambda foo: foo.replace(' n\'t', 'n\'t'), component2Sentence[f])


	#Save schema information and C and Q
	with open('lexicalSchemeOriginal', 'wb') as fp:
	    pickle.dump(lexicalScheme, fp)	
	with open('schemeOriginal', 'wb') as fp:
	    pickle.dump(scheme, fp)
	if whichModel==0:		
		with open('component1SentenceOriginal', 'wb') as fp:
			pickle.dump(component1Sentence, fp)
		with open('component2SentenceOriginal', 'wb') as fp:
			pickle.dump(component2Sentence, fp)	
		with open('entityOneArrayOriginal', 'wb') as fp:
	   		pickle.dump(entityOneArray, fp)
	elif whichModel==1:
		with open('component1SentenceOriginalSyn', 'wb') as fp:
			pickle.dump(component1Sentence, fp)
		with open('component2SentenceOriginalSyn', 'wb') as fp:
			pickle.dump(component2Sentence, fp)	
		with open('entityOneArrayOriginalSyn', 'wb') as fp:
			pickle.dump(entityOneArray, fp)
		with open('synonymsComponent1OriginalSyn', 'wb') as fp:
	    		pickle.dump(synonymsComponent1, fp)		
		with open('synonymsComponent2OriginalSyn', 'wb') as fp:
	    		pickle.dump(synonymsComponent2, fp)	 
		with open('verbComponent2OriginalSyn', 'wb') as fp:
	    		pickle.dump(verbComponent2, fp)	   
	#Maybe here put an end of sentence marker


if __name__ == "__main__":
    main()




