from sklearn import naive_bayes, feature_extraction, pipeline
from bin.service import Logger, Environment, CardStorage


class SciKitLearn:

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()
        self.storage = CardStorage.CardStorage()

    def phased_context_search(self, query, not_empty=None):

        enable_git = self.environment.get_service_enable_git()
        if enable_git is True:
            cards = self.storage.get_all_cards(not_empty)
        else:
            cards = self.storage.get_jira_and_confluence_cards(not_empty)
        normalized_cards, card_ids = self.normalize_cards(cards)

        context_ids = []
        self.phased_search(normalized_cards, card_ids, query, context_ids)
        while len(context_ids) > 18:
            documents = self.storage.get_cards(context_ids)
            normalized_cards, card_ids = self.normalize_cards(documents)
            context_ids = []
            self.phased_search(normalized_cards, card_ids, query, context_ids)

        cards = self.storage.get_cards(context_ids)
        sorted_cards = self.storage.sort_cards(cards, 9, False)

        return sorted_cards

    def phased_search(self, documents, ids, query, context_ids, phase=None):

        if phase is None:
            phase = len(ids)

        if phase > 500:
            chunk_documents = self.chunks(documents, phase)
            chunk_ids = list(self.chunks(ids, phase))
            phase = int(round(phase / 2))
            i = 0
            for chunked_documents in chunk_documents:
                chunked_ids = chunk_ids[i]
                self.phased_search(chunked_documents, chunked_ids, query, context_ids, phase)
                i += 1
        else:
            try:
                winning_context_ids = self.unphased_context_search(documents, ids, query)
                context_ids += winning_context_ids
            except Exception as e:
                self.logger.add_entry(self.__class__.__name__, e)

    def unphased_context_search(self, documents, ids, query):

        context_ids = []
        docs_new = [query]

        count_vectorizer = feature_extraction.text.CountVectorizer()
        X_train_counts = count_vectorizer.fit_transform(documents)
        tfidf_transformer = feature_extraction.text.TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        X_new_counts = count_vectorizer.transform(docs_new)
        X_new_tfidf = tfidf_transformer.transform(X_new_counts)

        clf_context = naive_bayes.MultinomialNB().fit(X_train_tfidf, ids)
        predicted_context_id = clf_context.predict(X_new_tfidf)

        context_id = int(predicted_context_id.astype(int))
        context_ids.append(context_id)

        """clf_relevancy = naive_bayes.BernoulliNB().fit(X_train_tfidf, ids)
        predicted_relevancy_id = clf_relevancy.predict(X_new_tfidf)

        relevancy_id = int(predicted_relevancy_id.astype(int))
        context_ids.append(relevancy_id)"""

        return context_ids

    @staticmethod
    def chunks(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    @staticmethod
    def suggest_keywords(title, text, keywords, documents):

        docs_new = [title + ' ' + text]

        count_vectorizer = feature_extraction.text.CountVectorizer()
        X_train_counts = count_vectorizer.fit_transform(documents)
        tfidf_transformer = feature_extraction.text.TfidfTransformer()
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        X_new_counts = count_vectorizer.transform(docs_new)
        X_new_tfidf = tfidf_transformer.transform(X_new_counts)

        clf_context = naive_bayes.MultinomialNB().fit(X_train_tfidf, keywords)
        suggested_keywords = clf_context.predict(X_new_tfidf)

        return suggested_keywords.astype(str)[0]

    @staticmethod
    def normalize_cards(cards):
        normalized_cards = []
        card_ids = []

        for card in cards:
            normalized_card = ''
            if card['title'] is not None:
                normalized_card += str(card['title'])
            if card['text'] is not None:
                normalized_card += ' ' + str(card['text'])
            if card['keywords'] is not None:
                normalized_card += ' ' + str(' '.join(card['keywords']))
            normalized_content = str(normalized_card)
            card_id = int(card['id'])
            if normalized_content != '' and card_id > 0:
                card_ids.append(card_id)
                normalized_cards.append(normalized_content)

        return normalized_cards, card_ids
