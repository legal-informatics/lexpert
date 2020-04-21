import re
import numpy as np
try:
    from Akoma.utilities.utilities import *
    from Akoma.utilities.ETree import *
except ModuleNotFoundError:
    try:
        from utilities.utilities import *
        from utilities.ETree import *
    except ModuleNotFoundError:
        print("Error import")
        exit(-1)


# '((члан|став|тачка|тачке|podtaчка|алинеја).? [0-9]+(\\.)?,?\\s?)+(\\s овог \\s\w*)?'

def ranges(nums):
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s + 1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))


def find_range_list(stringToScan, edges):
    position = 0;
    listOfIndex = []
    pomList = []
    for pom in re.finditer("[0-9]+(?=[,. )])", stringToScan):
        if int(pom.group()) == edges[position][0] and edges[position][0] == edges[position][1]:
            listOfIndex.append([pom.regs[0], pom.regs[0]])
            position = position + 1
        elif int(pom.group()) == edges[position][0]:
            pomList = []
            pomList.append(pom.regs[0])
        elif int(pom.group()) == edges[position][1]:
            pomList.append(pom.regs[0])
            listOfIndex.append(pomList)
            position = position + 1
    return listOfIndex


# akn/<država>/act/<godina publikovanja u formatu YYYY-MM-DD ili samo YYYY>/<broj akta u godini ili ako se ne zna "nn">/srb@/
# <!main, !imedoc.akn ili !schedule_1.pdf (extenzija manifestacije)>/<chp_4 je chapter 4>
# art_3__para_5__point_c

