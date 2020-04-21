"""
 Iz svakog pravnog akta izvucemo clanove, reci u okviru tih clanove (tokenizacija), lem, stem. Konvertujemo reci u id.
"""
from os import path
import re
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd

# from gensim.models import Word2Vec
# from gensim.models import Word2Vecs
try:
    from Akoma.connector import connector
    from Akoma.convertToLatin import Convert
    from Akoma.convertToLatin import regex_patterns
    from Akoma.utilities import utilities
except ModuleNotFoundError as e1:
    print(e1)
    try:
        from convertToLatin import regex_patterns
        from connector import connector
        from convertToLatin import Convert
        from utilities import utilities
    except ModuleNotFoundError as e2:
        print(e2)
        exit(-1)


def get_stop_words():
    stop_words_file = open(path.dirname(__file__) + "/stopwords.txt", mode="r+", encoding="utf8")
    stop_words = stop_words_file.readlines()
    stop_words = list(str(x).replace("\n", "") for x in stop_words)
    stop_words_file.close()
    return stop_words


def get_file_names_in_folder(file_path):
    from os import listdir
    from os.path import isfile, join
    filenames = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    return filenames


def get_file_names(folder_data, aktovi_folder):
    # folderData=data aktoviFolder=aktovi_raw_lat
    base_path = path.dirname(__file__)
    file_path = path.abspath(path.join(base_path, "..", folder_data, aktovi_folder))
    filenames = get_file_names_in_folder(file_path)
    return filenames, file_path


def listToString(list_data):
    val = ""
    for i in range(0, len(list_data)):
        val += list_data[i] + " "
    return val


def get_tf_idf_values_from_text(text: str, return_just_words=True, threshold=0.09, max_elements=0,
                                latin=True, debug=False):
    """
    Returns most used words in text by TF-IDF, uses RAW Legal documents (without HTML)
    :param text: Text which to be processed
    :param return_just_words:  True return just words, False return value list [ word, probability]
    :param threshold:  threshold for probability to be added in return value
    :param max_elements:  Set return to max elements, ex. want just top 5 most relevant, then set max_elements to 5
    :param latin: If cyrilic set to true
    :param debug:  Prints values
    :return: Returns most used words in document, Type LIST, Depending on return_just_words, threshold and max_elements
    """
    stop_words = get_stop_words()
    tag_clan = "Član"
    if not latin:
        tag_clan = "Члан"
    act_array = []

    if text.find("<p") != -1:
        text = regex_patterns.strip_html_tags(text)

    if re.search(tag_clan + " [0-9]*\.", text) is None:  # Deprecated. if someone misses latin parameter
        text = Convert.convert_string(text)

    list_to_str = text + tag_clan + " 0."

    found = re.finditer(tag_clan + " [0-9]*\.", list_to_str)
    start_from = 0
    ends_to = 0
    for m in found:
        if start_from.__eq__(ends_to):
            ends_to = 0
        else:
            ends_to = m.start()
        if ends_to != 0:
            insert_string = list_to_str[start_from:ends_to]  # m.group().strip() = what was found in regex
            act_array.append(insert_string)
        start_from = m.end()

    c_bl = "#NBLC"
    tokens = connector.only_lam(c_bl.join(act_array))
    tokens = [tok for tok in tokens if tok not in stop_words or tok.isdigit()]
    clans = " ".join(tokens)
    list_clan_for_file = clans.split(c_bl)  # Otpimized

    if len(act_array) == 0:
        return []

    vectorizer = TfidfVectorizer()
    result = vectorizer.fit_transform(list_clan_for_file)

    if debug:
        print(vectorizer.get_feature_names())

    first_vector_tfidfvectorizer = result[0]  # get the first vector out (for the first document)

    df = pd.DataFrame(first_vector_tfidfvectorizer.T.todense(), index=vectorizer.get_feature_names(),
                      columns=["tfidf"])  # place tf-idf values in a pandas data frame
    df = df.sort_values(by=["tfidf"], ascending=False)

    list_words = list()
    for row in df.itertuples():
        if row.tfidf <= threshold:
            break
        list_words.append([row.Index, row.tfidf])
        if max_elements != 0:
            if max_elements <= len(list_words):
                break
    if debug:
        print(df.head())
    if return_just_words:
        list_words = [item[0] for item in list_words]
    return list_words


def get_tf_idf_values_document(folder_path, filenames=None, return_just_words=True, threshold=0.09, max_elements=0,
                               with_file_names=True, latin=True, debug=False):
    """
    Returns most used words in document by TF-IDF, uses RAW Legal documents (without HTML)
    :param folder_path: folder path to files which should be processed
    :param filenames: if specific files want to be processed (list of filenames) to get tfdif values of them
    :param return_just_words:  True return just words, False return value list [ word, probability]
    :param threshold:  threshold for probability to be added in return value
    :param max_elements:  Set return to max elements, ex. want just top 5 most relevant, then set max_elements to 5
    :param with_file_names:  Add filename in list of returned values next to most important words
    :param latin: If cyrilic set to true
    :param debug:  Prints values
    :return: Returns most used words in document, Type LIST, Depending on return_just_words, threshold and max_elements
    """
    if not filenames:
        file_names = get_file_names_in_folder(folder_path)
    elif isinstance(filenames, str):
        file_names = [filenames]
    else:
        file_names = filenames

    results = []
    tag_clan = "Član"
    if not latin:
        tag_clan = "Члан"

    for filename in file_names:
        list_clan_for_file = []
        print("Start " + str(filename))
        # break_word = break_word + 1
        check = folder_path + "/" + filename  # path.join(folder_path, filename)
        try:
            file = open(check, encoding="utf8")
        except FileNotFoundError:
            print(">Error tf-idf FileNotFoundError:" + check)
            continue
        all_lines = "".join(file.readlines())

        list_words = get_tf_idf_values_from_text(all_lines, return_just_words=return_just_words, threshold=threshold,
                                                 max_elements=max_elements,
                                                 latin=latin, debug=debug)
        if with_file_names:
            results.append([filename, list_words])
        else:
            results.append(list_words)
        if debug:
            print(results[len(results) - 1])
    return results


if __name__ == '__main__':
    # filenames , folderPath = get_file_names("data", "aktovi_raw_lat")
    filenames = ["1.html", "2.html"]
    path_folder = utilities.get_root_dir().replace("\\", "/") + "/data/acts"
    tf_idf_values = get_tf_idf_values_document(path_folder, filenames=filenames, return_just_words=False, with_file_names=True, latin=False)
    got_file = open(path_folder + "/" + filenames[0], mode="r", encoding="utf-8")
    text = "".join(got_file.readlines())
    #tf_idf_val2 = get_tf_idf_values_from_text(text, return_just_words=True, latin=False)
    #print(tf_idf_val2)
    print(tf_idf_values)
    for el in tf_idf_values:
        print([item[0] for item in el])  # FILES if return file names also
        print([item[1] for item in el])  # WORDS if return file names also
