from sklearn import naive_bayes, feature_extraction, pipeline
from bin.service import Logger, Environment, CardStorage
import threading


ready_states = []
context_ids = []


class SciKitLearn:

    global ready_states, context_ids

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()
        self.storage = CardStorage.CardStorage()

    def search(self, query, not_empty=None):

        global context_ids
        context_ids = []

        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards(not_empty)
        else:
            cards = self.storage.get_jira_and_confluence_cards(not_empty)
        normalized_keywords, normalized_titles, normalized_texts, card_ids = self.normalize_cards(cards)

        self.threaded_search(normalized_keywords, card_ids, query)
        self.threaded_search(normalized_titles, card_ids, query)
        self.threaded_search(normalized_texts, card_ids, query)

        final_cards = self.storage.get_cards(context_ids)
        sorted_cards = self.storage.sort_cards(final_cards, 9)

        return sorted_cards

    def threaded_search(self, documents, ids, query):

        global ready_states
        total_count = len(ids)
        chunk_size = int(round(total_count / 10))
        document_chunks = self.chunks(documents, chunk_size)
        id_chunks = list(self.chunks(ids, chunk_size))
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

        global ready_states, context_ids
        docs_new = [query]

        text_clf = pipeline.Pipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])

        for i in range(1, 3):
            if len(documents) > 0 and len(ids) > 0:
                text_context = text_clf.fit(documents, ids)
                text_id = text_context.predict(docs_new)
                found_id = int(text_id.astype(int))
                if found_id not in context_ids:
                    context_ids.append(found_id)
                index = ids.index(found_id)
                del(documents[index])
                del(ids[index])

        ready_states.append(True)

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def normalize_cards(cards):
        normalized_keywords = []
        normalized_titles = []
        normalized_texts = []
        card_ids = []

        for card in cards:
            normalized_keyword = ''
            normalized_title = ''
            normalized_text = ''
            if card['title'] is not None:
                normalized_title = str(card['title'])
            if card['text'] is not None:
                normalized_text = str(card['text'])
            if card['keywords'] is not None:
                normalized_keyword = str(' '.join(card['keywords']))
            card_id = int(card['id'])
            if card_id > 0:
                if normalized_keyword == '':
                    normalized_keyword = 'empty'
                if normalized_title == '':
                    normalized_title = 'empty'
                if normalized_text == '':
                    normalized_text = 'empty'
                card_ids.append(card_id)
                normalized_keywords.append(normalized_keyword)
                normalized_titles.append(normalized_title)
                normalized_texts.append(normalized_text)

        return normalized_keywords, normalized_titles, normalized_texts, card_ids
