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
from operator import itemgetter
import itertools
from PyDictionary import PyDictionary
dictionary=PyDictionary()

def similarity(word1, word2):
    allsyns1 = set(ss for ss in wordnet.synsets(word1))
    allsyns2 = set(ss for ss in wordnet.synsets(word2))
    try:
      best = max((wordnet.wup_similarity(s1, s2) or 0) for s1, s2 in 
        itertools.product(allsyns1, allsyns2))
    except: 
      best = 0
    return best

"""
#if want to used word embeddings for similarity scores, use the following instead.
import gensim
#getting word embeddings
print "Loading word embeddings"
model_w2v = gensim.models.KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin.gz', binary=True)  

def similarity(word1, word2):
    sim = model_w2v.wv.similarity(word1, word2)
    return sim
"""

def similarity_filter(C1, C2, threshhold):
    #if either query list is empty, skip filtering and return
    if (not C1) or (not C2):
        return C1, C2, [], []
    elif all(len(q1.split()) > 1 for q1 in C1) or all(len(q2.split()) > 1 for q2 in C2):
        return C1, C2, [], []
    
    newC1 = []
    newC2 = []
    discardedC1 = []
    discardedC2 = []
    single_word_queries = []
    for q1, q2 in itertools.product(C1, C2):
        #if a single word in both queries
        if (len(q1.split()) == 1) and (len(q2.split()) == 1):
            score = similarity(q1, q2)
            single_word_queries.append([score, q1, q2])
        #don't filter multi-word queries
        else:
            if (q1 not in newC1) and (len(q1.split()) > 1):
                newC1.append(q1)
            if q2 not in newC2 and (len(q2.split()) > 1):
                newC2.append(q2)
    #if not an empty list of single word qeries, proceed to filter
    if single_word_queries:
        #sort by highest similarity score pairs
        single_word_queries.sort(key=itemgetter(0), reverse=True)
        #add highest similarity query pair
        newC1.append(single_word_queries[0][1])
        newC2.append(single_word_queries[0][2])
        max_score = float(single_word_queries[0][0])
        for score, q1, q2 in single_word_queries[1:]:
            #if above threshhold, add to query set if not already in
            if save_divide(score,max_score) > threshhold:
                if q1 not in newC1:
                    newC1.append(q1)
                if q2 not in newC2:
                    newC2.append(q2)
    # if empty single word queries, and new queries, just return original
    else:
        if not newC1:
            newC1 = C1
        if not newC2:
            newC2 = C2
    
    #figuring out discarded elements
    for q in C1: 
        if q not in newC1:
            discardedC1.append(q)
    for q in C2:
        if q not in newC2:
            discardedC2.append(q)
            
    return newC1, newC2, discardedC1, discardedC2

def save_divide(a, b):
    if b == 0:
        return 1.0
    else:
        return a/b


threshhold = 0.6
filtered = True
whichModel= 1

#Winograd sentences parsed by CoreNLP, stored as XML files, loaded and sorted
listOfXmlFiles=glob.glob('winogradXML/*xml')
listOfXmlFiles.sort()
listOfXmlFiles=listOfXmlFiles

allSentences=[]

n = n 
scheme=[0 for _ in range(n)]
lexicalScheme=[0 for _ in range(n)]
entityOneArray=['' for _ in range(n)]
entityOneWholeWord=['' for _ in range(n)]
verbComponent1=[set() for _ in range(n)]
verbComponent2=[set() for _ in range(n)]
component1Sentence=[set() for _ in range(n)]
component2Sentence=[set() for _ in range(n)]
discardedC1 = [set() for _ in range(n)]
discardedC2 = [set() for _ in range(n)]
synonymsComponent1=[{} for _ in range(n)]
synonymsComponent2=[{} for _ in range(n)]

f2=open("winogradSolutions.txt") 
lines=f2.readlines()    

listOfAuxVerbs=["is","get","gets","was","were","can","could","did","does","have","may","might",
                "should","will","would","had","are","has","been","being", "must", "ought to", 
                "shall", "do","having", "be","got"]

if sys.argv[1]=='standard':
    whichModel=0
elif sys.argv[1]=='synonym':
    whichModel=1

if len(sys.argv) > 2:
    if sys.argv[2] == 'filter':
        filtered = True

