from bin.service import Logger, NotificationStorage, UserStorage


class Notifications:

    def __init__(self):
        self.notification_storage = NotificationStorage.NotificationStorage()
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
            dict_notifications = []
            notifications = self.notification_storage.get_notifications(user.id)
            self.notification_storage.flag_notifications_as_notified(notifications)
            for notification in notifications:
                notification = dict(notification)
                if '_id' in notification:
                    del(notification['_id'])
                dict_notifications.append(dict(notification))
            result['items'].append({
                'notifications': dict_notifications
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
