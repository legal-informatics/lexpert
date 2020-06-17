from numpy import asarray
from numpy import zeros
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import tensorflow_hub as hub
from keras import backend as k
from bert_embedding import BertEmbedding
from os import path


def tokenize(docs):
    t = Tokenizer()
    t.fit_on_texts(docs)
    vocab_size = len(t.word_index) + 1
    return t, vocab_size


def glove_embedding(docs, max_length,file_path='glove.6B/glove.6B.100d.txt'):
    t, vocab_size = tokenize(docs)
    encoded_docs = t.texts_to_sequences(docs)
    padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
    embeddings_index = dict()
    f = open(file_path, encoding="utf-8")
    for line in f:
        values = line.split()
        word = values[0]
        coefs = asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    f.close()
    print('Loaded %s word vectors.' % len(embeddings_index))
    # create a weight matrix for words in training docs
    embedding_matrix = zeros((vocab_size, 100))
    for word, i in t.word_index.items():
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            embedding_matrix[i] = embedding_vector
    return embedding_matrix, padded_docs, vocab_size


def create_data_for_elmo(sentences, max_length):
    x = [[w[0] for w in s] for s in sentences]
    new_x = []
    for seq in x:
        new_seq = []
        for i in range(max_length):
            if len(seq) > i:
                new_seq.append(seq[i])
            else:
                new_seq.append("PADword")
        new_x.append(new_seq)
    return new_x


def elmo_embedding(x):
    max_len = 75
    sess = tf.Session()
    k.set_session(sess)
    elmo_model = hub.Module("https://tfhub.dev/google/elmo/2", trainable=True)
    sess.run(tf.global_variables_initializer())
    sess.run(tf.tables_initializer())
    batch_size = 32
    return elmo_model(inputs={"tokens": tf.squeeze(tf.cast(x, tf.string)),
                              "sequence_len": tf.constant(batch_size * [max_len])}, signature="tokens", as_dict=True)[
        "elmo"]


def bert_embedding(sentences, max_length, model='reldi'):
    if model.lower() == "reldi":
        path_str = 'bert/bert_embeddings.csv'
    elif model.lower() == "hr500k":
        path_str = 'bert/bert_embeddings.csv'
    else:
        exit(-100)
    if path.exists(path_str):
        embeddings = read_from_bert_txt(max_length)
    else:
        embeddings = bert_embedding_sentence(sentences)
        save_bert_to_txt(embeddings, path_str)
    return embeddings


def bert_embedding_sentence(sentences):
    bert_embedding_model = BertEmbedding(model='bert_12_768_12', dataset_name='wiki_multilingual')
    result = bert_embedding_model(sentences)
    embeddings = [[word for word in sentence[1]] for sentence in result]
    return embeddings


def save_bert_to_txt(embeddings, path_file="bert/bert_embeddings.csv"):
    with open(path_file, "w") as file:
        for sentence in embeddings:
            for word in sentence:
                for i in word:
                    file.write(str(i) + "\n")
                file.write("WORD_END\n")
            file.write("SENTENCE_END\n")


def read_from_bert_txt(max_length):
    with open("bert/bert_embeddings.csv", "r") as file:
        line = file.readline()
        sentences = []
        word = []
        embeddings = []
        cnt = 0
        while line:
            if line == "WORD_END\n":
                sentences.append(word)
                word = []
                cnt = cnt + 1
            elif line == "SENTENCE_END\n":
                if cnt < max_length:
                    for _ in range(max_length - len(sentences)):
                        empty_list = [0] * len(sentences[0])
                        sentences.append(empty_list)
                embeddings.append(sentences)
                sentences = []
                word = []
                cnt = 0
            else:
                word.append(float(line))
            line = file.readline()
        embeddings.append([])
    return embeddings[:-1]
