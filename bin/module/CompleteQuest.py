from bin.service import Logger, UserStorage, AchievementStorage


class CompleteQuest:

    def __init__(self):
        self.logger = Logger.Logger()
        self.user_storage = UserStorage.UserStorage()
        self.achievement_storage = AchievementStorage.AchievementStorage()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            user = self.user_storage.get_user()
            self.achievement_storage.track_quest_completed(user['id'])

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
