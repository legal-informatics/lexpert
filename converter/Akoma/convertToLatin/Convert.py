import io


def getListOfFiles(filePath):
    onlyfiles = [f for f in listdir(filePath) if isfile(join(filePath, f))]
    return onlyfiles


def gen_converter(dict_swicher, char: str):
    func = dict_swicher.get(char, "Invalid")
    if func == "Invalid":
        return char
    return func


def convert_serbian_number(serbian_number: str):
    """
    Prva,Druga,Treca
    :param char:
    :return:
    """
    switcher = {
        'prva': 1,
        'druga': 2,
        'treća': 3,
        'četvrta': 4,
        'peta': 5,
        'šesta': 6,
        'sedma': 7,
        'osma': 8,
        'deveta': 9,
        'deseta': 10,
        'jedanaesta': 11,
        'dvanaesta': 12,
        'trinaesta': 13,
        'četrnaesta': 14,
        'petnaesta': 15,
        'šesnaesta': 16,
        'sedamnaesta': 17,
        'osamnaesta': 18,
        'devetnaesta': 19,
        'dvadeseta': 20,
        'dvadesetprva': 21,
        'dvadesetdruga': 22,
        'dvadesettreća': 23,
        'dvadesetčetvrta': 24,
        'dvadesetpeta': 25,
        'dvadesetšesta': 26,
        'dvadesetsedma': 27,
        'dvadesetosma': 28,
        'dvadesetdeveta': 29,
        'trideseta': 30,
        'прва': 1,
        'друга': 2,
        'трећа': 3,
        'четврта': 4,
        'пета': 5,
        'шеста': 6,
        'седма': 7,
        'осма': 8,
        'девета': 9,
        'десета': 10,
        'једанаеста': 11,
        'дванаеста': 12,
        'тринаеста': 13,
        'четрнаеста': 14,
        'петнаеста': 15,
        'шеснаеста': 16,
        'седамнаеста': 17,
        'осамнаеста': 18,
        'деветнаеста': 19,
        'двадесета': 20,
        'двадесетпрва': 21,
        'двадесетдруга': 22,
        'двадесеттрећа': 23,
        'двадесетчетврта': 24,
        'двадесетпета': 25,
        'двадесетшеста': 26,
        'двадесетседма': 27,
        'двадесетосма': 28,
        'двадесетдевета': 29,
        'тридесета': 30,
    }
    func = switcher.get(serbian_number, "Invalid")
    if func == "Invalid":
        return serbian_number
    return func


def top(rez):
    if rez > 1:
        return 1
    else:
        return rez


def cap(rez):
    while rez > 1:
        rez = rez - 1
    if rez < 0:
        rez = abs(rez)
    return rez


def convert(char):
    switcher = {
        'А': "A",
        'Б': "B",
        'В': "V",
        'Г': "G",
        'Д': "D",
        'Ђ': "Đ",
        'Е': "E",
        'Ж': "Ž",
        'З': "Z",
        'И': "I",
        'Ј': "J",
        'К': "K",
        'Л': "L",
        'Љ': "LJ",
        'М': "M",
        'Н': "N",
        'Њ': "NJ",
        'О': "O",
        'П': "P",
        'Р': "R",
        'С': "S",
        'Т': "T",
        'Ћ': "Ć",
        'У': "U",
        'Ф': "F",
        'Х': "H",
        'Ц': "C",
        'Ч': "Č",
        'Џ': "DŽ",
        'Ш': "Š",
        'а': "a",
        'б': "b",
        'в': "v",
        'г': "g",
        'д': "d",
        'ђ': "đ",
        'е': "e",
        'ж': "ž",
        'з': "z",
        'и': "i",
        'ј': "j",
        'к': "k",
        'л': "l",
        'љ': "lj",
        'м': "m",
        'н': "n",
        'њ': "nj",
        'о': "o",
        'п': "p",
        'р': "r",
        'с': "s",
        'т': "t",
        'ћ': "ć",
        'у': "u",
        'ф': "f",
        'х': "h",
        'ц': "c",
        'ч': "č",
        'џ': "dž",
        'ш': "š",
    }
    func = switcher.get(char, "Invalid")
    if func == "Invalid":
        return char
    return func


def convert_string(to_process):
    return "".join([convert(el) for el in to_process])


if __name__ == '__main__':
    print("Main start")

    from os import listdir
    from os import path
    from os.path import isfile, join

    basePath = path.dirname(__file__)
    filePath = path.abspath(path.join(basePath, "..", "data", "acts"))
    fileOut = path.abspath(path.join(basePath, "..", "data", "racts"))

    filenames = getListOfFiles(filePath)
    extens = ".txt"
    for filename in filenames:
        check = path.join(filePath, filename);
        outputApsolute = path.join(fileOut, filename);
        file = open(check, encoding="utf8")
        # a = "".join(file.readlines())
        # b = convert_string(a)
        outputFile = open(outputApsolute, mode="x", encoding="utf8")
        for line in file:
            for ch in line:
                outputFile.write(convert(ch))
