import numpy as np
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
from keras.models import Model, Input
from keras.layers import LSTM, Embedding, Dense, TimeDistributed
from keras.layers import Bidirectional, Lambda
from keras.callbacks import ModelCheckpoint
import keras.backend as K
import tensorflow as tf
import pickle
from keras_contrib.layers import CRF
from named_enitity_recognition.readutils import SentenceGetter, read_and_prepare_csv
from named_enitity_recognition.embeddings import glove_embedding, bert_embedding, elmo_embedding, \
    create_data_for_elmo
from test_scripts import testEmbeddingNNWithTestKorpus
from named_enitity_recognition import embeddings
from os import path


def sparse_loss(y_true, y_pred):
    foo = tf.nn.sparse_softmax_cross_entropy_with_logits(labels=y_true, logits=y_pred)
    v = tf.reduce_mean(foo)
    return v


def custom_loss(y_true, y_pred):
    sess = tf.Session()
    with sess.as_default():
        # print(K.print_tensor(y_pred))
        # output_shape = y_pred.get_shape()
        # targets = K.cast(tf.reshape(y_true, [-1]), 'int64')
        # logits = tf.reshape(y_pred, [-1, int(output_shape[-1])])
        # print(K.print_tensor(logits))
        # res = tf.nn.sparse_softmax_cross_entropy_with_logits(
        #     labels=targets,
        #     logits=logits)
        unweighted_loss = K.sparse_categorical_crossentropy(y_true, y_pred)
    return unweighted_loss


if __name__ == "__main__":
    embedding_type = "Bert"  # GloVe, Elmo, Bert
    max_len = 75
    data = read_and_prepare_csv("../data/ner/datasetReldiSD.csv")

    data.tail(10)

    words = list(set(data["Word"].values))
    n_words = len(words)  # n_words

    tags = list(set(data["Tag"].values))
    n_tags = len(tags)  # n_tags

    getter = SentenceGetter(data)

    sent = getter.get_next()

    sentences = getter.sentences
    docs = getter.get_docs()

    largest_sen = max(len(sen) for sen in sentences)
    print('biggest sentence has {} words'.format(largest_sen))

    word2idx = {w: i + 2 for i, w in enumerate(words)}
    word2idx["UNK"] = 1
    word2idx["PAD"] = 0
    idx2word = {i: w for w, i in word2idx.items()}

    if path.exists(path='../data/ner/bert_idx2tag.csv'):
        idx2tag = testEmbeddingNNWithTestKorpus.bert_load_index2tag()
        tag2idx = {value: key for key, value in idx2tag.items()}
        saving = False
    else:
        tag2idx = {t: i + 1 for i, t in enumerate(tags)}
        tag2idx["PAD"] = 0
        idx2tag = {i: w for w, i in tag2idx.items()}
        saving = True

    padded_docs = []
    vocab_size = 0
    embedding_matrix = []
    bert_size = 0
    if embedding_type == "GloVe":
        embedding_matrix, padded_docs, vocab_size = glove_embedding(docs, max_len)
        file_path = "../data/ner/neuralNetworkModelGloVe.h5"
    elif embedding_type == "Elmo":
        padded_docs = create_data_for_elmo(sentences, max_len)
        file_path = "../data/ner/neuralNetworkModelElmo.h5"
    elif embedding_type == "Bert":
        padded_docs = bert_embedding(docs, max_len)  # "hr500k"
        bert_size = len(padded_docs[0][0])
        file_path = "../data/ner/neuralNetworkModelBert.h5"
    else:
        raise ValueError("Embedded type not supported")

    y = [[tag2idx[w[2]] for w in s] for s in sentences]

    y = pad_sequences(maxlen=max_len, sequences=y, value=tag2idx["PAD"], padding='post', truncating='post')

    X_word_tr, X_word_te, y_tr, y_te = train_test_split(padded_docs, y, test_size=0.1, random_state=2018)

    X_word_te = X_word_te[:384]
    y_te = y_te[:384]
    # input and embedding for words
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

    model.compile(optimizer="adam", loss=crf.loss_function, metrics=[crf.accuracy])
    # adam # loss=sparse_categorical_crossentropy # metrics=['categorical_accuracy'] # #loss=custom_loss
    model.summary()

    checkpointer = ModelCheckpoint(filepath=file_path,
                                   verbose=0,
                                   mode='auto',
                                   save_best_only=True,
                                   monitor='val_loss')
    batch_size = 32
    X_tr, X_val = X_word_tr[:1792], X_word_tr[1792:3488]
    y_tr, y_val = y_tr[:1792], y_tr[1792:3488]
    y_tr = y_tr.reshape(y_tr.shape[0], y_tr.shape[1], 1)
    y_val = y_val.reshape(y_val.shape[0], y_val.shape[1], 1)
    history = model.fit(np.array(X_tr), y_tr, validation_data=(np.array(X_val), y_val), batch_size=batch_size,
                        epochs=1,
                        verbose=1)

    y_pred = model.predict(np.array(X_word_te))

    # model.save_weights(filepath=file_path)

    if embedding_type == 'GloVe' or embedding_type == "Bert":
        model.save(filepath=file_path)

    if embedding_type == 'Elmo':
        model.save_weights(filepath=file_path)

    i = 100
    p = np.argmax(y_pred[i], axis=-1)
    print("{:15}||{:5}||{}".format("Word", "True", "Pred"))
    print(30 * "=")
    if saving:
        with open('../data/ner/bert_idx2tag.csv', 'w') as f:
            writing = [str(key) + "," + str(value) + "\n" for key, value in idx2tag.items()]
            f.writelines(writing)

    checking = True  # To check if saving is the problem with NN
    if checking:
        print("START CHECKING")
        sentences = testEmbeddingNNWithTestKorpus.load_data("../data/ner/datasetTestNer.csv")
        # sentences = sentences[:20]
        list_words, list_vals = testEmbeddingNNWithTestKorpus.bert_prepare_sentences(sentences)
        embedded = embeddings.bert_embedding_sentence(list_words)
        embedded = testEmbeddingNNWithTestKorpus.padding_adv(embedded)
        check = model.predict(np.array(X_word_te))
        got = model.predict(embedded)
        print("Done Predicting")
        labels = testEmbeddingNNWithTestKorpus.bert_get_tag(got, list_words, list_vals, idx2tag)
        try:
            list_kategories = testEmbeddingNNWithTestKorpus.accuracy_recall(labels)
            results = testEmbeddingNNWithTestKorpus.avg_metrics_from_kategories(list_kategories)
            testEmbeddingNNWithTestKorpus.avg_metrics_from_kategories(list_kategories, with_other=True)
        except ZeroDivisionError:
            print("DIV BY ZERO")

    for w, t, pred in zip(X_word_te[i], y_te[i], p):
        if embedding_type == 'Bert':
            print("{:5} {}".format(idx2tag[t], idx2tag[pred]))

        else:
            if w != 0:
                print("{:15}: {:5} {}".format(w, t, pred))

    if embedding_type == 'GloVe':
        with open('../data/ner/word_to_index.pickle', 'wb') as f:
            pickle.dump(word2idx, f)

        with open('../data/ner/tag_to_index.pickle', 'wb') as f:
            pickle.dump(tag2idx, f)
