"""
Check with validation data downloaded from babushka-bench (https://github.com/clarinsi/babushka-bench)
"""
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed
from keras.layers import Bidirectional, Lambda
from keras.layers.merge import add
import keras.backend as K
from keras_contrib.layers import CRF
import tensorflow as tf
from keras import models
import pickle
import nltk
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report
from keras.preprocessing.text import text_to_word_sequence
import pickle
from named_enitity_recognition import embeddings
from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv
from named_enitity_recognition.embeddings import glove_embedding, bert_embedding, elmo_embedding, \
    create_data_for_elmo


def load_model(embedding_type: str, max_len=75):  # GloVe, Elmo, Bert
    data = read_and_prepare_csv("../data/ner/datasetReldiSD.csv")

    words = list(set(data["Word"].values))
    tags = list(set(data["Tag"].values))
    n_tags = len(tags)  # n_tags
    getter = SentenceGetter(data)
    sentences = getter.sentences
    docs = getter.get_docs()
    largest_sen = max(len(sen) for sen in sentences)
    print('biggest sentence has {} words'.format(largest_sen))

    word2idx = {w: i + 2 for i, w in enumerate(words)}
    word2idx["UNK"] = 1
    word2idx["PAD"] = 0

    vocab_size = 0
    embedding_matrix = []
    bert_size = 0
    if embedding_type.lower() == "GloVe".lower():
        embedding_matrix, padded_docs, vocab_size = glove_embedding(docs, max_len,
                                                                    '../named_enitity_recognition/glove.6B/glove.6B.100d.txt')
        path = "../data/ner/neuralNetworkModelGloVe.h5"
    elif embedding_type.lower() == "Elmo".lower():
        padded_docs = create_data_for_elmo(sentences, max_len)
        path = "../data/ner/neuralNetworkModelElmo.h5"
    elif embedding_type.lower() == "Bert".lower():
        padded_docs = bert_embedding(docs, max_len)
        bert_size = len(padded_docs[0][0])
        path = "../data/ner/neuralNetworkModelBert.h5"
    else:
        raise ValueError("Embedded type not supported")

    emb_word = 0
    word_in = 0
    if embedding_type == "GloVe":
        word_in = Input(shape=(max_len,))
        emb_word = Embedding(input_dim=vocab_size, weights=[embedding_matrix], output_dim=100, input_length=max_len,
                             mask_zero=True)(word_in)
    elif embedding_type == "Elmo":
        word_in = Input(shape=(max_len,), dtype=tf.string)
        emb_word = Lambda(elmo_embedding, output_shape=(max_len, 1024))(word_in)
    elif embedding_type == "Bert":
        emb_word = Input(shape=(max_len, bert_size))
    x = Bidirectional(LSTM(units=512, return_sequences=True,
                           recurrent_dropout=0.2, dropout=0.2))(emb_word)
    # out = TimeDistributed(Dense(n_tags + 1, activation="softmax"))(x)
    x2 = TimeDistributed(Dense(256, activation="relu"))(x)

    crf = CRF(n_tags + 1, sparse_target=True)  # CRF layer
    out = crf(x2)  # output

    if embedding_type == "Bert":
        model = Model(emb_word, out)
    else:
        model = Model(word_in, out)

    model.load_weights(filepath=path)
    return model


def load_data(path, docs=False):
    """
    :param path:
    :param docs: if docs == True then return getter.get_docs
    :return:
    """
    df = read_and_prepare_csv(path)
    getter = SentenceGetter(df)
    if docs is True:
        return [getter.sentences, getter.get_docs()]
    else:
        return getter.sentences


def padding_adv(embed, y=75, z=768):
    size = len(embed)
    result = np.zeros((size, y, z))
    rr = [np.array(emb) for emb in embed]
    result[:, :, :] = [padding(el, y, z) for el in rr]
    return result


def padding(embed, y=75, z=768):
    val = np.array(embed)
    result = np.zeros((y, z))
    result[:val.shape[0], :val.shape[1]] = val
    return result


def bert_load_index2tag(path='../data/ner/bert_idx2tag.csv'):
    index2tag = dict()
    with open(path, 'r') as f:
        lines = f.readlines()
        for i in range(len(lines)):
            to_file = lines[i].split(',')
            index2tag[int(to_file[0])] = to_file[1].replace("\n", "")
    return index2tag


def bert_get_tag(vec, list_sen, true_values=None, index2tag=None, debug=True):
    if index2tag is None:
        index2tag = bert_load_index2tag()
    sent = list()
    for i, el in enumerate(vec):
        tokens = nltk.word_tokenize(list_sen[i])
        for j in range(0, len(tokens)):
            if j >= 75:
                break
            prob_class = np.argmax(np.array(el[j])[1:]) + 1  #
            if true_values is None:
                true_val = ""
            else:
                try:
                    true_val = true_values[i][j]
                except IndexError:
                    print("Kod ove sekvence nema", list_sen[i])
                    print("J-ti", str(j), "clan size(", len(true_values), ")", true_values[i])
                    true_val = "O"

            if debug:
                print(tokens[j], " ", index2tag[int(prob_class)], true_val)
            sent.append([tokens[j], index2tag[int(prob_class)], true_val])
        if debug:
            print()
    return sent


def bert_prepare_sentences(sentence):
    list_val = [[word[2] for word in el] for el in sentence]
    list_word = [" ".join([word[0] for word in el]) for el in sentence]
    return list_word, list_val


def find_fscore(precision, recall):
    return 2 * ((precision * recall) / (precision + recall))


