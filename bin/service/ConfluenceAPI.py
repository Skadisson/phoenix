from bin.service import Environment
from bin.service import Logger
from bin.service import CardTransfer
from bin.service import RegEx
from bin.service import Storage
from atlassian import Confluence
import time


class ConfluenceAPI(Storage.Storage):

    def __init__(self):
        super().__init__()
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
        space_keys = self.load_space_keys()
        confluence_ids = []
        for space_key in space_keys:
            start = float(time.time())
            confluence_entries = {}
            space_entries = self.load_entries_from_space(space_key)
            for confluence_id in space_entries:
                exists = self.entry_exists(confluence_id)
                if exists is True:
                    continue
                confluence_ids.append(confluence_id)
                confluence_entries[confluence_id] = space_entries[confluence_id]
            self.cache_entries(confluence_entries)
            cached_current = len(confluence_entries)
            cached_total += cached_current
            stop = float(time.time())
            seconds = (stop - start)
            print('>>> cached {} confluence entries from space "{}" of {} entries total after {} seconds'.format(cached_current, space_key, cached_total, seconds))
            time.sleep(wait)
        self.transfer_entries()

    def load_space_keys(self):
        space_keys = []

        spaces = self.confluence.get_all_spaces()
        for space in spaces['results']:
            if space['key'] not in space_keys:
                space_keys.append(space['key'])

        return space_keys

    def get_confluence_ids(self):
        phoenix = self.mongo.phoenix
        confluence_storage = phoenix.confluence_storage
        return list(confluence_storage.distinct('id'))

    def get_confluence_card_ids(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        return list(card_storage.distinct('relation_id', {'relation_type': 'confluence'}))

    def transfer_entries(self):
        confluence_ids = self.get_confluence_ids()
        confluence_card_ids = self.get_confluence_card_ids()
        confluence_ids_to_transfer = list(set(confluence_ids) - set(confluence_card_ids))
        print('>>> confluence synchronization started for {} cards'.format(len(confluence_ids_to_transfer)))
        confluence_entries = self.load_cached_entries(confluence_ids_to_transfer)
        created_card_ids = self.card_transfer.transfer_confluence(confluence_entries)
        created_current = len(created_card_ids)
        print('>>> confluence synchronization completed, {} new cards created'.format(created_current))

    def entry_exists(self, confluence_id):
        phoenix = self.mongo.phoenix
        confluence_storage = phoenix.confluence_storage
        entry = confluence_storage.find_one({'id': confluence_id}, no_cursor_timeout=True)
        return entry is not None

    def load_entries_from_space(self, space='CS'):

        space_pages = {}
        limit = 50
        start = 0
        try:
            pages = self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='page')
            pages += self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='blogpost')
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
                pages += self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='blogpost')
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

    def load_cached_entries(self, confluence_ids=None):
        try:
            phoenix = self.mongo.phoenix
            confluence_storage = phoenix.confluence_storage
            if confluence_ids is None:
                return confluence_storage.find(no_cursor_timeout=True)
            else:
                return confluence_storage.find({'id': {'$in': confluence_ids}}, no_cursor_timeout=True)
        except Exception as e:
            self.logger.add_entry(self.__class__.__name__, str(e))
