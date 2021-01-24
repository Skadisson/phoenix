from bin.service import Environment
from bin.service import Logger
import pymongo
import time


class Storage:

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()
        self.mongo = None
        self.connect_mongodb()

    def connect_mongodb(self):
        connected = False
        tries = 0
        max_tries = 3
        delay_seconds = 3
        start = time.time()
        while connected is False and tries <= max_tries:
            tries += 1
            try:
                endpoint = self.environment.get_endpoint_mongo_db_cloud()
                if endpoint != '':
                    self.mongo = pymongo.MongoClient(endpoint)
                else:
                    self.mongo = pymongo.MongoClient()
                connected = True
            except Exception as e:
                self.logger.add_entry(self.__class__.__name__, e)
                connected = False
                time.sleep(delay_seconds)
        if connected is False:
            took_seconds = time.time() - start
            raise Exception(f"{self.__class__.__name__}: Connection to mongodb failed after {max_tries} tries and {took_seconds} seconds.")
