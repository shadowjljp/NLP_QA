from Project import *
import time
index_sentence_time = time.time()
project = Project()
# %%
# insert articles
# project.insert_data_elasticsearch()

#project.delete_sentence_index()
#insert sentences
#project.index_sentences_elasticsearch('sentences')
#print("--- %s seconds ---" % (time.time() - index_sentence_time))
#~25 min
#%%
# query

question = "When did the Internet arrive in Iran?"


articlesId = project.query_articles(question)
results = project.search_sentences(question, articlesId, 'sentences', 10)
results1 = project.query_sentences_no_article(question, 'sentences')
print(results[0][2])

# %%
# accuracy
#project.article_accuracy()
#num in top 10 but not top 1: 479
#total questions: 2505
#top 1: 2009
#accuracy: 0.801996
#accuracy_sentence_time = time.time()
#project.sentence_accuracy()
#print("--- %s seconds ---" % (time.time() - accuracy_sentence_time))
#num in top 10 sentences but not top 1: 616
#total questions: 2505
#num correct: 1306
#accuracy: 0.521357

#project.sentence_accuracy()


#%%
#for task3 taking input file :xlsx
# output CSV
#example_file_path = "../QA_test/sample.xlsx"
#project.task3_xlsx(example_file_path)

#for task3 taking input file :txt
# output CSV
#example_file_path_txt = "../QA_test/short_test.txt"
example_file_path_txt= "../QA_test/test.txt"
project.task3_txt(example_file_path_txt)

#======================================================
# num in top 10: 2490
# total questions: 2505
# top 1: 2280
# accuracy: 0.994012

#%%
#for task1
# output txt file
#project.task1("../articles/58.txt")


