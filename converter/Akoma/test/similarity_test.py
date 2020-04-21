import difflib
import os
import re
import statistics
import xml.etree.ElementTree as ET

try:
    from Akoma.utilities import utilities
    from Akoma.utilities import ETree
    from Akoma.convertToLatin.Convert import top
except ModuleNotFoundError:
    try:
        from utilities import utilities
        from utilities import ETree
        from convertToLatin.Convert import top
    except ModuleNotFoundError:
        print("Import error")

map_found_org = {
    ETree.get_akoma_tag("deo"): 0,
    ETree.get_akoma_tag("glava"): 0,
    ETree.get_akoma_tag("odeljak"): 0,
    ETree.get_akoma_tag("pododeljak"): 0,
    ETree.get_akoma_tag("clan"): 0,
    ETree.get_akoma_tag("stav"): 0,
    ETree.get_akoma_tag("tacka"): 0,
    ETree.get_akoma_tag("podtacka"): 0,
    ETree.get_akoma_tag("alinea"): 0}

map_found_new = {
    ETree.get_akoma_tag("deo"): 0,
    ETree.get_akoma_tag("glava"): 0,
    ETree.get_akoma_tag("odeljak"): 0,
    ETree.get_akoma_tag("pododeljak"): 0,
    ETree.get_akoma_tag("clan"): 0,
    ETree.get_akoma_tag("stav"): 0,
    ETree.get_akoma_tag("tacka"): 0,
    ETree.get_akoma_tag("podtacka"): 0,
    ETree.get_akoma_tag("alinea"): 0}


def find_structure_sim(got_text_new, got_text_org):
    tree_new = ET.fromstring(got_text_new)
    tree_org = ET.fromstring(got_text_org)
    for key in map_found_org:
        found = ETree.get_elements(tree_org, key)
        map_found_org[key] = found
    for key in map_found_new:
        found = ETree.get_elements(tree_new, key)
        map_found_new[key] = found
    has = 0
    fp = 0
    total_org = sum([len(map_found_org[el]) for el in map_found_org])
    for key in map_found_new:
        new_ids = [el.attrib['wId'] for el in map_found_new[key]]
        org_ids = [el.attrib['wId'] for el in map_found_org[key]]
        for new_wid in new_ids:
            if new_wid in org_ids:
                has = has + 1
            else:
                fp = fp + 1
    return has / has + fp, has / total_org


def find_ref_similarity(text_new, text_org):
    """
    Return precision and recall for references in document annotated and new
    :param text_new: New document made
    :param text_org: Annotated by hand document
    :return: precision,recall
    """
    new_refs = re.findall('<ref .*?>', text_new)
    org_refs = re.findall("<ref .*?>", text_org)
    false_positive = list()
    false_negative = list()
    has = 0
    not_fp = False
    for el in new_refs:
        href = re.findall('href=".*"', el)
        if len(href) == 0:
            false_positive.append(el)
            break
        else:
            href = href[0]
        for check in org_refs:
            if href in check:
                has = has + 1
                not_fp = True
                break
        if not not_fp:
            false_positive.append(el)
        not_fp = False
    for elem in org_refs:
        href = re.findall('href=".*"', elem)
        if len(href) == 0:
            false_negative.append(elem)
            break
        else:
            href = href[0]
        for check in org_refs:
            if href in check:
                not_fp = True
        if not not_fp:
            false_negative.append(elem)
        not_fp = True
    fn = len(false_negative)
    fp = len(false_positive)
    return has / has + fp, has / len(org_refs)


def load_data(source_new, source_annotated):
    try:
        new = open(source_new, mode="r", encoding="UTF-8")
        annotated = open(source_annotated, mode="r", encoding="UTF-8")
    except FileNotFoundError:
        exit(-1)
    new_text = "".join(new.readlines())
    annotated_text = "".join(annotated.readlines())
    new.close()
    annotated.close()
    return new_text, annotated_text


def find_fscore(precision, recall):
    return top(2 * ((precision * recall) / (precision + recall)))


def find_f1score_ref_similarity(new_text, annotated_text):
    f_prec, f_rec = find_ref_similarity(new_text, annotated_text)
    return top(find_fscore(f_prec,f_rec))


def find_f1score_hir_structure_similarity(new_text, annotated_text):
    structure_pres, structure_recall = find_structure_sim(new_text, annotated_text)
    return find_fscore(structure_pres, structure_recall)


def find_similarity(text, text2):
    similarity = difflib.SequenceMatcher(None, text, text2).ratio()
    return similarity


if __name__ == "__main__":
    location_annotated = "../data/annotated/"
    location_data = "../data/akoma_result/"
    annotated_files = utilities.sort_file_names(os.listdir(location_annotated))
    f1_list = []
    sim_list = []
    f1_struct_list = []
    for i in range(0, len(annotated_files)):
        text_new, text_ann = load_data(location_data + annotated_files[i], location_annotated + annotated_files[i])
        similarity = find_similarity(text_new, text_ann)
        f1 = find_f1score_ref_similarity(text_new, text_ann)
        f1_struct = find_f1score_hir_structure_similarity(text_new,text_ann)
        f1_struct_list.append(f1_struct)
        f1_list.append(f1)
        sim_list.append(similarity)
        print(annotated_files[i])
        print("F1 ref=" + str(f1))
        print("F1 struct=" + str(f1_struct))
        print("SIM=" + str(similarity))

    print("F1_REF_AVG :" + str(statistics.mean(f1_list)))
    print("F1_STRUCT_AVG=" + str(statistics.mean(f1_struct_list)))
    print("SIM_AVG :" + str(statistics.mean(sim_list)))
