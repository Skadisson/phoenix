from bin.service import CardStorage, Logger, QueryStorage, UserStorage, AchievementStorage


class Click:

    def __init__(self):
        self.card_storage = CardStorage.CardStorage()
        self.query_storage = QueryStorage.QueryStorage()
        self.logger = Logger.Logger()
        self.user_storage = UserStorage.UserStorage()
        self.achievement_storage = AchievementStorage.AchievementStorage()

    def run(self, card_id, query, loading_seconds, frontend):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            user = self.user_storage.get_user()
            card = self.card_storage.get_card(card_id)
            card['clicks'] += 1
            card_type = None
            if 'SERVICE' in card['external_link']:
                card_type = 'service'
            elif 'DEVOPS' in card['external_link']:
                card_type = 'devops'
            elif 'QS' in card['external_link']:
                card_type = 'qa'
            elif 'BRANDBOX5' in card['external_link']:
                card_type = 'product'
            self.achievement_storage.track_card_clicked(user['id'], card_type)
            self.query_storage.store_query(card_id, query, loading_seconds, frontend)
            self.card_storage.store_card(card)
            result['items'].append({
                'clicks': card['clicks']
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
