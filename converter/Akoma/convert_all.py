import io
import os
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import sys

try:
    import Akoma
    from Akoma.convertToLatin import regex_patterns
    from Akoma.utilities import ETree, utilities
    from Akoma.preprocessing import init_akoma
    from Akoma.tokenizer.HTMLTokenizer import HTMLTokenizer
    from Akoma.form_akoma.AkomaBuilder import AkomaBuilder
    from Akoma.reasoner.BasicReasoner import BasicReasoner
    from Akoma.reasoner.OdlukaReasoner import OdlukaReasoner
    from Akoma.form_akoma.MetadataBuilder import MetadataBuilder
    from Akoma.named_enitity_recognition.references import add_refs
    from Akoma.tokenizer.BasicTokenizer import BasicTokenizer
    from Akoma.named_enitity_recognition.ner import do_ner_on_sentences, do_spacy_ner, fix_dates
    from Akoma.convertToLatin.Convert import convert
    from Akoma.utilities.utilities import DOC_TYPE
    from Akoma.form_akoma import Metadata
except ModuleNotFoundError as sureError:
    try:
        from utilities import ETree, utilities
        from convertToLatin import regex_patterns
        from preprocessing import init_akoma
        from tokenizer.HTMLTokenizer import HTMLTokenizer
        from tokenizer.BasicTokenizer import BasicTokenizer
        from form_akoma.AkomaBuilder import AkomaBuilder
        from tokenizer import patterns
        from reasoner.BasicReasoner import BasicReasoner
        from reasoner.OdlukaReasoner import OdlukaReasoner
        from form_akoma.MetadataBuilder import MetadataBuilder
        from form_akoma import Metadata
        from named_enitity_recognition.references import add_refs
        from named_enitity_recognition.ner import do_ner_on_sentences, do_spacy_ner, fix_dates
        from convertToLatin.Convert import convert
        from utilities.utilities import DOC_TYPE
    except ModuleNotFoundError as newError:
        if not sureError.name.__eq__("Akoma") or not newError.name.__eq__("Akoma"):
            print(newError)
            print("Error")
            exit(-1)

sys.setrecursionlimit(10000000)
ner_list = []


#

def send_to_NER(stablo):
    global ner_list
    for el in stablo.iter(tag="paragraph"):
        for elem in el.iter(tag="p"):
            if elem.text is not None:
                if len(elem.text) > 10:
                    val = "".join([convert(s) for s in elem.text])
                    ner_list.append(val)


def not_invalid(text):
    if "<" in text:
        return False
    if ">" in text:
        return False
    return True


def add_ner_tags(map_of_values, stablo, metadata_builder):
    # Misc values are ignored, as they don't have a representation in the FRBR ontology
    ref = ETree.get_elements(stablo, "references")[0]

    for key in map_of_values:

        if key == "deriv" or key == "per":
            for element in map_of_values[key]:
                link = metadata_builder.translator[element]
                if '#' not in link:
                    link = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCPerson'
                if not_invalid(element):
                    ref.append(
                        ET.Element("TLCPerson", {"href": link,
                                                 "showAs": element}))  # http://purl.org/vocab/frbr/core#Person"
        elif key == "loc":
            for element in map_of_values[key]:
                link = metadata_builder.translator[element]
                if '#' not in link:
                    link = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCLocation'
                if not_invalid(element):
                    ref.append(
                        ET.Element("TLCLocation", {"href": link,
                                                   "showAs": element}))  # "http://purl.org/vocab/frbr/core#Place"
        elif key == "org":
            for element in map_of_values[key]:
                link = metadata_builder.translator[element]
                if '#' not in link:
                    link = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCOrganization'
                if not_invalid(element):
                    ref.append(ET.Element("TLCOrganization",
                                          {"href": link,
                                           "showAs": element}))  # "http://purl.org/vocab/frbr/core#CorporateBody"
        elif key == "date":
            for element in map_of_values[key]:
                if not_invalid(element):
                    link = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCEvent'
                    ref.append(
                        ET.Element("TLCEvent", {"href": link,
                                                "showAs": element}))  # "http://purl.org/vocab/frbr/core#Event"


