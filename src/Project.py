import requests
import stanza
import os  # to access files
import nltk
from nltk.corpus import wordnet
from queue import PriorityQueue
# https://www.elastic.co/guide/en/elasticsearch/reference/current/zip-windows.html
# https://towardsdatascience.com/getting-started-with-elasticsearch-in-python-c3598e718380
# setup elastic search locally
from elasticsearch import Elasticsearch


class Project():
    nlp = stanza.Pipeline(lang='en',
                          processors='tokenize,mwt,pos,lemma,depparse,ner')
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    index_name = 'articles'
    query = ""
    query_pos = ""
    query_lemma = ""
    query_ne = ""
    synonyms = ""
    hypernyms = ""
    hyponyms = ""
    meronyms = ""
    holonyms = ""

    # priorityQueue
    pq = PriorityQueue()

    # %%
    def delete_sentence_index(self):
        self.es.indices.delete(index='sentences', ignore=400)

    # %%

    # insert/index the articles into elasticsearch
    def insert_data_elasticsearch(self):
        # Using WordNet, extract hypernymns, hyponyms, meronyms, AND holonyms as features
        nltk.download('wordnet')

        stanza.download('en')
        # added depparse for dependency parsing

        Project.es.ping()

        if not Project.es.indices.exists(Project.index_name):
            Project.es.indices.create(index=Project.index_name, ignore=400)
            print("index created")

        # NLP pipeline
        # Tokenize text into  sentences and words.
        # Lemmatize the words to extract lemmas as features
        # POS tag the words to extract POS tag features
        path = os.path.join(os.getcwd(), '..', 'articles')
        for article in os.listdir(path):
            # avoid .ds_store hidden file
            if (article.startswith('.')):
                continue
            i = article.split('/')
            # sentences = []
            tokens = []
            # lemmas = []
            pos = []
            ne = []
            es_doc = {}

            # for article in os.listdir(os.getcwd()):
            with open(os.path.join(path, article), 'r', encoding='utf-8') as lines:
                article_id = os.path.splitext(i[-1])[0]
                for line in lines:
                    print(f'====== Name of Article {i[-1]}  =======')
                    # print(line)
                    doc = Project.nlp(line)
                    for sentence in doc.sentences:
                        # sentences.append(sentence.text)
                        # print(sentence)
                        for word in sentence.words:
                            # tokenize a sentence.
                            tokens.append(word.text)
                            # part of speech tag: format is like this : word_POS
                            pos.append(word.text + "_" + word.upos)
                            # lemma format is like this : word_lemma
                            # lemmas.append(word.text + "_" + word.lemma)
                        for ent in sentence.ents:
                            # named entity format is like this: entity_type
                            ne.append(ent.text + "_" + ent.type)

                es_doc = {
                    'article_id': int(article_id),
                    'text': tokens,
                    'pos': pos,
                    'ne': ne
                }
                res = Project.es.index(index=Project.index_name, id=article_id, document=es_doc)
                print(res['result'])
                # article.close()

    # %%
    def index_sentences_elasticsearch(self, index_name):
        path = os.path.join(os.getcwd(), '..', 'articles')
        for article in os.listdir(path):
            # avoid .ds_store hidden file
            if (article.startswith('.')):
                continue
            i = article.split('/')
            # sentences = []
            tokens = []
            lemmas = []
            pos = []
            ne = []
            ne_types = []
            es_sentence = {}

            with open(os.path.join(path, article), 'r', encoding='utf-8') as lines:
                article_id = os.path.splitext(i[-1])[0]
                for line in lines:
                    print(f'====== Name of Article {i[-1]}  =======')
                    # print(line)
                    doc = self.nlp(line)
                    for sentence in doc.sentences:
                        # sentences.append(sentence.text)
                        # print(sentence)
                        for word in sentence.words:
                            # tokenize a sentence.
                            tokens.append(word.text)
                            # part of speech tag: format is like this : word_POS
                            pos.append(word.text + "_" + word.upos)
                            # lemma format is like this : word_lemma
                            #lemmas.append(word.text + "_" + word.lemma)
                            lemmas.append(word.lemma)
                        for ent in sentence.ents:
                            # named entity format is like this: entity_type
                            ne.append(ent.text + "_" + ent.type)
                            ne_types.append(ent.type)

                        es_sentence = {
                            'article_id': int(article_id),
                            'original_sentence': sentence.text,
                            'text': tokens,
                            'pos': pos,
                            'ne': ne,
                            'ne_types': ne_types,
                            'lemmas': lemmas,
                        }
                        # print(article_id, tokens)
                        res = self.es.index(index=index_name, document=es_sentence)
                        # print(res['result'])
                        # print(tokens)
                        # print(pos)
                        tokens = []
                        lemmas = []
                        pos = []
                        ne = []
                        ne_types = []
                        es_sentence = {}



