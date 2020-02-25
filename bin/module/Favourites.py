from bin.service import FavouriteStorage, Logger
from bin.entity import User


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

            """TODO: User Handling"""
            user = User.User()
            user.id = 1
            favourites = self.storage.get_user_favourites(user)
            dict_favourites = []
            for favourite_id in favourites:
                dict_favourites.append(favourites[favourite_id].__dict__)
            result['items'].append({
                'favourites': dict_favourites
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result