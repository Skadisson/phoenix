from bin.service import Environment
from bin.entity import Card
from bin.entity import Favourite
from bin.entity import User
from shutil import copyfile
import pickle
import os
import time
import copy


class FavouriteStorage:

    def __init__(self, cache_path=None):
        self.environment = Environment.Environment()
        if cache_path is None:
            self.cache_path = self.environment.get_path_favourites()
        else:
            self.cache_path = cache_path

    def add_favourite(self, card, user):
        """TODO: TBI"""

    def favourite_exists(self, card, user):
        """TODO: TBI"""

    def load_favourites(self):
        """TODO: TBI"""

    def remove_favourite(self, card, user):
        """TODO: TBI"""

    def store_favourites(self, favourites):
        """TODO: TBI"""

    def toggle_favourite(self, card, user):
        """TODO: TBI"""
