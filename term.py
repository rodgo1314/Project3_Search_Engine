## Project 3 - Search Engine - Term representation
## term.py

class TermClass:

    def __init__(self, term_str):
        self.term = term_str
        self.frequencies = {}       ## folder_path : frequency of term
        self.positions = {}         ## folder_path : positions of term
        self.folders = {}           ## folder_path : tf_idf


    def add_freq(self, fp, term_freq):
        self.add_folder_path(fp)
        self.frequencies[fp] = term_freq
        return term_freq

    def add_position(self, fp, pos):
        self.add_folder_path(fp)
        if fp not in self.positions:
            self.positions[fp] = []
            
        self.positions[fp].append(pos)

        return pos

    def add_folder_path(self, fp):
        if fp not in self.folders:
            self.folders[fp] = 0

    def get_freq(self, fp):
        return self.frequencies[fp]

    def get_position(self, fp):
        return self.positions[fp]

    def get_folder_paths(self):
        return self.folders

    def get_count(self):
        return len(self.folders)

    def create_json_str(self):
        result = {
            "term" : self.term,
            "frequencies" : self.frequencies,
            "positions" : self.positions,
            "folder_paths" : self.folders
            }
        return result
