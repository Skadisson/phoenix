from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from pandas import DataFrame
import collections


class SciKitLearn:

    def __init__(self):
        """TBI"""

    def assertain(self, source_headers, source, target_headers, target):

        count_vect = CountVectorizer()
        source_df = DataFrame(source)
        source_list = list(source_df['words'].astype(str))
        jira_id_list = list(source_df['jira_id'].astype(int))
        source_x = count_vect.fit_transform(source_list)
        source_tf_transformer = TfidfTransformer(use_idf=False).fit(source_x)
        source_tf_x = source_tf_transformer.transform(source_x)
        target_x = count_vect.fit_transform(target)
        target_tf_x = source_tf_transformer.transform(target_x)

        print(source_tf_x)
        print(target_tf_x)
        exit()

        clf = MultinomialNB().fit(source_tf_x, jira_id_list)
        prediction = clf.predict(target_tf_x)
        print(prediction)

        exit()