#%%
# Extract the tokens
    def extract_tokens(self,sentence):
        tokens = ""
        for word in sentence.words:
            tokens += word.text + " "
                
        return tokens
        

#%%
# Extract the lemmas
    def extract_lemmas(self,sentence, include_token):
        lemma = ""
        for word in sentence.words:
            if include_token == True:
                lemma += word.text + "_" + word.lemma + " "
            else:
                lemma += word.lemma + " " 
                
        return lemma

#%% Extract the POS tags
    def extract_pos(self,sentence):
        pos = ""
        for word in sentence.words:
            pos += word.text + "_" + word.upos + " " 
            
        return pos

#%% Extract WordNet synonyms
    def extract_synonyms(self, synset):
        synonyms = ""
        for syn in synset:
#                    syn_name = syn.name().split('.')[0]
#                    if syn_name != word.text and synonyms.find(syn_name) == -1:
#                        synonyms += syn_name + " "
            for l in syn.lemmas():
                if l.name() not in synonyms:
                    synonyms += l.name() + " "
        return synonyms

#%% Extract WordNet hypernyms
    def extract_hypernyms(self, synset):
        hypernyms = ""
        for syn in synset:
            hyper = syn.hypernyms()
            for h in hyper:
#                        h_name = h.name().split('.')[0]
#                        hypernyms += h_name + " "
                for l in h.lemmas():
                    if l.name() not in hypernyms:
                        hypernyms += l.name() + " "
        return hypernyms
            
#%% Extract WordNet hyponyms
    def extract_hyponyms(self, synset):
        hyponyms = ""
        for syn in synset:
            hypo = syn.hyponyms()
            for h in hypo:
#                        h_name = h.name().split('.')[0]
#                        hyponyms += h_name + " "
                for l in h.lemmas():
                    if l.name() not in hyponyms:
                        hyponyms += l.name() + " "
        return hyponyms
#%% Extract WordNet holonyms
    def extract_holonyms(self, synset):
        holonyms = ""
        for syn in synset:
            holo = syn.part_holonyms()
            for h in holo:
#                        h_name = h.name().split('.')[0]
#                        holonyms += h_name + " "
                for l in h.lemmas():
                    if l.name() not in holonyms:
                        holonyms += l.name() + " "
        return holonyms

#%% Extract WordNet meronyms
    def extract_meronyms(self, synset):
        meronyms = ""
        for syn in synset:
            mero = syn.part_meronyms()
            for m in mero:
#                        m_name = m.name().split('.')[0]
#                        meronyms += m_name + " "
                for l in m.lemmas():
                    if l.name() not in meronyms:
                        meronyms += l.name() + " "
        return meronyms
    
