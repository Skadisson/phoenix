from bin.service import Info, Logger


class Analytics:

    def __init__(self):
        self.info = Info.Info()
        self.logger = Logger.Logger()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:
            fact_count = self.info.get_fact_count()
            idea_count = self.info.get_idea_count()
            click_count = self.info.get_click_count()
            favourite_count = self.info.get_favourite_count()
            new_facts_this_week = self.info.get_new_facts_this_week()
            new_facts_this_month = self.info.get_new_facts_this_month()
            log_entries = self.info.get_last_log_entries()
            query_count = self.info.get_query_count()
            result['items'].append({
                'fact_count': fact_count,
                'idea_count': idea_count,
                'click_count': click_count,
                'favourite_count': favourite_count,
                'new_facts_this_week': new_facts_this_week,
                'new_facts_this_month': new_facts_this_month,
                'log_entries': log_entries,
                'query_count': query_count
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
