from bin.service import CardStorage, Logger, NotificationStorage, UserStorage


class Store:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.notification_storage = NotificationStorage.NotificationStorage()
        self.logger = Logger.Logger()

    def run(self, title, text, keywords, external_link, card_id):

        result = {
            'items': [],
            'success': True,
            'error': None
        }

        if title == '' or text == '':
            result['success'] = False
            result['error'] = 'Title or text missing'
            return result

        try:

            user_storage = UserStorage.UserStorage()
            user = user_storage.get_user()
            card_exists = False
            if card_id > 0:
                card_exists = self.storage.card_exists(card_id)

            if card_exists:
                card = self.storage.get_card(card_id)
                card['title'] = title
                card['text'] = text
                card['external_link'] = external_link
                card['keywords'] = keywords.split(',')
                if card['editors'] is None:
                    card['editors'] = []
                if user.short not in card['editors']:
                    card['editors'].append(user.short)
                if card['author'] is None:
                    card['author'] = user.short
                card['type'] = 'fact'
                self.storage.update_card(card)
            else:
                card_id = self.storage.create_card(title, text, keywords, external_link)
                self.notification_storage.add_notification(card_id, title, user.id, False)

            result['items'].append({
                'card_id': card_id
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
