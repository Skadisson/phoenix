from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes, feature_extraction
from bin.service import Logger


class SciKitLearn:

    def __init__(self):
        self.logger = Logger.Logger()

    def phased_context_search(self, documents, ids, query):
        context_ids = []
        self.phased_search(documents, ids, query, context_ids)
        return context_ids

    def phased_search(self, documents, ids, query, context_ids, phase=1):

        total = len(ids)
        chunk = total / phase

        if phase < 10 and chunk >= 1:
            phase += 1
            chunk_documents = self.chunks(documents, phase)
            chunk_ids = list(self.chunks(ids, phase))
            i = 0
            for chunked_documents in chunk_documents:
                chunked_ids = chunk_ids[i]
                self.phased_search(chunked_documents, chunked_ids, query, context_ids, phase)
                i += 1
        else:
            try:
                context_ids += self.unphased_context_search(documents, ids, query)
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

        """clf_relevancy = naive_bayes.BernoulliNB().fit(X_train_tfidf, ids)
        predicted_relevancy_id = clf_relevancy.predict(X_new_tfidf)"""

        """TODO: relevancy search"""
        """TODO: mutliple predictions"""
        """TODO: context/relevancy sorting"""

        context_id = int(predicted_context_id.astype(int))
        context_ids.append(context_id)

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
