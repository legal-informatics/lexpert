import pickle
import numpy as np
from itertools import groupby

try:
    import Akoma
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
    from Akoma.connector.connector import tokenize_pos
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
except ModuleNotFoundError as sureError:
    try:
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
        from connector.connector import tokenize_pos
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
    except ModuleNotFoundError as newError:
        if not sureError.name == "Akoma" or not newError.name == "Akoma":
            print(newError)
            print("Error")
            exit(-1)

filename = 'data/ner/modelReldiD.sav'
crf = pickle.load(open(filename, 'rb'))

# deriv_elements = []
# loc_elements = []
# org_elements = []
# per_elements = []
# misc_elements = []
# date_elements = []


"""
O
B-deriv-per

B-loc
I-loc

B-org
I-org

B-per
I-per

B-misc
I-misc

B-date
I-date
"""


def find_elements(element, res_list, map_of_lists):
    res_list = res_list[0]
    last = None
    continuous = ""
    for x in range(len(res_list)):
        if res_list[x] != 'O':
            tag = res_list[x].split('-')
            if tag[0] == 'B':
                if last is not None:
                    map_of_lists[last].append(continuous)
                last = tag[1]
                continuous = element[x]
            elif last == tag[1]:
                continuous = continuous + ' ' + element[x]
            else:
                last = None
    if continuous != "":
        if last is not None:
            map_of_lists[last].append(continuous)


def do_ner_on_sentences(sentences):
    map_of_lists = {'deriv': [], 'loc': [], 'org': [], 'per': [],
                    'misc': [], 'date': []}

    merged_sentences = "`".join(sentences)
    w = tokenize_pos(merged_sentences)

    df = [(x, y) for x, y, z in w]
    separated_list = [list(group) for key, group in groupby(df, key=lambda t: t[0] != '`') if key]

    for tw in separated_list:
        el = [x for x, y in tw]
        y_pred = crf.predict([sent2features(tw)])
        find_elements(el, y_pred, map_of_lists)

    for key in map_of_lists:
        map_of_lists[key] = list(np.unique(map_of_lists[key]))

    return map_of_lists
