import pandas as pd
import requests
import stanza
import os  # to access files
import nltk
from nltk.corpus import wordnet
from queue import PriorityQueue
import csv
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
                            lemmas.append(word.text + "_" + word.lemma)
                        for ent in sentence.ents:
                            # named entity format is like this: entity_type
                            ne.append(ent.text + "_" + ent.type)

                        es_sentence = {
                            'article_id': int(article_id),
                            'original_sentence': sentence.text,
                            'text': tokens,
                            'pos': pos,
                            'ne': ne,
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
                        es_sentence = {}

    #        es_doc = {
    #             'article_id': int(article_id),
    #             'sentences' :[
    #                   {
    #                   'sentence': sentence_original_text,
    #                   'lemma' : lemma
    #                   'text': tokens,
    #                   'pos': pos,
    #                   'ne': ne
    #                   }
    #             ],
    #         }
    #
    #
    #
    #
    #
    #
    #
    #

    # query processing
    # ADD dependency parsing and wordnet

    # %%
    def query_articles(self, question):
        question = question
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
            for word in sentence.words:
                # tokenize a sentence.
                query += word.text + " "
                # part of speech tag: format is like this : word_POS
                query_pos += word.text + "_" + word.upos + " "
                # lemma format is like this : word_lemma
                query_lemma += word.text + "_" + word.lemma + " "

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
                    syn_name = syn.name().split('.')[0]
                    if syn_name != word.text and synonyms.find(syn_name) == -1:
                        synonyms += syn_name + " "
                        # Extract hypernymns
                    hyper = syn.hypernyms()
                    for h in hyper:
                        h_name = h.name().split('.')[0]
                        hypernyms += h_name + " "
                    hypo = syn.hyponyms()
                    for h in hypo:
                        h_name = h.name().split('.')[0]
                        hyponyms += h_name + " "
                    holo = syn.part_holonyms()
                    for h in holo:
                        h_name = h.name().split('.')[0]
                        holonyms += h_name + " "
                    mero = syn.part_meronyms()
                    for m in mero:
                        m_name = m.name().split('.')[0]
                        meronyms += m_name + " "

            for ent in sentence.ents:
                # named entity format is like this: entity_type
                query_ne += ent.text + "_" + ent.type + " "

        #        print(query)
        #        print(query_pos)
        #        print(query_lemma)
        #        print(query_ne)
        #        print(synonyms)
        #        print(hypernyms)
        #        print(hyponyms)
        #        print(holonyms)
        #        print(meronyms)
        #        print(query + synonyms + hypernyms)

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

        # search_param = {
        #
        #            "bool": {
        #              "should": [
        #                {"match": {
        #                   "text" : query
        #                }
        #              },
        #                {
        #                  "match": {
        #                    "pos": query_pos
        #                  }
        #                }
        #
        #              ]
        #            }
        #
        # }

        # search_param = {
        #        'match': {
        #            'text': query
        #        }
        # }

        # execute query
        res = Project.es.search(index=Project.index_name, query=search_param)
        # print('===================================')
        # print('res', res)
        # print('===================================')
        # print([(hit['_source']['article_id'], hit['_score']) for hit in res['hits']['hits']])
        result = [hit['_source']['article_id'] for hit in res['hits']['hits']]
        return result
        # [(222, 28.443619), (360, 20.216982), (273, 19.12777), (177, 17.02761), (287, 15.546484), (288, 14.089401), (179, 14.036338), (56, 13.599551), (109, 12.828577), (282, 12.752726)]

    # %%
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
                syn_name = syn.name().split('.')[0]
                if syn_name != word.text and self.synonyms.find(syn_name) == -1:
                    self.synonyms += syn_name + " "
                    # Extract hypernymns
                hyper = syn.hypernyms()
                for h in hyper:
                    h_name = h.name().split('.')[0]
                    self.hypernyms += h_name + " "
                hypo = syn.hyponyms()
                for h in hypo:
                    h_name = h.name().split('.')[0]
                    self.hyponyms += h_name + " "
                holo = syn.part_holonyms()
                for h in holo:
                    h_name = h.name().split('.')[0]
                    self.holonyms += h_name + " "
                mero = syn.part_meronyms()
                for m in mero:
                    m_name = m.name().split('.')[0]
                    self.meronyms += m_name + " "

        for ent in sentence.ents:
            # named entity format is like this: entity_type
            self.query_ne += ent.text + "_" + ent.type + " "

    # %%
    # Run query_builder before running this one, it builds proper search_param for the elasticsearch, need to run multiple times for different article_id
    # Output: single search result in list.  (score after weigh, articles id, sentence)
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
        result = [(hit['_source']['original_sentence'], hit['_score'], hit['_source']['article_id']) for hit in res['hits']['hits']]
        # print(result)

        # print([( hit['_source']['article_id'], hit['_score']) for hit in
        # res['hits']['hits']])
        return result

    # %%
    # output list (score, id, text) with weigh
    def search_sentences(self, question, articlesId, index_name, weigh):
        results = []
        self.pq.queue.clear()
        query_nlp = self.nlp(question)
        for sentence in query_nlp.sentences:
            self.query_builder(sentence)
        for id in articlesId:
            tuple_list_total = self.search_param_builder(question, id, index_name)  # ('text', 21.672752, 222)
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
    def accuracy(self):
        total_sen = 0
        num_top10 = 0
        num_top1 = 0
        with open(os.path.join(os.getcwd(), '..', "QA_test\QA Data.txt"), 'r',
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
                    query = ""
                    query_pos = ""
                    query_lemma = ""
                    query_ne = ""
                    synonyms = []
                    hypernyms = []
                    hyponyms = []
                    meronymns = []
                    holonyms = []

                    # also perform dependency parsing
                    query_nlp = Project.nlp(q)
                    for sentence in query_nlp.sentences:
                        for word in sentence.words:
                            # tokenize a sentence.
                            query += word.text + " "
                            # part of speech tag: format is like this : word_POS
                            query_pos += word.text + "_" + word.upos + " "
                            # lemma format is like this : word_lemma
                            query_lemma += word.text + "_" + word.lemma + " "

                        for ent in sentence.ents:
                            # named entity format is like this: entity_type
                            query_ne += ent.text + "_" + ent.type + " "

                    search_param = {

                        "bool": {
                            "should": [
                                {"match": {
                                    "text": query
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
                    top_docs = [(hit['_source']['article_id']) for hit in res['hits']['hits']]
                    cnt = 0
                    for doc in top_docs:
                        cnt += 1
                        if int(article) == doc:
                            num_top10 += 1
                            if (cnt == 1):
                                num_top1 += 1
                            break

        data.close()

        print("num in top 10: " + str(num_top10))
        print("total questions: " + str(total_sen))
        print("top 1: " + str(num_top1))
        print("accuracy: %f" % (num_top10 / total_sen))

    # %%
    # test the accuracy of the sentence retrieval model on QA data
    # ~20 min to run
    def sentence_accuracy(self):
        total_sen = 0
        num_top10 = 0
        num_correct = 0
        #        with open(os.path.join(os.getcwd(), '..', "QA_test\QA Data.txt"), 'r',
        #                  encoding='utf-8') as data:

        with open(os.path.join(os.getcwd(),"..", "QA_test\QA Data.txt"), 'r',
                  encoding='utf-8') as data, open("Missed_questions.txt", 'w', encoding='utf-8') as missed:
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


    def task3(self, example_file_path):
        data = pd.read_excel(example_file_path)
        with open('../QA_test/sample_output.csv','w',newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',',quotechar=" ",quoting=csv.QUOTE_MINIMAL)
            for index, row in data.iterrows():
                question = row['question']
                top10_id = self.query_articles(question) #(article id, score)
                #print(top10_id)
                result = self.search_sentences(question,top10_id,"sentences",10)  #(score, article_id, answer_sentence) in list
                article_id = result[0][1]
                answer_sentence = result[0][2]
                #print(article_id)
                #print(answer_sentence)
                spamwriter.writerow([question, article_id, answer_sentence])
