from bin.service import Environment
import pickle
import os
import time
import copy


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

    def get_confluence_card(self, confluence_id):
        found_card = None
        cards = self.get_all_cards()
        for card_id in cards:
            card = cards[card_id]
            if card.relation_type == 'confluence' and card.relation_id == confluence_id:
                found_card = card
                break

        return found_card

    def get_next_card_id(self):

        cards = self.get_all_cards()
        card_ids = []
        for card_id in cards:
            card_ids.append(card_id)

        if len(card_ids) == 0:
            next_id = 1
        else:
            next_id = max(card_ids) + 1

        return next_id

    def store_cards(self, cards):
        cache_file = self.cache_path
        file = open(cache_file, "wb")
        pickle.dump(cards, file)

    def card_exists(self, card_id):
        card = self.get_card(card_id)

        return card is not None

    def get_card(self, card_id):
        card = None
        cards = self.get_all_cards()
        if card_id in cards:
            card = cards[card_id]

        return card

    def update_card(self, card):
        success = False
        existing_card = self.get_card(card.id)
        if existing_card is not None:
            existing_card.changed = time.time()
            existing_card.text = card.text
            existing_card.title = card.title
            existing_card.relation_id = card.relation_id
            existing_card.relation_type = card.relation_type
            existing_card.author = card.author
            existing_card.keywords = card.keywords
            existing_card.editors = card.editors

            if existing_card.versions is None:
                existing_card.versions = []
            existing_card.versions.append(copy.deepcopy(existing_card))
            if existing_card.author is not None and existing_card.type == 'idea':
                existing_card.type = 'fact'
            else:
                existing_card.type = card.type
            self.store_card(existing_card)

        return success

    def store_card(self, card):
        cards = self.get_all_cards()
        cards[card.id] = card
        self.store_cards(cards)

    def update_editors(self, card_id, editor):
        card = self.get_card(card_id)
        if card.author is None:
            card.author = editor
        if card.editors is None:
            card.editors = []
        if editor not in card.editors:
            card.editors.append(editor)
        self.update_card(card)
