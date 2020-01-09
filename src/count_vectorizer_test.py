import os
import pickle
from sklearn import feature_extraction, naive_bayes

cache_file = '../tmp/cache'
file_exists = os.path.exists(cache_file)
if file_exists:
    file = open(cache_file, "rb")
    content = pickle.load(file)
    descriptions = []
    keys = []
    for ticket_id in content:
        ticket = content[ticket_id]
        title = str(ticket['Title'])
        description = str(ticket['Text'])
        description += " || " + str(title)
        comments = ticket['Comments']
        if comments is not None:
            description += " || " + (" || ".join(comments))
        keywords = ticket['Keywords']
        if keywords is not None:
            description += " || " + (", ".join(keywords))
        project = ticket['Project']
        if project is not None:
            description += " || " + project
        key = ticket['Key']
        if description is not None and key is not None:
            keys.append(key)
            descriptions.append(str(description))
    count_vectorizer = feature_extraction.text.CountVectorizer()
    X_train_counts = count_vectorizer.fit_transform(descriptions)
    tf_transformer = feature_extraction.text.TfidfTransformer(use_idf=False).fit(X_train_counts)
    X_train_tf = tf_transformer.transform(X_train_counts)
    tfidf_transformer = feature_extraction.text.TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    clf = naive_bayes.MultinomialNB().fit(X_train_tfidf, keys)
    docs_new = ['Ich hab da mal ein Problem mit SMTP auf Rancher', 'Hilfe der Server geht nicht', 'Arvato Mwst', 'Bei Frank-Flechtwaren stimmen die Bilder nicht']
    X_new_counts = count_vectorizer.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)
    predicted = clf.predict(X_new_tfidf)
    for doc, category in zip(docs_new, predicted):
        print('%r => %s' % (doc, category))
else:
    print('failed')
