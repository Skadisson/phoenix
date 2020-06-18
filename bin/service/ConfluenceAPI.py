from bin.service import Environment
from bin.service import Logger
from bin.service import CardTransfer
from bin.service import RegEx
from atlassian import Confluence
from pymongo import MongoClient
import time


class ConfluenceAPI:

    def __init__(self):
        self.mongo = MongoClient()
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.confluence = Confluence(
            self.environment.get_endpoint_confluence_host(),
            username=self.environment.get_endpoint_confluence_user(),
            password=self.environment.get_endpoint_confluence_password()
        )
        self.card_transfer = CardTransfer.CardTransfer()
        self.regex = RegEx.RegEx()

    def sync_entries(self, wait=2):
        cached_total = 0
        confluence_spaces = self.environment.get_map_confluence_spaces()
        for confluence_space in confluence_spaces:
            start = float(time.time())
            confluence_entries = {}
            space_entries = self.load_entries_from_space(confluence_space)
            confluence_ids = []
            for confluence_id in space_entries:
                confluence_ids.append(confluence_id)
                confluence_entries[confluence_id] = space_entries[confluence_id]
            self.cache_entries(confluence_entries)
            cached_current = len(confluence_entries)
            cached_total += cached_current
            stop = float(time.time())
            seconds = (stop - start)
            print('>>> cached {} confluence entries of {} entries total after {} seconds'.format(cached_current, cached_total, seconds))
            time.sleep(wait)
        confluence_entries = self.load_cached_entries()
        created_card_ids = self.card_transfer.transfer_confluence(confluence_entries)
        created_current = len(created_card_ids)
        print('>>> confluence synchronization completed, {} new cards created'.format(created_current))

    def load_entries_from_space(self, space='CS'):

        space_pages = {}
        limit = 50
        start = 0
        try:
            pages = self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='page')
        except Exception as err:
            self.logger.add_entry(self.__class__.__name__, str(err) + "; with space " + space)
            pages = []
        while len(pages) > 0:
            for page in pages:
                space_pages[page['id']] = {
                    'space': space,
                    'id': page['id'],
                    'title': page['title'],
                    'body': self.regex.mask_text(page['body']['view']['value']),
                    'created': page['history']['createdDate'],
                    'link': self.environment.get_endpoint_confluence_host() + page['_links']['webui']
                }
            start += limit
            try:
                pages = self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='page')
            except Exception as err:
                self.logger.add_entry(self.__class__.__name__, str(err) + "; with space " + space)
                pages = []

        return space_pages

    def cache_entries(self, entries):
        try:
            phoenix = self.mongo.phoenix
            confluence_storage = phoenix.confluence_storage
            for entry_id in entries:
                entry = confluence_storage.find_one({'id': entry_id})
                if entry is not None:
                    confluence_storage.replace_one({'id': entry_id}, entries[entry_id])
                else:
                    confluence_storage.insert_one(entries[entry_id])
        except Exception as e:
            self.logger.add_entry(self.__class__.__name__, str(e))

    def load_cached_entries(self):
        try:
            phoenix = self.mongo.phoenix
            confluence_storage = phoenix.confluence_storage
            return confluence_storage.find()
        except Exception as e:
            self.logger.add_entry(self.__class__.__name__, str(e))
