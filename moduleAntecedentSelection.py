"""
Created on Tue May 23 17:34:14 2017

@author: Ali Emami
"""

import numpy 
import pickle
import copy
import sys


def main():
	whichModel=0

	if sys.argv[1]=='standard':
		whichModel=0
	elif sys.argv[1]=='synonym':
		whichModel=1
	elif sys.argv[1]=='gold':
		whichModel=2



	if whichModel==0:
		#Open from file Sets C (context) and Q (query) 
		#I.E for first Winograd sentence: C=[u'refused'], Q=[u'feared violence', u'feared']
		#C=component1Sentence, Q=component2Sentence

		with open('Standard Model/component1SentenceOriginal', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Standard Model/component2SentenceOriginal', 'rb') as fp:
		    component2Sentence=pickle.load(fp)

		#Open from  file Sets info (sentences scraped from Bing) and infoGoogle (sentences scraped from Google) of the structure:
		#info[winogradQuestionNumber]=set([('evidence-sentence-class (patient or agent)', c, q, sentence), i.e:
		#[('patient', u'refused', u'feared violence', u' while GOP Rep. Louis Gohmert of Texas refused to hold his planned town hall meeting, saying he feared violence')
		with open('Standard Model/informationOfSentenceOriginal', 'rb') as fp:
		    info=pickle.load(fp)

		#Didn't get google results for standard
		infoGoogle=[set() for _ in range(len(component1Sentence))]

		#Open heuristic decision matrix immediately generated from scraping process (no sentence weighting)
		with open('Standard Model/decisionExpandedScoringOriginal', 'rb') as fp:
	    		decision=pickle.load(fp)

	elif whichModel==1:
		#Open from file Sets C (context) and Q (query)
		#I.E for first Winograd sentence: C=[u'refused'], Q=[u'feared violence', u'feared']
		#C=component1Sentence, Q=component2Sentence

		with open('Synonym Model/component1SentenceOriginalSyn', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Synonym Model/component2SentenceOriginalSyn', 'rb') as fp:
		    component2Sentence=pickle.load(fp)


		#Open from  file Sets info (sentences scraped from Bing) and infoGoogle (sentences scraped from Google) of the structure:
		#info[winogradQuestionNumber]=set([('evidence-sentence-class (patient or agent)', c, q, sentence), i.e:
		#[('patient', u'refused', u'feared violence', u' while GOP Rep. Louis Gohmert of Texas refused to hold his planned town hall meeting, saying he feared violence')
		with open('Synonym Model/informationOfSentenceOriginalSyn', 'rb') as fp:
		    info=pickle.load(fp)
		with open('Synonym Model/informationOfSentenceOriginalGoogleAutomatic', 'rb') as fp:
		    infoGoogle=pickle.load(fp)
		with open('informationOfSentenceOriginalSyn', 'rb') as fp:
		    info2=pickle.load(fp)
		#with open('informationOfSentenceOriginalGoogleAutomatic', 'rb') as fp:
		    #infoGoogle2=pickle.load(fp)
	
		#Open heuristic decision matrix immediately generated from scraping process (no sentence weighting)
		with open('Synonym Model/decisionExpandedScoringOriginalSyn', 'rb') as fp:
	    		decision=pickle.load(fp)

	elif whichModel==2:
		#Open from file Sets C (context) and Q (query) (These would be Gold Standard)
		#I.E for first Winograd sentence: C=[u'refused'], Q=[u'feared violence', u'feared']
		#C=component1Sentence, Q=component2Sentence

		with open('Gold Model/component1SentenceOriginalGold', 'rb') as fp:
		    component1Sentence=pickle.load(fp)
		with open('Gold Model/component2SentenceOriginalGold', 'rb') as fp:
		    component2Sentence=pickle.load(fp)

		#Open from  file Sets info (sentences scraped from Bing) and infoGoogle (sentences scraped from Google) of the structure:
		#info[winogradQuestionNumber]=set([('evidence-sentence-class (patient or agent)', c, q, sentence), i.e:
		#[('patient', u'refused', u'feared violence', u' while GOP Rep. Louis Gohmert of Texas refused to hold his planned town hall meeting, saying he feared violence')
		with open('Gold Model/informationOfSentenceOriginalGold', 'rb') as fp:
		    info=pickle.load(fp)
		with open('Gold Model/informationOfSentenceOriginalGoogle', 'rb') as fp:
		    infoGoogle=pickle.load(fp)

		#Open heuristic decision matrix immediately generated from scraping process (no sentence weighting)
		with open('Gold Model/decisionExpandedScoringOriginalGold2', 'rb') as fp:
	    		decision=pickle.load(fp)

	#Open matrix indicating which Winograd sentence is in the form of Class A (denoted by value 0) or class B (denoted by value 1)	
	with open('lexicalSchemeOriginal', 'rb') as fp:
	    lexicalSchemeOriginal=pickle.load(fp)

	#Open matrix indicating which Winograd sentence is in the form of Class A.1 (E1PredCE2+PPredQ, denoted by value 0) or Class A.2 (E1PredCE2+PredQP, denoted by value 1)
	with open('schemeOriginal', 'rb') as fp:
	    scheme=pickle.load(fp)



	#Instantiate various parameters that are involved in weighing evidence sentences, including number of evidence-patient, number of evidence-agent, average token length of clauses, etc.
	patientCount=[0 for _ in range(len(component1Sentence))]
	agentCount=[0 for _ in range(len(component1Sentence))]
	totalCount=[0 for _ in range(len(component1Sentence))]
	agentClause1LengthAverage=[0 for _ in range(len(component1Sentence))]
	agentClause2LengthAverage=[0 for _ in range(len(component1Sentence))]
	patientClause1LengthAverage=[0 for _ in range(len(component1Sentence))]
	patientClause2LengthAverage=[0 for _ in range(len(component1Sentence))]
	patientRatio=[0 for _ in range(len(component1Sentence))]
	agentRatio=[0 for _ in range(len(component1Sentence))]
	agentClause1SpecificRatio=[0 for _ in range(len(component1Sentence))]
	agentClause2SpecificRatio=[0 for _ in range(len(component1Sentence))]
	patientClause1SpecificRatio=[0 for _ in range(len(component1Sentence))]
	patientClause2SpecificRatio=[0 for _ in range(len(component1Sentence))]
	patientNonSpecificRatio=[0 for _ in range(len(component1Sentence))]
	agentNonSpecificRatio=[0 for _ in range(len(component1Sentence))]
	totalClause1SpecificCount=[0 for _ in range(len(component1Sentence))]
	totalClause2SpecificCount=[0 for _ in range(len(component1Sentence))]
	totalNonSpecificCount=[0 for _ in range(len(component1Sentence))]

	#Instiate an updated decision matrix that takes into account scoring of sentence strengths
	decision2=['' for _ in range(len(component1Sentence))]


	info2=copy.deepcopy(info)
	info3=copy.deepcopy(infoGoogle)
	info4=copy.deepcopy(info2)
	#info5=copy.deepcopy(infoGoogle2)

	#Calculate Evidence Strengths and update decision matrix, decision2

	#For each winograd sentence:
	for f in range(0,len(component1Sentence)):
		agentCount[f]=0
		patientCount[f]=0
		totalCount[f]=0
		totalClause1SpecificCount[f]=0
		totalClause2SpecificCount[f]=0
		totalNonSpecificCount[f]=0

		#Keep popping from (copy of) info sets sentences and use them to increment patientCount or agentCount, incrementing twice if the sentences are more specific (containing clauses with more than one token length; i.e "was mad at" vs. "mad"--Do this for bing sentences
		while len(info2[f])>0:
			sentence=info2[f].pop()
			label=sentence[0]
			clause1=sentence[1]
			clause2=sentence[2]
			totalCount[f]+=1

			#If the sentence was labelled as evidence-agent and contained some multi-word clause, agentCount iterated by 2
			if (len(clause1.split(' '))>1 or len(clause2.split(' '))>1) and label=='agent':
				totalClause1SpecificCount[f]+=1
				agentClause1SpecificRatio[f]+=1
				agentCount[f]+=2
			#If the sentence was labelled as evidence-patient and contained some multi-word clause, patientCount iterated by 2
			if (len(clause1.split(' '))>1 or len(clause2.split(' '))>1) and label=='patient':
				totalClause1SpecificCount[f]+=1
				patientClause1SpecificRatio[f]+=1
				patientCount[f]+=2
			#If the sentence was labelled as evidence-patient and did not contain some multi-word clause, patientCount iterated by 1
			if len(clause2.split(' '))==1 and len(clause1.split(' '))==1 and label=='patient':
				totalNonSpecificCount[f]+=1
				patientNonSpecificRatio[f]+=1
				patientCount[f]+=1
			#If the sentence was labelled as evidence-agent and did not contain some multi-word clause, agentCount iterated by 1
			if len(clause2.split(' '))==1 and len(clause1.split(' '))==1 and label=='agent':
				totalNonSpecificCount[f]+=1
				agentNonSpecificRatio[f]+=1
				agentCount[f]+=1

			if label=='agent':
				agentClause1LengthAverage[f]+=len(clause1.split(' '))
				agentClause2LengthAverage[f]+=len(clause2.split(' '))
			
			elif label=='patient':
				patientClause1LengthAverage[f]+=len(clause1.split(' '))
				patientClause2LengthAverage[f]+=len(clause2.split(' '))
	
		#Do the same as above, but with Google sentences
			
		while len(info3[f])>0:
			sentence=info3[f].pop()
			label=sentence[0]
			clause1=sentence[1]
			clause2=sentence[2]
			totalCount[f]+=1

			if (len(clause1.split(' '))>1 or len(clause2.split(' '))>1) and label=='agent':
				totalClause1SpecificCount[f]+=1
				agentClause1SpecificRatio[f]+=1
				agentCount[f]+=2
			if (len(clause1.split(' '))>1 or len(clause2.split(' '))>1) and label=='patient':
				totalClause1SpecificCount[f]+=1
				patientClause1SpecificRatio[f]+=1
				patientCount[f]+=2

			if len(clause2.split(' '))==1 and len(clause1.split(' '))==1 and label=='patient':
				totalNonSpecificCount[f]+=1
				patientNonSpecificRatio[f]+=1
				patientCount[f]+=1
			if len(clause2.split(' '))==1 and len(clause1.split(' '))==1 and label=='agent':
				totalNonSpecificCount[f]+=1
				agentNonSpecificRatio[f]+=1
				agentCount[f]+=1
			if label=='agent':
				agentClause1LengthAverage[f]+=len(clause1.split(' '))
				agentClause2LengthAverage[f]+=len(clause2.split(' '))
			
			elif label=='patient':
				patientClause1LengthAverage[f]+=len(clause1.split(' '))
				patientClause2LengthAverage[f]+=len(clause2.split(' '))



				
	
		#Comparison rule determining value of decision2; if agentCount>patientCount, decision is that the winograd sentence is agent-resolving (value of 0), otherwise it is patient resolving (value of 1)
		if agentCount[f]>patientCount[f]:
			decision2[f]=0
		elif agentCount[f]<=patientCount[f] and (agentCount[f]!=0 or patientCount[f]!=0):
			decision2[f]=1

	
		#Other parameters that I didn't ultimately use but that were indicating ratios and other information about the sentences
		agentClause1LengthAverage[f]=agentClause1LengthAverage[f]/((totalCount[f]+1)*1.0)
		agentClause2LengthAverage[f]=agentClause2LengthAverage[f]/((totalCount[f]+1)*1.0)
		patientClause1LengthAverage[f]=patientClause1LengthAverage[f]/((totalCount[f]+1)*1.0)
		patientClause2LengthAverage[f]=patientClause2LengthAverage[f]/((totalCount[f]+1)*1.0)
		patientRatio[f]=patientCount[f]/((totalCount[f]+1)*1.0)
		agentRatio[f]=agentCount[f]/((totalCount[f]+1)*1.0)
		agentClause1SpecificRatio[f]=agentClause1SpecificRatio[f]/((totalClause1SpecificCount[f]+1)*1.0)
		agentClause1SpecificRatio[f]=agentClause2SpecificRatio[f]/((totalClause2SpecificCount[f]+1)*1.0)
		patientClause1SpecificRatio[f]=patientClause1SpecificRatio[f]/((totalClause1SpecificCount[f]+1)*1.0)
		patientClause2SpecificRatio[f]=patientClause2SpecificRatio[f]/((totalClause2SpecificCount[f]+1)*1.0)
		agentNonSpecificRatio[f]=agentNonSpecificRatio[f]/((totalNonSpecificCount[f]+1)*1.0)
		patientNonSpecificRatio[f]=patientNonSpecificRatio[f]/((totalNonSpecificCount[f]+1)*1.0)


	#Instantiate some variables
	decisionTrain=decision2[0:273]
	target=[0 for _ in range(len(decisionTrain))]
	decisionNP=numpy.array(decisionTrain)
	decisionNP[decisionNP==''] = numpy.nan
	decisionNP = decisionNP.astype(numpy.float)

	#Create an index matrix indicating which winograd sentences are class A (validWino), and which yielded results (answered)
	validWino=numpy.where(numpy.array(lexicalSchemeOriginal)==0)[0]
	answered=numpy.where(numpy.array(~numpy.isnan(decisionNP)))[0]

	#Number of Winograd Questions answered, and that were valid (Class A)
	numberOfWinogradAnsweredClassA=numpy.count_nonzero(~numpy.isnan(decisionNP[validWino]))

	#Number of Winograd Questions answered
	numberOfWinogradAnswered=numpy.count_nonzero(~numpy.isnan(decisionNP))

	#Number of Winograd Questions Correctly Answered
	correctA=0
	correctB=0
	correctC=0
	correctD=0

	#Open Winograd Solutions
	f2=open("winogradSolutions.txt")
	lines=f2.readlines()

	countOO=0

	#Fill up target matrix according to the solutions, which is a matrix indicating the correct and incorrect answers (0 is agent resolving, 1 is patient resolving) (entries should thus look like [0,1,0,1,0,1..]
	for f in range(0,len(decisionNP)):
		answer=lines[f*10+7].split('\n')[0].lower().split()[-1]

	
		if 1:
			if answer=='a':
				correctAnswer=0
				target[f]=correctAnswer
			else:
				correctAnswer=1
				target[f]=correctAnswer
			countOO=countOO+1
	

	
	countOO=0
	#Compare target with decision2, and iterate correct count.
	for f in range(0,len(decisionNP)):
		answer=lines[f*10+7].split('\n')[0].lower().split()[-1]

		#if not worried about only answering valid Winograd questions (Class A), then take out "f in validWino"
		if f in answered and f in validWino:
			if answer=='a':
				correctAnswer=0
			else:
				correctAnswer=1
			countOO=countOO+1
			if decision2[f]==correctAnswer:
				correctB+=1
	
		#featureMatrix[f]=featureMatrix[f][0:6]
	

	#The performance:
	correctTraditionalClassA=correctB/(numberOfWinogradAnsweredClassA*1.0)


	countOO=0

	#Compare target with decision2, and iterate correct count.
	for f in range(0,len(decisionNP)):
		answer=lines[f*10+7].split('\n')[0].lower().split()[-1]

		#if not worried about only answering valid Winograd questions (Class A), then take out "f in validWino"
		if f in answered:
			if answer=='a':
				correctAnswer=0
			else:
				correctAnswer=1
			countOO=countOO+1
			if decision2[f]==correctAnswer:
				correctA+=1
	
		#featureMatrix[f]=featureMatrix[f][0:6]
	

	#The performance:
	correctTraditional=correctA/(numberOfWinogradAnswered*1.0)



	#Relaxed Setting Performance
	decisionRelaxed=decision2

	#Relaxed Scenario (starting from Winograd Question 256 and higher, there is actually a Winograd-Triplet, so it shifts the assumption that the even number Winograd questions are the first in the twin, so correct for this.
	for f in range(0,len(decisionNP)):
		if f<256:
			if f%2==1:
				diffAgentPatientFirst=agentCount[f-1]-patientCount[f-1]
				diffAgentPatientSecond=agentCount[f]-patientCount[f]
				if diffAgentPatientFirst>diffAgentPatientSecond:
					decisionRelaxed[f-1]=0
					decisionRelaxed[f]=1
				elif diffAgentPatientFirst<diffAgentPatientSecond:
					decisionRelaxed[f-1]=1
					decisionRelaxed[f]=0	
		if f>=256:
			if f%2==0:
				diffAgentPatientFirst=agentCount[f-1]-patientCount[f-1]
				diffAgentPatientSecond=agentCount[f]-patientCount[f]
				if diffAgentPatientFirst>diffAgentPatientSecond:
					decisionRelaxed[f-1]=0
					decisionRelaxed[f]=1
				elif diffAgentPatientFirst<diffAgentPatientSecond:
					decisionRelaxed[f-1]=1
					decisionRelaxed[f]=0	

	
	#Calculate correct count	
	for f in range(0,len(decisionNP)):
		answer=lines[f*10+7].split('\n')[0].lower().split()[-1]

	
		if f in answered:
			if answer=='a':
				correctAnswer=0	
			else:
				correctAnswer=1
			countOO=countOO+1
			if decisionRelaxed[f]==correctAnswer:
				correctC+=1
	
		#featureMatrix[f]=featureMatrix[f][0:6]

	#Performance Relaxed:	
	correctRelaxedNoRestriction= correctC/(numberOfWinogradAnswered*1.0)

	
	for f in range(0,len(decisionNP)):
		answer=lines[f*10+7].split('\n')[0].lower().split()[-1]

	
		if f in answered and f in validWino:
			if answer=='a':
				correctAnswer=0
			else:
				correctAnswer=1
			countOO=countOO+1
			if decisionRelaxed[f]==correctAnswer:
				correctD+=1
	
		#featureMatrix[f]=featureMatrix[f][0:6]

	#Performance Relaxed:	
	correctRelaxedClassA= correctD/(numberOfWinogradAnsweredClassA*1.0)
	#Print Accuracies:

	print "Traditional Setting Performance, no class restrictions: "
	print "Number of Correct: " +str(correctA)
	print "Precision: " + str(correctTraditional) 
	print "Recall: " + str(correctA/273.0)
	print "F1: " + str((2*correctTraditional*(correctA/273.0))/(correctTraditional+(correctA/273.0)))

	print "" 
	print "" 

	print "Traditional Setting Performance, Class A: "
	print "Number of Correct: " +str(correctB)
	print "Precision: " + str(correctTraditionalClassA) 
	print "Recall: " + str(correctB/233.0)
	print "F1: " + str((2*correctTraditionalClassA*(correctB/233.0))/(correctTraditionalClassA+(correctB/233.0)))

	print "hello"

if __name__ == "__main__":
    main()


