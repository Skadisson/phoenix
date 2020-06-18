from bin.service import CardStorage
from bin.service import SciKitLearn
from bin.service import Environment


class ContextSearch:

    def __init__(self):
        self.environment = Environment.Environment()
        self.storage = CardStorage.CardStorage()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()

    def search(self, query):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards()
        else:
            cards = self.storage.get_jira_and_confluence_cards()
        normalized_cards, card_ids = self.normalize_cards(cards)
        context_card_ids = self.sci_kit_learn.phased_context_search(normalized_cards, card_ids, query)
        """context_card_ids = self.sci_kit_learn.unphased_context_search(normalized_cards, card_ids, query)"""

        while len(context_card_ids) > 9:
            cards = self.storage.get_cards(context_card_ids)
            normalized_cards, card_ids = self.normalize_cards(cards)
            context_card_ids = self.sci_kit_learn.phased_context_search(normalized_cards, card_ids, query)

        return context_card_ids

    @staticmethod
    def normalize_cards(cards):
        normalized_cards = []
        card_ids = []

        for card in cards:
            normalized_card = ''
            if card['title'] is not None:
                normalized_card += str(card['title'])
            if card['text'] is not None:
                normalized_card += ' ' + str(card['text'])
            if card['keywords'] is not None:
                normalized_card += ' ' + str(' '.join(card['keywords']))
            normalized_content = str(normalized_card)
            card_id = int(card['id'])
            if normalized_content != '' and card_id > 0:
                card_ids.append(card_id)
                normalized_cards.append(normalized_content)

        return normalized_cards, card_ids

    def suggest_keywords(self, title, text):

        query = title + ' ' + text
        cards = self.storage.get_jira_cards()
        normalized_cards, card_ids = self.normalize_cards(cards)
        card_ids = self.sci_kit_learn.unphased_context_search(normalized_cards, card_ids, query)
        card_id = card_ids[0]
        card = self.storage.get_card(card_id)
        keywords = ','.join(card.keywords)

        return keywords
