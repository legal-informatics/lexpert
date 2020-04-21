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
    from Akoma.named_enitity_recognition.ner import do_ner_on_sentences
    from Akoma.convertToLatin.Convert import convert
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
        from named_enitity_recognition.references import add_refs
        from named_enitity_recognition.ner import do_ner_on_sentences
        from convertToLatin.Convert import convert
    except ModuleNotFoundError as newError:
        if not sureError.name.__eq__("Akoma") or not newError.name.__eq__("Akoma"):
            print(newError)
            print("Error")
            exit(-1)

sys.setrecursionlimit(10000000)


def send_to_NER(stablo):
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


def add_ner_tags(map_of_values, stablo):
    # Misc values are ignored, as they don't have a representation in the FRBR ontology
    ref = ETree.get_elements(stablo, "references")[0]
    for key in map_of_values:
        if key == "deriv" or key == "per":
            for element in map_of_values[key]:
                if not_invalid(element):
                    ref.append(
                        ET.Element("TLCPerson", {"href": "http://purl.org/vocab/frbr/core#Person", "showAs": element}))
        elif key == "loc":
            for element in map_of_values[key]:
                if not_invalid(element):
                    ref.append(
                        ET.Element("TLCLocation", {"href": "http://purl.org/vocab/frbr/core#Place", "showAs": element}))
        elif key == "org":
            for element in map_of_values[key]:
                if not_invalid(element):
                    ref.append(ET.Element("TLCOrganization",
                                          {"href": "http://purl.org/vocab/frbr/core#CorporateBody", "showAs": element}))
        elif key == "date":
            for element in map_of_values[key]:
                if not_invalid(element):
                    ref.append(
                        ET.Element("TLCEvent", {"href": "http://purl.org/vocab/frbr/core#Event", "showAs": element}))


def apply_akn_tags(text: str, meta_name: str, skip_tfidf_ner=False):
    """
    Applies to text Akoma Ntoso 3.0 tags for Republic of Serbia regulations
    :param text: HTML or plain text
    :param meta_name: name which was meta added in file, 15 tag in meta, use function in MetadataBuilder.add_new_meta or
    add manually in Akoma/data/meta/allmeta.csv
    :param skip_tfidf_ner: Don't add references> TLCconcept for document and TLC for ner, if true speeds up execution by a lot
    :return: Labeled xml string
    """
    akoma_root = init_akoma.init_xml("act")
    repaired = False
    if text.find("<p") == -1:
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
    reasoner.start()

    if reasoner.current_hierarchy[4] == 0:
        akoma_root = init_akoma.init_xml("act")
        metabuilder = MetadataBuilder("data/meta/allmeta.csv")
        metabuilder.build(fajl, akoma_root, skip_tfidf=skip_tfidf_ner)

        builder = AkomaBuilder(akoma_root)
        if not repaired:
            reasoner = OdlukaReasoner(HTMLTokenizer(html_root), builder)
        else:
            reasoner = OdlukaReasoner(BasicTokenizer(text), builder)
        reasoner.start()

    result_str = builder.result_str().replace("&lt;", "~vece;").replace("&gt;", "~manje;").replace("&quot;", "~navod;")
    if not skip_tfidf_ner:
        send_to_NER(akoma_root)
        map_ret = do_ner_on_sentences(ner_list)
        add_ner_tags(map_ret, akoma_root)  # print(ret)
        ner_list.clear()

    try:
        result_stablo = add_refs(akoma_root, result_str, metabuilder.expressionuri)
    except Exception as e:
        file_ref_exeption = open(utilities.get_root_dir() + "/data/" + "za_ninu.txt", mode="a+")
        file_ref_exeption.write(meta_name + ":" + str(e) + "\n")
        file_ref_exeption.close()
        return result_str
    result_str = ETree.prettify(result_stablo).replace("&lt;", "<") \
        .replace("&gt;", ">").replace("&quot;", "\"").replace('<references source="#somebody"/>', "")

    result_str = result_str.replace("~vece;", "&gt;").replace("~manje;", "&lt;").replace("~navod;", "&quot;")
    return result_str


ner_list = []


def convert_html(source, destination, skip_tfidf_ner=False):
    try:
        opened = io.open(source, mode="r", encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError("File not exist")
    text = "".join(opened.readlines())
    full_strip = regex_patterns.strip_html_tags_exept(text)  #
    meta_file_name = source.split("/")[-1]
    result_str = apply_akn_tags(full_strip, meta_file_name, skip_tfidf_ner=skip_tfidf_ner)
    f = io.open(destination, mode="w", encoding="utf-8")
    f.write(result_str)
    f.close()


if __name__ == "__main__":

    nastavi = "51.html"

    idemo = False
    stani = [
        "1005.html", "980.html", "986.html", "981.html", "210.html", "1033.html"  # problematicni PROVERITI 176
        , "180.html"]  # Veliki fajlovi
    location_source = "data/acts"
    fajls = utilities.sort_file_names(os.listdir(location_source))

    for fajl in fajls:
        if fajl == nastavi:
            idemo = True
        if not idemo:
            continue
        if fajl in stani:
            continue
        print(fajl)
        # try:
        convert_html(location_source + '/' + fajl, 'data/akoma_result/' + fajl[:-5] + ".xml", skip_tfidf_ner=False)
        # except Exception as e:
        #     file_exeption = open(utilities.get_root_dir() + "/data/" + "za_andriju.txt", mode="a+")
        #     file_exeption.write(fajl + ":" + str(e) + "\n")
        #     file_exeption.close()
