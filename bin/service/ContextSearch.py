from bin.service import CardStorage
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query, include_jira):

        cards = self.storage.search_cards_by_title(query, include_jira)
        if cards.count() == 0:
            cards = self.storage.search_cards_fulltext(query, include_jira)
        if cards.count() == 0:
            cards = self.storage.get_all_cards('title', include_jira)

        if cards.count() <= 0 or cards.count() > 6:
            sorted_cards = self.sci_kit_learn.search(query, 'normal_title', None, include_jira)
        else:
            sorted_cards = self.storage.sort_cards(cards, 6)

        return sorted_cards

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.sci_kit_learn.search(query, 'normal_keyword')
        card = cards[0]
        keywords = ','.join(card['keywords'])

        return keywords
