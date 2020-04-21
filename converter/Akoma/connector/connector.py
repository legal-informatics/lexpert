import subprocess
from os import path

debug = False
path_base = path.dirname(__file__).replace("\\", "/")
mac_variable = False  # TODO: Change this if your a mac user

command_string = "python2 "
if mac_variable:
    command_string = "python "


def tokenize(string_data):  # Only to tokenize data
    # noinspection SpellCheckingInspection,SpellCheckingInspection

    python2_command_token = command_string + path_base + "/../../reldi-tagger/tokeniser/tokeniser.py sr --file " + \
                            path_base + "/../connector/tokenize.txt"

    to_file(path_base + "/tokenize.txt", string_data)

    process = subprocess.Popen(python2_command_token.split(), stdout=subprocess.PIPE, bufsize=1,
                               universal_newlines=True, encoding='utf-8')

    output, error = process.communicate()

    lines = output.split('\n')

    info = [s.split('\t') for s in lines if s.strip() != '']
    if debug:
        print(output)
        print(info)
    return info


def pos_lem(data_file):  # POS and Lam
    relative_file = "-f " + path_base + "/../connector/" + data_file
    # noinspection SpellCheckingInspection

    python2_command = command_string + path_base + "/../../reldi-tagger/tagger.py sr -l " + relative_file
    if debug:
        print(python2_command)
    process = subprocess.Popen(python2_command.split(), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True,
                               encoding='utf-8')

    output, error = process.communicate()
    if debug:
        print(output)

    lines = output.split('\n')

    info = [s.split('\t') for s in lines if s.strip() != '']
    if debug:
        print(info)
    return info


def to_file(filename, content):
    f = open(filename, "w+", encoding='utf-8')
    # for a in content:
    #     f.write(a[0] + "\n")
    if type(content) is list:
        for a in content:
            f.write(a[0] + "\n")
    else:
        f.write(content)
    f.write("\n\n")
    f.flush()
    f.close()


def tokenize_pos(string_data):
    info = tokenize(string_data)
    to_file(path_base + '/text.txt', "\n".join(s[1] for s in info))
    pos_info = pos_lem('text.txt')
    if debug:
        print(pos_info)
    return pos_info


def only_lam(string_data):
    info = tokenize_pos(string_data)
    return [s[2] for s in info]


def listToString(s):
    # initialize an empty string
    str1 = ""
    # traverse in the string
    for i in range(0, len(s)):
        if s[i] == ".":
            str1 += s[i] + "\n"
        else:
            if (s[i] == "član" or s[i] == "члан") and '.' in s[i + 1]:
                str1 += "\n" + s[i] + " "
            else:
                if "." in s[i]:
                    if checkIfRomanNumeral(s[i].replace('.', '')):
                        str1 += "\n" + s[i] + " "
                    else:
                        str1 += s[i] + " "
                else:
                    str1 += s[i] + " "
        # return string
    return str1


def checkIfRomanNumeral(numeral):
    numeral = {c for c in numeral.upper()}
    validRomanNumerals = {c for c in "MDCLXVI()"}
    return not numeral - validRomanNumerals


# noinspection SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection,SpellCheckingInspection
if __name__ == "__main__":
    sanityCheck = only_lam('студената и игара \n')
    sanityCheckLat = only_lam("studenata i igara \n")

    print(sanityCheckLat)
    print(sanityCheck)
