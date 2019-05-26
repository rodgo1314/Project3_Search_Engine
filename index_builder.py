## Project 3 - Search Engine - Index Building
## index_builder.py

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

logger = logging.getLogger(__name__)
        
class Parser:
    '''
    This class is responsible for parsing through each URL, tokenizing terms,
    and indexing them.
    '''

    def __init__(self, json_data):
        self.json_data = json_data
        #list of the folder pages aka (index of pages)
        self.folder_pages = []
        self.corpus_length = 0


    # reads bookkeeping.json and appends to list of folder_pages
    # also keeps count of the corpus
    def load_json_data(self):
        with open(self.json_data) as x:
            try:
                data = json.load(x)
            except ValueError:
                data = {}
        for d in data:
            self.corpus_length = self.corpus_length + 1 #length should be 37497
            self.folder_pages.append(d)

    def tokenize_data(self,folder_index):
        regular_expression = "\w+"
        tokenizer = RegexpTokenizer(regular_expression)
        word_position = 0
        JSON_FILE_NAME = os.path.join(".", "WEBPAGES_RAW", folder_index)
        data = open(JSON_FILE_NAME, encoding="utf8").read()

        soup = BeautifulSoup(data, "lxml")

        body = ""
        for script in soup(["script", "style"]):    ## removes any js or css
            script.decompose()

        for info in soup.find_all("html"):
            ##print("NEW LINE: " + str(info))
            body = info.text + body + " "
        new_body = tokenizer.tokenize(body.lower())

        
        return new_body



class IndexBuilder:
    '''Builds the inverted index. Goes'''
    def __init__(self, json_data):
        self.json_data = json_data
        
        self.pages = {}
        self.inverted_index = {}
        self.frequency_dict = {}

        self.corpus_length = 0

    def build_index(self):
        '''Part 1 on building the index: Parsers and tokenizes each unique term,
        checks if the term is valid, and creates a TermClass object for each term.
        The TermClass object is added to the inverted index'''
        parser = Parser(self.json_data)
        parser.load_json_data()

        self.corpus_length = parser.corpus_length

        count = 0
        for folder_path in parser.folder_pages:
            print(folder_path)
            self.pages[folder_path] = parser.tokenize_data(folder_path)
            count += 1
            if count == 500:
                print("count == 500")
                break

        print("building inverted index")
        for folder_path, list_of_terms in self.pages.items():
            term_position = 0
            temp_freq_dict = {}
            
            for term in list_of_terms:
                
                if self.is_term_valid(term):

                    ## This captures term frequency in the document/url itself
                    if term in temp_freq_dict:
                        temp_freq_dict[term] += 1
                    else:
                        temp_freq_dict[term] = 1

                    ## This captures term frequency in the whole corpus (37,497 urls)
                    self.add_to_frequency_dict(term)


                    ## Add the position of a term to the TermClass position list.
                    if term in self.inverted_index:
                        self.inverted_index[term].add_position(folder_path, term_position)
                    else:
                        t = TermClass(term)
                        t.add_position(folder_path, term_position)
                        self.inverted_index[term] = t

                term_position = term_position + 1
            
            ## Add to the inverted vertex the term's frequency in the url, and the document/url
            for term, term_class in self.inverted_index.items():
                if term in temp_freq_dict:
                    self.inverted_index[term].add_freq(folder_path, temp_freq_dict[term])
                    self.inverted_index[term].add_folder_path(folder_path)


    def finalize_index(self):
        '''Part 2 of building the index: This performs the td-idf for each term, and
        adds this # to the inverted_index'''
        for k,v in index.inverted_index.items():
            
            for folder_path in v.folders:
                ## calculate tf(term, doc) = count of t in d / # of words in d
                term_count = v.frequencies[folder_path]
                word_count_in_folder_path = len(self.pages[folder_path])

                tf = term_count / word_count_in_folder_path


                ## calculate df = occurrence of t in corpus

                ## idf = log(N/(df + 1))

                weightage = self.corpus_length / (self.frequency_dict[k] + 1)
                idf = math.log(weightage)

                tf_idf = tf * idf

                v.folders[folder_path] = tf_idf

        return
    
    def get_page(self, folder_path):
        '''Get content of a specific folder path in a form of a list'''
        return self.pages[folder_path]


    def add_to_frequency_dict(self, term):
        '''Count the # of the times the term appears in the whole corpus'''
        if term in self.frequency_dict:
            self.frequency_dict[term] += 1
        else:
            self.frequency_dict[term] = 1

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
    index = IndexBuilder("bookkeeping.json")

    print("Parsing and tokenizing each url......")
    index.build_index()
    print("Finalizing inverted index......")
    index.finalize_index()
    print("Done! Size of inverted index: " + str(len(index.inverted_index)))

    file = open("analytics.txt", "w+", encoding='utf-8')
    file.write("Length of corups (37,497?): " + str(index.corpus_length) + "\n")
    file.write("Length of frequency dict: " + str(len(index.frequency_dict)) + "\n")
    file.write("Length of inverted_index: " + str(len(index.inverted_index)) + "\n\n\n")

    for k,v in sorted(index.inverted_index.items()):
        file.write("Term: " + k + "\n")
        file.write("Appears (v.folders) in the following folder paths: " + str(v.folders) + "\n")
        file.write("Positions (v.positions) of the term in each folder path: " + str(v.positions) + "\n")
        file.write("Frequencies (v.frequencies) of the term in each folder path: " + str(v.frequencies) + "\n")
        file.write("# of times it appears in the corpus: " + str(index.frequency_dict[k]) + "\n")
        file.write("\n\n\n")

    print(index.frequency_dict["string"])
