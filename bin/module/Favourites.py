from bin.service import FavouriteStorage, Logger, UserStorage


class Favourites:

    def __init__(self):
        self.storage = FavouriteStorage.FavouriteStorage()
        self.logger = Logger.Logger()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            user_storage = UserStorage.UserStorage()
            user = user_storage.get_user()
            favourites = self.storage.get_user_favourites(user)
            dict_favourites = []
            for favourite in favourites:
                favourite = dict(favourite)
                del(favourite['_id'])
                dict_favourites.append(favourite)
            favourites_by_name = sorted(dict_favourites, key=lambda fav: fav['card_title'], reverse=True)
            result['items'].append({
                'favourites': favourites_by_name
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
