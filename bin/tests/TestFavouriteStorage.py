from bin.service import FavouriteStorage
from bin.entity import Card
from bin.entity import User
from bin.entity import Favourite
import os
import random


class TestCardTransfer:

    def __init__(self, test_path):
        self.test_path = test_path
        self.transfer = FavouriteStorage.FavouriteStorage(self.test_path)

    def run(self):

        users = self.create_random_users(10)
        cards = self.create_random_cards(20)
        clicks = 10000
        expected_favourites = []



        return True

    def create_random_cards(self, length):
        cards = []
        for card_id in range(1, length):
            cards.append(self.create_random_card(card_id))
        return cards

    @staticmethod
    def create_random_card(card_id):
        card = Card.Card()
        card.id = card_id
        card.likes = 0

        return card

    def create_random_users(self, length):
        users = []
        for user_id in range(1, length):
            users.append(self.create_random_user(user_id))
        return users

    @staticmethod
    def create_random_user(user_id):
        user = User.User()
        user.id = user_id
        user.alias = random.getrandbits(3)

        return user
