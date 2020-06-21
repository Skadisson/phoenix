from bin.service import CardStorage, Environment, Logger, FavouriteStorage, QueryStorage
import time, statistics


class Info:

    def __init__(self):
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.card_storage = CardStorage.CardStorage()
        self.favourite_storage = FavouriteStorage.FavouriteStorage()
        self.query_storage = QueryStorage.QueryStorage()

    def get_idea_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.card_storage.get_all_cards()
        else:
            cards = self.card_storage.get_jira_and_confluence_cards()
        idea_count = 0
        for card in cards:
            if card['type'] == 'idea':
                idea_count += 1
        return idea_count

    def get_fact_count(self):
        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.card_storage.get_all_cards()
        else:
            cards = self.card_storage.get_jira_and_confluence_cards()
        fact_count = 0
        for card in cards:
            if card['type'] == 'fact':
                fact_count += 1
        return fact_count

    def get_jira_count(self):
        jira_count = 0
        cards = self.card_storage.get_jira_cards()
        for card in cards:
            jira_count += 1
        return jira_count

    def get_confluence_count(self):
        confluence_count = 0
        cards = self.card_storage.get_confluence_cards()
        for card in cards:
            confluence_count += 1
        return confluence_count

    def get_git_count(self):
        git_count = 0
        cards = self.card_storage.get_git_cards()
        for card in cards:
            git_count += 1
        return git_count

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

    def get_average_loading_time(self):
        loading_times = []
        queries = self.query_storage.get_queries()
        for query in queries:
            if 'loading_seconds' in query:
                loading_times.append(int(query['loading_seconds']))
        return statistics.mean(loading_times)
