from bin.service import ShoutOutStorage, Logger, NotificationStorage, UserStorage, AchievementStorage


class ShoutOut:

    def __init__(self):
        self.so_storage = ShoutOutStorage.ShoutOutStorage()
        self.notification_storage = NotificationStorage.NotificationStorage()
        self.logger = Logger.Logger()
        self.achievement_storage = AchievementStorage.AchievementStorage()
        self.user_storage = UserStorage.UserStorage()

    def run(self, card_id, text):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            user = self.user_storage.get_user()
            shout_outs_before = self.so_storage.get_card_shout_outs(card_id)
            shout_out = self.so_storage.add_shout_out(card_id, text, user['id'])
            self.achievement_storage.track_shout_out(user['id'], shout_outs_before.count())
            is_added = False
            if shout_out is not None:
                is_added = True
                notification_exists = self.notification_storage.un_notified_notification_exists(card_id, user['id'])
                if notification_exists is False:
                    self.notification_storage.add_notification(card_id, text, user['id'], True)
                shout_out = dict(shout_out)
                shout_out['short'] = user['short']
                shout_out['name'] = user['name']
            result['items'].append({
                'is_added': is_added,
                'shout_out': shout_out
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
