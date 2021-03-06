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
        if cards.count() == 0:
            cards = self.storage.get_all_cards('title')

        if cards.count() <= 0 or cards.count() > 6:
            sorted_cards = self.sci_kit_learn.search(query, 'normal_title', None)
        else:
            sorted_cards = self.storage.sort_cards(cards, 6)

        return sorted_cards

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.sci_kit_learn.search(query, 'normal_keyword')
        card = cards[0]
        keywords = ','.join(card['keywords'])

        return keywords
