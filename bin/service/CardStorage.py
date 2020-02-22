from bin.service import Environment
import pickle
import os


class CardStorage:

    def __init__(self, cache_path=None):
        self.environment = Environment.Environment()
        if cache_path is None:
            self.cache_path = self.environment.get_path_card_cache()
        else:
            self.cache_path = cache_path

    def add_card(self, card):
        cards = self.get_all_cards()
        cards[card.id] = card
        self.store_cards(cards)

    def get_all_cards(self):
        cache_file = self.cache_path
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            file = open(cache_file, "wb")
            content = {}
            pickle.dump(content, file)
        return content

    def get_jira_card(self, ticket_id):
        found_card = None
        cards = self.get_all_cards()
        for card_id in cards:
            card = cards[card_id]
            if card.relation_type == 'jira' and card.relation_id == ticket_id:
                found_card = card
                break

        return found_card

    def get_next_card_id(self):
        cards = self.get_all_cards()
        card_ids = []
        for card_id in cards:
            card_ids.append(card_id)
        next_id = max(card_ids) + 1

        return next_id

    def store_cards(self, cards):
        cache_file = self.cache_path
        file = open(cache_file, "wb")
        pickle.dump(cards, file)
