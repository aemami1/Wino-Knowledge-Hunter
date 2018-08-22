#+TITLE: Winograd Schema Challenge Knowledge Hunting Module
#+AUTHOR: Ali Emami

* Idea

Our  method  works  by  (i)  generating  queries  from  a  parsed  representation
of  a  Winograd  question,  (ii)  acquiring  rele- vant  knowledge  using  Information  Retrieval, and (iii) reasoning on the gathered knowledge.

** Procedure

1. (i) Query Generation Module -- moduleQueryGenerator.py. Must be run using flags indicating query generation method ("standard" or "synonym", as in, through the command prompt: "python moduleComponentExtractor.py standard". It produces the set C, the set Q, and the set containing the first entities for the 273 Winograd Sentences by using the parsed CoreNLP representation of the Winograd sentences and various linguistic rules.

2. (ii) Knowledge Hunting Module -- moduleKnowledgeHunter.py. Must be run using flags indicating query generation method ("standard", synonym", or "gold", as in, through the command prompt: "python moduleKnowledgeHunter.py standard". It takes the set C, the set Q, and the set containing the first entities for the 273 Winograd Sentences and scrapes Bing results for these sets queried in all combinations (i.e "refused" +"feared violence" -"councilmen"), resolves sentences that have an ambiguous target pronoun using CoreNLP, and outputs these in the form of sets of evidence sentences per Winograd sentence. 

(iii) Antecedent Selection Module -- moduleAntecedentSelection.py. Must be run using flags indicating query generation method ("standard" or "synonym", as in, through the command prompt: "python moduleAntecedentSelection.py standard". It takes the information produced by the previous module and weighs each sentence retrieved for each Winograd sentence and scores them in order to make a coreference decision, in both the traditional and relaxed Winograd setting. The module prints out results for each of the settings in terms of P, R and F1. 