further = "(\\.?\\s?,?\\s?)"
azbuka_pattern = '[a-zA-Zабвгдђежзијклљмнњопрстћуфхцчџш]?'
regexBroj = '[0-9]+'
regexBrojSlovo = '[0-9]+[a-zA-Zабвгдђежзијклљмнњопрстћуфхцчџш]?'
nabrajanje = '(члан.?.?\\s*[0-9]+' + azbuka_pattern + ')' + further + '(став.?\\s*[0-9]+' + azbuka_pattern + ')?' + further + '(тач(ка|ки|ке|ку|ком)?\.?\\s*[0-9]+(?!(°|.°|..°))' + azbuka_pattern + '\)?)?'
nabrajanjeCl = '(чл.\\s*[0-9]+' + azbuka_pattern + '\.?)(((,)|(.?\\s*и)|(\\s*или\\s*))(\\s*[0-9]+' + azbuka_pattern + '\.?))*'
nabrajanjeClDoCl = '(чл.\\s*[0-9]+' + azbuka_pattern + '\.)(\\s*до\\s*)((чл.\\s*)?[0-9]+' + azbuka_pattern + '(\.|,))'
nabrajanjeClCrtaClan = '(чл.\\s*[0-9]+' + azbuka_pattern + '\.?)\\s*(–|-|−|‒)\\s*((чл.\\s*)?[0-9]+' + azbuka_pattern + '\.?)'
nabrajanje2 = '(члан.?.?\\s*[0-9]+' + azbuka_pattern + ')?' + further + '(став.?.?\\s*[0-9]+)?' + further + '(тач(ка|ки|ке|ку|ком)?\.?\\s*[0-9]+(?!(°|.°|..°))' + azbuka_pattern + ')?'
nabrajanjeStavTacka = '(став(ом|а|у)?\\s*[0-9]+' + azbuka_pattern + '\.?)\\s*(тач(ка|ки|ке|ку|ком)?\.?\\s*([0-9]+(?!(°|.°|..°))' + azbuka_pattern + ')\)?)?'
nabrajanjeTacka = '(члан.?.?\\s*[0-9]+' + azbuka_pattern + ')?\\s*(став.?.?\\s*[0-9]+' + azbuka_pattern + ')?\\s*(тач(ка|ки|ке|ку|ком)?\.?\\s*[0-9]+(?!(°|.°|..°))' + azbuka_pattern + ')'
nabrajanjeClZakon = '(члан.?\\s*([0-9]+' + azbuka_pattern + ').?)(\\s*)(Закона\\s*(–|-|−|‒)\\s*([0-9]+)\/([0-9]+)-[0-9]+)'
nabrajanjeStavUzastopno = '(чл.?.?.?.?\.?\\s*[0-9]+' + azbuka_pattern + '.?\\s*)?(ст.(?<=[ ,.])\\s*[0-9]+' + azbuka_pattern + '\.?)((\\s*до\\s*)|(\\s*–\\s*|\\s*-\\s*|\\s*−\\s*))((ст.\\s*)?[0-9]+' + azbuka_pattern + '(\.|,)?)'
nabrajanjeStav = '(чл.?.?.?.?\.?\\s*[0-9]+' + azbuka_pattern + '.?\\s*)?(ст.(?<=[ ,.])\\s*[0-9]+' + azbuka_pattern + '\.?)(((,)|(.?\\s*и)|(\\s*или\\s*))(\\s*[0-9]+' + azbuka_pattern + '\.?))*'
nabrajanjeTacakaUzastopno = '(чл.?.?.?.?\.?\\s*[0-9]+' + azbuka_pattern + '.?\\s*)?(ст(ав|аву|авом|ава)?\.?\\s*[0-9]+' + azbuka_pattern + '\.?)?\\s*(тач(ка|ки|ке|ку|ком)?\.?\\s*[0-9]+(?!(°|.°|..°))' + azbuka_pattern + '(\.|\))?)((\\s*до\\s*)|(\\s*–\\s*|\\s*-\\s*|\\s*−\\s*))((тач(ка|ки|ке|ку|ком)?\.?\\s*)?[0-9]+' + azbuka_pattern + '(\.|,|\))?)'
nabrajanjeTackaNeuzastopno = '(чл.?.?.?.?\.?\\s*[0-9]+' + azbuka_pattern + '.?\\s*)?(ст(ав|аву|авом|ава)?\.?\\s*[0-9]+' + azbuka_pattern + '\.?)?\\s*(тач(ка|ки|ке|ку|ком)?\.?\\s*[0-9]+(?!(°|.°|..°))' + azbuka_pattern + '(\.|\))?)(((,)|(.?\\s*и)|(\\s*или\\s*))(\\s*[0-9]+' + azbuka_pattern + '(\)|\.)?))*'
nabrajanjeDrZakon = '([0-9]+)\/([0-9]+) – др\. закон'
nabrajanjeSluzbeniGlasnikDatum = '([0-9]+)(\s*од\s*[0-9]+.*?)([0-9]+)'
nabrajanjeDrZakonDatum = '([0-9]+\.?)(\\s*од\\s*[0-9]+.*?)([0-9]+)(\\s*-\\s*др\.?\\s*закон)'


def make_reference(cnt, this_id, start, end, ending, stringo, longer, useLonger=True):
    open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"" + this_id + "/!main~" + ending + "\" >"

    if useLonger:
        start = start + longer

    stringo = stringo[:start] + open + stringo[start:]
    longer += len(open)

    if useLonger:
        end = end + longer
    else:
        end = end + len(open)

    stringo = stringo[:end] + "</ref>" + stringo[end:]
    longer += len("</ref>")

    cnt += 1
    return stringo, longer, cnt


def make_reference_for_clZakon(cnt, this_id, m, stringo, longer):
    if m.group(5).isdigit():
        open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m.group(6) + "/" + m.group(5) \
               + "/srp@/!main~/art_" + m.group(2) + "\">"
    else:
        open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m.group(7) + "/" + m.group(6) \
               + "/srp@/!main~/art_" + m.group(2) + "\">"

    stringo = stringo[:m.start() + longer] + open + stringo[m.start() + longer:]
    longer += len(open)

    stringo = stringo[:m.end() + longer] + "</ref>" + stringo[m.end() + longer:]
    longer += len("</ref>")

    cnt += 1
    return stringo, longer, cnt


