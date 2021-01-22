from bin.service import Info, Logger, UserStorage


class Ping:

    def __init__(self):
        self.info = Info.Info()
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
            fact_count = self.info.get_fact_count()
            idea_count = self.info.get_idea_count()
            result['items'].append({
                'user_name': user['name'],
                'user_short': user['short'],
                'fact_count': fact_count,
                'idea_count': idea_count
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
