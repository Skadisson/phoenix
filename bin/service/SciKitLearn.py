from sklearn import naive_bayes, feature_extraction, pipeline
from bin.service import Logger, Environment, CardStorage, NormalCache, SciKitPipeline
import threading
import re
import time
import pickle
import os


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
        max_results = 6

        search_profile = {}
        if cards is None:

            search_profile['load_normalized_cards'] = time.time()
            if include_jira:
                documents, card_ids = self.normal_cache.load_normalized_cards(not_empty, True)
            else:
                non_jira_cards = list(self.storage.get_all_cards('title', include_jira))
                non_jira_card_ids = [d['id'] for d in non_jira_cards]
                documents, card_ids = self.normal_cache.get_normalized_cards(non_jira_card_ids, True)
            search_profile['card_count'] = len(documents)
            search_profile['load_normalized_cards'] = time.time() - search_profile['load_normalized_cards']

            if len(card_ids) > 0 and len(documents) > 0:
                search_profile['threaded_search'] = time.time()
                self.threaded_search(documents, card_ids, query)
                search_profile['context_count'] = len(context_ids)
                search_profile['threaded_search'] = time.time() - search_profile['threaded_search']

                search_profile['wrap_up_search'] = time.time()
                self.wrap_up_search(query, max_results)
                search_profile['wrap_up_search'] = time.time() - search_profile['wrap_up_search']

            search_profile['get_cards'] = time.time()
            final_cards = self.storage.get_cards(context_ids)
            self.add_probabilities(final_cards)
            search_profile['get_cards'] = time.time() - search_profile['get_cards']

            search_profile['filter_cards'] = time.time()
            filtered_cards = self.filter_cards(final_cards, query)
            search_profile['filter_cards'] = time.time() - search_profile['filter_cards']

            search_profile['sort_cards'] = time.time()
            sorted_cards = self.storage.sort_cards(filtered_cards, max_results)
            search_profile['sort_cards'] = time.time() - search_profile['sort_cards']

        else:

            search_profile['normalize_cards'] = time.time()
            documents, card_ids = self.normal_cache.normalize_cards(cards)
            search_profile['card_count'] = len(documents)
            search_profile['normalize_cards'] = time.time() - search_profile['normalize_cards']

            search_profile['threaded_search'] = time.time()
            self.threaded_search(documents, card_ids, query)
            search_profile['threaded_search'] = time.time() - search_profile['threaded_search']

            search_profile['wrap_up_search'] = time.time()
            self.wrap_up_search(query, max_results)
            search_profile['wrap_up_search'] = time.time() - search_profile['wrap_up_search']

            search_profile['get_cards'] = time.time()
            final_cards = self.storage.get_cards(context_ids)
            self.add_probabilities(final_cards)
            search_profile['get_cards'] = time.time() - search_profile['get_cards']

            search_profile['filter_cards'] = time.time()
            filtered_cards = self.filter_cards(final_cards, query)
            search_profile['filter_cards'] = time.time() - search_profile['filter_cards']

            search_profile['sort_cards'] = time.time()
            sorted_cards = self.storage.sort_cards(filtered_cards, max_results)
            search_profile['sort_cards'] = time.time() - search_profile['sort_cards']

        """self.logger.add_entry(self.__class__.__name__, search_profile)"""

        return sorted_cards

    def add_probabilities(self, final_cards):
        global context_ids, probabilities
        for final_card in final_cards:
            if final_card is not None and 'id' in final_card:
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
        self.logger.add_entry(self.__class__.__name__, f"->threaded_search: Searching through {total_count} cards in chunks of {chunk_size}.")
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

    def context_search(self, documents, ids, query):

        global ready_states, context_ids, probabilities
        docs_new = [query]

        """clf_path = self.environment.get_path_clf()
        if os.path.exists(clf_path):
            file = open(clf_path, "rb")
            text_context = pickle.load(file)
        else:
            text_clf = pipeline.Pipeline([
                ('vect', feature_extraction.text.CountVectorizer()),
                ('tfidf', feature_extraction.text.TfidfTransformer()),
                ('clf', naive_bayes.MultinomialNB()),
            ])
            text_context = text_clf.fit(documents, ids)"""

        text_clf = pipeline.Pipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])
        text_clf.fit(documents, ids)
        probability_list = list(text_clf.predict_proba(docs_new)[0])
        predicted_id = int(text_clf.predict(docs_new)[0])
        context_ids.append(predicted_id)
        predicted_index = ids.index(predicted_id)
        if predicted_index < len(probability_list):
            probabilities.append(probability_list[predicted_index])
        else:
            probabilities.append(1.0)
            self.logger.add_entry(self.__class__.__name__, f"->context_search: Index {predicted_index} not found within {len(probability_list)} probabilities.")

        ready_states.append(True)

    def wrap_up_search(self, query, chunk_count=6):

        global context_ids, probabilities, ready_states
        chunk_size = int(round(len(context_ids) / chunk_count))
        documents, card_ids = self.normal_cache.get_normalized_cards(context_ids)
        if chunk_size > 0:
            document_chunks = self.chunks(documents, chunk_size)
            id_chunks = list(self.chunks(card_ids, chunk_size))
        else:
            document_chunks = [documents]
            id_chunks = [card_ids]

        context_ids = []
        probabilities = []
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
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def filter_cards(cards, query):
        filtered_cards = []
        words = query.split(' ')
        for card in cards:
            if card is not None:
                text = str(card['title']) + " " + str(card['text'])
                if card['keywords'] is not None:
                    text += " " + str(' '.join(card['keywords']))
                for word in words:
                    count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(word), text))
                    if count > 0:
                        filtered_cards.append(card)
                        break
        return filtered_cards

    def train(self):

        chunk_size = 1000
        start = float(time.time())
        card_documents, card_ids = self.normal_cache.load_normalized_cards()
        print(f">>> training with {len(card_documents)} cards and chunk size of {chunk_size} cards each")

        document_chunks = list(self.chunks(card_documents, chunk_size))
        id_chunks = list(self.chunks(card_ids, chunk_size))

        text_clf = SciKitPipeline.SciKitPipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])

        chunks_total = len(document_chunks)
        index = 0
        while index < chunks_total:
            start_chunk = float(time.time())
            ids = id_chunks[index]
            documents = document_chunks[index]
            text_clf.partial_fit(documents, ids, card_ids)
            stop_chunk = float(time.time())
            chunk_seconds = (start_chunk - stop_chunk)
            index += 1
            print(f">>> completed training of chunk {index}/{chunks_total} after {chunk_seconds} seconds")

        clf_path = self.environment.get_path_clf()
        file = open(clf_path, "wb")
        pickle.dump(text_clf, file)
        model_volume = os.stat(clf_path).st_size
        model_volume_gb = round(model_volume / 1024 / 1024 / 1024, 2)

        stop = float(time.time())
        seconds = (stop - start)
        print(f">>> training successful after {seconds} seconds with a size of {model_volume_gb} GB")
