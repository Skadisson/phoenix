from bin.service import FavouriteStorage
from bin.entity import Card
from bin.entity import User
import os
import random


class TestFavouriteStorage:

    def __init__(self, test_favourite):
        self.test_favourite = test_favourite
        self.test_user_count = 10
        self.test_card_count = 20
        self.test_favourite_count = 1000

    def run(self):

        is_existing = os.path.exists(self.test_favourite)
        if is_existing:
            os.remove(self.test_favourite)

        favourite_storage = FavouriteStorage.FavouriteStorage(self.test_favourite)
        users = self.create_random_users(self.test_user_count)
        cards = self.create_random_cards(self.test_card_count)
        expected_favourites = {}

        clicks = self.test_favourite_count
        while clicks > 0:
            card_id = random.randint(1, self.test_card_count)
            user_id = random.randint(1, self.test_user_count)
            card = cards[card_id]
            user = users[user_id]
            favourite, is_added = favourite_storage.toggle_favourite(card, user)
            if is_added:
                expected_favourites[favourite.id] = favourite
            else:
                del(expected_favourites[favourite.id])
            clicks -= 1

        actual_favourites = favourite_storage.get_all_favourites()
        success = actual_favourites == expected_favourites

        return success

    def create_random_cards(self, length):
        cards = {}
        for card_id in range(1, length + 1):
            cards[card_id] = self.create_random_card(card_id)
        return cards

    @staticmethod
    def create_random_card(card_id):
        card = Card.Card()
        card.id = card_id
        card.likes = 0
        card.title = random.getrandbits(10)

        return card

    def create_random_users(self, length):
        users = {}
        for user_id in range(1, length + 1):
            users[user_id] = self.create_random_user(user_id)
        return users

    @staticmethod
    def create_random_user(user_id):
        user = User.User()
        user.id = user_id
        user.alias = random.getrandbits(3)

        return user
