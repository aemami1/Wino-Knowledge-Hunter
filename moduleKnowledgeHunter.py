
# -*- coding: utf-8 -*-
"""
Created on Tue May 23 17:34:14 2017

@author: Ali Emami
"""

import sys
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


def main(): 
	def compare(s1, s2):
		#for c in string.punctuation:
			#s1= s1.replace(c,"")
			#s2=s2.replace(c,"")
		#s1=s1.replace("  ", " ")
		#s2=s2.replace("  ", " ")
		return s1.find(s2)

	def loop_is_text_present(max_attempts=3):
	    attempt = 1
	    while True:
		try:
		    return browser.find_element_by_tag_name("body")
		except StaleElementReferenceException:
		    if attempt == max_attempts:
		        raise
		    attempt += 1
		 
	def agentVsPatient(component1Sentence,component2Sentence,entityOne,scheme):

	
		information = set()
		sentences = set()


		numberofAgentClause1GreaterThanOne=0
		numberofAgentClause2GreaterThanOne=0
		numberofAgentClause1LessThanOneClause2LessThanOne=0
		numberofPatientClause1GreaterThanOne=0
		numberofPatientClause2GreaterThanOne=0
		numberofPatientClause1LessThanOneClause2LessThanOne=0

		features=[0 for x in range(7)]

		captchaSolve=-1
		agentCount=0
		patientCount=0
		sentenceCount=0
		parsedCount=0
		agentScore=0
		patientScore=0
		clause1BiggestLength=0
		clause2BiggestLength=0
		listOfAuxVerbs=["","is","was","were","can","could","did","does","have","may","might","should","will","would","had","are","has","been","being", "must", "ought to", "shall", "do","having", "be","got","with","made","when"]
		for clause1 in component1Sentence:

			if captchaSolve==1:
				break
			for clause2 in component2Sentence:

				clause2=clause2.strip()
				clause1=clause1.strip()
				if clause1==clause2:
					break
				print clause1
				print clause2
				if clause1=='' or clause2=='' or clause1 in listOfAuxVerbs or clause2 in listOfAuxVerbs :
					if clause2 in listOfAuxVerbs:
						component2Sentence.remove(clause2)
						break
					if clause1 in listOfAuxVerbs:
						component1Sentence.remove(clause1)
						break
				if captchaSolve==1:
					break


				q="\""+clause1+"\"++\""+clause2 +"\""

				q=q.replace('\"','%22')
				q = q.replace(' ', '+')
				q=q+" -winograd"
				q=q+" -"+entityOne
				qManual="+\""+clause1+"\" +\""+clause2 +"\"" + "-winograd" +  " -"+entityOne #+"-\""+entityOne+"\"" #+  " -"+"\"winograd\""#+entityOneArray[f] #+ " -winograd" #+  " -"+entityOne
				#qManual=clause1 +" + " + clause2 + " + " + "-winograd" +  " -"+entityOneArray[f]
			
				body = browser.find_element_by_tag_name("body")
				counter = 0
				foundCount=0
				foundIt=0
				captchaSolve=-1
				listOfSentences=set()
				isAnotherPage=1

				inputElement=browser.find_element_by_id("sb_form_q")
				inputElement.clear()
				inputElement.send_keys(qManual)
				inputElement.send_keys(Keys.ENTER)
				time.sleep(1)
				for i in range(0,10):
				    #WAIT A BIT YEA LOL
				    #wait_abit()
				    #TRY THIS MANUAL:
				    



				    body = browser.find_element_by_tag_name("body")
				    body = loop_is_text_present()#browser.find_element_by_tag_name("body")
			
				    if body.text.find("Our systems have detected unusual traffic from your computer network")>=0:
					captchaSolve=1
					break
				    if body.text.find("did not match any documents")>0:
					break
				    if body.text.find("No results found")>0:
					break

				    listOfSnippets=body.text.replace("https",
				"<stuff>").replace("www.","<stuff>").replace("authors","<stuff>").replace(".com","<stuff>").replace("...","<stuff>").replace("\n","<stuff>").replace(".net","<stuff>").split("<stuff>")

				    for snippet in listOfSnippets:

					if len(snippet.split(' '))>5 and compare(snippet.lower()," "+clause1+" ")!=-1 and compare(snippet.lower()," "+clause2+" ")!=-1 and abs(compare(snippet.lower(),clause1)+len(clause1)-compare(snippet.lower(),clause2))<70:
					    foundIt=1
					    index1=snippet.lower().find(clause1)
					    index2=snippet.lower().find(clause2)
					    firstIndex=0
					    if index1>index2:
						lengthOfPronounAfterVerb=0
						increment=0
						if snippet[index1+len(clause1):].find(' ')>=0:
							lengthOfPronounAfterVerb=snippet[index1+len(clause1):].index(' ')
							increment=len(clause1)+lengthOfPronounAfterVerb
					
					    else:
						increment=len(clause2)
					    stringy=snippet[firstIndex:max(index1,index2)+increment]
					    stringy=stringy.split(' - ')[len(stringy.split(' - '))-1]
					    if len(stringy.split('\n'))>1:
						stringy=stringy.split('\n')[1]
					    print "Sentence found: " + stringy
					    listOfSentences.add(stringy)
					    foundCount+=1
					    sentenceCount+=1
					    if foundCount>=5000:
						break
				    #try:
				    #	browser.find_element_by_class_name("sb_pagN").click()
				    #except:
				    # 	newPage=1

				    if foundCount>=5000:
					break
				    try:
				   	browser.find_element_by_class_name("sb_pagN").click()
				    except:
					break
				




				#-----------------------------------------------------------------------------------------

				if foundCount>0:	
					for sentenceFull in listOfSentences:
						if sentenceFull!='':
							#sentence="She was appreciative and thankful for all the help she had received"
							splitSentences= sentenceFull.replace('.....', 'REPLACETHIS').replace('....', 'REPLACETHIS').replace('...', 'REPLACETHIS').split('REPLACETHIS')						
						
							for sentence in splitSentences:
							

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
										passive=0
										clause1IndexSplit=sentence.lower().split(" ").index(clause1.split(" ")[0])
										if sentence.lower().split(" ")[clause1IndexSplit-1] in listOfAuxVerbs:
											passive=1
										for entitySet in parsed['coref']:
											EntityBeforeClause1=0
											EntityAfterClause1=0
											EntityBeforeClause2=0
											EntityAfterClause2=0
											EntityBetweenClause1AndClause2=0
											EntityBetweenClause2AndClause1=0
											posessive=0
										
											for corefChain in entitySet:
												for entity in corefChain:
													if entity[0].lower() in ["my","his","her","their","your","our"]:
														posessive=1
													#if sentence.index(entity[0]+' ')==0:
													if (clause1 in entity[0].lower()) or (clause2 in entity[0].lower()):
														raise Exception()
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
															
														if indexOfWord-clause1Index>0 and indexOfWord-(clause1Index+len(clause1))<=10:
															EntityAfterClause1=1
														if (clause2Index+whereInClause2IsPronoun)-indexOfWord >=0 and clause2Index-indexOfWord<10+len(entity[0]):
															EntityBeforeClause2=1
														if indexOfWord-clause2Index>0 and indexOfWord-(clause2Index+len(clause2))<=10:
															EntityAfterClause2=1
														if indexOfWord>clause1Index and indexOfWord-clause2Index<10:
															EntityBetweenClause1AndClause2=1
														if indexOfWord>clause2Index and indexOfWord-clause1Index<10:
															EntityBetweenClause2AndClause1=1
										
											if scheme==0:
												if (EntityBeforeClause1 and EntityBeforeClause2):
													agentIsReferredTo=1
													patientIsReferredTo=0
													if passive==1 or posessive==1:
														agentIsReferredTo=0
														patientIsReferredTo=1
														print "patient, passive"
													break
												elif EntityAfterClause1 and EntityBeforeClause2:
													patientIsReferredTo=1 
													agentIsReferredTo=0
													if passive==1:
														agentIsReferredTo=1
														patientIsReferredTo=0
														print "agent, passive"
											
											
													break
											elif scheme==1:
												if (EntityBeforeClause1 and EntityAfterClause2):
													agentIsReferredTo=1
													patientIsReferredTo=0
													if passive==1 or posessive==1:
														agentIsReferredTo=0
														patientIsReferredTo=1
											
													break
												elif EntityAfterClause1 and EntityAfterClause2:
													patientIsReferredTo=1 
													agentIsReferredTo=0
													if passive==1:
														agentIsReferredTo=1
														patientIsReferredTo=0
											
											
													break	

											#Within reasonable distance

											
										if agentIsReferredTo==1 and sentence.strip().strip(' "') not in sentences:
											agentCount+=1
											agentScore+=1*len(clause1.split(' '))+1*len(clause2.split(' '))
											if clause1Index<clause2Index:
												agentScore+=1*len(clause1.split(' '))+1*len(clause2.split(' '))
											print "Agent Referred: " + sentence
											parsedCount+=1
											information.add(('agent', clause1, clause2, sentence))
											if len(clause1.split(' '))>1:
												numberofAgentClause1GreaterThanOne+=1
											if len(clause2.split(' '))>1:
												numberofAgentClause2GreaterThanOne+=1
											if len(clause1.split(' '))==1 and len(clause2.split(' '))==1 :
												numberofAgentClause1LessThanOneClause2LessThanOne+=1

											sentences.add(sentence.strip().strip(' "'))
										elif patientIsReferredTo==1 and sentence.strip().strip(' "') not in sentences:
											patientCount+=1
											patientScore+=1*len(clause1.split(' '))+1*len(clause2.split(' '))
											#Patient score more heavily weighted
										
											if clause1Index<clause2Index:
												patientScore+=1*len(clause1.split(' '))+1*len(clause2.split(' '))
											print "Patient Referred: " + sentence
											parsedCount+=1
											information.add(('patient', clause1, clause2, sentence))
											if len(clause1.split(' '))>1:
												numberofPatientClause1GreaterThanOne+=1
											if len(clause2.split(' '))>1:
												numberofPatientClause2GreaterThanOne+=1
											if len(clause1.split(' '))==1 and len(clause2.split(' '))==1 :
												numberofPatientClause1LessThanOneClause2LessThanOne+=1
											sentences.add(sentence.strip().strip(' "'))
									except:
										agentCount+=0
						
		print "AgentCount:"
		print agentCount
		print "PatientCount:"
		print patientCount
		patientScore=patientScore*2

		features[0]=numberofAgentClause1GreaterThanOne
		features[1]=numberofAgentClause2GreaterThanOne
		features[2]=numberofAgentClause1LessThanOneClause2LessThanOne
		features[3]=numberofPatientClause1GreaterThanOne
		features[4]=numberofPatientClause2GreaterThanOne
		features[5]=numberofPatientClause1LessThanOneClause2LessThanOne
		features[6]=0

		return [agentCount,patientCount,agentScore,patientScore,sentenceCount,parsedCount,information, features]





	whichModel=0

	if sys.argv[1]=='standard':
		whichModel=0
	elif sys.argv[1]=='synonym':
		whichModel=1
	elif sys.argv[1]=='gold':
		whichModel=2


	corenlp = StanfordCoreNLP()
	if whichModel==0:
		with open('Standard Model/component1SentenceOriginal', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Standard Model/component2SentenceOriginal', 'rb') as fp:
		    component2Sentence=pickle.load(fp)
		with open('Standard Model/entityOneArrayOriginal', 'rb') as fp:
		    entityOneArray=pickle.load(fp)
	elif whichModel==1:
		with open('Synonym Model/component1SentenceOriginalSyn', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Synonym Model/component2SentenceOriginalSyn', 'rb') as fp:
		    component2Sentence=pickle.load(fp)
		with open('Synonym Model/entityOneArrayOriginalSyn', 'rb') as fp:
		    entityOneArray=pickle.load(fp)
	elif whichModel==2:
		with open('Gold Model/component1SentenceOriginalGold', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Gold Model/component2SentenceOriginalGold', 'rb') as fp:
		    component2Sentence=pickle.load(fp)
		with open('Gold Model/entityOneArrayOriginal', 'rb') as fp:
		    entityOneArray=pickle.load(fp)

	with open('schemeOriginal', 'rb') as fp:
	    scheme=pickle.load(fp)
	with open('lexicalSchemeOriginal', 'rb') as fp:
	    lexicalScheme=pickle.load(fp)

	informationOfSentence=[set() for _ in range(len(component1Sentence))]
	decision=['' for _ in range(len(component1Sentence))]
	agentCount=[0 for _ in range(len(component1Sentence))]
	patientCount=[0 for _ in range(len(component1Sentence))]
	agentScore=[0 for _ in range(len(component1Sentence))]
	patientScore=[0 for _ in range(len(component1Sentence))]
	sentenceCount=[0 for _ in range(len(component1Sentence))]
	parsedCount=[0 for _ in range(len(component1Sentence))]
	featureMatrix = [[0 for x in range(7)] for y in range(len(component1Sentence))]

	#browser = webdriver.Firefox()

	#FOR CHROME, make sure updated chromedriver in folder.
	#chromedriver = "/home/2012/aemami1/stanford-corenlp-python-master/chromedriver"
	#os.environ["webdriver.chrome.driver"] = chromedriver
	#browser = webdriver.Chrome(chromedriver)
		
	#FOR FIREFOX
	binary = FirefoxBinary('/home/ml/aemami1/Downloads/firefox/firefox-bin')
	browser=webdriver.Firefox(firefox_binary=binary)
	browser.get("https://www.bing.com")
	time.sleep(2)
	browser.find_element_by_id("id_sc").click()
	time.sleep(2)
	browser.find_element_by_class_name("hb_titlerow").click()
	time.sleep(2)
	browser.find_element(By.PARTIAL_LINK_TEXT, 'More').click()

	#Change country

	time.sleep(2)
	inputElement=browser.find_element_by_id("rpp")
	time.sleep(2)
	inputElement.click()
	inputElement.send_keys(Keys.DOWN)
	inputElement.send_keys(Keys.DOWN)
	inputElement.send_keys(Keys.DOWN)
	inputElement.send_keys(Keys.DOWN)
	inputElement.send_keys(Keys.ENTER)
	browser.find_element_by_id("sv_btn").click()


	#Change settings
	browser.get("https://www.bing.com")
	time.sleep(2)
	browser.find_element_by_id("id_sc").click()
	time.sleep(2)
	browser.find_element_by_class_name("hb_titlerow").click()
	time.sleep(2)
	browser.find_element(By.PARTIAL_LINK_TEXT, 'More').click()
	time.sleep(2)
	inputElement=browser.find_element(By.PARTIAL_LINK_TEXT, 'Change your').click()
	inputElement=browser.find_element(By.PARTIAL_LINK_TEXT, 'Change your').click()
	inputElement=browser.find_element(By.PARTIAL_LINK_TEXT, 'Change your').click()
	time.sleep(3)
	browser.find_element(By.PARTIAL_LINK_TEXT, 'United States - English').click()

	indicesToBeRedone=[i for i, x in enumerate(scheme) if x == 1]
	indicesOfGoodWinogradQuestions=[i for i, x in enumerate(scheme) if x == 0]

	for f in range(0,273):

		if True:
			print f
			[agentCount2,patientCount2,agentScore2,patientScore2,sentenceCount2,parsedCount2,information, features]=agentVsPatient(component1Sentence[f],component2Sentence[f], entityOneArray[f],scheme[f])
			agentCount[f]=agentCount2
			patientCount[f]=patientCount2
			agentScore[f]=agentScore2
			patientScore[f]=patientScore2
			sentenceCount[f]=sentenceCount2
			parsedCount[f]=parsedCount2
			informationOfSentence[f]=information
			featureMatrix[f]=features
			print featureMatrix[f]

			if agentCount[f]==0 and patientCount[f]==0:
				decision[f]=''
			elif agentCount[f]>patientCount[f]:
				decision[f]=0
				print decision
			elif patientCount[f]>=agentCount[f]:
				decision[f]=1
				print decision
			if whichModel==0:
				with open('decisionExpandedScoringOriginal', 'wb') as fp:
			    		pickle.dump(decision, fp)
				with open('informationOfSentenceOriginal', 'wb') as fp:
					pickle.dump(informationOfSentence,fp)
				with open('parsedCountOriginal','wb') as fp:
					pickle.dump(parsedCount,fp)
				with open('sentenceCountOriginal','wb') as fp:
					pickle.dump(sentenceCount,fp)
				with open('featureMatrixOriginal','wb') as fp:
					pickle.dump(featureMatrix,fp)
			if whichModel==1:
				with open('decisionExpandedScoringOriginalSyn', 'wb') as fp:
			    		pickle.dump(decision, fp)
				with open('informationOfSentenceOriginalSyn', 'wb') as fp:
					pickle.dump(informationOfSentence,fp)
				with open('parsedCountOriginalSyn','wb') as fp:
					pickle.dump(parsedCount,fp)
				with open('sentenceCountOriginalSyn','wb') as fp:
					pickle.dump(sentenceCount,fp)
				with open('featureMatrixOriginalSyn','wb') as fp:
					pickle.dump(featureMatrix,fp)
			if whichModel==2:
				with open('decisionExpandedScoringOriginalGold', 'wb') as fp:
			    		pickle.dump(decision, fp)
				with open('informationOfSentenceOriginalGold', 'wb') as fp:
					pickle.dump(informationOfSentence,fp)
				with open('parsedCountOriginalGold','wb') as fp:
					pickle.dump(parsedCount,fp)
				with open('sentenceCountOriginalGold','wb') as fp:
					pickle.dump(sentenceCount,fp)
				with open('featureMatrixOriginalGold','wb') as fp:
					pickle.dump(featureMatrix,fp)



if __name__ == "__main__":
    main()


		
