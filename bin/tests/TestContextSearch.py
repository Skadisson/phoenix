from bin.service import ContextSearch


class TestContextSearch:

    def __init__(self, cache_path):
        self.relevancy_search = ContextSearch.ContextSearch(cache_path)
        self.target_id = 10
        self.query = 'Falsch zugeordnete Angebote'

    def run(self):

        card_ids = self.relevancy_search.search(self.query)
        success = self.target_id in card_ids

        return success
