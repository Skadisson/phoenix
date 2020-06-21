from bin.service import CardStorage, Logger, QueryStorage


class Click:

    def __init__(self):
        self.card_storage = CardStorage.CardStorage()
        self.query_storage = QueryStorage.QueryStorage()
        self.logger = Logger.Logger()

    def run(self, card_id, query, loading_seconds):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            card = self.card_storage.get_card(card_id)
            card['clicks'] += 1
            self.query_storage.store_query(card_id, query, loading_seconds)
            self.card_storage.store_card(card)
            result['items'].append({
                'clicks': card['clicks']
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
