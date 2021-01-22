from bin.service import CardStorage, FavouriteStorage, Logger, UserStorage


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

            user_storage = UserStorage.UserStorage()
            user = user_storage.get_user()
            card = self.card_storage.get_card(card_id)
            favourite, is_added = self.favourite_storage.toggle_favourite(card, user)
            if favourite is not None:
                favourite = dict(favourite)
            result['items'].append({
                'is_added': is_added,
                'favourite': favourite
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
