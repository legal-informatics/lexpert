import pandas as pd
import numpy as np
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import pickle

try:
    import Akoma
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
except ModuleNotFoundError as sureError:
    try:
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
    except ModuleNotFoundError as newError:
        if not sureError.name.__eq__("Akoma") or not newError.name.__eq__("Akoma"):
            print(newError)
            print("Error")
            exit(-1)

df = read_and_prepare_csv('../data/ner/datasetReldiSD.csv')

# X = df.drop(['Tag'], axis=1)
# v = DictVectorizer(sparse=False)
# X = v.fit_transform(X.to_dict('records'))
y = df.Tag.values
classes = np.unique(y)
classes = classes.tolist()
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state=0)
# print(X_train.shape, y_train.shape)

# per = Perceptron(verbose=10, n_jobs=-1, max_iter=5)
# per.partial_fit(X_train, y_train, classes)
#
# new_classes = classes.copy()
# new_classes.pop()
# print(new_classes)
#
#
# print(classification_report(y_pred=per.predict(X_test), y_true=y_test, labels=new_classes))

# sgd = SGDClassifier() # nema dovoljno memorije
# sgd.partial_fit(X_train, y_train, classes)
#
# new_classes = classes.copy()
# new_classes.pop()
# print(new_classes)
#
# print(classification_report(y_pred=sgd.predict(X_test), y_true=y_test, labels=new_classes))

from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(color_codes=True)
sns.set(font_scale=1)

# plt.rcParams['figure.figsize'] = (20.0, 10.0)
# plt.figure(figsize=(10, 5))
# ax = sns.countplot('Tag', data=df.loc[df['Tag'] != 'O'])
# ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha="center")
# plt.tight_layout()
# plt.show()

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from collections import Counter
from sgt import Sgt

getter = SentenceGetter(df)
sentences = getter.sentences

X = [sent2features(s) for s in sentences]
y = [sent2labels(s) for s in sentences]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=0)

crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
#crf.fit(X_train, y_train)
from sklearn.model_selection import cross_val_predict, cross_val_score
new_classes = classes.copy()
new_classes.pop()
print(new_classes)
y_pred = cross_val_predict(estimator=crf, X=X, y=y, cv=5)
#y_pred = crf.predict(X_test)
print(metrics.flat_classification_report(y, y_pred, labels=new_classes))

# def print_transitions(trans_features):
#     for (label_from, label_to), weight in trans_features:
#         print("%-6s -> %-7s %0.6f" % (label_from, label_to, weight))
# print("Top likely transitions:")
# print_transitions(Counter(crf.transition_features_).most_common(20))
# print("\nTop unlikely transitions:")
# print_transitions(Counter(crf.transition_features_).most_common()[-20:])
#
# def print_state_features(state_features):
#     for (attr, label), weight in state_features:
#         print("%0.6f %-8s %s" % (weight, label, attr))
# print("Top positive:")
# print_state_features(Counter(crf.state_features_).most_common(30))
# print("\nTop negative:")
# print_state_features(Counter(crf.state_features_).most_common()[-30:])

filename = "../data/ner/modelReldiD.sav"
pickle.dump(crf, open(filename, 'wb'))
