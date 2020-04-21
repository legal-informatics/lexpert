try:
    from Akoma.form_akoma.Metadata import Metadata
except ModuleNotFoundError:
    try:
        from form_akoma.Metadata import Metadata
    except ModuleNotFoundError:
        print("Error")
        exit()


def get_meta(filename: str, path: str = "..//data/meta/allmeta.csv"):
    """

    :param filename: name of scraped document
    :param path: path to metadata csv file
    :return: Metadata.class or None if not found
    """
    csv = open(path, mode="r", encoding="utf-8")
    for line in csv.readlines():
        values = line.strip().split("#")
        if filename == values[14]:
            csv.close()
            return Metadata(values)
    csv.close()
    return None


def sort_file_names(file_names_list):
    from functools import cmp_to_key
    return sorted(file_names_list, key=cmp_to_key(compare_file_names))


def compare_file_names(item1: str, item2: str):
    num1 = int(item1[0:item1.find(".")])
    num2 = int(item2[0:item2.find(".")])
    return num1 - num2


def get_root_dir():
    from os import path
    pather = path.dirname(__file__)
    path_this = path.normpath(pather)
    i = path_this.rfind("\\")
    if i == -1:  # MAC FIND
        i = pather.rfind('/')
    b = path_this[:i]
    return b


if __name__ == "__main__":
    a = get_meta("1.html")
    print(a.act_name)

    print(get_root_dir())
    print("End")