#%% Extract Named entities
    def extract_ne(self, sentence):
        ne = ""
        for ent in sentence.ents:
            ne += ent.text + "_" + ent.type + " "
        return ne
            

    # %%
    def query_articles(self, question):
        query = ""
        query_pos = ""
        query_lemma = ""
        query_ne = ""
        synonyms = ""
        hypernyms = ""
        hyponyms = ""
        meronyms = ""
        holonyms = ""

        query_nlp = Project.nlp(question)
        
        for sentence in query_nlp.sentences:
            # tokenize a sentence.
            query += self.extract_tokens(sentence)
            # part of speech tag: format is like this : word_POS
            query_pos += self.extract_pos(sentence)
            # lemma format is like this : word_lemma
            query_lemma += self.extract_lemmas(sentence, False)
            # named entity format is like this: entity_type
            query_ne += self.extract_ne(sentence)
            
            for word in sentence.words:
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
                    
                synonyms += self.extract_synonyms(synset)
                hypernyms += self.extract_hypernyms(synset)
                hyponyms += self.extract_hyponyms(synset)
                holonyms += self.extract_holonyms(synset)
                meronyms += self.extract_meronyms(synset)


            
        search_param = {

            "bool": {
                "should": [
                    {"match": {
                        "text": query + synonyms + hypernyms 
                    }
                    },
                    {
                        "match": {
                            "pos": query_pos
                        }
                    },
                    {
                        "match": {
                            "ne": query_ne
                        }
                    }
                ]
            }

        }

        # execute query
        res = Project.es.search(index=Project.index_name, query=search_param)
        result = [hit['_source']['article_id'] for hit in res['hits']['hits']]
        return result




    
#%%
    def query_sentences(self, question, articlesId, index_name):
        query = ""
        query_pos = ""
        query_lemma = ""
        query_ne = ""
        synonyms = ""
        hypernyms = ""
        hyponyms = ""
        holonyms = ""
        meronyms = ""
        
        query_nlp = Project.nlp(question)
        
        for sentence in query_nlp.sentences:
            # tokenize a sentence.
            query += self.extract_tokens(sentence)
            # part of speech tag: format is like this : word_POS
            query_pos += self.extract_pos(sentence)
            # lemma format is like this : word_lemma
            query_lemma += self.extract_lemmas(sentence, False)
            # named entity format is like this: entity_type
            query_ne += self.extract_ne(sentence)
            
            for word in sentence.words:
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
                    
                synonyms += self.extract_synonyms(synset)
                hypernyms += self.extract_hypernyms(synset)
                hyponyms += self.extract_hyponyms(synset)
                holonyms += self.extract_holonyms(synset)
                meronyms += self.extract_meronyms(synset)
                #print(synonyms)
            
        if "when" in question.lower():
            #print("when")
            search_param = {

                "bool": {
                    "must" : {"match": {
                                "ne_types": "DATE"
                                }
                            },
                    "filter": {
                        "term": {"article_id": articlesId},
                    },
                    "should": [
                        {"match": {
                            "text": query + synonyms + hypernyms
                        }
                        },
                        {
                            "match": {
                                "pos": query_pos
                            }
                        },
                        {
                            "match": {
                                "lemma": query_lemma
                            }
                        },
                        {
                            "match": {
                                "ne": query_ne
                            }
                        }
    
                    ],
    
                }
            }
        elif "who" in question.lower():
            #print("when")
            search_param = {

                "bool": {
                    "must" : {"match": {
                                "ne_types": "PERSON + ORG"
                                }
                            }, 
                    "filter": {
                        "term": {"article_id": articlesId},
                    },
                    "should": [
                        {"match": {
                            "text": query + synonyms + hypernyms
                        }
                        },
                        {
                            "match": {
                                "pos": query_pos
                            }
                        },
                        {
                            "match": {
                                "lemma": query_lemma
                            }
                        },
                        {
                            "match": {
                                "ne": query_ne
                            }
                        }
    
                    ],
    
                }
            }
        else:
            search_param = {
    
                "bool": {
                    "filter": {
                        "term": {"article_id": articlesId}
                    },
                    "should": [
                        {"match": {
                            "text": query + synonyms + hypernyms
                        }
                        },
                        {
                            "match": {
                                "pos": query_pos
                            }
                        },
                        {
                            "match": {
                                "ne": query_ne
                            }
                        },
                        {
                            "match": {
                                "lemma": query_lemma
                            }
                        },
    
                    ],
    
                }
            }
                
        res = self.es.search(index=index_name, query=search_param)
        result = [(hit['_source']['original_sentence'], hit['_score'], hit['_source']['article_id']) for hit in
                  res['hits']['hits']]

        return result

        
        

    # %%
    # output list (score, id, text) with weigh
    def search_sentences(self, question, articlesId, index_name, weigh):
        results = []
        self.pq.queue.clear()
        #query_nlp = self.nlp(question)
        #for sentence in query_nlp.sentences:
            #self.query_builder(sentence)
        for id in articlesId:
            #tuple_list_total = self.search_param_builder(question, id, index_name)  # ('text', 21.672752, 222)
            tuple_list_total = self.query_sentences(question, id, index_name)
            for tuple_list in tuple_list_total:
                self.pq.put((tuple_list[1] * -1 * weigh, tuple_list[2], tuple_list[0]))  # (score, id, text)
            weigh -= 1

        top_10 = 0
        while top_10 < 10:
            top_10 += 1
            # print(f'top {top_10} sentences ', self.pq.get())
            results.append(self.pq.get())

        return results

    # %%
    # test the accuracy of the IR model on QA data
    def article_accuracy(self):
        total_sen = 0
        num_top10 = 0
        num_top1 = 0
        with open(os.path.join(os.getcwd(), '..', "QA_test\QA Data1.txt"), 'r',
                  encoding='utf-8') as data:
            lines = data.readlines()
            for line in lines:
                article = line[line.find("[") + 1: line.find(",")]
                print(article)
                new_line = line.split("(", 1)[1]
                # print(new_line)
                questions = new_line.split(", (")
                for question in questions:
                    total_sen += 1
                    q = question[1: question.find("?") + 1]
                    # print(q + "\n")
                    
                    if( q != " "):
                        articlesId = self.query_articles(q)

                        in_top10 = False
                        for i,doc in enumerate(articlesId):
                            if int(article) == doc and in_top10 == False:
                                if i == 0:
                                    num_top1 += 1
                                    break
                                else:
                                    num_top10 += 1
                                    in_top10 = True
                                    
                                

        data.close()

        print("num in top 10 but not top 1: " + str(num_top10))
        print("total questions: " + str(total_sen))
        print("top 1: " + str(num_top1))
        print("accuracy: %f" % (num_top1 / total_sen))

    # %%
    # test the accuracy of the sentence retrieval model on QA data
    # ~20 min to run
    def sentence_accuracy(self):
        total_sen = 0
        num_top10 = 0
        num_correct = 0
        with open(os.path.join(os.getcwd(), '..', "QA_test\QA Data.txt"), 'r',
                  encoding='utf-8') as data, open("Missed_questions.txt", 'w', encoding='utf-8') as missed:

