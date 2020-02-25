from bin.service import CardStorage, Logger


class Favourite:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.logger = Logger.Logger()

    def run(self, card_id):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            """TODO: TBI"""

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
