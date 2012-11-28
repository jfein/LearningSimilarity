import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus.reader.wordnet import WordNetError
from collections import Counter

DATA_PATH = "../data/taggers.txt"
f = open(DATA_PATH, 'r')
tags= {}
for line in f:
        line= line.strip()
        pair= line.split(' ')
        tags[pair[0]]= pair[1]

sentence = "dog"
tokens = nltk.word_tokenize(sentence)
tagged = nltk.pos_tag(tokens)
newSentence = ""
print tagged[0]
i = 0;
for tag in tagged:
	if tag[1] in tags:
		word = tokens[i]
		pos = tags[tag[1]]
		listOfSyn = []
		print pos
		senses = ["01", "02", "03", "04", "05", "06"]
		try:
		
			for s in senses:
				string =  word + "." + pos + "." + s 
				try:
					new = wn.synset(string)
					print new.lemma_names
					listOfSyn = listOfSyn +  new.lemma_names
				except WordNetError:
					print "No more senses after sense " + s
			listOfSyn.sort()
			counter = Counter(listOfSyn)	
			listOfSyn[0] = counter.most_common()[0][0]
			if len(newSentence) == 0:
				newSentence = newSentence + listOfSyn[0]
			else:
				newSentence = newSentence + " " + listOfSyn[0]
		except WordNetError:
			if len(newSentence) == 0:
				newSentence = newSentence + tag[0]
			else:
				newSentence = newSentence + " " + tag[0]

	
	else: 
		if len(newSentence) == 0:
			newSentence = newSentence + tag[0]
		else:
			newSentence = newSentence + " " + tag[0]
	i=i+1	
print newSentence