#        with open(os.path.join(os.getcwd(), "QA_test\QA Data.txt"), 'r',
#                  encoding='utf-8') as data, open("Missed_questions.txt", 'w', encoding='utf-8') as missed:
            lines = data.readlines()
            for line in lines:
                article = line[line.find("[") + 1: line.find(",")]
                # print(article)
                new_line = line.split("(", 1)[1]
                # print(new_line)
                questions = new_line.split(", (")
                for question in questions:
                    total_sen += 1
                    q = question[1: question.find("?") + 1]
                    # print(q + "\n")
                    answer = question[question.find("?") + 5: question.find("')")]
                    # answer = question[question.find(",") + 2: question.find("')")]
                    cleaned_answer = answer.strip("'\"")

                    if (q != ""):
                        articlesId = self.query_articles(q)
                        results = self.search_sentences(question, articlesId, 'sentences', 10)

                        correct = False
                        in_top10 = False
                        top_ans = results[0][2]
                        for i, result in enumerate(results):
                            if cleaned_answer in result[2] and in_top10 == False:
                                if (i == 0):
                                    num_correct += 1
                                    correct = True
                                    break
                                else:
                                    num_top10 += 1
                                    in_top10 = True
                        if correct == False:
                            missed.write(article + "\t" + q + "\t" + cleaned_answer + "\t" + top_ans + "\n")
                            print(q)

        data.close()

        print("num in top 10 sentences but not top 1: " + str(num_top10))
        print("total questions: " + str(total_sen))
        print("num correct: " + str(num_correct))
        print("accuracy: %f" % (num_correct / total_sen))

