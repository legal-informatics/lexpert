import utilities
import xml.etree.ElementTree as ET
import math
from termcolor import colored

# https://eli.thegreenplace.net/2012/03/15/processing-xml-in-python-with-elementtree/

TAG_DEO = 'part'
TAG_GLAVA = 'chapter'
TAG_ODELJAK = 'section'
TAG_PODODELJAK = 'subsection'
TAG_CLAN = 'article'
TAG_STAV = 'paragraph'  # 'clause'
TAG_TACKA = 'point'
TAG_PODTACKA = 'hcontainer'
TAG_ALINEA = 'alinea'

Tag_dict = {'deo': TAG_DEO, 'glava': TAG_GLAVA, 'odeljak': TAG_ODELJAK, 'pododeljak': TAG_PODODELJAK, 'clan': TAG_CLAN,
            'stav': TAG_STAV, 'tacka': TAG_TACKA, 'podtacka': TAG_PODTACKA, 'alinea': TAG_ALINEA}

# CNS = '{http://www.akomantoso.org/2.0}'
CNS = '{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}'
CID = "wId"


def get_akoma_tag(name):
    """
    Iz tagova pravnih propisa vraća tagove u Akoma Ntoso specifikacije koji su dogovoreni
    :param name: Name of hierarchical element in legal document like Deo,Glava ....
    :return: Appointed tag in Akoma Ntoso 3.0 specification
    """
    name = name.lower()
    return Tag_dict[name]  # Tag_dict.get(name)


def append_to_element_by_id(root, name, id, new_element, namespace=CNS):
    if not ET.iselement(new_element):
        raise ValueError('Expected new element should be element of ElementTree library')
    ret = get_elements_by_id(root, name, id, namespace)
    ret[0].append(new_element)


def get_elements(root, name, namespace=CNS,debug=False):
    ret = [iter_chapter for iter_chapter in root.iter(tag=namespace + name)]
    if len(ret) == 0:
        ret = [iter_chapter for iter_chapter in root.iter(tag=name)]
    if len(ret) == 0:
        if debug:
            text_error = ">>ElementTree no " + name + " found using get_elements in utilities.Etree"
            print(colored(text_error, 'red'))
    return ret


def get_elements_by_id(root, name, id, namespace=CNS):
    ret = [iter_chapter for iter_chapter in get_elements(root, name, namespace) if iter_chapter.attrib[CID] == id]
    return ret


def get_glavas_by_id(root, id, namespace=CNS):
    ret = get_elements_by_id(root, TAG_GLAVA, id, namespace)
    return ret


def get_glavas(root, namespace=CNS):
    return get_elements(root, TAG_GLAVA, namespace)


def get_clans(root, namespace=CNS):
    return get_elements(root, TAG_CLAN, namespace)


def get_clan_by_id(root, id, namespace=CNS):
    return get_elements_by_id(root, TAG_CLAN, id, namespace)


def init_parent(tree):
    global Parent_map
    Parent_map = {c: p for p in tree.iter() for c in p}
    return Parent_map


def prettify(root):
    import xml.dom.minidom
    dom = xml.dom.minidom.parseString(ET.tostring(root, encoding='UTF-8', method="xml").decode())
    return dom.toprettyxml()


def get_parent_by_tag(element, tag_name, tree=None, max_up=10):
    global Parent_map
    i = 1
    if tree is not None and len(Parent_map) == 0:
        tree = init_parent(tree)
    max_up = math.fabs(max_up)
    while i <= max_up:
        parent = get_parent_nth_parent(element, i, tree)
        if parent is None:
            return None
        i = i + 1
        if parent.tag == tag_name:
            return parent
    return None


def get_parent_nth_parent(element, parent=1, tree=None):
    """
    Vraca roditelja nekog u stablu
    :param element: Element which parent is searched for
    :param parent: number of hirarhical parents to get
    :param tree: call init_parent metod with tree to build parent child bonds, better use init_parent than always put need to pass Root_Tree in tree
    :return: n-th parent type element from xml.etree.Element
    """
    global Parent_map
    if tree is not None and len(Parent_map) == 0:
        tree = init_parent(element)
    else:
        tree = Parent_map
    if len(Parent_map) == 0:
        print("Error in get_parent_nth_parent metode in ETree.py")
        print("Call init parent first")
        return None
    if parent == 0:
        return element
    else:
        new_el = tree.get(element)
        if element is None:
            return element
        else:
            return get_parent_nth_parent(new_el, parent - 1)


Parent_map = dict()

if __name__ == "__main__":
    # Deprecated
    # f = open(path, mode="r", encoding="utf8")
    # lines = f.readlines()
    # str_lines = "".join(lines)
    # rootic = ET.fromstring(str_lines)

    path = utilities.get_root_dir() + "/data/akoma_result/85.xml"

    tree = ET.parse(path)

    ns = CNS
    g = get_glavas_by_id(tree, "gla1", ns)

    to_add = ET.fromstring('<chapter id="new_chap"><num>10</num><content>Zakon rada</content></chapter>\n')  # RADI
    to_add2 = ET.fromstring('<chapter id="new_2"><num>20</num><content>Zakon buca</content></chapter>\n')  # RADI

    append_to_element_by_id(tree, 'chapter', 'gla1', to_add2)  # Primer dodavanja
    g[0].append(to_add)  # Primer kada rucno dodajes na bilo koje element u stablu
    Root = tree.getroot()

    # ET.dump(Root)
    init_parent(tree)  # Priprema hashmape za poziva get_parent

    # Ako se uradi init_parent, Moze se pristupiti samo preko tag=ns+'p' tagu, zatim se samo get parents,
    # ne trebaju ove sve for petlje

    for el_clan in Root.iter(tag="article"):  # Primer pristupa svakom članu
        clan_id = el_clan.attrib[CID]
        for el_stav in el_clan.iter(tag='paragraph'):
            for el_content_p_tag in el_stav.iter(tag='p'):
                got_parent = get_parent_nth_parent(el_content_p_tag, 2)  # Pribavljanje roditelja
                got_parent2 = get_parent_by_tag(el_content_p_tag, 'article')
                stav_text = el_content_p_tag.text
                print(stav_text)
            print(el_stav.tag)
    print(el_clan.tag, el_clan.attrib)

    ET.dump(Root)

    for child_of_root in Root:
        print(child_of_root.tag, child_of_root.attrib)
