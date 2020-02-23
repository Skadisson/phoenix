from bin.service import ContextSearch


class TestContextSearch:

    def __init__(self, cache_path):
        self.relevancy_search = ContextSearch.ContextSearch(cache_path)
        self.target_id = 10
        self.query = 'Falsch zugeordnete Angebote'
        self.title = '6-Seiter Bemaßung'
        self.text = 'Abmessungen beim Flyer 6-Seiten sind noch nicht korrekt'

    def run(self):

        card_ids = self.relevancy_search.search(self.query)
        success = self.target_id in card_ids

        if success:
            expected_keywords = 'bb42,calculation,dimensions,generation,merge,pdf,print'
            actual_keywords = self.relevancy_search.suggest_keywords(self.title, self.text)
            success = expected_keywords == actual_keywords

        return success
