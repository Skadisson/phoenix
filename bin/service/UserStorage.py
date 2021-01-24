from bin.service import Storage
from bin.entity import User
import uuid


class UserStorage(Storage.Storage):

    def get_user(self):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        mac_number = uuid.getnode()
        user = user_storage.find_one({'id': mac_number})
        if user is None:
            raise Exception('No active user found.')
        return user

    def get_user_by_id(self, user_id):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        user = user_storage.find_one({'id': user_id})
        return user

    def user_exists(self):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        mac_number = uuid.getnode()
        users = user_storage.find({'id': mac_number})
        return users.count() > 0

    def short_exists(self, short):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        users = user_storage.find({'short': short})
        return users.count() > 0

    def create_user(self):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        mac_number = uuid.getnode()
        user = User.User()
        user.id = mac_number
        user.name = 'anonymous'
        user.short = 'ano'
        user_storage.insert_one(dict(user))

    def rename_user(self, name):
        phoenix = self.mongo.phoenix
        user_storage = phoenix.user_storage
        mac_number = uuid.getnode()
        name_parts = name.split(' ')
        if len(name_parts) > 1:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            if len(first_name) >= 2:
                short = str(first_name[0]).upper() + str(first_name[1]).upper() + str(last_name[0]).upper()
                i = 1
                while self.short_exists(short):
                    i += 1
                    short = str(first_name[0]).upper() + str(first_name[1]).upper() + str(last_name[0]).upper() + str(i)
                user = {'id': mac_number, 'name': name, 'short': short}
                user_storage.replace_one({'id': mac_number}, user)
            else:
                raise Exception('User name is invalid.')
        else:
            raise Exception('User name is invalid.')

        return user
