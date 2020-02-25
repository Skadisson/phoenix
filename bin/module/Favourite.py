from bin.service import CardStorage, FavouriteStorage, Logger
from bin.entity import User


class Favourite:

    def __init__(self):
        self.card_storage = CardStorage.CardStorage()
        self.favourite_storage = FavouriteStorage.FavouriteStorage()
        self.logger = Logger.Logger()

    def run(self, card_id):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            """TODO: User Handling"""
            user = User.User()
            user.id = 1
            card = self.card_storage.get_card(card_id)
            favourite, is_added = self.favourite_storage.toggle_favourite(card, user)
            result['items'].append({
                'is_added': is_added,
                'favourite': favourite.__dict__
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
