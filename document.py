## Project 3 - Search Engine - Term representation
## term.py

class Document:

    def __init__(self, docId, term_str):
        self.doc_id = docId         ## str
        self.term = term_str
        self.frequency = 0          ## frequency of term in the doc
        self.positions = []         ## positions of that term
        self.tf_idf = 0