def avg_metrics_from_kategories(list_kat: list, with_other=False, debug=True) -> list:
    """
    :param list_kat: return value from accuracy_recall_f1 function
    :param with_other: If sum will take other tag in account
    :param debug: If values are printed
    :return: metrics precision,recall,f1
    """
    if with_other is False:
        list_temp = list()
        for i in range(len(list_kat)):
            if list_kat[i][0].lower() != "o":
                list_temp.append(list_kat[i])
        list_kat = list_temp
    ret = [sum([el[1] for el in list_kat]) / len(list_kat), sum([el[2] for el in list_kat]) / len(list_kat),
           sum([el[1] for el in list_kat]) / len(list_kat)]
    if debug:
        if with_other is True:
            text = "With O"
        else:
            text = "Without O"

        print("AVG ", text, "Precision:", ret[0], " Recall:", ret[1], " F1:", ret[2])
    return ret


def print_kat(list_kat):
    l = [el[0] for el in list_kat]
    for i in range(len(l)):
        print('{0: <5}'.format(l))
    print("{:.2f <5}", list_kat[0][1])  # formated print
    pass


def accuracy_recall(new_labels, debug=True):
    lab = list(set([el[2] for el in new_labels]))
    list_kat = list()
    for l in lab:
        # foo = [el for el in new_labels if el[2] == l]
        fp = sum([1 for el in new_labels if el[1] == l and el[2] != el[1]])
        tp = sum([1 for el in new_labels if el[2] == l and el[2] == el[1]])
        fn = sum([1 for el in new_labels if el[2] == l and el[2] != el[1]])
        try:
            precision = tp / (tp + fp)
        except ZeroDivisionError:
            precision = 0

        try:
            recall = tp / (tp + fn)
        except ZeroDivisionError:
            recall = 0

        try:
            f1 = find_fscore(precision, recall)
        except ZeroDivisionError:
            f1 = 0
        # fp = fp * 1 + 0
        # tp = tp * 1 + 0
        # fn = fn * 1 + 0
        list_kat.append([l, precision, recall, f1])
        if debug:
            print("----", l, "------")
            print("Precision", precision)
            print("Recall", recall)
            print("F1", f1)
    return list_kat


def load_model_by_type(emb_type, max_len=75):
    if emb_type.lower() == "elmo" or emb_type.lower() == "glove":
        model = load_model(embedding_type, max_len)
    else:
        # if emb_type.lower() == "GloVe".lower():
        #     path = "../data/ner/neuralNetworkModelGloVe_old.h5"
        if emb_type.lower() == "Bert".lower():
            path = "../data/ner/neuralNetworkModelBert.h5"
        else:
            quit(-1)
        model = models.load_model(path)
    return model


def test_model(model, emb_type='bert', max_len=75, fast=False):
    # TODO finish
    idx2tag = bert_load_index2tag('../data/ner/bert_idx2tag.csv')
    if emb_type.lower() == 'bert':
        print("START CHECKING")
        new_sentences = load_data("../data/ner/datasetTestNer.csv")
        if fast is True:
            new_sentences = new_sentences[:30]
        new_list_words, new_list_vals = bert_prepare_sentences(new_sentences)
        print("START EMBEDDING")
        words_embedded = embeddings.bert_embedding_sentence(list_words)
        words_embedded = padding_adv(words_embedded)
        print("START PREDICITING")
        got = model.predict(words_embedded)
        print("Done Predicting")
        list_labels = bert_get_tag(got, new_list_words, new_list_vals, idx2tag)
        got_list_kategories = accuracy_recall(list_labels)
        avg_metrics_from_kategories(got_list_kategories)
        avg_metrics_from_kategories(got_list_kategories, with_other=True)
    elif emb_type.lower() == 'elmo':
        print("TODO")
    elif emb_type.lower() == 'glove':
        sentences, docs = load_data("../data/ner/datasetTestNer.csv", docs=True)
        _, padded_docs, _ = glove_embedding(docs, max_len, "../named_enitity_recognition/glove.6B/glove.6B.100d.txt")
        got = model.predict(padded_docs)
        list_labels = bert_get_tag(got, new_list_words, new_list_vals, idx2tag)
        got_list_kategories = accuracy_recall(list_labels)
        avg_metrics_from_kategories(got_list_kategories)
        avg_metrics_from_kategories(got_list_kategories, with_other=True)
        print("A")


test_model(None, 'glove')

if __name__ == "__main__":
    embedding_type = "Bert"  # Elmo Bert Glove
    max_length = 75
    trained_model = load_model_by_type(embedding_type, max_length)
    print("Done Loading model")
    if embedding_type.lower() == 'bert':
        sentences = load_data("../data/ner/datasetTestNer.csv")
        sentences = sentences[:30]
        list_words, list_vals = bert_prepare_sentences(sentences)
        print("Start Embedding")
        embedded = embeddings.bert_embedding_sentence(list_words)
        print("Done Embedding")
        embedded = padding_adv(embedded)
        print("Start Predicting")
        got = trained_model.predict(embedded)
        print("Done Predicting")
        labels = bert_get_tag(got, list_words, list_vals)
        list_kategories = accuracy_recall(labels)
        results = avg_metrics_from_kategories(list_kategories)
        avg_metrics_from_kategories(list_kategories, with_other=True)
    elif embedding_type.lower() == 'elmo':
        print("A")
    elif embedding_type.lower() == 'glove':
        sentences, docs = load_data("../data/ner/datasetTestNer.csv", docs=True)
        trained_model.predict(docs)
        print("A")
