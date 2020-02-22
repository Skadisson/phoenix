from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes, feature_extraction


class SciKitLearn:

    def __init__(self):
        self.count_vectorizer = CountVectorizer()

    def context_search(self, documents, ids, query):

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

        return [context_id]
