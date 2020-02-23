from bin.module import Latest
from bin.service import ContextSearch, CardStorage, Logger


class Search:

    def __init__(self):
        self.search = ContextSearch.ContextSearch()
        self.storage = CardStorage.CardStorage()
        self.latest = Latest.Latest()
        self.logger = Logger.Logger()

    def run(self, query):

        if query is '':
            return self.latest.run()

        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            found_cards = []
            card_ids = self.search.search(query)
            for card_id in card_ids:
                card = self.storage.get_card(card_id)
                card.versions = None
                found_cards.append(card.__dict__)
            result['items'].append({
                'query': query,
                'cards': found_cards
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result