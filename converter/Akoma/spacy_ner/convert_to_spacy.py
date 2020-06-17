import pandas as pd
from utilities import utilities
from named_enitity_recognition import readutils


def convert_to_tsv(input_file, output_file):
    df = readutils.read_and_prepare_csv(input_file)
    df = df.drop(axis=1, labels=["Sentence #"])
    df.to_csv(output_file, index=False, encoding="utf-8", sep="\t", header=False)


def tsv_to_json_format(input_path, output_path, unknown_label):
    import json
    f = open(input_path, 'r', encoding="utf-8")  # input file
    fp = open(output_path, 'w', encoding="utf-8")  # output file
    data_dict = {}
    annotations = []
    label_dict = {}
    pos_dict = []
    s = ''
    start = 0
    for line in f:
        word, pos, entity = line.split('\t')
        if word == '""""': # Decoding from pandas encoding
            word = '"'
        if '.\t' not in line:
            pos_dict.append(pos)
            s += word + " "
            entity = entity[:len(entity) - 1]
            if entity != unknown_label:
                if len(entity) != 1:
                    # print(len(entity),"Yes")
                    d = {}
                    d['text'] = word
                    # print(d['text'])
                    d['start'] = start
                    d['end'] = start + len(word) - 1
                    # print(d['start'],d['end'])
                    try:
                        label_dict[entity].append(d)
                    except:
                        label_dict[entity] = []
                        label_dict[entity].append(d)
            start += len(word) + 1
        else:
            s += word
            pos_dict.append(pos)
            data_dict['content'] = s
            s = ''
            label_list = []
            for ents in list(label_dict.keys()):
                for i in range(len(label_dict[ents])):
                    if label_dict[ents][i]['text'] != '':
                        l = [ents, label_dict[ents][i]]
                        for j in range(i + 1, len(label_dict[ents])):
                            if label_dict[ents][i]['text'] == label_dict[ents][j]['text']:
                                di = {}
                                di['start'] = label_dict[ents][j]['start']
                                di['end'] = label_dict[ents][j]['end']
                                di['text'] = label_dict[ents][i]['text']
                                l.append(di)
                                label_dict[ents][j]['text'] = ''
                        label_list.append(l)

            for entities in label_list:
                label = {}
                label['label'] = [entities[0]]
                label['points'] = entities[1:]
                annotations.append(label)
            data_dict['annotation'] = annotations
            data_dict['tags'] = pos_dict
            pos_dict = []
            annotations = []
            json.dump(data_dict, fp, ensure_ascii=False)
            fp.write('\n')
            data_dict = {}
            start = 0
            label_dict = {}


def json_to_spacy(input_file=None, output_file=None):
    #  main("Data/ner_corpus_260_custom.json","Data/ner_corpus_260_custom2")
    import pickle
    import json
    try:
        training_data = []
        lines = []
        with open(input_file, 'r', encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            data = json.loads(line)
            text = data['content']
            entities = []
            for annotation in data['annotation']:
                point = annotation['points'][0]
                labels = annotation['label']
                if not isinstance(labels, list):
                    labels = [labels]

                for label in labels:
                    if label == 'Tag':
                        continue
                    entities.append((point['start'], point['end'] + 1, label))

            training_data.append((text, {"entities": entities}))

        print(training_data)

        with open(output_file, 'wb') as fp:
            pickle.dump(training_data, fp)
    except Exception as e:
        print(e)
        return None


if __name__ == '__main__':
    dir = utilities.get_root_dir()
    file = dir + "/data/ner/datasetReldiSDCopy.csv"
    # convert_to_tsv(file, output_file=dir + "/data/spacy/reldi.tsv") # No need to do more than once
    tsv_to_json_format(dir + "/data/spacy/reldi.tsv", dir + "/data/spacy/reldiD.json", "abc")
    json_to_spacy(dir + "/data/spacy/reldiD.json", dir + "/data/spacy/reldiD_spacy.json")
    # main(file_from2,file_to)
