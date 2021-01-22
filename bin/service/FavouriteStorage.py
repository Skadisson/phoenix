from bin.entity import Favourite
from bin.service import Environment
from pymongo import MongoClient
import time


class FavouriteStorage:

    def __init__(self):
        self.environment = Environment.Environment()
        self.mongo = MongoClient(self.environment.get_endpoint_mongo_db_cloud())

    def add_favourite(self, card, user):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite_id = self.get_next_id()
        favourite = self.create_favourite(favourite_id, card, user)
        favourite_storage.insert_one(dict(favourite))
        return favourite

    @staticmethod
    def create_favourite(favourite_id, card, user):
        favourite = Favourite.Favourite()
        favourite.id = favourite_id
        favourite.created = time.time()
        favourite.user_id = user['id']
        favourite.card_id = card['id']
        favourite.card_title = card['title']
        return favourite

    def find_favourite(self, card, user):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite = favourite_storage.find_one({'card_id': card['id'], 'user_id': user['id']})
        return favourite

    def favourite_exists(self, card, user):
        favourite = self.find_favourite(card, user)
        return favourite is not None

    def get_all_favourites(self):
        return self.load_favourites()

    def get_favourite(self, favourite_id):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite = favourite_storage.find_one({'id': favourite_id})
        return favourite

    def get_ranked_favourite_card_ids(self):
        card_ids = {}
        favourites = self.load_favourites()
        for favourite in favourites:
            if favourite['card_id'] not in card_ids:
                card_ids[favourite['card_id']] = 1
            else:
                card_ids[favourite['card_id']] += 1
        return card_ids

    def get_next_id(self):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        max_id_favourites = favourite_storage.find(sort=[('id', -1)]).limit(1)
        if max_id_favourites.count() > 0:
            next_id = max_id_favourites[0]['id'] + 1
        else:
            next_id = 1

        return next_id

    def get_user_favourites(self, user):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        user_favourites = favourite_storage.find({'user_id': user['id']})
        return user_favourites

    def load_favourites(self):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourites = favourite_storage.find()
        return favourites

    def remove_favourite(self, card, user):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite_storage.remove({'card_id': card['id'], 'user_id': user['id']})

    def toggle_favourite(self, card, user):
        favourite = None
        favourite_exists = self.favourite_exists(card, user)
        if favourite_exists:
            is_added = False
            self.remove_favourite(card, user)
        else:
            is_added = True
            favourite = self.add_favourite(card, user)
        return favourite, is_added

    def update_favourite_title(self, card_id, title):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite = self.get_favourite_by_card_id(card_id)
        if favourite is not None:
            favourite['card_title'] = title
            favourite_storage.replace_one({'id': favourite['id']}, favourite)

    def get_favourite_by_card_id(self, card_id):
        phoenix = self.mongo.phoenix
        favourite_storage = phoenix.favourite_storage
        favourite = favourite_storage.find_one({'card_id': card_id})
        return favourite
