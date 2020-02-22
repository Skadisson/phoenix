from bin.service import CardStorage
from bin.service import Environment
from bin.service import SciKitLearn


class ContextSearch:

    def __init__(self, cache_path=None):
        self.storage = CardStorage.CardStorage(cache_path)
        self.sci_kit_learn = SciKitLearn.SciKitLearn()
        self.environment = Environment.Environment()

    def search(self, query):
        cards = self.storage.get_all_cards()
        normalized_cards, card_ids = self.normalize_cards(cards)
        context_card_ids = self.sci_kit_learn.context_search(normalized_cards, card_ids, query)

        return context_card_ids

    @staticmethod
    def normalize_cards(cards):
        normalized_cards = []
        card_ids = []

        for card_id in cards:
            card = cards[card_id]
            card_ids.append(card_id)
            normalized_card = ''
            if card.title is not None:
                normalized_card += str(card.title)
            if card.text is not None:
                normalized_card += ' ' + str(card.text)
            if card.keywords is not None:
                normalized_card += ' ' + str(' '.join(card.keywords))
            normalized_cards.append(str(normalized_card))

        return normalized_cards, card_ids