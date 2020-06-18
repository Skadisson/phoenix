from bin.service import CardStorage
from bin.service import Environment


class Info:

    def __init__(self):
        self.environment = Environment.Environment()
        self.storage = CardStorage.CardStorage()

    def get_idea_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards()
        else:
            cards = self.storage.get_jira_and_confluence_cards()
        idea_count = 0
        for card in cards:
            if card['type'] == 'idea':
                idea_count += 1
        return idea_count

    def get_fact_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards()
        else:
            cards = self.storage.get_jira_and_confluence_cards()
        fact_count = 0
        for card in cards:
            if card['type'] == 'fact':
                fact_count += 1
        return fact_count

    def get_jira_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards()
        else:
            cards = self.storage.get_jira_and_confluence_cards()
        jira_count = 0
        for card in cards:
            if card['relation_type'] == 'jira':
                jira_count += 1
        return jira_count

    def get_confluence_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards()
        else:
            cards = self.storage.get_jira_and_confluence_cards()
        confluence_count = 0
        for card in cards:
            if card['relation_type'] == 'confluence':
                confluence_count += 1
        return confluence_count
