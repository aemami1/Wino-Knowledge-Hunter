# -*- coding: utf-8 -*-
"""
Created on Tue May 23 17:34:14 2017

@author: user
"""

import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from nltk import word_tokenize, pos_tag
from selenium.webdriver.chrome.options import Options
#q = raw_input("Enter the search query")

#Works
#clause1="tried to"
#clause2="but he wasn't successful"
#pronoun="he"

#Works
#clause1="couldn't lift"
#clause2="because he was so weak"
#pronoun="he"

#Works
clause1="thank"
clause2="for all the help she had received"
#pronoun="she"

#clause1="thank"
#clause2="for all the help she had given"
#pronoun="she"

#Works
#clause1= "doesn't fit"
#clause2= "because it is too large"

#Works
#clause1 = "envies"
#clause2 = "although he is successful"

#Works
#clause1 = "jealous"
#clause2 = "because he is successful"

#Works
#clause1= "couldn't see him"
#clause2= "because he is so tall"

#Works
#clause1= "couldn't see"
#clause2= "because he is so short"

#clause1="vindicated"
#clause2="when he won"

#WORKS
#clause1="zoomed by him"
#clause2="going so fast"

#Works
#clause1="tried to call"
#clause2="wasn't available"

#Works
#clause1="asked him"
#clause2="answer"

#Works
#clause1="asked him"
#clause2="repeat it"

#Works
#clause1="stuck a pin through"
#clause2="had a hole"

#Works
#clause1="follow his example"
#clause2="influence me"

#Works
#clause1="won't fit"
#clause2="because it's too tight"

#clause1="promised me to leave"
#clause2="he left"

#Works
#clause1="knocked on his door"
#clause2="he did not answer"

#Works
#clause1="knocked on his door"
#clause2="I did not get an answer"

#works
#clause1="signaled the barman"
#clause2="her empty glass"

#works
#clause1="he lifted her"
#clause2="onto his shoulders"

#works
#clause1="he lifted her"
#clause2="onto her bed"

#works
#clause1="stretching his back"
#clause2="he smiled at"

#
#clause1="patting his back"
#clause2="he smiled at"

#
#clause1= "she spoke to"
#clause2= "breaking his concentration"







#Jane knocked on Susan's door but she did not get an answer.

q="\""+clause1+"\"++\""+clause2 +"\""

q=q.replace('\"','%22')
q = q.replace(' ', '+')
q=q+" -winograd"

#browser = webdriver.Firefox()

chromedriver = "/home/2012/aemami1/stanford-corenlp-python-master/chromedriver"
os.environ["webdriver.chrome.driver"] = chromedriver
browser = webdriver.Chrome(chromedriver)

body = browser.find_element_by_tag_name("body")
body.send_keys(Keys.CONTROL + 't')
counter = 0
foundCount=0
foundIt=0
captchaSolve=-1
listOfSentences=['' for _ in range(10)]
for i in range(0,10):
    browser.get("https://www.google.com/search?q=" + q + "&start=" +
str(counter))
    body = browser.find_element_by_tag_name("body")
    if body.text.find("Our systems have detected unusual traffic from your computer network")>0:
        captchaSolve=1
        break
    if body.text.find("did not match any documents")>0:
        break
    if body.text.find("No results found")>0:
        break

    listOfSnippets=body.text.replace("https",
"<stuff>").replace("www.","<stuff>").replace("authors","<stuff>").replace(".com","<stuff>").replace(".net","<stuff>").split("<stuff>")

    for snippet in listOfSnippets:
        if snippet.lower().find(clause1)!=-1 and snippet.lower().find(clause2)!=-1 and abs(snippet.lower().find(clause1)+len(clause1)-snippet.lower().find(clause2))<70:
            foundIt=1
            index1=snippet.lower().find(clause1)
            index2=snippet.lower().find(clause2)
            firstIndex=snippet.lower().find("\n")
            if index1>index2:
                increment=len(clause1)
            else:
                increment=len(clause2)
            stringy=snippet[firstIndex:max(index1,index2)+increment]
            stringy=stringy.split(' - ')[len(stringy.split(' - '))-1]
            if len(stringy.split('\n'))>1:
                stringy=stringy.split('\n')[1]
            print "Sentence found: " + stringy
            listOfSentences[foundCount]=stringy
            foundCount+=1
            if foundCount==10:
                break

    counter += 10
    if foundCount==5:
        break
if captchaSolve!=1:
    browser.quit()


def FirstOrSecond(sentence):
    text = word_tokenize(sentence)
    tagged_sentence=pos_tag(text)
    noVerbYet=1
    secondEntity=""
    firstEntity=""
    for token in tagged_sentence:
        if noVerbYet==1 and token[1].find('PRP')==0:
            firstEntity=token[0]
            firstEntity=firstEntity.lower()
        elif noVerbYet==1 and token[1].find('V')==0:
            noVerbYet=0
        elif noVerbYet==0 and token[1].find('PRP')==0:
            secondEntity=token[0]
            secondEntity=secondEntity.lower()
    if firstEntity==secondEntity:
        return "first"
    else:
        return "second"


#-----------------------------------------------------------------------------------------

from corenlp import *
from simplejson import loads
import pickle
corenlp = StanfordCoreNLP()
with open('component1Sentence', 'rb') as fp:
    component1Sentence=pickle.load(fp)
with open('component2Sentence', 'rb') as fp:
    component2Sentence=pickle.load(fp)
sentence="She was appreciative and thankful for all the help she had received"		
parsed=loads(corenlp.parse("She was appreciative and thankful for all the help she had received"))


#check to see if the entity to which pronoun co-refurs is before or after root:
actorIsReferredTo=0
agentIsRefferedTo=1

root=parsed['sentences'][0]['dependencies'][0][2]
rootIndex=sentence.index(root)
for entity in parsed['coref'][0][0]:
	if entity[3]<rootIndex:
		actorIsReferredTo=1
		agentIsReferredTo=0
		break
		
