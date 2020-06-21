from bin.entity import Query
from pymongo import MongoClient
import time


class QueryStorage:

    def __init__(self):
        self.mongo = MongoClient()

    def store_query(self, card_id, searched_query):
        if searched_query != '':
            query = Query.Query()
            query.card_id = card_id
            query.query = searched_query
            query.searched = time.time()
            self.mongo.phoenix.query.insert_one(dict(query))

    def get_queries(self):
        return self.mongo.phoenix.query.find()
