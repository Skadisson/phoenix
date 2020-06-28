from bin.entity import Query
from pymongo import MongoClient
import time


class QueryStorage:

    def __init__(self):
        self.mongo = MongoClient()

    def store_query(self, card_id, searched_query, loading_seconds, frontend):
        if searched_query != '' or card_id > 0:
            query = Query.Query()
            query.card_id = card_id
            query.query = searched_query
            query.searched = time.time()
            query.loading_seconds = loading_seconds
            query.frontend = frontend
            self.mongo.phoenix.query.insert_one(dict(query))

    def get_queries(self):
        return self.mongo.phoenix.query.find()

    def get_desktop_queries(self):
        return self.mongo.phoenix.query.find({'frontend': 'desktop'})

    def get_mobile_queries(self):
        return self.mongo.phoenix.query.find({'frontend': 'mobile'})

    def get_queries_with_loading_time(self):
        return self.mongo.phoenix.query.find({'loading_seconds': {'$gt': 0}})