#%%
    # Build the query, query_POS,query_lemma and wordnet, only need to run it once
    def query_builder(self, sentence):
        self.query = ""
        self.query_pos = ""
        self.query_lemma = ""
        self.query_ne = ""
        self.synonyms = ""
        self.hypernyms = ""
        self.hyponyms = ""
        self.holonyms = ""
        self.meronyms = ""

        for word in sentence.words:
            # tokenize a sentence.
            self.query += word.text + " "
            # part of speech tag: format is like this : word_POS
            self.query_pos += word.text + "_" + word.upos + " "
            # lemma format is like this : word_lemma
            self.query_lemma += word.text + "_" + word.lemma + " "

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

            for syn in synset:
#                syn_name = syn.name().split('.')[0]
#                if syn_name != word.text and self.synonyms.find(syn_name) == -1:
#                    self.synonyms += syn_name + " "
                for l in syn.lemmas():
                        if l.name() not in self.synonyms:
                            self.synonyms += l.name() + " "
                    # Extract hypernymns
                hyper = syn.hypernyms()
                for h in hyper:
#                    h_name = h.name().split('.')[0]
#                    self.hypernyms += h_name + " "
                    for l in h.lemmas():
                            if l.name() not in self.hypernyms:
                                self.hypernyms += l.name() + " "
                hypo = syn.hyponyms()
                for h in hypo:
#                    h_name = h.name().split('.')[0]
#                    self.hyponyms += h_name + " "
                    for l in h.lemmas():
                            if l.name() not in self.hyponyms:
                                self.hyponyms += l.name() + " "
                holo = syn.part_holonyms()
                for h in holo:
#                    h_name = h.name().split('.')[0]
#                    self.holonyms += h_name + " "
                    for l in h.lemmas():
                            if l.name() not in self.holonyms:
                                self.holonyms += l.name() + " "
                mero = syn.part_meronyms()
                for m in mero:
#                    m_name = m.name().split('.')[0]
#                    self.meronyms += m_name + " "
                    for l in m.lemmas():
                            if l.name() not in self.meronyms:
                                self.meronyms += l.name() + " "

        for ent in sentence.ents:
            # named entity format is like this: entity_type
            self.query_ne += ent.text + "_" + ent.type + " "

#%%
    # Run query_builder before running this one, it builds proper search_param for the elasticsearch, need to run multiple times for different article_id
    # Output: Returns top 10 results in list.  (score after weigh, articles id, sentence)
    def search_param_builder(self, question, articlesId, index_name):
        question = question.strip().lower()
        question_arr = question.split()
        if question_arr[0] != 'what':
            search_param = {

                "bool": {
                    "filter": {
                        "term": {"article_id": articlesId}
                    },
                    "should": [
                        {"match": {
                            "text": self.query + self.synonyms + self.hypernyms 
                        }
                        },
                        {
                            "match": {
                                "pos": self.query_pos
                            }
                        },
                        {
                            "match": {
                                "lemma": self.query_lemma
                            }
                        },

                    ],

                }
            }
        else:
            search_param = {

                "bool": {
                    "filter": {
                        "term": {"article_id": articlesId}
                    },
                    "should": [
                        {"match": {
                            "text": self.query + self.synonyms + self.hypernyms
                        }
                        },
                        {
                            "match": {
                                "pos": self.query_pos
                            }
                        },
                        {
                            "match": {
                                "ne": self.query_ne
                            }
                        },
                        {
                            "match": {
                                "lemma": self.query_lemma
                            }
                        },

                    ],

                }
            }
        res = self.es.search(index=index_name, query=search_param)
        # print(self.query)  # What enables scientists to better study plants now ?
        # print(self.query_pos)
        # print(self.query_lemma)
        # print(query_ne)
        # print('synonyms ==> ', self.synonyms)
        # print('hypernyms ==> ', self.hypernyms)
        # print(self.query + self.synonyms + self.hypernyms)
        # print('===================================')
        # print('res', res)
        # print('===================================')
        # result = [(" ".join(hit['_source']['text']), hit['_score'], hit['_source']['article_id']) for hit in res['hits']['hits']]
        result = [(hit['_source']['original_sentence'], hit['_score'], hit['_source']['article_id']) for hit in
                  res['hits']['hits']]
        # print(result)

        # print([( hit['_source']['article_id'], hit['_score']) for hit in
        # res['hits']['hits']])
        return result