def make_reference_for_dr_zakon(cnt, this_id, m, stringo, longer):
    open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m.group(2) + "/" + m.group(1) \
           + "/srp@\">"

    stringo = stringo[:m.start() + longer] + open + stringo[m.start() + longer:]
    longer += len(open)

    stringo = stringo[:m.end() + longer] + "</ref>" + stringo[m.end() + longer:]
    longer += len("</ref>")

    cnt += 1
    return stringo, longer, cnt


def make_reference_for_nabrajanje_stava(matches, pom_string, stringToScan, stringStart, longerStart, this_id, longer,
                                        cnt, stringo):
    stringToScan = stringToScan + " "
    if len(matches) == 1:
        retval = pom_string + "para_" + str(matches[0])
    else:
        matches = [int(i) for i in matches]
        matches.sort()
        edges = ranges(matches)

        if len(edges) == 1:
            retval = pom_string + "para_" + str(matches[0]) + "->para_" + str(matches[len(matches) - 1])
        else:
            range_list_for = find_range_list(stringToScan, edges)
            index = 0
            for edge in edges:
                if edge[0] == edge[1]:
                    start = range_list_for[index][0][0] + stringStart - longerStart + longer
                    difference = range_list_for[index][1][1] - range_list_for[index][0][0]
                    end = difference + start
                    ending = pom_string + "para_" + str(edge[0])
                    stringo, longer, cnt = make_reference(cnt, this_id, start, end, ending, stringo, longer, False)
                    index = index + 1
                else:
                    start = range_list_for[index][0][0] + stringStart - longerStart + longer
                    difference = range_list_for[index][1][1] - range_list_for[index][0][0]
                    end = difference + start
                    ending = pom_string + "para_" + str(edge[0]) + "->para_" + str(edge[1])
                    stringo, longer, cnt = make_reference(cnt, this_id, start, end, ending, stringo,
                                                          longer, False)
                    index = index + 1
            return stringo, longer, cnt
    return retval


def get_ending_for_clan_do_clan(m):
    retval = ""
    if m.group(1):
        m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(1))
        if m1:
            retval += "art_" + m1.group(0) + "->"
    if m.group(3):
        m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(3))
        if m1:
            retval += "art_" + m1.group(0)
        else:
            m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(4))
            retval += "art_" + m1.group(0)
    return retval


def get_reference_for_stav_nabrajanje(m, stringo, clan_id=""):
    pomLista = clan_id.split('-')
    pomBroj = re.findall(regexBrojSlovo, pomLista[len(pomLista) - 1])
    pom_string = "art_" + pomBroj[0] + "__"
    retval = ""
    if m.group(2):
        m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(2))
        if m1:
            retval += pom_string + "para_" + m1.group(0) + "->"
    if m.group(6):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(6))
        if m2:
            retval += "para_" + m2.group(0) + "_"
    return retval[:-1]


def get_reference_for_tacka_nabrajanje(m, stringo, clan_id="", stav_id=""):
    pomLista = clan_id.split('-')
    pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
    pom_string = "art_" + pomBroj[0] + "__"
    pomLista = stav_id.split('-')
    pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
    pom_string += "para_" + pomBroj[0] + "__"
    retval = ""
    if m.group(3):
        m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(3))
        if m1:
            retval += pom_string + "point_" + m1.group(0) + "->"
    if m.group(8):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(8))
        if m2:
            retval += "point_" + m2.group(0) + "_"
    elif m.group(9):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(9))
        if m2:
            retval += "point_" + m2.group(0) + "_"
        elif m.group(10):
            m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(10))
            if m2:
                retval += "point_" + m2.group(0) + "_"
    return retval[:-1]


def get_reference_for_clan_stav_tacka(m):
    retval = ""
    if m.group(1):
        m1 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(1))
        if m1:
            retval += "art_" + m1.group(0) + "_"
    if m.group(3):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(3))
        if m2:
            retval += "_para_" + m2.group(0) + "_"
    if m.group(5):
        m3 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(5))
        if m3:
            retval += "_point_" + m3.group(0) + "_"
    return retval


