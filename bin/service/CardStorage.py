from bin.service import FavouriteStorage, ShoutOutStorage, UserStorage, Storage
from bin.entity import Card
import time
import pymongo


class CardStorage(Storage.Storage):

    def __init__(self):
        super().__init__()
        self.so_storage = ShoutOutStorage.ShoutOutStorage()
        self.add_text_indices()

    def add_text_indices(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        try:
            card_storage.create_index([('title', pymongo.TEXT), ('text', pymongo.TEXT)])
        except Exception as e:
            print(e)

    def add_card(self, card):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card_storage.insert_one(card)

    def get_all_cards(self, not_empty=None):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        if not_empty is not None:
            cards = card_storage.find({'$and': [{not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
        else:
            cards = card_storage.find()
        return cards

    def get_all_ideas(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'type': 'idea'})
        return cards

    def get_all_facts(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'type': 'fact'})
        return cards

    def search_cards_by_title(self, title):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'title': title})
        return cards

    def search_cards_fulltext(self, query):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'$text': {'$search': query}})
        return cards

    def search_cards_by_query(self, query):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'title': {'$regex': str(query)}})
        return cards

    def get_jira_confluence_and_phoenix_cards(self, not_empty=None):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        if not_empty is not None:
            jira_cards = card_storage.find({'$and': [{'relation_type': 'jira'}, {not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
            confluence_cards = card_storage.find({'$and': [{'relation_type': 'confluence'}, {not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
            phoenix_cards = card_storage.find({'$and': [{'relation_type': None}, {not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
        else:
            jira_cards = card_storage.find({'relation_type': 'jira'})
            confluence_cards = card_storage.find({'relation_type': 'confluence'})
            phoenix_cards = card_storage.find({'relation_type': None})
        return jira_cards, confluence_cards, phoenix_cards

    def get_jira_and_confluence_ideas(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'$and': [{'relation_type': {'$in': ['jira', 'confluence', None]}}, {'type': 'idea'}]})
        return cards

    def get_jira_and_confluence_facts(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'$and': [{'relation_type': {'$in': ['jira', 'confluence', None]}}, {'type': 'fact'}]})
        return cards

    def get_jira_cards(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'relation_type': 'jira'})
        return cards

    def get_jira_card(self, ticket_id):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        card = card_storage.find_one({'relation_type': 'jira', 'relation_id': ticket_id})
        return card

    def get_confluence_cards(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'relation_type': 'confluence'})
        return cards

    def get_git_cards(self, not_empty=None):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        if not_empty is not None:
            git_cards = card_storage.find({'$and': [{'relation_type': 'git'}, {not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
        else:
            git_cards = card_storage.find({'relation_type': 'git'})
        return git_cards

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

    def get_timed_facts(self, target_time):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        cards = card_storage.find({'changed': {'$gt': target_time}, 'type': 'fact'})
        return cards

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
            favourite_storage = FavouriteStorage.FavouriteStorage()
            favourite_storage.update_favourite_title(card['id'], card['title'])

        return success

    def store_card(self, card):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        stored_card = card_storage.find_one({'id': card['id']})
        if stored_card is not None:
            card_storage.replace_one({'id': card['id']}, card)
        else:
            card_storage.insert_one(card)

    def get_latest_cards(self, count):
        git_enabled = self.environment.get_service_enable_git()

        cards = []
        if git_enabled:
            cards += list(self.get_git_cards('title'))

        jira_cards, confluence_cards, phoenix_cards = self.get_jira_confluence_and_phoenix_cards('title')
        cards += list(jira_cards) + list(confluence_cards) + list(phoenix_cards)
        shout_outs_exist = False

        latest_cards = []
        for check_card in cards:
            if check_card['clicks'] > 0:
                shout_outs = self.so_storage.get_card_shout_outs(check_card['id'])
                check_card['shout_outs'] = shout_outs.count()
                if check_card['shout_outs'] > 0:
                    check_card['clicks'] += 1000000000000
                    if shout_outs_exist is False:
                        shout_outs_exist = True
                latest_cards.append(check_card)

        latest_cards = sorted(latest_cards, key=lambda card: card['shout_outs'], reverse=False)
        latest_cards = self.sort_cards(latest_cards, count)

        return latest_cards

    @staticmethod
    def sort_cards(cards, count):
        cards_by_date = sorted(cards, key=lambda card: card['changed'], reverse=True)
        cards_by_click = sorted(cards_by_date, key=lambda card: card['clicks'], reverse=True)
        cards_by_type = sorted(cards_by_click, key=lambda card: card['type'], reverse=False)
        limited_cards = cards_by_type[:count]
        sorted_cards = []
        for sorted_card in limited_cards:
            if '_id' in sorted_card:
                del(sorted_card['_id'])
            sorted_cards.append(sorted_card)

        return sorted_cards

    def create_card(self, title, text, keywords, external_link):
        user_storage = UserStorage.UserStorage()
        user = user_storage.get_user()

        card = Card.Card()
        card.id = self.get_next_card_id()
        card.title = title
        card.text = text
        card.keywords = keywords.split(',')
        card.created = time.time()
        card.changed = time.time()
        card.external_link = external_link
        card.type = 'fact'
        card.author = user['short']
        card.editors = [user['short']]
        self.store_card(dict(card))

        return card.id
