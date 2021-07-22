from bin.service import Logger, UserStorage, AchievementStorage


class Achievements:

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
            achievement = self.achievement_storage.get_achievement(user['id'])
            achievements = self.achievement_storage.update_achievements(user['id'])
            if '_id' in achievement:
                del(achievement['_id'])
            result['items'].append({
                'achievement': dict(achievement),
                'achievements': achievements
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
