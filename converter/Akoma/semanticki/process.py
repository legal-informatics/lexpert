import re

try:
    from Akoma.tfidf.tfidf import get_tf_idf_values_document
    import Akoma.semanticki.util as util
    from Akoma.utilities import utilities
    import Akoma.semanticki.owl as owl
    from Akoma.convertToLatin import Convert
    import Akoma.datetime
except ModuleNotFoundError as e1:
    print(e1)
    try:
        from tfidf.tfidf import get_tf_idf_values_document
        import semanticki.util as util
        from utilities import utilities
        import semanticki.owl as owl
        from convertToLatin import Convert
        import datetime
    except ModuleNotFoundError as e2:
        print(e2)
        exit(-1)


def inside_important(tfidf, clan_info, iter):
    tf_inside = []
    for tf in tfidf:
        found = re.search(tf[0], clan_info[iter])
        if found is not None:
            tf_inside.append(tf[0])
    return tf_inside


def to_latin(str):
    return "".join([Convert.convert(s) for s in str])


def to_time(str_date):
    return datetime.datetime.strptime(str_date, '%Y-%m-%d').date()


def add_meta_to_act(curr_zakon, meta):
    curr_zakon.id_local.append(str(meta.eli))
    curr_zakon.title = [to_latin(meta.act_name)]
    curr_zakon.date_publication = to_time(meta.datum_usvajanja)
    curr_zakon.title_short.append(to_latin(meta.act_name.split(":")[0]))

    curr_zakon.first_date_entry_in_force = to_time(meta.datum_primene)
    curr_zakon.date_applicability.append(to_time(meta.datum_stupanja))
    curr_zakon.number = [meta.publication['number']]
    curr_zakon.version_date = to_time(meta.datum_usvajanja)
    curr_zakon.publisher = [to_latin(meta.donosilac)]
    curr_zakon.published_in = [to_latin(meta.izdavac)]

    print(curr_zakon)


def check_meta(string):
    if ".txt" in string:
        string = string.replace(".txt", ".html")
    return string


def write_stat_info(curr_zakon, dis, file, stat_len):
    file.write("{0}: {1} :{2}\n".format(curr_zakon, stat_len, "|".join(dis)))


def generate_owl(folder_path, filenames=None):
    result = get_tf_idf_values_document(folder_path, filenames=filenames, return_just_words=False)
    stat_file = open("stats.txt", "w", encoding="utf-8")
    for el in result:
        s_file = el[0]
        f = open(folder_path + "\\" + s_file, "r", encoding="utf-8")
        info = "".join(f.readlines())
        # for q in el[1]:
        #     print(q)

        stat_len = len(re.findall(r'\w+', info))

        clans_data = util.from_content_to_act_list(info)
        clan_info = util.gather_clans(info)
        # Otvori fajl, pronađe strukture, generišu clanovi, dodaju se
        # print(clans_data)
        meta = utilities.get_meta(check_meta(s_file), utilities.get_root_dir() + "\\data\\meta\\allmeta.csv")
        if meta == None:
            print("Warn - " + el[0] + "missing meta")
            continue
        latin_name = to_latin(meta.act_name).replace(' ', '_')
        # latin_name = meta.act_name.replace(" ", '_')
        dis = {}
        curr_zakon = owl.add_legal_resource(latin_name)
        add_meta_to_act(curr_zakon, meta)

        i = 0
        for info in clan_info:

            curr_sub = owl.add_legal_sub(latin_name.split(":")[0] + '_' + info.replace(' ', '_'))
            is_about = inside_important(el[1], clans_data, i)
            for new_concept in is_about:
                if new_concept not in dis:
                    dis[new_concept] = owl.add_concept(new_concept)

            if is_about.__len__ != 0:
                curr_sub.is_about = [dis[s] for s in is_about]
            curr_sub.is_part_of = [curr_zakon]
            i = i + 1
        curr_zakon.is_about = [dis[s] for s in dis]
        write_stat_info(curr_zakon, dis, stat_file, stat_len)
    s_file.close()
    owl.save()


if __name__ == '__main__':
    from os import listdir
    from os.path import isfile, join

    base_path = utilities.get_root_dir()
    folder_path = base_path + "/data/lat_acts"
    only_files = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    ordered = [str(el) + ".txt" for el in range(1, 200)]
    generate_owl(folder_path, filenames=ordered)  # onlyfiles[:10])   filenames=["86.txt", "200.txt"])