#Go through each XML File, and extract Q and C
for f in range(0, n):
    firstINindex=0

    print f
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
    for pos in range(len(tagged)):
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
    entityOneArray[f]=entityOne[-1]

    #Which Syntactic Structure
    entityOneSpecific=entityOne[-1]
    entityTwoSpecific=entityTwo[-1]
    verbBetweenEntities=0
    entityOneEncountered=0
    entityTwoEncountered=0
    theSentence=lines[f*10]
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

        if annotated_text.sentences[0]['tokens'][i]['word'].lower()==entityOne[-1].lower():
            positionOfFirstEntity=i
        if len(entityTwo)>0:
            if annotated_text.sentences[0]['tokens'][i]['word'].lower()==entityTwo[-1].lower():
                positionOfSecondEntity=i-(len(entityTwo)-1)
        if i>positionOfFirstEntity and i>positionOfSecondEntity and positionOfFirstEntity!=-1 and positionOfSecondEntity!=-1 and (annotated_text.sentences[0]['tokens'][i]['pos']=='IN' or annotated_text.sentences[0]['tokens'][i]['pos']=='CC' or annotated_text.sentences[0]['tokens'][i]['word']=='.' or annotated_text.sentences[0]['tokens'][i]['pos']=='PRP' or annotated_text.sentences[0]['tokens'][i]['pos']=='PRP$'):
            positionOfStop=i
            break

    sentence=""
    for i in range(positionOfFirstEntity,positionOfSecondEntity+1):
        sentence+=annotated_text.sentences[0]['tokens'][i]['word'] +' '   

    entityOneString=''
    for p in range(len(entityOne)):
        if p!=len(entityOne)-1:
            entityOneString+=entityOne[p]+' '
        else:
            entityOneString+=entityOne[p]

    entityTwoString=''
    for p in range(len(entityTwo)):
        if p!=len(entityTwo)-1:
            entityTwoString+=entityTwo[p]+' '
        else:
            entityTwoString+=entityTwo[p]


    counter=0

    #Add in verb phrases for set C
    temp=sentence.lower().replace(entityOne[-1].lower(),"").strip()
    if temp.lower().rsplit(' ', 1)[0] not in listOfAuxVerbs:
        component1Sentence[f].add(temp.lower().rsplit(' ', 1)[0])

    #Add in synonyms of verb for set C
    for verb in verbComponent1[f]:
        if verb not in listOfAuxVerbs:
            component1Sentence[f].add(verb)
            try:
                topn_syns = model_w2v.most_similar(positive=verb, topn=syn_n)
                synonymSet = [x[0].lower() for x in topn_syns]
            except:
                synonymSet = []
            synonymsComponent1[f]=synonymSet
            """
            if len(wordnet.synsets(verb,wordnet.VERB))>0:
                synonyms = wordnet.synsets(verb,wordnet.VERB)[0]
                synonymSet = synonyms.lemma_names()

                synonymsComponent1[f]=synonymSet
            """
            try:
                for synonym in synonymsComponent1[f]:
                    synonym=synonym.replace("_"," ")
                    if whichModel==1:
                        component1Sentence[f].add(synonym)
                    if len(component1Sentence[f])>=max_queries:
                        break
                if len(component1Sentence[f])>=max_queries:
                    break
            except:
                break



    component1Sentence[f] = map(lambda foo: foo.replace(' n\'t', 'n\'t'), component1Sentence[f])



    #Similar process to find set Q
    for j in range(len(annotated_text.sentences)):
        sentences = annotated_text.sentences[j]
        lastINindex=len(sentences['tokens'])
        if j == 0:
            for i in range(positionOfSecondEntity+1,lastINindex):
                if firstINindex==0 and  i>=positionOfSecondEntity+len(entityTwo) and (sentences['tokens'][i]['pos']=='IN' or sentences['tokens'][i]['pos']=='CC' or sentences['tokens'][i]['word']=='.' or sentences['tokens'][i]['word']==',' ) and sentences['tokens'][i]['word']!='on':
                    if sentences['tokens'][i]['word']!=',' and sentences['tokens'][i]['word']!='.':
                        firstINindex=i
                        break
                    else:
                        firstINindex=i+1
                        break

            for i in range(firstINindex+1,len(sentences['tokens'])):
                if (sentences['tokens'][i]['pos']=='IN' or sentences['tokens'][i]['pos']=='CC' or sentences['tokens'][i]['pos']=='TO'):
                    lastINindex=i
                    break
        else:
            firstINindex=0


        pronounReplaced=0
        sentence=""
        isAdj=0

        for k in range(firstINindex,len(sentences['tokens'])):
            if sentences['tokens'][k]['pos'].find('V')==0 or sentences['tokens'][k]['pos'].find('JJ')==0 or (sentences['tokens'][k]['pos'].find('NN')==0 and sentences['tokens'][k-1]['pos'].find('IN')==0) :
                verbComponent2[f].add(sentences['tokens'][k]['word'])
                if sentences['tokens'][k]['pos'].find('JJ')==0:
                    isAdj=1

            if sentences['tokens'][k]['pos'].find('PRP')!=0 and sentences['tokens'][k]['pos']!='.' :                    
                if k!=firstINindex:
                    sentence+=sentences['tokens'][k]['word']+' '

            elif sentences['tokens'][k]['pos'].find('PRP')==0:
                if sentences['tokens'][k]['pos']=='PRP':
                    sentence+=''
                    pronounReplaced=1
                elif pronounReplaced==1:
                    sentence+=sentences['tokens'][k]['word']+' '    

        if sentence.strip() not in listOfAuxVerbs:              
            component2Sentence[f].add(sentence.strip())

        for verb in verbComponent2[f]:
            if verb not in listOfAuxVerbs: 
                component2Sentence[f].add(verb)
                try:
                    topn_syns = model_w2v.most_similar(positive=verb, topn=syn_n)
                    synonymSet = [x[0].lower() for x in topn_syns]
                except:
                    synonymSet = []
                synonymsComponent2[f]=synonymSet
                """
                if len(wordnet.synsets(verb,wordnet.VERB))>0 or (isAdj==1 and len(wordnet.synsets(verb,wordnet.ADJ))>0):
                    if len(wordnet.synsets(verb,wordnet.VERB))>0:               
                        synonyms = wordnet.synsets(verb,wordnet.VERB)[0]
                    else:
                        synonyms = wordnet.synsets(verb,wordnet.ADJ)[0]
                    synonymSet = synonyms.lemma_names()

                    synonymsComponent2[f]=synonymSet
                """
                try:
                    for synonym in synonymsComponent2[f]:
                        synonym=synonym.replace("_"," ")
                        if whichModel==1:
                            component2Sentence[f].add(synonym)
                        if len(component2Sentence[f])>=max_queries:
                            break
                    if len(component2Sentence[f])>=max_queries:
                        break
                except:
                    break
    component2Sentence[f] = map(lambda foo: foo.replace(' n\'t', 'n\'t'), component2Sentence[f])

    component1Sentence[f] = filter(None, component1Sentence[f])
    component2Sentence[f] = filter(None, component2Sentence[f])
    if filtered:
        component1SentenceFiltered, component2SentenceFiltered, discardedC1[f], discardedC2[f] = similarity_filter(
                                                        component1Sentence[f], component2Sentence[f], threshhold)
        print component1Sentence[f], component2Sentence[f]
        print component1SentenceFiltered, component2SentenceFiltered


