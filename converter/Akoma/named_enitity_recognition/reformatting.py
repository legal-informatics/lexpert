# data_selected = "reldi"
# data_selected = "drugi"
# data_selected = "hr500k"
data_selected = "hr500k"

if data_selected == "reldi":
    data_file = open("../data/ner/set.sr.conll", "r", encoding="utf-8")
elif data_selected == "drugi":
    data_file = open("../data/ner/dev_ner.conllu", "r", encoding="utf-8")
elif data_selected == "hr500k":
    data_file = open("../data/ner/hr500k.conll", "r", encoding="utf-8")
elif data_selected == "test_ner":
    data_file = open("../data/ner/test_ner.conllu", "r", encoding="utf-8")
else:
    print("Unknown file to work with")
    exit(-1)

data_list = []
write_next = True
for line in data_file:
    if line.strip().__len__() < 1:
        data_list.append(("", "", "", ""))
        continue
    elif line[0] == '#':
        continue
    try:
        split = line.strip().replace('\t', " ").split(" ")
        wordsplit = split[1]
        lemmasplit = split[2]

        if data_selected == "reldi":
            possplit = split[4]  # reldi
            tagsplit = split[10]  # reldi
        elif data_selected == "drugi":
            possplit = split[3]  # drugi
            tagsplit = split[9]  # drugi
        elif data_selected == "test_ner":
            possplit = split[3]  # reldi
            tagsplit = split[9]  # reldi
        elif data_selected == "hr500k":  # :
            possplit = split[4]  # hr500k
            tagsplit = split[10]  # hr500k

        t = (wordsplit.rsplit(), lemmasplit.rsplit(), possplit.rsplit(), tagsplit.rsplit())
        data_list.append(t)
    except:
        print(line.strip())  # if this comes to show, it means there was a error

i = 1
new_file_name = ""
if data_selected == "reldi":
    new_file_name = "../data/ner/datasetReldiS.csv"
elif data_selected == "drugi":
    new_file_name = "../data/ner/datasetDrugi.csv"
elif data_selected == "hr500k":
    new_file_name = "../data/ner/datasetHr500k.csv"
elif data_selected == "test_ner":
    new_file_name = "../data/ner/datasetTestNer.csv"

try:
    new_file = open(new_file_name, "w+", encoding="utf-8")
    new_file.write("Sentence #\tWord\tPos\tTag\n")
    for a, b, c, d in data_list:
        if a == "":
            write_next = True
            i = i + 1
        else:
            if write_next:
                write_next = False
                new_file.write("Sentence: {3}\t{0}\t{1}\t{2}\n".format(str(a[0]), str(c[0]), str(d[0]), i))
            else:
                new_file.write("\t{0}\t{1}\t{2}\n".format(str(a[0]), str(c[0]), str(d[0])))
    new_file.close()
except:
    print("Error while writing file")
print("Done")
