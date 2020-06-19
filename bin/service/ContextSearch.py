from bin.service import CardStorage
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query):
        return self.sci_kit_learn.phased_context_search(query)

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        card_ids = self.sci_kit_learn.phased_context_search(query, 'keywords')
        card_id = card_ids[0]
        card = self.storage.get_card(card_id)
        keywords = ','.join(card['keywords'])

        return keywords
