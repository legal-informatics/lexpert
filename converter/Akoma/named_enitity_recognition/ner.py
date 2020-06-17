import pickle
import numpy as np
from itertools import groupby
import spacy
import numpy

try:
    import Akoma
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
    from Akoma.connector.connector import tokenize_pos
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
    from Akoma.spacy_ner import UseSpacy
    from Akoma.utilites import utilities
except ModuleNotFoundError as sureError:
    try:
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
        from connector.connector import tokenize_pos
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
        from utilities import utilities
    except ModuleNotFoundError as newError:
        if not sureError.name == "Akoma" or not newError.name == "Akoma":
            print(newError)
            print("Error")
            exit(-1)

filename = 'data/ner/modelReldiD.sav'
crf = pickle.load(open(filename, 'rb'))
NER_OBJ = None
TAGS = None
CALL = 0
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
                continuous = continuous + ' ' + replace_junk(element[x])
                continuous = continuous.strip()
            else:
                last = None
    if continuous != "":
        if last is not None:
            map_of_lists[last].append(continuous)


def fix_dates(map_of_entities: dict):
    if map_of_entities.get('date') is None:
        return
    list_dates = map_of_entities['date']
    saving = []
    for date in list_dates:
        date = date.strip()
        month = utilities.month_in(date)
        has_year_and_day = utilities.number_in(date)
        has_year = utilities.number_in(date, just_year=True)
        has_day = utilities.number_in(date, just_day=True)
        special_date = utilities.special_date(date)
        if (month and has_year_and_day) or special_date or has_year or (has_day and month):
            saving.append(date)
    map_of_entities['date'] = saving


def replace_junk(text: str, strict=False) -> str:
    val = text.replace("*", "").replace("~", "").replace("„", "").replace("”", "").replace(")", "").replace(
        "(", "").replace("“", "").replace("–", "").replace("’", "").strip()
    if strict:
        val = val.replace(".", '').replace(",", "")
    return val


def sort_got_data(doc, map_of_lists, keys) -> None:
    continuous = ""
    last = None
    old = None
    for index, token in enumerate(doc):
        if 'date' in token.ent_type_:
            strict = False
        else:
            strict = True
        check = replace_junk(token.text, strict)
        if len(check) < 2:
            continue
        if token.ent_type_ == "":
            tag = ["O", "O"]
        else:
            tag = token.ent_type_.split("-")
        if "B" == tag[0]:
            if len(doc) == index + 1:
                map_of_lists[tag[1]].append(continuous)
                continuous = ""
                continue
            if last is None and old is not None:
                map_of_lists[old].append(continuous)
                continuous = ""
            last = tag[1]
            if last is not None:
                if map_of_lists.get(last) is None:
                    map_of_lists[last] = []
            continuous = continuous + " " + replace_junk(token.text, strict)
            continuous = continuous.strip()
        elif last == tag[1]:
            continuous = continuous + ' ' + replace_junk(token.text, strict)
            continuous = continuous.strip()
        else:
            if last is not None:
                old = last
            last = None

    for key in keys:
        map_of_lists[key] = list(np.unique(map_of_lists[key]))
        # print("How are we here? Text: " + token.text + " LABEL" + token.label_)


def my_component_pipe(doc):
    """ Add POS tag from reldi and lemma to tokens in document, for now passed by global param TAGS
    :param doc:
    :return:
    """
    from spacy.symbols import TAG, LEMMA
    from spacy.tokens import Doc
    global TAGS
    pos = [doc.vocab.strings.add(el[1]) for el in TAGS if el[0] != '`']
    lemma = [doc.vocab.strings.add(el[2]) for el in TAGS if el[0] != '`']
    words = [el[0] for el in TAGS if el[0] != '`']
    attrs = [TAG, LEMMA]
    arr = numpy.array(list(zip(pos, lemma)), dtype="uint64")
    doc.from_array(attrs, arr)
    new_doc = Doc(doc.vocab, words=words).from_array(attrs, arr)
    # for tok in new_doc:
    #     print(tok.tag_ + " " + tok.lemma_)
    return new_doc


def do_spacy_ner(sentences, model="xx_ent_wiki_sm", custom=True):
    global NER_OBJ
    global TAGS
    if NER_OBJ is None:
        if custom:
            NER_OBJ = spacy.load(utilities.get_root_dir() + "/data/spacy/model")
        else:
            NER_OBJ = spacy.load(model)
    merged_sentences = "`".join(sentences)
    w = tokenize_pos(merged_sentences)
    TAGS = w
    if 'my_pos' not in NER_OBJ.pipe_names:
        NER_OBJ.add_pipe(my_component_pipe, name="my_pos", first=True)
    text = " ".join(sentences)
    doc2 = NER_OBJ(text)
    ents = doc2.ents
    new_ents = [[el.label_, el.text] for el in ents]
    keys = (np.unique(
        [str.lower(el[0]).replace("b-", "").replace("i-", "") for el in new_ents]))  # ["PER","ORG","MISC","LOC"]
    map_of_lists = dict()
    for key in keys:
        map_of_lists[key] = []
    if not custom:
        for entries in new_ents:
            entries[1] = replace_junk(entries[1], True)
            if len(entries[1]) < 2:
                continue
            map_of_lists[str.lower(entries[0])].append(entries[1])
        for key in keys:
            map_of_lists[key] = list(np.unique(map_of_lists[key]))
    else:
        sort_got_data(doc2, map_of_lists, keys)
    for i in map_of_lists:
        print(i + ":" + str(len(map_of_lists[i])))
        print(map_of_lists[i])
    return map_of_lists


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
