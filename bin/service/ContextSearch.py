from bin.service import CardStorage
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query):
        return self.sci_kit_learn.phased_context_search(query, 'title')

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.sci_kit_learn.phased_context_search(query, 'keywords')
        card = cards[0]
        keywords = ','.join(card['keywords'])

        return keywords
