## Project 3 - Search Engine - Search and Retrieval
## search_engine.py

import sys
import pickle
import time
from nltk.tokenize import RegexpTokenizer
import json


class SearchEngine():

    def __init__(self,query,index):
        self.query = query
        self.index = index

    def token_query(self):
        regular_expression = "\w+"
        tokenizer = RegexpTokenizer(regular_expression)
        query_dict = {}

        tokenized_query = tokenizer.tokenize(self.query.lower())

        for token in tokenized_query:
            if token not in query_dict.keys():
                query_dict[token] = self.index[token]








                #query_dict[token] = 0
                #query_dict[token] += score


        return query_dict

    def score_query(self,query_dict):
        scored_dict = {}
        for token in query_dict.keys():
            if token in self.index.keys():
                for path in self.index[token].keys():
                    if path in scored_dict.keys():
                        score = self.index[token][path][0]
                        scored_dict[path] += score
                    if path not in scored_dict.keys():
                        scored_dict[path] = self.index[token][path][0]

        return scored_dict



    def rank_results(self,scored_dict):

        return sorted(scored_dict.items(), key=lambda x: (-x[1], x[0]), reverse=False)

    def show_top_pages(self,ranked_results):
        top_pages = []
        count = 0
        if len(ranked_results) == 0:
            print("no results ")

        else:
            with open("bookkeeping.json") as data_file:
                try:
                    data = json.load(data_file)
                except ValueError:
                    data = {}

                for result in ranked_results:
                    count += 1
                    top_pages.append(data[result[0]])
                    if count == 5:
                        break
        return top_pages










if "__main__" == __name__:

    start = time.time()

    print("unpickling")
    pickle_off = open("master_index.pickle", "rb")
    index = pickle.load(pickle_off)

    print("pickled")

##  writing all of the index to a file to see if it's the same as what was
##  written in analytics.py (conclusion: they're the same)
    
##    file = open("analytics-pickle-version.txt", "w+", encoding='utf-8')
##
##    file.write("Size of index: " + str(len(index)) + "\n")
##
##    print("writing to file")
##
##    for k,v in sorted(index.items()):
##        file.write("Term: " + k + "\n")
##        file.write("Appears (v.folders) in the following folder paths: ")
##
##        for doc in v:
##            file.write(doc + ": " + str(v[doc][0]) + "; ")
##        file.write("\n")
##        
##        file.write("Positions (v.positions) of the term in each folder path: ")
##
##        for doc in v:
##            file.write(doc + ": " + str(v[doc]) + ", ")
##        file.write("\n")
##        
####        file.write("Frequencies (v.frequencies) of the term in each folder path: ")
####
####        for doc in v:
####            file.write(doc.doc_id + ": " + str(doc.frequency) + ", ")
####        file.write("\n")
##        
##        file.write("\n\n\n")

    end = time.time()
    print(end - start)

    print("begin search")
    while True:
        query = input("input a query: ")

        if query == "exit":
            sys.exit(0)

        SE = SearchEngine(query,index)
        result = SE.token_query()

        scored = SE.score_query(result)
        ranked_pages = SE.rank_results(scored)
        for page in SE.show_top_pages(ranked_pages):
            print(page)
        #pages_dict = SE.rank_results(result)
        #print (pages_dict)
            #SE.rank_results(result)
        # except:
        #     print(query + " not found in index")
        #     pass

##    print(index["china"]["0/464"])
