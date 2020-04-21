import re


def from_file_to_act_list(file):
    f = open(file, "r", encoding="utf-8")
    content = "".join(f.readlines())
    f.close()
    return from_content_to_act_list(content)


def from_content_to_act_list(content):
    act_array = []
    list_to_str = content + "Član 0."
    found = re.finditer("Član [0-9]*\.", list_to_str)
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
    return act_array


def gather_clans(content):
    return re.findall("Član [0-9]*\.", content)

#
# res = []
# easyPat = re.compile("Član [0-9]+[.]")
# exist = re.search(easyPat, content)
# patt = re.compile('Član [0-9]+[.](.*\n)*?Član [0-9]+[.]')
# while exist != None:
#     t = re.search(patt, content)
#
#     end = re.search(easyPat, content[exist.span()[1]+1:])
#     res.append(t.group(0).split("\n")[1].split("Član ")[0])
#     content = content[end.span(0)[1]+1:content.__len__()]
#     exist = re.search(easyPat, content)
#    #exist = re.search("Član", content)
#     #content[t.:]
# print(res)
