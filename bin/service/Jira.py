from bin.service import Environment
import os
import pickle


class Jira:

    def __init__(self):
        self.environment = Environment.Environment()

    def load_tickets(self):
        tickets = None
        jira_cache_path = self.environment.get_path_jira_cache()
        file_exists = os.path.isfile(jira_cache_path)
        if file_exists:
            file = open(jira_cache_path, "rb")
            tickets = pickle.load(file)
            file.close()
        return tickets