#Few corrections 
lexicalScheme[39]=0
lexicalScheme[265]=1

if filtered:
    discarded = 0
    for i in range(len(discardedC1)):
        if (not discardedC1[i]) and (not  discardedC2[i]):
            pass
        else:
            discarded += 1
    print "Passages affected by filter: %d" % discarded

#Save schema information and C and Q
folder = "StandardModified/"
with open(folder + 'lexicalScheme', 'wb') as fp:
    pickle.dump(lexicalScheme, fp)  
with open(folder + 'scheme', 'wb') as fp:
    pickle.dump(scheme, fp)
if whichModel==0:
    folder = "StandardModified/"
    with open(folder + 'component1Sentence', 'wb') as fp:
        pickle.dump(component1Sentence, fp)
    with open(folder + 'component2Sentence', 'wb') as fp:
        pickle.dump(component2Sentence, fp) 
    with open(folder + 'entityOneArray', 'wb') as fp:
        pickle.dump(entityOneArray, fp)
    if filtered:
        with open(folder + 'discardedC1', 'wb') as fp:
            pickle.dump(discardedC1, fp)
        with open(folder + 'discardedC2', 'wb') as fp:
            pickle.dump(discardedC2, fp)
elif whichModel==1:
    folder = "SynonymModifiedNew/"
    with open(folder + 'component1SentenceSyn', 'wb') as fp:
        pickle.dump(component1Sentence, fp)
    with open(folder + 'component2SentenceSyn', 'wb') as fp:
        pickle.dump(component2Sentence, fp)
    with open(folder + 'entityOneArraySyn', 'wb') as fp:
        pickle.dump(entityOneArray, fp)
    with open(folder + 'synonymsComponent1Syn', 'wb') as fp:
        pickle.dump(synonymsComponent1, fp)
    with open(folder + 'synonymsComponent2Syn', 'wb') as fp:
        pickle.dump(synonymsComponent2, fp)
    with open(folder + 'verbComponent2Syn', 'wb') as fp:
        pickle.dump(verbComponent2, fp)
    if filtered:
        with open(folder + 'discardedSynC1', 'wb') as fp:
                pickle.dump(discardedC1, fp)
        with open(folder + 'discardedSynC2', 'wb') as fp:
                pickle.dump(discardedC2, fp)
