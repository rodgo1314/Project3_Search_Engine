## Project 3 - Search Engine - Index Building
## index_builder.py

# def buildInvertedIndex(self):
# 		pages = self.pages_to_words()
# 		invertedIndex = {}
# 		for file_name in pages.keys():
# 			for word in pages[file_name].keys():
# 				if word not in invertedIndex.keys():
#
# 					invertedIndex[word] = {}
# 					invertedIndex[word][file_name] = []
# 					invertedIndex[word][file_name] = pages[file_name][word]
# 				else:
# 					invertedIndex[word][file_name] = []
# 					invertedIndex[word][file_name] = pages[file_name][word]
# 		# print(invertedIndex)
# 		return invertedIndex


import logging
import os
import re
from lxml import etree
from collections import defaultdict
from bs4 import BeautifulSoup
import sys
import json
from nltk.tokenize import RegexpTokenizer
from term import TermClass
import math

import pickle
import time

logger = logging.getLogger(__name__)

class IndexBuilder:
    '''Builds the inverted index. Goes'''
    def __init__(self, json_data):
        self.json_data = json_data
        self.folder_pages = []
        self.corpus_length = 0

        self.pages = {}
        self.content = {}
        self.inverted_index = {}
        self.frequency_dict = {}


    def load_json_data(self):
        with open(self.json_data) as x:
            try:
                data = json.load(x)
            except ValueError:
                data = {}
        for d in data:
            self.corpus_length += 1 #length should be 37497
            self.folder_pages.append(d)

    def tokenize_data(self, folder_index):
        regular_expression = "\w+"
        tokenizer = RegexpTokenizer(regular_expression)
        word_position = 0
        token_dict = {}

        JSON_FILE_NAME = os.path.join(".", "WEBPAGES_RAW", folder_index)
        data = open(JSON_FILE_NAME, encoding="utf8").read()

        soup = BeautifulSoup(data, "lxml")

        # looks for body of the file and gets unique term
        body = ""
        for script in soup(["script", "style"]):  ## removes any js or css
            script.decompose()

        for info in soup.find_all("html"):
            ##print("NEW LINE: " + str(info))
            body = info.text + body + " "
        new_body = tokenizer.tokenize(body.lower())
        self.content[folder_index] = new_body

        # looks for title tags which will weigh more
        title = ""
        for info in soup.find_all("title"):
            title = info.text + " "
        new_title = tokenizer.tokenize(title.lower())


        # looks for heading 1 to add weight
        heading1 = ""
        for info in soup.find_all("h1"):
            heading1 = info.text + " "
        new_heading1 = tokenizer.tokenize(heading1.lower())

        # looks for heading 2 to add weight
        heading2 = ""
        for info in soup.find_all("h2"):
            heading2 = info.text + " "
        new_heading2 = tokenizer.tokenize(heading2.lower())

        # finally looks for heading 3 add weight
        heading3 = ""
        for info in soup.find_all("h3"):
            heading3 = info.text + " "
        new_heading3 = tokenizer.tokenize(heading3.lower())

        # looks for meta description and adds weight only 1 weight
        # meta_description = soup.find('meta', attrs={"name": "description"})
        # for info in soup.find('meta', attrs={"name": "description"}):
        #     meta_description = info.text + meta_description + " "
        # new_meta_description = tokenizer.tokenize(meta_description.lower())



        for token in new_body:
            # if the token is in the dictionary already then
            # it will add to the frequency and keep track of the postion
            if token in token_dict.keys():
                token_dict[token][0] += 1
                token_dict[token].append(word_position)
                word_position += 1

            #adds token(unique word) to the dictionay whos
            #values are in position [0] the word frequency
            #and in position[1] is the word position
            #then adds 1 after appending the word position
            #so that it keeps track of the position
            if token not in token_dict.keys():
                if self.is_term_valid(token):
                    token_dict[token] = []
                    token_dict[token].append(1)
                    token_dict[token].append(word_position)
                    word_position+=1
                    #print(token_dict)




        #adding weights to the frequency and then we
        #will normalize them
        #word_in_title_freq = 0
        # will add a 5 weight if word is in title
        for token in new_title:
            try:
                token_dict[token][0] += 3
            except KeyError:
                #print(KeyError)
                pass

        for token in new_heading1:
            try:
                token_dict[token][0] += 3
            except KeyError:
                pass

        for token in new_heading2:
            try:
                token_dict[token][0] +=3
            except KeyError:
                pass

        for token in new_heading3:
            try:
                token_dict[token][0] += 3
            except KeyError:
                pass

        # for token in new_meta_description:
        #      token_dict[token][0] +=3




        return token_dict





    def build_index(self):
        '''Part 1 on building the index: Parsers and tokenizes each unique term,
        checks if the term is valid, and creates a TermClass object for each term.
        The TermClass object is added to the inverted index'''


        count = 0
        for folder_path in self.folder_pages:
