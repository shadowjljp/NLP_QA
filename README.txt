To run the project, the following needs to be installed:

1. Python
2. ElasticSearch 
   -download ElasticSearch to run locally: https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.16.1-windows-x86_64.zip
   -unzip the folder to a directory

To startup ElasticSearch, using CMD, cd to the elasticsearch-7.15.2 folder and enter the command: .\bin\elasticsearch.bat
If it does not work, cd to elasticsearch-7.15./bat and enter command: elasticsearch.bat

To demo the project, open run.py:

To index the information into Elasticsearch, uncomment the following lines and run:

	project.insert_data_elasticsearch()
	project.index_sentences_elasticsearch('sentences')

Note: Each takes about 25 min. to run. These two lines only need to run once, please comment them out once they are finished.

Demo Task 1
-Run project.task1(file_path) where file_path is the filepath of the file to extract the NLP features. The output file with the features will be generated in the QA_test folder called Task1_Output.txt.

Ex: file_path = "../articles/58.txt"


Demo Task 3 
-Run project.task3_txt(file_path) where file_path is the filepath of the input file containing the questions. The output will be generated in the QA_test folder called sample_output.csv.

Ex: file_path = "../QA_test/questions.txt"

Accuracy evaluation:
Input format is the same as Task3.

