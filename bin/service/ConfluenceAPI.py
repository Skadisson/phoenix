from bin.service import Environment
from atlassian import Confluence
import os
import pickle


class ConfluenceAPI:

    def __init__(self):
        self.environment = Environment.Environment()
        self.confluence = Confluence(
            self.environment.get_endpoint_confluence_host(),
            username=self.environment.get_endpoint_confluence_user(),
            password=self.environment.get_endpoint_confluence_password()
        )

    def sync_entries(self):

        confluence_spaces = self.environment.get_map_confluence_spaces()

        confluence_entries = []
        for confluence_space in confluence_spaces:
            confluence_entries += self.load_entries_from_space(confluence_space)
        self.cache_entries(confluence_entries)

        return len(confluence_entries)

    def load_entries_from_space(self, space='CS'):

        space_pages = []
        limit = 50
        start = 0
        pages = self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='page')
        while len(pages) > 0:
            for page in pages:
                space_pages.append({
                    'space': space,
                    'id': page['id'],
                    'title': page['title'],
                    'body': page['body']['view']['value'],
                    'created': page['history']['createdDate'],
                    'link': self.environment.get_endpoint_confluence_host() + page['_links']['webui']
                })
            start += limit
            pages = self.confluence.get_all_pages_from_space(space, start=start, limit=limit, status=None, expand='body.view,history', content_type='page')

        return space_pages

    def cache_entries(self, entries):

        confluence_cache_path = self.environment.get_path_confluence_cache()
        file = open(confluence_cache_path, "wb")
        pickle.dump(obj=entries, file=file)
        file.close()

    def load_cached_entries(self):

        confluence_entries = []
        confluence_cache_path = self.environment.get_path_confluence_cache()
        file_exists = os.path.isfile(confluence_cache_path)
        if file_exists:
            file = open(confluence_cache_path, "rb")
            confluence_entries = pickle.load(file)
            file.close()

        return confluence_entries
