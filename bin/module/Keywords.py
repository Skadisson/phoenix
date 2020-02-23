from bin.service import CardStorage, ContextSearch, SciKitLearn, Logger


class Keywords:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.context_search = ContextSearch.ContextSearch()
        self.sci_kit_learn = SciKitLearn.SciKitLearn()
        self.logger = Logger.Logger()

    def run(self, title, text):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            suggested_keywords = self.context_search.suggest_keywords(title, text)
            result['items'].append({
              'suggested_keywords': suggested_keywords
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
