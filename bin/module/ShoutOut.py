from bin.service import ShoutOutStorage, Logger
from bin.entity import User


class ShoutOut:

    def __init__(self):
        self.so_storage = ShoutOutStorage.ShoutOutStorage()
        self.logger = Logger.Logger()

    def run(self, card_id, text):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            """TODO: User Handling"""
            user = User.User()
            user.id = 1
            shout_out = self.so_storage.add_shout_out(card_id, text, user.id)
            is_added = False
            if shout_out is not None:
                is_added = True
                shout_out = dict(shout_out)
            result['items'].append({
                'is_added': is_added,
                'favourite': shout_out
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
