from bin.service import CardStorage, Logger
import copy


class Store:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
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

            card_exists = False
            if card_id > 0:
                card_exists = self.storage.card_exists(card_id)

            if card_exists:
                card = self.storage.get_card(card_id)
                card.title = title
                card.text = text
                card.external_link = external_link
                card.keywords = keywords.split(',')
                """TODO: User Handling"""
                if card.editors is None:
                    card.editors = []
                if 'ses' not in card.editors:
                    card.editors.append('ses')
                if card.author is None:
                    card.author = 'ses'
                card.type = 'fact'
                self.storage.update_card(card)
            else:
                card_id = self.storage.create_card(title, text, keywords, external_link)

            result['items'].append({
                'card_id': card_id
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
