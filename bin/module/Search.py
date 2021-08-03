from bin.module import Latest
from bin.service import ContextSearch, CardStorage, Logger, UserStorage, AchievementStorage
import re


class Search:

    def __init__(self):
        self.search = ContextSearch.ContextSearch()
        self.card_storage = CardStorage.CardStorage()
        self.latest = Latest.Latest()
        self.logger = Logger.Logger()
        self.user_storage = UserStorage.UserStorage()
        self.achievement_storage = AchievementStorage.AchievementStorage()

    def run(self, query, include_jira):

        if query == '':
            return self.latest.run()
        if include_jira == 'True':
            include_jira = True
        else:
            include_jira = False

        result = {
            'items': [],
            'success': True,
            'error': None
        }
        """try:"""

        found_cards = []
        words = None
        if query.isnumeric():
            card_ids = [int(query)]
            cards = self.card_storage.get_cards(card_ids)
        else:
            user = self.user_storage.get_user()
            self.achievement_storage.track_search_triggered(user['id'])
            cards = self.search.search(query, include_jira)
            words = str(query).split()
        for card in cards:
            if '_id' in card:
                del(card['_id'])
            card['words'] = {}
            if words is not None:
                i = 0
                for word in words:
                    if i > 6:
                        card['words']['...'] = 0
                        break
                    count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), card['text']))
                    count += sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), card['title']))
                    card['words'][word] = count
                    i += 1
            if card not in found_cards:
                found_cards.append(card)
        result['items'].append({
            'query': query,
            'count': len(found_cards),
            'cards': found_cards
        })

        """except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)"""

        return result
