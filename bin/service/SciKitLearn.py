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
        normalized_keywords, normalized_titles, normalized_texts, card_ids = self.normalize_cards(cards)

        context_ids = []
        self.phased_search(normalized_keywords, card_ids, query, context_ids)
        self.phased_search(normalized_titles, card_ids, query, context_ids)
        self.phased_search(normalized_texts, card_ids, query, context_ids)

        cards = self.storage.get_cards(list(set(context_ids)))
        sorted_cards = self.storage.sort_cards(cards, 9)

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

        text_clf = pipeline.Pipeline([
            ('vect', feature_extraction.text.CountVectorizer()),
            ('tfidf', feature_extraction.text.TfidfTransformer()),
            ('clf', naive_bayes.MultinomialNB()),
        ])
        text_context = text_clf.fit(documents, ids)
        text_id = text_context.predict(docs_new)
        context_ids.append(int(text_id.astype(int)))

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
