from Project import *

project = Project()
# %%
# insert articles
# project.insert_data_elasticsearch()

#insert sentences
#project.index_sentences_elasticsearch('sentences')
#~25 min
#%%
# query
question = "When did Tucson's main power plant begin operation?"

articlesId = project.query_articles(question)
results = project.search_sentences(question, articlesId, 'sentences', 10)
print(results[0][2])
# %%
# accuracy
#project.article_accuracy()
#project.sentence_accuracy()

#======================================================
# num in top 10: 2490
# total questions: 2505
# top 1: 2280
# accuracy: 0.994012



