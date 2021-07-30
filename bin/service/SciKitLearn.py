from sklearn import naive_bayes, feature_extraction, pipeline
from bin.service import Logger, Environment, CardStorage, NormalCache
import threading
import re
import time


ready_states = []
context_ids = []
probabilities = []


class SciKitLearn:

    global ready_states, context_ids, probabilities

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()
        self.storage = CardStorage.CardStorage()
        self.normal_cache = NormalCache.NormalCache()

    def search(self, query, not_empty=None, cards=None, include_jira=True):

        global context_ids, probabilities
        context_ids = []
        probabilities = []

        search_profile = {}
        if cards is None:

            search_profile['load_normalized_cards'] = time.time()
            if include_jira:
                documents, card_ids = self.normal_cache.load_normalized_cards(not_empty)
            else:
                non_jira_cards = list(self.storage.get_all_cards('title', include_jira))
                non_jira_card_ids = [d['id'] for d in non_jira_cards]
                documents, card_ids = self.normal_cache.get_normalized_cards(non_jira_card_ids)
            search_profile['card_count'] = len(documents)
            search_profile['load_normalized_cards'] = time.time() - search_profile['load_normalized_cards']

            if len(card_ids) > 0 and len(documents) > 0:
                search_profile['threaded_search'] = time.time()
                self.threaded_search(documents, card_ids, query)
                search_profile['context_count'] = len(context_ids)
                search_profile['threaded_search'] = time.time() - search_profile['threaded_search']

            search_profile['get_cards'] = time.time()
            final_cards = self.storage.get_cards(context_ids)
            self.add_probabilities(final_cards)
            search_profile['get_cards'] = time.time() - search_profile['get_cards']

            search_profile['filter_cards'] = time.time()
            filtered_cards = self.filter_cards(final_cards, query)
            search_profile['filter_cards'] = time.time() - search_profile['filter_cards']

            search_profile['sort_cards'] = time.time()
            sorted_cards = self.storage.sort_cards(filtered_cards, 6)
            search_profile['sort_cards'] = time.time() - search_profile['sort_cards']

        else:

            search_profile['normalize_cards'] = time.time()
            documents, card_ids = self.normal_cache.normalize_cards(cards)
            search_profile['card_count'] = len(documents)
            search_profile['normalize_cards'] = time.time() - search_profile['normalize_cards']

            search_profile['threaded_search'] = time.time()
            self.threaded_search(documents, card_ids, query)
            search_profile['threaded_search'] = time.time() - search_profile['threaded_search']

            search_profile['get_cards'] = time.time()
            final_cards = self.storage.get_cards(context_ids)
            self.add_probabilities(final_cards)
            search_profile['get_cards'] = time.time() - search_profile['get_cards']

            search_profile['filter_cards'] = time.time()
            filtered_cards = self.filter_cards(final_cards, query)
            search_profile['filter_cards'] = time.time() - search_profile['filter_cards']

            search_profile['sort_cards'] = time.time()
            sorted_cards = self.storage.sort_cards(filtered_cards, 6)
            search_profile['sort_cards'] = time.time() - search_profile['sort_cards']

        self.logger.add_entry(self.__class__.__name__, search_profile)

        return sorted_cards

    @staticmethod
    def add_probabilities(final_cards):
        global context_ids, probabilities
        for final_card in final_cards:
            card_id = final_card['id']
            probability_index = context_ids.index(card_id)
            final_card['probability'] = probabilities[probability_index]

    def threaded_search(self, documents, ids, query):

        global ready_states
        total_count = len(ids)
        if total_count > 100:
            chunk_size = int(round(total_count / 100))
        else:
            chunk_size = int(round(total_count / 10))
        if chunk_size > 0:
            document_chunks = self.chunks(documents, chunk_size)
            id_chunks = list(self.chunks(ids, chunk_size))
        else:
            document_chunks = [documents]
            id_chunks = [ids]

        processes = []
        ready_states = []

        i = 0
        for document_chunk in document_chunks:
            id_chunk = id_chunks[i]
            processes.append(threading.Thread(target=self.context_search, args=(document_chunk, id_chunk, query)))
            i += 1

        for process in processes:
            process.start()

        while len(ready_states) < len(processes):
            pass

        for process in processes:
            process.join()

    @staticmethod
    def context_search(documents, ids, query):

        global ready_states, context_ids, probabilities
        docs_new = [query]

        text_clf = pipeline.Pipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])

        text_context = text_clf.fit(documents, ids)
        probability_list = list(text_context.predict_proba(docs_new)[0])
        predicted_id = int(text_context.predict(docs_new)[0])
        context_ids.append(predicted_id)
        probabilities.append(probability_list[ids.index(predicted_id)])

        ready_states.append(True)

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def filter_cards(cards, query):
        filtered_cards = []
        words = query.split(' ')
        for card in cards:
            text = str(card['title']) + " " + str(card['text'])
            if card['keywords'] is not None:
                text += " " + str(' '.join(card['keywords']))
            for word in words:
                count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text))
                if count > 0:
                    filtered_cards.append(card)
                    break
        return filtered_cards
