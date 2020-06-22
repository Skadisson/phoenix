from bin.entity import ShoutOut
from bin.service import Environment
from pymongo import MongoClient
import time


class ShoutOutStorage:

    def __init__(self):
        self.mongo = MongoClient()
        self.environment = Environment.Environment()
        self.shout_out_life_time = 60 * 60 * 24
        self.shout_out_life_time *= self.environment.get_service_shout_out_liftime_days()

    def add_shout_out(self, card_id, text, user_id=0):
        exists = self.shout_out_exists(card_id, user_id)
        shout_out = None
        if exists is False:
            phoenix = self.mongo.phoenix
            shout_out_storage = phoenix.shout_out_storage
            shout_out = self.create_shout_out(card_id, text, user_id)
            shout_out_storage.insert_one(dict(shout_out))
        return shout_out

    @staticmethod
    def create_shout_out(card_id, text, user_id=0):
        shout_out = ShoutOut.ShoutOut()
        shout_out.card_id = card_id
        shout_out.created = time.time()
        shout_out.text = text
        shout_out.user_id = user_id
        return shout_out

    def shout_out_exists(self, card_id, user_id):
        phoenix = self.mongo.phoenix
        shout_out_storage = phoenix.shout_out_storage
        lifetime_range = time.time() - self.shout_out_life_time
        shout_outs = shout_out_storage.find({'card_id': card_id, 'user_id': user_id, 'created': {'$gt': lifetime_range}})
        return shout_outs.count() > 0

    def card_id_has_shout_out(self, card_id):
        shout_outs = self.get_card_shout_outs(card_id)
        return shout_outs.count() > 0

    def get_card_shout_outs(self, card_id):
        phoenix = self.mongo.phoenix
        shout_out_storage = phoenix.shout_out_storage
        lifetime_range = time.time() - self.shout_out_life_time
        shout_outs = shout_out_storage.find({'card_id': card_id, 'created': {'$gt': lifetime_range}})
        return shout_outs

    def get_shout_outs(self):
        phoenix = self.mongo.phoenix
        shout_out_storage = phoenix.shout_out_storage
        lifetime_range = time.time() - self.shout_out_life_time
        shout_outs = shout_out_storage.find({'created': {'$gt': lifetime_range}})
        return shout_outs
