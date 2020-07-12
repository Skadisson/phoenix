from bin.service import CardStorage
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query):

        cards = self.storage.search_cards_by_title(query)
        if cards.count() == 0:
            cards = self.storage.search_cards_fulltext(query)

        print(cards.count())
        if cards.count() == 0 or cards.count() > 9:
            sorted_cards = self.sci_kit_learn.search(query, 'title', cards)
        else:
            sorted_cards = self.storage.sort_cards(cards, 9)

        return sorted_cards

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.sci_kit_learn.search(query, 'keywords')
        card = cards[0]
        keywords = ','.join(card['keywords'])

        return keywords
