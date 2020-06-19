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
            if query.isnumeric():
                card_ids = [int(query)]
                cards = self.storage.get_cards(card_ids)
            else:
                cards = self.search.search(query)
            for card in cards:
                if '_id' in card:
                    del(card['_id'])
                found_cards.append(card)
            result['items'].append({
                'query': query,
                'count': len(found_cards),
                'cards': found_cards
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
