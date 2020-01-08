import os
import pickle
from sklearn import feature_extraction, datasets, naive_bayes, pipeline

categories = ['alt.atheism', 'soc.religion.christian', 'comp.graphics', 'sci.med']
twenty_train = datasets.fetch_20newsgroups(subset='train', categories=categories, shuffle=True, random_state=42)
count_vectorizer = feature_extraction.text.CountVectorizer()
X_train_counts = count_vectorizer.fit_transform(twenty_train.data)
tf_transformer = feature_extraction.text.TfidfTransformer(use_idf=False).fit(X_train_counts)
X_train_tf = tf_transformer.transform(X_train_counts)
tfidf_transformer = feature_extraction.text.TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
clf = naive_bayes.MultinomialNB().fit(X_train_tfidf, twenty_train.target)
docs_new = ['God is love', 'OpenGL on the GPU is fast']
X_new_counts = count_vectorizer.transform(docs_new)
X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(X_new_tfidf)
print(X_train_counts.shape)
print(count_vectorizer.vocabulary_.get(u'algorithm'))
print(X_train_tf.shape)
print(X_train_tfidf.shape)
for doc, category in zip(docs_new, predicted):
    print('%r => %s' % (doc, twenty_train.target_names[category]))
exit()

cache_file = '../tmp/cache'
file_exists = os.path.exists(cache_file)
if file_exists:
    file = open(cache_file, "rb")
    content = pickle.load(file)
    descriptions = {}
    for ticket_id in content:
        ticket = content[ticket_id]
        title = ticket['Title']
        description = ticket['Text']
        comments = ticket['Comments']
        keywords = ticket['Keywords']
        descriptions[ticket_id] = description
    count_vectorizer = feature_extraction.text.CountVectorizer()
    X_train_counts = count_vectorizer.fit_transform(descriptions)
    print(X_train_counts.shape)
else:
    print('failed')
