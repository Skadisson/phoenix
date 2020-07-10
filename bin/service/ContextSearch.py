from bin.service import CardStorage
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query):

        title_cards = self.storage.search_cards_by_title(query)
        if title_cards.count() > 0:
            sorted_cards = self.storage.sort_cards(title_cards, 9)
            return sorted_cards

        return self.sci_kit_learn.search(query, 'title')

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.sci_kit_learn.search(query, 'keywords')
        card = cards[0]
        keywords = ','.join(card['keywords'])

        return keywords
