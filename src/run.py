from Project import *
import time
index_sentence_time = time.time()
project = Project()

# %%
# insert articles in Elasticsearch
# project.insert_data_elasticsearch()

#insert sentences in Elasticsearch
#project.index_sentences_elasticsearch('sentences')

#%%
# for Task 1 demo

project.task1("../articles/58.txt")
project.task1("../QA_test/questions.txt")

#%%
# sample query for Task 2 demo

question = "Who came after Reza Shah renounced the throne?"
#question = "When was the Gadsden Purchase?"
#question = "Who is the Supreme Leader?"

articlesId = project.query_articles(question)
results = project.search_sentences(question, articlesId, 'sentences', 10)
answer = results[0][2]
print(answer)


#%%
# for Task 3 demo
#for task3 taking input file :xlsx
# output CSV
#example_file_path = "../QA_test/sample.xlsx"
#project.task3_xlsx(example_file_path)

#for task3 taking input file :txt
# output CSV
#example_file_path_txt = "../QA_test/short_test.txt"
#example_file_path_txt= "../QA_test/test.txt"
example_file_path_txt = "../QA_test/questions.txt"
project.task3_txt(example_file_path_txt)

#%%
# article accuracy on QA test set
#project.article_accuracy()

# sentence accuracy on QA test set
#accuracy_sentence_time = time.time()
#project.sentence_accuracy()
#print("--- %s seconds ---" % (time.time() - accuracy_sentence_time))


