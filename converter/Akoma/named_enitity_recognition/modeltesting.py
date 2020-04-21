import pandas as pd
import numpy as np
import pickle

try:
    import Akoma
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, sent2features, sent2labels, sent2tokens
except ModuleNotFoundError as sureError:
    try:
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, sent2features, sent2labels, sent2tokens
    except ModuleNotFoundError as newError:
        if not sureError.name.__eq__("Akoma") or not newError.name.__eq__("Akoma"):
            print(newError)
            print("Error")
            exit(-1)


df = read_and_prepare_csv('../data/ner/datasetReldiSD.csv')

y = df.Tag.values
classes = np.unique(y)
classes = classes.tolist()

import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from collections import Counter

getter = SentenceGetter(df)
sentences = getter.sentences

X = [sent2features(s) for s in sentences]
y = [sent2labels(s) for s in sentences]
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=0)
X_test = X
y_test = y
filename = '../data/ner/modelReldiD.sav'
crf = loaded_model = pickle.load(open(filename, 'rb'))
y_pred = crf.predict(X_test)
new_classes = classes.copy()
new_classes.pop()
print(new_classes)

#y_pred = crf.predict(X_test)
#print(metrics.flat_classification_report(y_test, y_pred, labels = new_classes))

print(metrics.flat_classification_report(y_test, y_pred, labels=new_classes))

result = loaded_model.score(X_test, y_test)
print("Overall: ", str(result))
