from bin.service import CardStorage, Environment, Logger, FavouriteStorage, QueryStorage, ShoutOutStorage
import time, statistics


class Info:

    def __init__(self):
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.card_storage = CardStorage.CardStorage()
        self.favourite_storage = FavouriteStorage.FavouriteStorage()
        self.query_storage = QueryStorage.QueryStorage()
        self.so_storage = ShoutOutStorage.ShoutOutStorage()

    def get_idea_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.card_storage.get_all_ideas()
        else:
            cards = self.card_storage.get_jira_and_confluence_ideas()
        return cards.count()

    def get_fact_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.card_storage.get_all_facts()
        else:
            cards = self.card_storage.get_jira_and_confluence_facts()
        return cards.count()

    def get_jira_count(self):
        cards = self.card_storage.get_jira_cards()
        return cards.count()

    def get_confluence_count(self):
        cards = self.card_storage.get_confluence_cards()
        return cards.count()

    def get_git_count(self):
        cards = self.card_storage.get_git_cards()
        return cards.count()

    def get_click_count(self):
        click_count = 0
        cards = self.card_storage.get_all_cards('clicks')
        for card in cards:
            click_count += card['clicks']
        return click_count

    def get_favourite_count(self):
        favourite_count = 0
        favourites = self.favourite_storage.load_favourites()
        for favourite in favourites:
            favourite_count += 1
        return favourite_count

    def get_new_facts_this_week(self):
        fact_count = 0
        a_week = 60 * 60 * 24 * 7
        current_time = time.time()
        a_week_ago = current_time - a_week
        facts_this_week = self.card_storage.get_timed_facts(a_week_ago)
        for fact in facts_this_week:
            fact_count += 1
        return fact_count

    def get_new_facts_this_month(self):
        fact_count = 0
        a_month = 60 * 60 * 24 * 30
        current_time = time.time()
        a_month_ago = current_time - a_month
        facts_this_month = self.card_storage.get_timed_facts(a_month_ago)
        for fact in facts_this_month:
            fact_count += 1
        return fact_count

    def get_last_log_entries(self):
        return self.logger.get_latest_entries(3)

    def get_query_count(self):
        query_count = 0
        queries = self.query_storage.get_queries()
        for query in queries:
            query_count += 1
        return query_count

    def get_desktop_count(self):
        desktop_count = 0
        queries = self.query_storage.get_desktop_queries()
        for query in queries:
            desktop_count += 1
        return desktop_count

    def get_mobile_count(self):
        mobile_count = 0
        queries = self.query_storage.get_mobile_queries()
        for query in queries:
            mobile_count += 1
        return mobile_count

    def get_average_loading_time(self):
        loading_times = []
        queries = self.query_storage.get_queries_with_loading_time()
        for query in queries:
            if 'loading_seconds' in query:
                loading_times.append(int(query['loading_seconds']))
        if len(loading_times) > 0:
            return statistics.mean(loading_times)
        return 0

    def get_shout_out_count(self):
        shout_outs = self.so_storage.get_shout_outs()
        return shout_outs.count()

    def get_query_suggestions(self, query, include_jira=True):
        suggestions = []
        """queries = self.query_storage.get_queries_by_query(query)
        queries_limited = queries[:5]
        for query in queries_limited:
            if query['query'] not in suggestions:
                suggestions.append(query['query'])"""
        cards = self.card_storage.search_cards_by_query(query, include_jira)
        cards_limited = cards[:5]
        for card in cards_limited:
            if card['title'] not in suggestions:
                suggestions.append(card['title'])
        return suggestions
