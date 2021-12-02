from Project import *

project = Project()
# %%
# insert articles
# project.insert_data_elasticsearch()

#insert sentences
#project.index_sentences_elasticsearch('sentences')

# %%
# query

question = "What enables scientists to better study plants now?"
articlesId = project.query_articles(question)
project.search_sentences(question, articlesId, 'sentences', 10)

# %%
# accuracy
# project.accuracy()

#======================================================
# num in top 10: 2490
# total questions: 2505
# top 1: 2280
# accuracy: 0.994012
