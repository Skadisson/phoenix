from bin.service import FavouriteStorage
from bin.entity import Card
from bin.entity import User
from bin.entity import Favourite
import os


class TestCardTransfer:

    def __init__(self, test_path):
        self.test_path = test_path
        self.transfer = FavouriteStorage.FavouriteStorage(self.test_path)

    def run(self):

        """TODO: TBI"""

        return True
