import pickle
import numpy as np
from keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split

try:
    import Akoma
    from Akoma.named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
        sent2features, sent2labels, sent2tokens
except ModuleNotFoundError as sureError:
    try:
        from named_enitity_recognition.readutils import SentenceGetter, word2features, read_and_prepare_csv, \
            sent2features, sent2labels, sent2tokens
        from test import testEmbeddingNNWithTestKorpus
    except ModuleNotFoundError as newError:
        if not sureError.name.__eq__("Akoma") or not newError.name.__eq__("Akoma"):
            print(newError)
            print("Error")
            exit(-1)


def getPath(embedding_type: str) -> str:
    if embedding_type.lower() == "GloVe".lower():
        path = "../data/ner/neuralNetworkModelGloVe.h5"
    elif embedding_type.lower() == "Elmo".lower():
        path = "../data/ner/neuralNetworkModelElmo.h5"
    elif embedding_type.lower() == "Bert".lower():
        path = "../data/ner/neuralNetworkModelBert.h5"
    elif embedding_type.lower() == "CRF".lower():
        path = "../data/ner/neuralNetworkModel1.h5"
    else:
        raise ValueError("Embedded type not supported")
    return path


def test(path: str, embedding_type: str):
    data = read_and_prepare_csv(path)

    data.tail(10)

    words = list(set(data["Word"].values))
    n_words = len(words)  # n_words

    tags = list(set(data["Tag"].values))
    n_tags = len(tags)  # n_tags

    getter = SentenceGetter(data)

    sent = getter.get_next()

    sentences = getter.sentences

    max_len = 75
    max_len_char = 10

    file1 = open("../data/ner/word_to_index.pickle", "rb")
    file2 = open("../data/ner/tag_to_index.pickle", "rb")
    word2idx = pickle.load(file1)
    tag2idx = pickle.load(file2)

    idx2word = {i: w for w, i in word2idx.items()}
    idx2tag = {i: w for w, i in tag2idx.items()}

    file1.close()
    file2.close()

    X_word = [[word2idx[w[0]] for w in s] for s in sentences] #Embedding

    X_word = pad_sequences(maxlen=max_len, sequences=X_word, value=word2idx["PAD"], padding='post', truncating='post')

    chars = set([w_i for w in words for w_i in w])
    n_chars = len(chars)

    char2idx = {c: i + 2 for i, c in enumerate(chars)}
    char2idx["UNK"] = 1
    char2idx["PAD"] = 0

    X_char = []
    for sentence in sentences:
        sent_seq = []
        for i in range(max_len):
            word_seq = []
            for j in range(max_len_char):
                try:
                    word_seq.append(char2idx.get(sentence[i][0][j]))
                except:
                    word_seq.append(char2idx.get("PAD"))
            sent_seq.append(word_seq)
        X_char.append(np.array(sent_seq))

    y = [[tag2idx[w[2]] for w in s] for s in sentences]

    y = pad_sequences(maxlen=max_len, sequences=y, value=tag2idx["PAD"], padding='post', truncating='post')

    X_word_tr, X_word_te, y_tr, y_te = train_test_split(X_word, y, test_size=0.1, random_state=2018)
    X_char_tr, X_char_te, _, _ = train_test_split(X_char, y, test_size=0.1, random_state=2018)

    # model = load_model('../data/ner/neuralNetworkModel1.h5')
    model = testEmbeddingNNWithTestKorpus.load_model("Elmo")
    model.summary()

    y_pred = model.predict([X_word_te,
                            np.array(X_char_te).reshape((len(X_char_te),
                                                         max_len, max_len_char))])

    i = 100
    p = np.argmax(y_pred[i], axis=-1)
    print("{:15}||{:5}||{}".format("Word", "True", "Pred"))
    print(30 * "=")
    for w, t, pred in zip(X_word_te[i], y_te[i], p):
        if w != 0:
            print("{:15}: {:5} {}".format(idx2word[w], idx2tag[t], idx2tag[pred]))


if "__main__" == __name__:
    test("../data/ner/datasetTestNer.csv", "CRF")
