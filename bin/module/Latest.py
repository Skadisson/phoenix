from bin.service import CardStorage, Logger


class Latest:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.logger = Logger.Logger()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            cards = self.storage.get_latest_cards(20)
            result['items'].append({
                'cards': cards
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