def get_ending2(m, clan_id):
    retval = ""
    if m.group(1):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(1))
        if m2:
            retval += "para_" + m2.group(0) + "_"
    if m.group(3):
        m3 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(3))
        if m3:
            retval += "_point_" + m3.group(0) + "_"
    # print(retval[:-1])
    pomLista = clan_id.split('-')
    pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
    pom_string = ""
    if len(pomBroj) != 0:
        pom_string = "art_" + pomBroj[0] + "__"
    retval = pom_string + retval
    return retval[:-1]


def get_ending_clan_nabrajanje(stringo, m, cnt=0, this_id="", longer=0):
    beginLonger = longer
    stringStart = m.regs[0][0] + longer
    stringEnd = m.regs[0][1] + longer
    stringToScan = stringo[stringStart:stringEnd]
    stringToScan = stringToScan + " "
    matches = re.findall(regexBrojSlovo, stringToScan)
    if '27ј' in matches:
        matches.remove('27ј')
    for i in matches:
        ending = "art_" + str(i)
        match = re.search(i, stringToScan)
        start = match.regs[0][0] + m.regs[0][0] + beginLonger
        end = start + len(match.group(0))
        stringo, longer, cnt = make_reference(cnt, this_id, start, end, ending, stringo, longer, False)
        beginLonger = beginLonger + (longer - beginLonger)
    retval = (stringo, longer, cnt)
    return retval


def get_ending_stav_nabrajanje(stringo, m, cnt=0, this_id="", longer=0, clan_id=""):
    longerStart = longer
    stringStart = m.regs[0][0] + longer
    if clan_id != "" and m.group(1):
        stringStart = m.regs[1][1] + longer
    stringEnd = m.regs[0][1] + longer
    stringToScan = stringo[stringStart:stringEnd]
    stringToScan = stringToScan + " "
    matches = re.findall(regexBrojSlovo, stringToScan)
    pom_string = ""
    if clan_id != "":
        pomLista = clan_id.split('-')
        pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
        pom_string = "art_" + pomBroj[0] + "__"
    retval = make_reference_for_nabrajanje_stava(matches, pom_string, stringToScan, stringStart,
                                                 longerStart, this_id, longer, cnt, stringo)
    return retval


def get_ending_tacka_nabrajanje(stringo, m, cnt=0, this_id="", longer=0, clan_id="", stav_id=""):
    beginLonger = longer
    stringStart = m.regs[0][0] + longer
    dodatniLonger = 0
    if clan_id != "" and m.group(1):
        dodatniLonger = m.regs[1][1] - m.regs[0][0]
        stringStart = m.regs[1][1] + longer
    if stav_id != "" and m.group(2):
        dodatniLonger = m.regs[2][1] - m.regs[0][0]
        stringStart = m.regs[2][1] + longer
    stringEnd = m.regs[0][1] + longer
    stringToScan = stringo[stringStart:stringEnd]
    stringToScan = stringToScan + " "
    matches = re.findall(regexBrojSlovo, stringToScan)
    pom_string = ""
    if clan_id != "":
        pomLista = clan_id.split('-')
        pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
        pom_string = "art_" + pomBroj[0] + "__"
    if stav_id != "":
        pomLista = stav_id.split('-')
        pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
        pom_string += "para_" + pomBroj[0] + "__"
    for i in matches:
        ending = pom_string + "point_" + str(i)
        match = re.search(i, stringToScan)
        start = match.regs[0][0] + m.regs[0][0] + beginLonger + dodatniLonger
        end = start + len(match.group(0))
        stringo, longer, cnt = make_reference(cnt, this_id, start, end, ending, stringo, longer, False)
        beginLonger = beginLonger + (longer - beginLonger)
    retval = (stringo, longer, cnt)
    return retval


def get_ending(m):
    retval = get_reference_for_clan_stav_tacka(m)
    return retval[:-1]


