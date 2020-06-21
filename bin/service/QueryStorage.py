from bin.entity import Query
from pymongo import MongoClient
import time


class QueryStorage:

    def __init__(self):
        self.mongo = MongoClient()

    def store_query(self, card_id, searched_query, loading_seconds):
        if searched_query != '':
            query = Query.Query()
            query.card_id = card_id
            query.query = searched_query
            query.searched = time.time()
            query.loading_seconds = loading_seconds
            self.mongo.phoenix.query.insert_one(dict(query))

    def get_queries(self):
        return self.mongo.phoenix.query.find()
