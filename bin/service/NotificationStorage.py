from bin.entity import Notification
from bin.service import Environment
from pymongo import MongoClient
import time


class NotificationStorage:

    def __init__(self):
        """
        TODO: bin.service.Environment.Environment.get_endpoint_mongo_db_cloud
        """
        self.mongo = MongoClient()
        self.environment = Environment.Environment()

    def add_notification(self, card_id, title, user_id=0, is_shout_out=False):
        phoenix = self.mongo.phoenix
        notification_storage = phoenix.notification_storage
        notification = self.create_notification(card_id, title, user_id, is_shout_out)
        notification_storage.insert_one(dict(notification))
        return notification

    @staticmethod
    def create_notification(card_id, title, user_id=0, is_shout_out=False):
        notification = Notification.Notification()
        notification.card_id = card_id
        notification.title = title
        notification.created = time.time()
        notification.is_shout_out = is_shout_out
        notification.user_id = user_id
        notification.notified = None
        return notification

    def get_notifications(self, user_id):
        phoenix = self.mongo.phoenix
        notification_storage = phoenix.notification_storage
        notifications = notification_storage.find({'notified': None, 'user_id': user_id})
        return notifications

    def flag_notifications_as_notified(self, notifications):
        phoenix = self.mongo.phoenix
        notification_storage = phoenix.notification_storage
        for notification in notifications:
            notification['notified'] = time.time()
            notification_storage.replace_one({'card_id': notification['card_id'], 'user_id': notification['user_id']}, notification)

    def un_notified_notification_exists(self, card_id, user_id):
        phoenix = self.mongo.phoenix
        notification_storage = phoenix.notification_storage
        notification = notification_storage.find_one({'card_id': card_id, 'user_id': user_id})
        return notification is not None
