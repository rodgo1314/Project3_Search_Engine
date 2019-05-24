## Project 3 - Search Engine - Index Building
## index_builder.py

import logging
import os
import re
from lxml import etree
from urllib.parse import urlparse, urljoin, parse_qs
from corpus import Corpus
import queue
from collections import defaultdict
from bs4 import BeautifulSoup
import sys
import json
from nltk.tokenize import RegexpTokenizer

logger = logging.getLogger(__name__)

'''
    Milestone #1 only involves building an index for the corpus and a retrieval system

    here, the index is a file (or database??)


    ALGORITHM:
    
    for each url to be indexed:
        parse through url data and tokenize the url data/document

        for each term in the url data/document
            tokenize each term (and modify tokens if necessary)
            
            if the term are already in the index:
                add the document metadata/id# to the term
            else:
                create new space for the term
                add the document metadata/id# to the term
    
'''

class IndexBuilder:
    '''
    This class is responsible for parsing through each URL, tokenizing terms,
    and indexing them.
    '''

    def __init__(self, json_data):
        self.json_data = json_data
        #list of the folder pages aka (index of pages)
        self.folder_pages = []
        #self.corpus = Corpus()
        #self.freq_dict = dict()
        self.corpus_length = 0


    # reads bookkeeping.json and appends to list of folder_pages
    #also keeps count of the corpus
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
        data = open(JSON_FILE_NAME).read()

        body = ""
        for info in BeautifulSoup(data, "lxml").find_all("html"):
            body = info.text + body + " "
        new_body = tokenizer.tokenize(body.lower())

        return new_body







    def start_crawling(self):
       try:
        
            while self.frontier.has_next_url():
                url = self.frontier.get_next_url()
                logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched,
                            len(self.frontier))
                url_data = self.fetch_url(url)

            #### Here, we write code for tokenizing and indexing

            #### https://stackoverflow.com/questions/22799990/beatifulsoup4-get-text-still-has-javascript

                ## Using BeautifulSoup to scrape URLs
                soup = BeautifulSoup(url_data["content"], 'html.parser')

                ## remove any javascript code using BeautifulSoup
                for script in soup(["script","style"]):
                    script.decompose()

                text = soup.text

                text_list = text.split()

                ## The following code is from Project 1 Part A
                url_tokens = []
                toFilter = re.compile("[a-zA-Z0-9]+")
                for term in text_list:
                    url_tokens.extend(toFilter.findall(term))

                ##print(url_tokens)

                ## The following code is also from Project 1 Part A
                for term in url_tokens:
                    if term.lower() in self.freq_dict:
                        self.freq_dict[term.lower()] = self.freq_dict[term.lower()] + 1
                      ##  print(term.lower() + " " + str(self.freq_dict[term.lower()]))
                    else:
                        self.freq_dict[term.lower()] = 1
                      ##  print(term.lower() + " " + str(self.freq_dict[term.lower()]))

                for next_link in self.extract_next_links(url_data):
                    if self.corpus.get_file_name(next_link) is not None:
                        if self.is_valid(next_link):
                            self.frontier.add_url(next_link)
       except:

           ## When running the program and you kill the program w/ CRTL-C,
           ## it will print out a sorted dictionary with each term and their frequency
            self.print_output(self.freq_dict)




    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """

        file_name = self.corpus.get_file_name(url)  # looks up file name of url

        # create a dict which will have url info
        url_data = {'url': url, 'content': None, 'size': 0}
        try:

            with open(file_name,
                      'rb') as fobj:  # read and open file. if file can be opened, add in url, contents, and size of the file.
                xml = fobj.read()

            url_data['url'] = url
            url_data['content'] = xml
            url_data['size'] = os.path.getsize(file_name)

        except:  # if file can't be opened, print error
            print("file error")

        return url_data  # return dict of info

    def extract_next_links(self, url_data):
        """
         The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
         fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
         list of urls in their absolute form (some links in the content are relative and needs to be converted to the
         absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
         that have already been fetched. The frontier takes care of that.

         Suggested library: lxml
         """
        outputLinks = []
        root = etree.HTML(url_data['content'])  # creates an html object of the contents of the given url dict
        links = root.xpath(
            "//@href")  # extract all links with type "href" into a list of links. every url link will be preceded with 'href'

        for link in links:
            new_url = urljoin(url_data['url'],
                              link)  # constructs an absolute url by combining the original url info with scraped url links.
            ##print(new_url)
            if new_url not in self.frontier.urls_set:  # if this absolute url is new, then add it to the list, otherwise just continue.
                outputLinks.append(new_url)
                ## print(new_url)
            else:
                continue
                # return final list of all absolute links.
        return outputLinks


    def is_valid(self, url):
        return True   






    ## This function takes O(n) time, as it goes through each word and places them in an array
    def create_tokens(f):
        '''Given file f, go through each word in each line and place them as tokens in a array'''
        all_tokens = []
        
        toFilter = re.compile("[a-zA-Z0-9]+")
        for line in f:
            all_tokens.extend(toFilter.findall(line))

        return all_tokens


    def print_output(self, f_dict):
        '''Print the sorted k,v pairs of the dictionary'''
        count = 1 ## This is to keep track of where the last printed pair is to prevent output formatting issues
        
        for (k,v) in sorted(f_dict.items(), key = lambda i:(-i[1], i[0])):
            pair = k + "\t" + str(v)
            if (count < len(f_dict)):
                pair += "\n"
                
            sys.stdout.write(pair)  ## This is helpful in eliminating the extra last line that is printed with print()

            count = count + 1



if __name__ == '__main__':
    index = IndexBuilder("bookkeeping.json")
    index.load_json_data()
    pages = {}
    for folder_path in index.folder_pages:
        pages[folder_path] = index.tokenize_data(folder_path)
        break
    print(pages)
