#import the NLP libraries
import stanza
import os # to access files
import nltk
from nltk.corpus import wordnet
nltk.download('wordnet')
stanza.download('en')

#NLP pipeline, tokenizing, sentence segmenation, POS tagging, lemmatization, dependency parsing, and named entity recognition
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,ner') 

#%%

#Input text file to extract the NLP features
#article = input() 
#print("Features from " + article + " will be extracted.")
article = "questions.txt"
#with open("../articles/" + article,'r', encoding='utf-8') as lines:
with open(article,'r', encoding='utf-8') as lines:
    sentences = []
    tokens = []
    lemmas = []
    pos = []
    ne = []
    dep = []
    hypernyms = []
    hyponyms = []
    meronyms = []
    holonyms = []
    synonyms = []
    
    for line in lines:
        doc = nlp(line)
        for sentence in doc.sentences:   
            sentences.append(sentence.text)
            token_sen = []
            pos_sen = []
            lemma_sen = []
            dep_sen = []
            ne_sen = []
            synonym_sen = []
            hypernym_sen = []
            hyponym_sen = []
            meronym_sen = []
            holonym_sen = []
            
            for word in sentence.words:
                #tokenize a sentence.
                token_sen.append(word.text)
                #part of speech tag: format is like this : word_POS
                pos_sen.append(word.text + "_" + word.upos)
                #lemma format is like this : word_lemma
                lemma_sen.append(word.text + "_" + word.lemma)
                
                # Dependency Parsing
                if word.head > 0:
                    head = sentence.words[word.head - 1].text
                else:
                    head = "root"
                dep_sen.append('id:' + str(word.id) + '\tword:' +  word.text + '\thead id:'+ str(word.head) + '\thead:' + head + '\tdeprel:' + word.deprel + '\n')
                
                # Use WordNet to extract the hypernyms, hyponyms, meronyms, and holonyms
                if word.upos == "NOUN":
                    synset = wordnet.synsets(word.text, pos=wordnet.NOUN)
                elif word.upos == "VERB":
                    synset = wordnet.synsets(word.text, pos=wordnet.VERB)
                elif word.upos == "ADJ":
                    synset = wordnet.synsets(word.text, pos=wordnet.ADJ)
                elif word.upos == "ADV":
                    synset = wordnet.synsets(word.text, pos=wordnet.ADV)
                else:
                    synset = []
                    
                if(len(synset) > 0):  
                    syn = word.text + ": "
                    for s in synset:
                        for l in s.lemmas():
                            if l.name() not in syn:
                                syn += l.name() + " "
                    syn += "|"
                    synonym_sen.append(syn)
                    
                    
                for syn in synset:
                    if(len(synset) > 0):
                        #extract hypernyms
                        if(len(syn.hypernyms()) > 0):
                            hyper = word.text + ": "
                            for h in syn.hypernyms():
                                for l in h.lemmas():
                                    hyper += l.name() + " "
                            hyper += "|"
                            hypernym_sen.append(hyper)
                        
                        #extract hyponyms
                        if(len(syn.hyponyms()) > 0):
                            hypo = word.text + ": "
                            for h in syn.hyponyms():
                                for l in h.lemmas():
                                    hypo += l.name() + " "
                            hypo += "|"
                            hyponym_sen.append(hypo)
                        
                        #extract holonyms
                        if(len(syn.part_holonyms()) > 0):
                            holo = word.text + ": "
                            for h in syn.part_holonyms():
                                for l in h.lemmas():
                                    holo += l.name() + " "
                            holo += "|"
                            holonym_sen.append(holo)
                        
                        #extract meronyms
                        if(len(syn.part_meronyms()) > 0):
                            mero = word.text + ": "
                            for h in syn.part_meronyms():
                                for l in h.lemmas():
                                    mero += l.name() + " "
                            mero += "|"
                            meronym_sen.append(mero)
                                                
                        
#            for ent in sentence.ents:
#                #named entity format is like this: entity_type
#                ne_sen.append(ent.text + "_" + ent.type)
                        
            tokens.append(token_sen)
            pos.append(pos_sen)
            lemmas.append(lemma_sen)
            dep.append(dep_sen)
            ne.append(ne_sen)
            hypernyms.append(hypernym_sen)
            hyponyms.append(hyponym_sen)
            meronyms.append(meronym_sen)
            holonyms.append(holonym_sen)
            synonyms.append(synonym_sen)
                
                
#%%
#Write the extracted features to a text file called Task1_Output.txt
with open("Task1_Output.txt", 'w', encoding='utf-8') as output:
    for i, sen in enumerate(sentences):
        output.write("Sentence " + str(i) + ": " + sen + "\n")
        output.write("Tokens: " + "  ".join(tokens[i]) + "\n")
        output.write("Lemmas: " + " ".join(lemmas[i]) + "\n")
        output.write("POS: " + "  ".join(pos[i]) + "\n")
        output.write("Dependency parsing: " + "\t".join(dep[i]) + "\n")
        output.write("Synonyms: " + " ".join(synonyms[i]) + "\n")
        output.write("Hypernyms: " + " ".join(hypernyms[i]) + "\n")
        output.write("Hyponyms: " + " ".join(hyponyms[i]) + "\n")
        output.write("Holonyms: " + " ".join(meronyms[i]) + "\n")
        output.write("Meronyms: " + " ".join(holonyms[i]) + "\n")
        output.write("\n")
    
    