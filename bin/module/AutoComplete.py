from bin.service import Info, Logger


class AutoComplete:

    def __init__(self):
        self.info = Info.Info()
        self.logger = Logger.Logger()

    def run(self, query):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:
            suggestions = self.info.get_query_suggestions(query)
            result['items'].append({
                'suggestions': suggestions
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
