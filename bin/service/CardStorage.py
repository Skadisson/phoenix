from bin.service import FavouriteStorage
from bin.entity import Card
from pymongo import MongoClient
import time
import copy


class CardStorage:

    def __init__(self):
        self.mongo = MongoClient()
        self.favourite_card_ids = None

    def add_card(self, card):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card_storage.insert_one(card)

    def get_all_cards(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find()
        return cards

    def get_jira_and_confluence_cards(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'relation_type': {'$in': ['jira', 'confluence']}})
        return cards

    def get_jira_card(self, ticket_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'relation_type': 'jira', 'relation_id': ticket_id})
        return card

    def get_confluence_card(self, confluence_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'relation_type': 'confluence', 'relation_id': confluence_id})
        return card

    def get_git_card(self, git_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'relation_type': 'git', 'relation_id': git_id})
        return card

    def get_next_card_id(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        max_id = card_storage.find(sort=[('id', -1)]).limit(1)
        if max_id.count() > 0:
            next_id = max_id[0]['id'] + 1
        else:
            next_id = 1

        return next_id

    def card_exists(self, card_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'id': card_id})
        return card is not None

    def get_card(self, card_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'id': card_id})
        return card

    def get_cards(self, card_ids):
        cards = []
        for card_id in card_ids:
            cards.append(self.get_card(card_id))
        return cards

    def update_card(self, card):
        success = False
        existing_card = self.get_card(card['id'])
        if existing_card is not None:
            existing_card['changed'] = time.time()
            existing_card['text'] = card['text']
            existing_card['title'] = card['title']
            existing_card['relation_id'] = card['relation_id']
            existing_card['relation_type'] = card['relation_type']
            existing_card['author'] = card['author']
            existing_card['keywords'] = card['keywords']
            existing_card['editors'] = card['editors']
            existing_card['external_link'] = card['external_link']

            if existing_card['author'] is not None and existing_card['type'] == 'idea':
                existing_card['type'] = 'fact'
            else:
                existing_card['type'] = card['type']
            self.store_card(existing_card)

        return success

    def store_card(self, card):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'id': card['id']})
        if card is not None:
            card_storage.replace_one({'id': card['id']}, card)
        else:
            card_storage.insert_one(card)

    def get_latest_cards(self, count):
        latest_cards = []

        cards = self.get_jira_and_confluence_cards()
        self.load_favourite_card_ids()

        valid_cards = []
        for check_card in cards:
            len_title = len(check_card['title'])
            len_text = len(check_card['text'])
            if len_title > 0 and len_text > 0:
                if check_card['id'] in self.favourite_card_ids:
                    check_card['favourite'] = int(self.favourite_card_ids[check_card['id']])
                else:
                    check_card['favourite'] = 0
                valid_cards.append(check_card)

        cards_by_favourite = sorted(valid_cards, key=lambda card: card['favourite'], reverse=False)
        cards_by_date = sorted(cards_by_favourite, key=lambda card: card['changed'], reverse=True)
        cards_by_click = sorted(cards_by_date, key=lambda card: card['clicks'], reverse=True)
        cards_by_type = sorted(cards_by_click, key=lambda card: card['type'], reverse=False)
        limited_cards_by_date = cards_by_type[:count]
        for sorted_card in limited_cards_by_date:
            del(sorted_card['_id'])
            latest_cards.append(sorted_card)

        return latest_cards

    def load_favourite_card_ids(self):
        favourite_storage = FavouriteStorage.FavouriteStorage()
        self.favourite_card_ids = favourite_storage.get_ranked_favourite_card_ids()

    def create_card(self, title, text, keywords, external_link):
        card = Card.Card()
        card.id = self.get_next_card_id()
        card.title = title
        card.text = text
        card.keywords = keywords.split(',')
        card.created = time.time()
        card.changed = time.time()
        card.external_link = external_link
        card.type = 'fact'
        """TODO: user handling"""
        card.author = 'ses'
        card.editors = ['ses']
        self.store_card(card)

        return card.id