def apply_akn_tags(text: str, meta_name: str, skip_tfidf_ner=False, ner="crf", meta_data=None):
    """
    Applies to text Akoma Ntoso 3.0 tags for Republic of Serbia regulations
    :param text: HTML or plain text
    :param meta_name: name which was meta added in file, 15 tag in meta, use function in MetadataBuilder.add_new_meta or
    add manually in Akoma/data/meta/allmeta.csv
    :param skip_tfidf_ner: Don't add references> TLCconcept for document and TLC for ner, if true speeds up execution by a lot
    :param ner: chooses model which will be used, can be one of values: 'crf','spacy','spacy_default','reldi', crf best so far but slowest
    :param meta_data: type form_akoma/Metadata.py, if this is passed meta_name is not important, because file allmeta.csv is not searched and all data passed in meta_data is used for meta_data
    :return: Labeled xml string
    """
    global ner_list
    akoma_root = init_akoma.init_xml("act")
    repaired = False
    if text.find("<") == -1:
        repaired = True
    else:
        text = regex_patterns.strip_html_tags_exept(text)
    if not repaired:
        try:
            html_root = ET.fromstring("<article>" + text + "</article>")
        except Exception as e:
            got = BeautifulSoup(text, "lxml")
            text = got.prettify().replace("<html>", "").replace("</html>", "").replace("<body>", "").replace("</body>",
                                                                                                             "")
            html_root = ET.fromstring("<article>" + text + "</article>")
    metabuilder = MetadataBuilder("data/meta/allmeta.csv")
    metabuilder.build(meta_name, akoma_root, skip_tfidf_ner)
    # print(ETree.prettify(akoma_root))
    builder = AkomaBuilder(akoma_root)
    if not repaired:
        reasoner = BasicReasoner(HTMLTokenizer(html_root), builder)
    else:
        reasoner = BasicReasoner(BasicTokenizer(text), builder)
    reasoner.start(metabuilder)

    if reasoner.current_hierarchy[4] == 0:
        akoma_root = init_akoma.init_xml("act")
        metabuilder = MetadataBuilder("data/meta/allmeta.csv")
        if meta_data is None:
            metabuilder.build(fajl, akoma_root, skip_tfidf=skip_tfidf_ner)
        else:
            metabuilder.build(fajl, akoma_root, skip_tfidf=skip_tfidf_ner, passed_meta=meta_data)

        builder = AkomaBuilder(akoma_root)
        if not repaired:
            reasoner = OdlukaReasoner(HTMLTokenizer(html_root), builder)
        else:
            reasoner = OdlukaReasoner(BasicTokenizer(text), builder)
        reasoner.start(metabuilder)

    result_str = builder.result_str().replace("&lt;", "~vece;").replace("&gt;", "~manje;").replace("&quot;", "~navod;")
    if not skip_tfidf_ner:
        send_to_NER(akoma_root)
        if ner == "crf":
            map_ret = do_ner_on_sentences(ner_list)
        elif ner == "spacy":
            map_ret = do_spacy_ner(ner_list, custom=True)
        elif ner == "spacy_default":
            map_ret = do_spacy_ner(ner_list, custom=False)
        elif ner == "reldi":
            map_ret = {}
            print("Waiting for access to reldi NER from devs, TODO for future")
            exit(-1)
        if ner == "crf" or ner == "spacy" or ner == "spacy_default" or ner == "reldi":
            fix_dates(map_ret)
            events = utilities.regex_events(regex_patterns.strip_html_tags(text))
            utilities.entities_add_date(map_ret, events)  # Regex adding dates
            add_ner_tags(map_ret, akoma_root, metabuilder)
        ner_list.clear()

    try:
        result_stablo = add_refs(akoma_root, result_str, metabuilder.uri_expression)
    except Exception as e:
        file_ref_exeption = open(utilities.get_root_dir() + "/data/" + "za_ninu.txt", mode="a+")
        file_ref_exeption.write(meta_name + ":" + str(e) + "\n")
        file_ref_exeption.close()
        return result_str
    result_str = ETree.prettify(result_stablo).replace("&lt;", "<") \
        .replace("&gt;", ">").replace("&quot;", "\"").replace('<references source="#somebody"/>', "")

    result_str = result_str.replace("~vece;", "&gt;").replace("~manje;", "&lt;").replace("~navod;", "&quot;")
    return result_str


def convert_html(source, destination, skip_tfidf_ner=False, ner="crf"):
    try:
        opened = io.open(source, mode="r", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError("File not exist")
    text = "".join(opened.readlines())
    meta_file_name = source.split("/")[-1]
    result_str = apply_akn_tags(text, meta_file_name, skip_tfidf_ner=skip_tfidf_ner, ner=ner)
    f = io.open(destination, mode="w", encoding="utf-8")
    f.write(result_str)
    f.close()


if __name__ == "__main__":

    nastavi = "1.html"
    only_annotated = True  # just do annotated files
    idemo = False
    stani = [
        "1005.html", "980.html", "986.html", "981.html", "210.html", "1033.html"  # problematicni PROVERITI 176
        , "180.html"]  # Veliki fajlovi
    location_source = utilities.get_root_dir() + "/data/acts"
    annotated_source = utilities.get_root_dir() + "/data/annotated"
    fajls = utilities.sort_file_names(os.listdir(location_source))
    if only_annotated is True:
        fajls = utilities.sort_file_names(os.listdir(annotated_source))
        fajls = [el.replace(".xml", ".html") for el in fajls]
        idemo = True

    for fajl in fajls:
        if fajl == nastavi:
            idemo = True
        if not idemo:
            continue
        if fajl in stani:
            continue
        # if fajl != "2.html":
        #     continue
        print(fajl)
        # try:
        convert_html(location_source + '/' + fajl, 'data/akoma_result/' + fajl[:-5] + ".xml", skip_tfidf_ner=False,
                     ner="crf")
        # except Exception as e:
        #     file_exeption = open(utilities.get_root_dir() + "/data/" + "za_andriju.txt", mode="a+")
        #     file_exeption.write(fajl + ":" + str(e) + "\n")
        #     file_exeption.close()
