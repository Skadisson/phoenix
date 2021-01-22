from bin.service import Logger, UserStorage


class Name:

    def __init__(self):
        self.logger = Logger.Logger()

    def run(self, name):
        result = {
            'message': '',
            'success': True,
            'error': None
        }
        try:

            user_storage = UserStorage.UserStorage()
            try:
                user_storage.rename_user(name)
                result['message'] = 'Name geändert'
            except Exception as e:
                result['message'] = str(e)
                result['success'] = False

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
