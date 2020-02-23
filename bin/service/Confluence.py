from bin.service import Environment
import os
import pickle


class Confluence:

    def __init__(self):
        self.environment = Environment.Environment()

    def load_entries(self):
        confluence_entries = None
        confluence_cache_path = self.environment.get_path_confluence_cache()
        file_exists = os.path.isfile(confluence_cache_path)
        if file_exists:
            file = open(confluence_cache_path, "rb")
            confluence_entries = pickle.load(file)
            file.close()
        return confluence_entries
