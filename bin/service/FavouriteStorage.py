from bin.service import Environment
from bin.entity import Favourite
import pickle
import os
import time


class FavouriteStorage:

    def __init__(self, cache_path=None):
        self.environment = Environment.Environment()
        if cache_path is None:
            self.cache_path = self.environment.get_path_favourites()
        else:
            self.cache_path = cache_path
        self.favourites = {}
        self.load_favourites()

    def add_favourite(self, card, user):
        favourite_id = self.get_next_id()
        favourite = self.create_favourite(favourite_id, card, user)
        self.favourites[favourite_id] = favourite
        self.store_favourites()
        return favourite

    @staticmethod
    def create_favourite(favourite_id, card, user):
        favourite = Favourite.Favourite()
        favourite.id = favourite_id
        favourite.created = time.time()
        favourite.user_id = user.id
        favourite.card_id = card.id
        return favourite

    def favourite_exists(self, card, user):
        favourite = self.search_favourite(card, user)
        return favourite is not None

    def get_all_favourites(self):
        return self.favourites

    def get_favourite(self, favourite_id):
        if favourite_id in self.favourites:
            return self.favourites[favourite_id]
        else:
            return None

    def get_next_id(self):
        if len(self.favourites) > 0:
            favourite_ids = self.favourites.keys()
            next_id = max(favourite_ids) + 1
        else:
            next_id = 1
        return next_id

    def load_favourites(self):
        cache_file = self.cache_path
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            file = open(cache_file, "wb")
            content = {}
            pickle.dump(content, file)
        self.favourites = content

    def remove_favourite(self, card, user):
        favourite = self.search_favourite(card, user)
        if favourite is not None:
            del(self.favourites[favourite.id])
            self.store_favourites()
        return favourite

    def search_favourite(self, card, user):
        favourite = None
        for favourite_id in self.favourites:
            if self.favourites[favourite_id].card_id == card.id and self.favourites[favourite_id].user_id == user.id:
                favourite = self.favourites[favourite_id]
                break
        return favourite

    def store_favourites(self):
        cache_file = self.cache_path
        file = open(cache_file, "wb")
        pickle.dump(self.favourites, file)

    def toggle_favourite(self, card, user):
        favourite_exists = self.favourite_exists(card, user)
        if favourite_exists:
            is_added = False
            favourite = self.remove_favourite(card, user)
        else:
            is_added = True
            favourite = self.add_favourite(card, user)
        self.store_favourites()
        return favourite, is_added
