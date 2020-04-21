import pandas as pd
import numpy as np
from networkx.drawing.tests.test_pylab import plt
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import Perceptron
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, make_scorer
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

# X = df.drop(['Tag'], axis=1)
# v = DictVectorizer(sparse=False)
# X = v.fit_transform(X.to_dict('records'))
y = df.Tag.values
classes = np.unique(y)
classes = classes.tolist()
#X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.33, random_state=0)
#print(X_train.shape, y_train.shape)

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
# define fixed parameters and parameters to search
crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    max_iterations=100,
    all_possible_transitions=True
)

import scipy.stats

params_space = {
    'c1': scipy.stats.expon(scale=0.5),
    'c2': scipy.stats.expon(scale=0.05),
}
import itertools
Labels = y.copy()
unique_labels = np.unique(list(itertools.chain(*Labels)))

# use the same metric for evaluation
f1_scorer = make_scorer(metrics.flat_f1_score,
                        average='weighted', labels=unique_labels)

# search
rs = RandomizedSearchCV(crf, params_space,
                        cv=3,
                        verbose=1,
                        n_jobs=-1,
                        n_iter=50,
                        scoring=f1_scorer)
rs.fit(X_train, y_train)
crf.fit(X_train, y_train)

new_classes = classes.copy()
new_classes.pop()
print(new_classes)

y_pred = crf.predict(X_test)
print(metrics.flat_classification_report(y_test, y_pred, labels=new_classes))

# crf = rs.best_estimator_
print('best params:', rs.best_params_)
print('best CV score:', rs.best_score_)
print('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))

# _x = [s.parameters['c1'] for s in rs.cv_results_]
# _y = [s.parameters['c2'] for s in rs.cv_results_]
# _c = [s.mean_validation_score for s in rs.cv_results_]
#
# fig = plt.figure()
# fig.set_size_inches(12, 12)
# ax = plt.gca()
# ax.set_yscale('log')
# ax.set_xscale('log')
# ax.set_xlabel('C1')
# ax.set_ylabel('C2')
# ax.set_title("Randomized Hyperparameter Search CV Results (min={:0.3}, max={:0.3})".format(
#     min(_c), max(_c)
# ))
#
# ax.scatter(_x, _y, c=_c, s=60, alpha=0.9, edgecolors=[0,0,0])

print("Dark blue => {:0.4}, dark red => {:0.4}".format(min(_c), max(_c)))


def plot_grid_search(cv_results, grid_param_1, grid_param_2, name_param_1, name_param_2):
    # Get Test Scores Mean and std for each grid search
    scores_mean = cv_results['mean_test_score']
    scores_mean = np.array(scores_mean).reshape(len(grid_param_2),len(grid_param_1))

    scores_sd = cv_results['std_test_score']
    scores_sd = np.array(scores_sd).reshape(len(grid_param_2),len(grid_param_1))

    # Plot Grid search scores
    _, ax = plt.subplots(1,1)

    # Param1 is the X-axis, Param 2 is represented as a different curve (color line)
    for idx, val in enumerate(grid_param_2):
        ax.plot(grid_param_1, scores_mean[idx,:], '-o', label= name_param_2 + ': ' + str(val))

    ax.set_title("Grid Search Scores", fontsize=20, fontweight='bold')
    ax.set_xlabel(name_param_1, fontsize=16)
    ax.set_ylabel('CV Average Score', fontsize=16)
    ax.legend(loc="best", fontsize=15)
    ax.grid('on')


plot_grid_search(rs.cv_results_,  [s.parameters['c1'] for s in rs.cv_results_], [s.parameters['c2'] for s in rs.cv_results_], 'C1', 'C2')


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
