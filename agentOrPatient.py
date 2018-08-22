import string
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
from nltk import word_tokenize, pos_tag
from selenium.webdriver.chrome.options import Options
from corenlp import *
from simplejson import loads
import pickle
import time
from random import randint
from nltk import sent_tokenize, word_tokenize
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from unicodedata import category
from selenium.common.exceptions import StaleElementReferenceException
import copy
import csv

def agentOrpatient(sentence,clause1,clause2,sentences):
	answer=""
	agentCount=0
	patientCount=0
	listOfAuxVerbs=["is","was","were","can","could","did","does","have","may","might","should","will","would","had","are","has","been","being", "must", "ought to", "shall", "do","having", "be","got","with","made","when"]
	if sentence.lower().find(clause2)>=0 and sentence.lower().find(clause1)>=0:

								
									try:
										parsed=loads(corenlp.parse(sentence.encode('ascii', 'ignore').decode('ascii')))
						
										#check to see if the entity to which pronoun co-refurs is before or after root:
										agentIsReferredTo=0
										patientIsReferredTo=0

										root=parsed['sentences'][0]['dependencies'][0][2]
										#rootIndex=sentence.index(root)

										clause1Index=sentence.lower().index(clause1)
										clause2Index=sentence.lower().index(clause2)
										for entitySet in parsed['coref']:
											EntityBeforeClause1=0
											EntityAfterClause1=0
											EntityBeforeClause2=0
											EntityAfterClause2=0
											EntityBetweenClause1AndClause2=0
											EntityBetweenClause2AndClause1=0
											passive=0
											posessive=0
											for corefChain in entitySet:
												for entity in corefChain:
													if entity[0].lower() in ["my","his","her","their","your","our"]:
														posessive=1
													if (clause1 in entity[0].lower()) or (clause2 in entity[0].lower()):
														raise Exception()
													#if sentence.index(entity[0]+' ')==0:

													r = re.compile(r'\b%s\b' % entity[0], re.I)
													m = r.search(sentence)
													indexOfWord = m.start()
													indicesOfWord=[m.start() for m in r.finditer(sentence)]
													if clause2.lower().find(' '+entity[0].lower()+' ')>=0:
														whereInClause2IsPronoun=clause2.lower().find(' '+entity[0].lower()+' ')+1
													else:
														whereInClause2IsPronoun=0
													for indexOfWord in indicesOfWord:
												
														if clause1Index-indexOfWord>= 0 and clause1Index-indexOfWord<10+len(entity[0]):
															EntityBeforeClause1=1
															clause1IndexSplit=sentence.lower().split(" ").index(clause1.split(" ")[0])
															if sentence.lower().split(" ")[clause1IndexSplit-1] in listOfAuxVerbs:
																passive=1
											
														
														if indexOfWord-clause1Index>0 and indexOfWord-(clause1Index+len(clause1))<=10:
															EntityAfterClause1=1
															clause1IndexSplit=sentence.lower().split(" ").index(clause1.split(" ")[0])
															if sentence.lower().split(" ")[clause1IndexSplit-1] in listOfAuxVerbs:
																passive=1
														if (clause2Index+whereInClause2IsPronoun)-indexOfWord >=0 and clause2Index-indexOfWord<10+len(entity[0]):
															EntityBeforeClause2=1
														if indexOfWord-clause2Index>0 and indexOfWord-(clause2Index+len(clause2))<=10:
															EntityAfterClause2=1
														if indexOfWord>clause1Index and indexOfWord-clause2Index<10:
															EntityBetweenClause1AndClause2=1
														if indexOfWord>clause2Index and indexOfWord-clause1Index<10:
															EntityBetweenClause2AndClause1=1
										
										
											if (EntityBeforeClause1 and EntityBeforeClause2):
												agentIsReferredTo=1
												patientIsReferredTo=0
												if passive==1 or posessive==1:
													agentIsReferredTo=0
													patientIsReferredTo=1
											
												break
											elif (EntityAfterClause1 and EntityBeforeClause2):
												patientIsReferredTo=1 
												agentIsReferredTo=0
												if passive==1:
													agentIsReferredTo=1
													patientIsReferredTo=0
														
											
												break	

											#Within reasonable distance

											
										if agentIsReferredTo==1 and sentence.strip().strip(' "') not in sentences:
											agentCount+=1

											print "Agent Referred: " + sentence

										elif patientIsReferredTo==1 and sentence.strip().strip(' "') not in sentences:
											patientCount+=1
											#Patient score more heavily weighted
											print "Patient Referred: " + sentence
									except:
										agentCount+=0
									if agentCount==1:
										answer="agent"
									elif patientCount==1:
										answer="patient"
	else:
		answer="invalid"
	return answer

corenlp = StanfordCoreNLP()

with open('Synonym Model/informationOfSentenceOriginalSyn', 'rb') as fp:
	info=pickle.load(fp)
with open('Synonym Model/informationOfSentenceOriginalGoogleAutomatic', 'rb') as fp:
	infoGoogle=pickle.load(fp)

info2=copy.deepcopy(info)
info3=copy.deepcopy(infoGoogle)


myData = [["Sentence", "Clause 1", "Clause 2", "Valid Sentence", "Coreference Correct", "Heuristic Correct"]]


with open('scrapedSentencesAnalyze.csv', 'wb') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerows(myData)
	for f in range(0,273):
		while len(info2[f])>0:
			sentence=info2[f].pop()
			label=sentence[0]
			clause1=sentence[1]
			clause2=sentence[2]
			snippet=sentence[3].encode('ascii', 'ignore').decode('ascii')

			try:
				parsed=loads(corenlp.parse(snippet.encode('ascii', 'ignore').decode('ascii')))
				coreferenceChain=parsed['coref']
				answer=agentOrpatient(snippet,clause1,clause2,[""])
				writer.writerow([snippet,clause1, clause2, 1 ,coreferenceChain,answer])

			except:
				writer.writerow([snippet,clause1,clause2,0,"","neither"])	


		
print "hello"