def get_ending_tacka(m, clan_id):
    retval = ""
    if m.group(1):
        m2 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(1))
        if m2:
            retval += "para_" + m2.group(0) + "_"
    if m.group(3):
        m3 = re.search("([0-9]+" + azbuka_pattern + ")", m.group(3))
        if m3:
            retval += "_point_" + m3.group(0) + "_"
    # print(retval[:-1])
    pomLista = clan_id.split('-')
    pomBroj = re.findall(regexBroj, pomLista[len(pomLista) - 1])
    pom_string = "art_" + pomBroj[0] + "__"
    retval = pom_string + retval
    return retval[:-1]


def add_refs1(stringo, cnt, this_id):
    longer = 0
    for m in re.finditer(nabrajanje + '\\s*(овог)?', stringo):
        foundStNabrajanje = re.search(nabrajanjeStav, stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        foundTackaNabrajanje = re.search(nabrajanjeTackaNeuzastopno,
                                         stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        foundTackaNabrajanjeUzastopno = re.search(nabrajanjeTacakaUzastopno,
                                                  stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        if not re.search(nabrajanjeClZakon,
                         stringo[m.regs[0][0] + longer: m.regs[0][
                                                            1] + longer + 20]) and not foundStNabrajanje and not foundTackaNabrajanje and not foundTackaNabrajanjeUzastopno:
            ending = get_ending(m)
            stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    longer = 0
    for m in re.finditer(nabrajanjeClZakon, stringo):
        stringo, longer, cnt = make_reference_for_clZakon(cnt, this_id, m, stringo, longer)
    return stringo, cnt


def add_refsCl(stringo, cnt, this_id):
    longer = 0
    for m in re.finditer(nabrajanjeCl + '\\s*(овог)?', stringo):
        findPattern = re.match(nabrajanjeClDoCl, stringo[m.regs[0][0] + longer:m.regs[0][0] + 20 + longer])
        foundPattern = re.match(nabrajanjeClCrtaClan, stringo[m.regs[0][0] + longer:m.regs[0][0] + 20 + longer])
        if findPattern:
            ending = get_ending_for_clan_do_clan(findPattern)
        elif foundPattern:
            ending = get_ending_for_clan_do_clan(foundPattern)
        else:
            ending = get_ending_clan_nabrajanje(stringo, m, cnt, this_id, longer)
            if type(ending) is tuple:
                stringo = ending[0]
                longer = ending[1]
                cnt = ending[2]
                continue

        stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    return stringo, cnt


def add_refs_sluzbeni_glasnik(stringo, cnt):
    for m in re.finditer(nabrajanje2 + '(Службени.{0,25}?)([0-9]+\/[0-9]+)(\s*([,и])\s*([0-9]+\/[0-9]+))*', stringo):
        matches = re.findall("([0-9]+)\/([0-9]+)", m.group(0))
        for i in matches:
            longer = 0
            m1 = re.search("(" + i[0] + ")" + "/" + "(" + i[1] + ")", stringo)
            if m1:
                open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m1.group(2) + "/" + m1.group(
                    1) + "/srp@\">"
            else:
                open = "<ref " + "wId=\"ref" + str(cnt) + "\">"
            stringo = stringo[:m1.start()] + open + stringo[m1.start():]
            longer += len(open)

            stringo = stringo[:m1.end() + longer] + "</ref>" + stringo[m1.end() + longer:]
            longer += len("</ref>")
            cnt += 1

    return stringo, cnt


def add_refs3(stringo, cnt, this_id, clan_id):
    longer = 0
    for m in re.finditer(nabrajanjeStavTacka + '\\s*(овог)?', stringo, re.IGNORECASE):
        foundTackaNabrajanje = re.search(nabrajanjeTackaNeuzastopno,
                                         stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        foundTackaNabrajanjeUzastopno = re.search(nabrajanjeTacakaUzastopno,
                                                  stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        if not re.search(nabrajanje + '\\s*(овог)?', stringo[m.regs[0][0] + longer - 40: m.regs[0][
                                                                                             1] + longer]) and not foundTackaNabrajanje and not foundTackaNabrajanjeUzastopno:
            ending = get_ending2(m, clan_id)

            stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    return stringo, cnt


def add_refs_stavNabrajanje(stringo, cnt, this_id, clan_id):
    longer = 0
    for m in re.finditer(nabrajanjeStav + '\\s*(овог)?', stringo):
        clan_id = m.group(1) if m.group(1) else clan_id
        findPattern = re.match(nabrajanjeStavUzastopno, stringo[m.regs[0][0]:m.regs[0][0] + 20])
        if findPattern:
            firstIndex = findPattern.regs[0][0] + m.regs[0][0] + longer
            lastIndex = findPattern.regs[0][1] + m.regs[0][0] + longer
            ending = get_reference_for_stav_nabrajanje(findPattern, stringo[firstIndex:lastIndex], clan_id)
        else:
            ending = get_ending_stav_nabrajanje(stringo, m, cnt, this_id, longer, clan_id)
            if type(ending) is tuple:
                stringo = ending[0]
                longer = ending[1]
                cnt = ending[2]
                continue

        stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    return stringo, cnt


def add_refs_tacka(stringo, cnt, this_id, clan_id, stav_id):
    longer = 0
    for m in re.finditer(nabrajanjeTacka + '\\s*(овог)?', stringo, re.IGNORECASE):
        pomString = stringo[m.regs[0][0] + longer - 40: m.regs[0][1] + longer]
        if pomString == "":
            pomString = stringo[m.regs[0][0] + longer - 30: m.regs[0][1] + longer]
            if pomString == "":
                pomString = stringo[m.regs[0][0] + longer - 20: m.regs[0][1] + longer]
                if pomString == "":
                    pomString = stringo[m.regs[0][0] + longer - 10: m.regs[0][1] + longer]
        foundTackaNabrajanje = re.search(nabrajanjeTackaNeuzastopno,
                                         stringo[m.regs[0][0] + longer: m.regs[0][1] + longer + 20])
        if not re.search(nabrajanje + '\\s*(овог)?', pomString) and not re.search(nabrajanjeStavTacka + '\\s*(овог)?',
                                                                                  pomString) and not foundTackaNabrajanje:
            ending = get_ending_tacka(m, clan_id)

            stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    return stringo, cnt


def add_refs_tackaNabrajanje(stringo, cnt, this_id, clan_id, stav_id):
    longer = 0
    for m in re.finditer(nabrajanjeTackaNeuzastopno + '\\s*(овог)?', stringo):
        clan_id = m.group(1) if m.group(1) else clan_id
        stav_id = m.group(2) if m.group(2) else stav_id
        findPattern = re.match(nabrajanjeTacakaUzastopno, stringo[m.regs[0][0] + longer:m.regs[0][1] + 20 + longer])
        if findPattern:
            firstIndex = findPattern.regs[0][0] + m.regs[0][0] + longer
            lastIndex = findPattern.regs[0][1] + m.regs[0][0] + longer
            ending = get_reference_for_tacka_nabrajanje(findPattern, stringo[firstIndex:lastIndex], clan_id, stav_id)
            stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
        else:
            ending = get_ending_tacka_nabrajanje(stringo, m, cnt, this_id, longer, clan_id, stav_id)
            if type(ending) is tuple:
                stringo = ending[0]
                longer = ending[1]
                cnt = ending[2]
                continue
            stringo, longer, cnt = make_reference(cnt, this_id, m.start(), m.end(), ending, stringo, longer)
    return stringo, cnt


def add_refs_dr_zakon(stringo, cnt, this_id):
    longer = 0
    for m in re.finditer(nabrajanjeDrZakon, stringo, re.IGNORECASE):
        if not re.search(nabrajanje2 + '(Службени.*?)([0-9]+/[0-9]+)+', stringo[m.regs[0][0] - 40:m.regs[0][1]]):
            stringo, longer, cnt = make_reference_for_dr_zakon(cnt, this_id, m, stringo, longer)
    return stringo, cnt


def add_refs_sluzbeni_glasnik_datum(stringo, cnt):
    longer = 0
    for m1 in re.finditer(nabrajanjeSluzbeniGlasnikDatum, stringo):
        open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m1.group(3) + "/" + m1.group(
            1) + "/srp@\">"
        stringo = stringo[:m1.start() + longer] + open + stringo[m1.start() + longer:]
        longer += len(open)

        stringo = stringo[:m1.end() + longer] + "</ref>" + stringo[m1.end() + longer:]
        longer += len("</ref>")
        cnt += 1
    return stringo, cnt


def add_refs_dr_zakon_datum(stringo, cnt):
    longer = 0
    for m in re.finditer(nabrajanjeDrZakonDatum, stringo):
        open = "<ref " + "wId=\"ref" + str(cnt) + "\" href=\"akn/rs/act/" + m.group(3) + "/" + m.group(
            1) + "/srp@\">"
        stringo = stringo[:m.start()] + open + stringo[m.start():]
        longer += len(open)

        stringo = stringo[:m.end() + longer] + "</ref>" + stringo[m.end() + longer:]
        longer += len("</ref>")
        cnt += 1
    return stringo, cnt

def add_all_references(stav_text, cnt, this_id, clan_id, stav_id):
    stringoRet, cnt = add_refs1(stav_text, cnt, this_id)
    stringoRet, cnt = add_refsCl(stringoRet, cnt, this_id)
    stringoRet, cnt = add_refs_sluzbeni_glasnik(stringoRet, cnt)
    stringoRet, cnt = add_refs_sluzbeni_glasnik_datum(stringoRet, cnt)
    stringoRet, cnt = add_refs_dr_zakon(stringoRet, cnt, this_id)
    stringoRet, cnt = add_refs3(stringoRet, cnt, this_id, clan_id)
    stringoRet, cnt = add_refs_stavNabrajanje(stringoRet, cnt, this_id, clan_id)
    stringoRet, cnt = add_refs_tacka(stringoRet, cnt, this_id, clan_id, stav_id)
    stringoRet, cnt = add_refs_tackaNabrajanje(stringoRet, cnt, this_id, clan_id, stav_id)
    return stringoRet, cnt

def add_refs(stablo, stringo, this_id):
    cnt = 0
    listaClanova = get_elements(stablo, 'article', namespace="")
    listaObradjenihParagrafa = []

    for el_clan in listaClanova:  # Primer pristupa svakom članu
        clan_id = el_clan.attrib['wId']
        if ("gla6-clan42" in clan_id):
            print("")
        for el_stav in el_clan.iter('paragraph'):
            stav_id = el_stav.attrib['wId']
            if stav_id not in listaObradjenihParagrafa:
                if el_stav.attrib.get('class') is not 'special':
                    for el_content_p_tag in el_stav.iter('p'):
                        stav_text = el_content_p_tag.text.replace(">", "~vece;").replace("<", "~manje;").replace("\"",
                                                                                                                 "~navod;").replace(
                            "&gt;", "~vece;").replace("&lt;", "~manje;").replace("\"", "~navod;")
                        stringoRet, cnt = add_all_references(stav_text, cnt, this_id, clan_id, stav_id)
                        el_content_p_tag.text = stringoRet
                listaObradjenihParagrafa.append(el_stav.attrib['wId'])
        for el_heading in el_clan.iter('heading'):
            if el_heading.text:
                heading_text = el_heading.text
                stringoRet, cnt = add_all_references(heading_text, cnt, this_id, clan_id, "")
                el_heading.text = stringoRet

    for elem in stablo.iter(tag='longTitle'):
        p_text = elem[0].text
        stringoRet, cnt = add_all_references(p_text, cnt, this_id, "", "")
        elem[0].text = stringoRet

    return stablo
