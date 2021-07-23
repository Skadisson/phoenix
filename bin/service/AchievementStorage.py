from bin.entity import Achievement
from bin.service import Storage
import time
import os
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class AchievementStorage(Storage.Storage):

    def __init__(self):
        super().__init__()
        self.achievements_path = "config/achievements.yaml"

    def get_storage(self):
        phoenix = self.mongo.phoenix
        return phoenix.achievement_storage

    def get_achievement(self, user_id):
        storage = self.get_storage()
        achievement = storage.find_one({'user_id': user_id})
        return achievement

    def create_achievement(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is None:
            achievement = Achievement.Achievement()
            achievement.user_id = user_id
            storage = self.get_storage()
            storage.insert_one(dict(achievement))

    def update_achievements(self, user_id):
        achievement = dict(self.get_achievement(user_id))
        achievements = self.read_achievements()
        new_achievements = []
        for label in achievements:
            requirement = str(achievements[label]['requirement']).split(' >= ')
            if requirement[0] not in achievement:
                raise Exception(f"Requirement for {label} in {self.achievements_path} is missing or faulty.")
            if achievement[requirement[0]] >= int(requirement[1]) and label not in achievement['labels']:
                new_achievements.append(achievements[label])
                achievement['labels'].append(label)
                self.update_achievement(user_id, achievement)

        current_achievements = self.read_achievements_for_labels(achievement['labels'])
        return current_achievements, new_achievements

    def track_login(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            self.reset_today_trackers(achievement)
            achievement['last_login'] = time.time()
            achievement['logged_in'] += 1
            achievement['logged_in_today'] += 1
            self.update_achievement(user_id, achievement)

    def track_shout_out(self, user_id, shout_outs_before):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            if shout_outs_before > 0:
                achievement['shout_outs_reacted'] += 1
            achievement['shout_outs_created'] += 1
            achievement['shout_outs_created_today'] += 1
            self.update_achievement(user_id, achievement)

    def track_fact_created(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['facts_created'] += 1
            achievement['facts_created_today'] += 1
            self.update_achievement(user_id, achievement)

    def track_fact_edited(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['facts_edited'] += 1
            self.update_achievement(user_id, achievement)

    def track_idea_edited(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['ideas_edited'] += 1
            self.update_achievement(user_id, achievement)

    def track_card_clicked(self, user_id, card_type=None):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['cards_clicked'] += 1
            achievement['cards_clicked_today'] += 1
            if card_type is not None:
                achievement[f"{card_type}_tickets_clicked"] += 1
            self.update_achievement(user_id, achievement)

    def track_favourite_created(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['favourites_created'] += 1
            self.update_achievement(user_id, achievement)

    def track_favourite_deleted(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['favourites_deleted'] += 1
            self.update_achievement(user_id, achievement)

    def track_search_triggered(self, user_id):
        achievement = self.get_achievement(user_id)
        if achievement is not None:
            achievement['searches_triggered'] += 1
            achievement['searches_triggered_today'] += 1
            self.update_achievement(user_id, achievement)

    def update_achievement(self, user_id, achievement):
        storage = self.get_storage()
        storage.replace_one({'user_id': user_id}, achievement)

    def read_achievements(self):
        if os.path.isfile(self.achievements_path) is False:
            raise Exception(f"{self.achievements_path} is missing.")
        stream = open(self.achievements_path, 'rb')
        return load(stream, Loader=Loader)

    def read_achievements_for_labels(self, labels):
        achievements = []
        raw_achievements = self.read_achievements()
        for label in labels:
            if label not in raw_achievements:
                raise Exception(f"Label {label} is missing inside {self.achievements_path}.")
            achievements.append(raw_achievements[label])
        return achievements

    @staticmethod
    def reset_today_trackers(achievement):
        if achievement['last_login'] is not None:
            date_then = time.strftime("%Y-%m-%d", time.gmtime(achievement['last_login']))
            date_now = time.strftime("%Y-%m-%d", time.gmtime(time.time()))
            if date_then != date_now:
                achievement['facts_created_today'] = 0
                achievement['cards_clicked_today'] = 0
                achievement['logged_in_today'] = 0
                achievement['shout_outs_created_today'] = 0
                achievement['searches_triggered_today'] = 0
