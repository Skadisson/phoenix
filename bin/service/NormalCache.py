from bin.service import Storage
import time


class NormalCache(Storage.Storage):

    def __init__(self):
        super().__init__()

    def load_normalized_cards(self, not_empty=None):
        documents = []
        card_ids = []

        phoenix = self.mongo.phoenix
        normal_cache = phoenix.normal_cache
        if not_empty is not None:
            normalized_cards = normal_cache.find({'$and': [{not_empty: {'$ne': None}}, {not_empty: {'$ne': []}}]})
        else:
            normalized_cards = normal_cache.find()

        for normalized_card in normalized_cards:
            text = normalized_card['normal_keyword'] + ' ' + normalized_card['normal_title'] + ' ' + normalized_card['normal_text']
            if len(text.split()) > 0:
                card_ids.append(normalized_card['card_id'])
                documents.append(text)

        return documents, card_ids

    def get_normalized_cards(self, card_ids):
        phoenix = self.mongo.phoenix
        normal_cache = phoenix.normal_cache
        normal_cards = normal_cache.find({'card_id': {'$in': card_ids}})

        documents = []
        card_ids = []
        for normalized_card in normal_cards:
            text = normalized_card['normal_keyword'] + ' ' + normalized_card['normal_title'] + ' ' + normalized_card['normal_text']
            if len(text.split()) > 0:
                card_ids.append(normalized_card['card_id'])
                documents.append(text)

        return documents, card_ids

    def normalize_cards(self, cards):
        documents = []
        card_ids = []

        for card in cards:
            normalized_keyword, normalized_title, normalized_text, card_id = self.normalize_card(card)
            if card_id > 0 and (normalized_keyword != '' or normalized_title != '' or normalized_text != ''):
                card_ids.append(card_id)
                documents.append(normalized_keyword + ' ' + normalized_title + ' ' + normalized_text)

        return documents, card_ids

    def normalize_card(self, card):
        card_id = int(card['id'])
        normalized_keyword = ''
        normalized_title = ''
        normalized_text = ''

        if card_id > 0:
            phoenix = self.mongo.phoenix
            normal_cache = phoenix.normal_cache
            threshold = time.time() - (60 * 60 * 24)
            normal_card = normal_cache.find_one({'card_id': card_id, 'normal_time': {'$gt': threshold}})
            if normal_card is None:
                if card['title'] is not None:
                    normalized_title = str(card['title'])
                if card['text'] is not None:
                    normalized_text = str(card['text'])
                if card['keywords'] is not None:
                    normalized_keyword = str(' '.join(card['keywords']))
                if card_id > 0:
                    if normalized_keyword == '':
                        normalized_keyword = 'empty'
                    if normalized_title == '':
                        normalized_title = 'empty'
                    if normalized_text == '':
                        normalized_text = 'empty'
                new_normal_card = {
                    'card_id': card_id,
                    'normal_time': time.time(),
                    'normal_keyword': normalized_keyword,
                    'normal_title': normalized_title,
                    'normal_text': normalized_text
                }
                normal_card = normal_cache.find_one({'card_id': card_id})
                if normal_card is not None:
                    normal_cache.replace_one({'card_id': card_id}, new_normal_card)
                else:
                    normal_cache.insert_one(new_normal_card)
            else:
                normalized_keyword = normal_card['normal_keyword']
                normalized_title = normal_card['normal_title']
                normalized_text = normal_card['normal_text']

        return normalized_keyword, normalized_title, normalized_text, card_id