##            print(folder_path)
##            print(self.tokenize_data(folder_path))

            self.pages[folder_path] = self.tokenize_data(folder_path)
            count += 1
            if count % 1000 == 0:
                print(str(count))

##            if count == 1000:
##                break
        
        #print(self.pages)

        print("building inverted index")

        ## index is a dictionary, with term as the key and a doc dictionary as the value
        ##      the doc dictionary has the docId as the key, and a list of properties as the value
        ## {word : {docId : [freq, pos1, pos2, etc...]}}

        
        for folder_path, term_dict in self.pages.items():

            for term in term_dict:
                term_freq = term_dict[term][0]
                term_positions = term_dict[term][1:]
                
                if term in self.frequency_dict:
                    self.frequency_dict[term] += term_freq
                else:
                    self.frequency_dict[term] = term_freq
                
                if term not in self.inverted_index:
                    self.inverted_index[term] = {}

                if folder_path not in self.inverted_index[term]:
                    self.inverted_index[term][folder_path] = []

                
                self.inverted_index[term][folder_path].extend(term_dict[term])

        print("done initially building index...")



    def finalize_index(self):
        '''Part 2 of building the index: This performs the td-idf for each term, and
        adds this # to the inverted_index'''
        for term, doc_dict in index.inverted_index.items():

            for doc in doc_dict:
                term_count = doc_dict[doc][0]
                word_count_in_folder_path = len(self.content[doc])

                tf = term_count / float(word_count_in_folder_path)

                weightage = self.corpus_length / (len(doc_dict))
                
                idf = math.log(weightage) + 1

                tf_idf = tf * idf

                doc_dict[doc][0] = tf_idf

        return
        
    def get_page(self, folder_path):
        '''Get content of a specific folder path in a form of a list'''
        return self.pages[folder_path]

    def is_term_valid(self, term):
        stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves",
                     "you", "your", "yours", "yourself", "yourselves", "he", "him",
                     "his", "himself", "she", "her", "hers", "herself", "it", "its",
                     "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

        if term in stopwords:
            return False
        
        toFilter = re.match("[a-zA-Z0-9]+", term)
        if toFilter:
            return True

        return False



if __name__ == '__main__':

    start = time.time() ## recording execution time of program
    
    index = IndexBuilder("bookkeeping.json")
    index.load_json_data()

    print("Parsing and tokenizing each url......")
    index.build_index()
    print("Finalizing inverted index......")
    index.finalize_index()
    print("Done! Size of inverted index: " + str(len(index.inverted_index)))
    #
    file = open("analytics.txt", "w+", encoding='utf-8')
    file.write("Length of corups (37,497?): " + str(index.corpus_length) + "\n")
    file.write("Length of frequency dict: " + str(len(index.frequency_dict)) + "\n")
    file.write("Length of inverted_index: " + str(len(index.inverted_index)) + "\n\n\n")
    
    for k,v in sorted(index.inverted_index.items()):
        file.write("Term: " + k + "\n")
        file.write("Appears (v.folders) in the following folder paths: ")

        for doc in v:
            file.write(doc + ": " + str(v[doc][0]) + "; ")
        file.write("\n")
        
        file.write("Positions (v.positions) of the term in each folder path: ")

        for doc in v:
            file.write(doc + ": " + str(v[doc]) + ", ")
        file.write("\n")
        
##        file.write("Frequencies (v.frequencies) of the term in each folder path: ")
##
##        for doc in v:
##            file.write(doc.doc_id + ": " + str(doc.frequency) + ", ")
##        file.write("\n")
        
        file.write("# of times it appears in the corpus: " + str(index.frequency_dict[k]) + "\n")
        file.write("\n\n\n")


    ## we store the inverted index in a pickle file --> to be unpickled and used in search_engine.py
    pickling_on = open("master_index.pickle", "wb")
    pickle.dump(index.inverted_index, pickling_on)
    pickling_on.close()

    print("i just pickled")

    ## print(index.inverted_index["china"])

    end = time.time()
    print(end - start)

    sys.exit(0)
    #
    # #print(index.frequency_dict["string"])
