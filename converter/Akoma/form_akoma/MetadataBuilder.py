import xml.etree.ElementTree as ET
import io

try:
    from Akoma.utilities import utilities
    from Akoma.form_akoma.Metadata import Metadata
    from Akoma.preprocessing import init_akoma
    from Akoma.tfidf.tfidf import get_tf_idf_values_document, get_tf_idf_values_from_text
except ModuleNotFoundError:
    try:
        from utilities import utilities
        from form_akoma.Metadata import Metadata
        from preprocessing import init_akoma
        from tfidf.tfidf import get_tf_idf_values_document, get_tf_idf_values_from_text
        from convertToLatin import Convert
        from utilities.markoSemanticki import MarkovaIngenioznost
    except ModuleNotFoundError:
        print("Error")
        exit(-1)
import os

PREFIX = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
SOURCE = "#somebody"  # "#pravno-informacioni-sistem"
ADDED_DATE = "-01-01"


def valid_date(date, reduce=0):
    import datetime
    day, month, year = date.split('-')
    is_valid_date = True
    try:
        datetime.datetime(int(year), int(month), int(day))
    except ValueError:
        is_valid_date = False
    return is_valid_date


def extra_fix(check):
    yy, mm, dd = check.split('-')
    if len(check.split('-')) != 3:
        return check
    dd = int(dd)
    mm = int(mm)
    yy = int(yy)
    if mm == 1 or mm == 3 or mm == 5 or mm == 7 or mm == 8 or mm == 10 or mm == 12:
        max1 = 31
    elif mm == 4 or mm == 6 or mm == 9 or mm == 11:
        max1 = 30
    elif yy % 4 == 0 and yy % 100 != 0 or yy % 400 == 0:
        max1 = 29
    else:
        max1 = 28

    if mm < 1:
        mm = 1
    elif mm > 12:
        mm = 12
    if dd < 1:
        dd = 1
    elif dd > max1:
        dd = max1
    ret = str(yy) + "-" + str(mm) + "-" + str(dd)
    return fix_date(ret, False)


def fix_date(before, use_extra=True):
    a = before.split("-")
    if len(a) == 1:
        return before.replace(".", "") + ADDED_DATE;
    for i in range(0, len(a)):
        if len(a[i]) < 2:
            a[i] = "0" + a[i]
    after = "-".join(a)
    if use_extra:
        return extra_fix(after)
    return after


def add_new_meta(meta: Metadata):
    """
    If file to added meta
    Назив прописа  # ELI#Напомена издавача#Додатне информације#Врста прописа#Доносилац#Област#Група#Датум усвајања#Гласило и датум објављивања#Датум ступања на снагу основног текста#Датум примене#Правни претходник#Издавач#filename#Верзија на снази од#Почетак примене верзије#Број акта
    :param meta:
    :return: None, writes in file meta
    """
    file_meta = open(utilities.get_root_dir() + "/data/meta/allmeta.csv", mode="a")
    deli = "#"
    new_line = meta.act_name + deli + meta.eli + deli + meta.napomena_izdavaca + deli + meta.dodatne_informacije + deli + meta.vrsta_propisa + deli + meta.donosilac + deli + meta.oblast + deli + meta.grupa + deli + meta.datum_usvajanja + deli + meta.glasilo_i_datum + deli + meta.datum_stupanja + deli + meta.pravni_prethodnik + deli + meta.izdavac + deli + meta.filename + "\n"
    file_meta.write(new_line)
    file_meta.close()


class MetadataBuilder():

    def __init__(self, csv_file):
        if csv_file is not None:
            self.csv = io.open(csv_file, mode="r", encoding="utf-8")
        else:
            self.csv = None
        self.expressionuri = ""
        self.uri_expression = ""
        self.uri_work = ""
        self.uri_manifestation = ""
        self.number = ""
        self.meta = None
        self.classification = None
        self.lifecycle_node = None
        self.translator = MarkovaIngenioznost()


    def identification(self, metadata):
        base = ET.Element("identification", {"source": SOURCE})
        base.append(self.frbrwork(metadata["work"]["date"], metadata["work"]["version"], metadata["author"]))
        base.append(
            self.frbrexpression(metadata["manifest"]["date"], metadata["manifest"]["version"], metadata["editor"]))
        base.append(
            self.frbrmanifestation(metadata["manifest"]["date"], metadata["manifest"]["version"], metadata["editor"]))
        return base

    def frbrwork(self, date, version, author, country="Serbia"):
        base = ET.Element("FRBRWork")
        base.append(ET.Element("FRBRthis", {"value": self.uri_work + "/!main"}))
        base.append(ET.Element("FRBRuri", {"value": self.uri_work}))
        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {"href": author, "as": "#author"}))

        base.append(ET.Element("FRBRcountry", {"value": "rs", "refersTo": "http://dbpedia.org/page/" + country}))
        subtype = Convert.convert_string(self.meta.vrsta_propisa)
        base.append(ET.Element("FRBRsubtype",
                               {"value": subtype.lower(),
                                "refersTo": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#" \
                                            + subtype, "showAs": subtype}))
        base.append(ET.Element("FRBRnumber", {"value": self.number}))
        base.append(ET.Element("FRBRname", {"value": self.meta.act_name}))

        return base

    def frbrexpression(self, date, version, editor, lang="Serbian"):
        base = ET.Element("FRBRExpression")

        base.append(ET.Element("FRBRthis", {"value": self.uri_expression + "/!main"}))
        base.append(ET.Element("FRBRuri", {"value": self.uri_expression}))
        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {
            "href": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#Editor",
            "as": "#editor"}))
        base.append(ET.Element("FRBRlanguage",
                               {"language": "srp", "wId": "http://dbpedia.org/page/" + lang + "_language"}))
        self.expressionuri = "akn/rs/act/" + date + "/" + version + "/srp@"
        return base

    def frbrmanifestation(self, date, version, editor):
        base = ET.Element("FRBRManifestation")
        base.append(ET.Element("FRBRthis", {"value": self.uri_manifestation + "/!main"}))
        base.append(ET.Element("FRBRuri", {"value": self.uri_manifestation}))
        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {"href": "#lexpert_student_project", "as": "#editor"}))
        base.append(ET.Element("FRBRformat", {"value": "xml",
                                              "refersTo": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#xml"}))
        return base

    def publication(self, publication):
        date = fix_date(publication["date"])
        base = ET.Element("publication", {"date": date, "name": publication["journal"].lower(),
                                          "showAs": publication["journal"], "number": publication["number"]})
        return base

    """
        [{"wId": "vrsta", value: "Zakon"},
        {"wid": "oblast", ...},
        {"wid": "grupa", ...}
        ]
    """

    def clssification(self, clssifications):
        base = ET.Element("classification", {"source": SOURCE})
        self.classification = base
        for dict in clssifications:
            newk = ET.Element("keyword", {"wId": dict["id"], "value": dict["value"].lower(), "showAs": dict["value"],
                                          "href": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCTerm",
                                          "dictionary": "RS"})
            base.append(newk)
        return base

    """
        [{"wid": "usvajanje", date: "2018-12-21"},
        {"wid": "stupanje na snagu", date: "2018-12-21"},
        "wid": "primena", date: "2018-12-21"},
        ]
    """

    def workflow(self, workflows):
        base = ET.Element("workflow", {"source": SOURCE})
        for dict in workflows:
            newk = ET.Element("step", {"wId": dict["id"], "date": dict["date"],
                                       "by": "/akn/rs/srp@ontology"})  # TODO Andrija TLC Person or TLC Organization reference
            base.append(newk)
        return base

    def lifecycle(self, lifecycles):
        base = ET.Element("lifecycle", {"source": self.meta.eli})
        self.lifecycle_node = base
        link = self.meta.eli
        base.append(
            ET.Element("eventRef",
                       {"source": link,
                        "href": "#datum_usvajanja", "date": self.meta.datum_usvajanja, "type": "generation"}))
        base.append(
            ET.Element("eventRef",
                       {"source": link, "href": "#datum_pocetak_primene",
                        "date": self.meta.datum_primene, "type": "generation"}))
        base.append(
            ET.Element("eventRef",
                       {"source": link, "href": "#datum_stupanja_na_snagu",
                        "date": self.meta.datum_stupanja, "type": "generation"}))
        # for date in lifecycles:
        #     found_i = date.find("/") + 1
        # if cnt == 1:
        #     newk = ET.Element("eventRef",
        #                       {"wId": "e" + str(cnt), "refersTo": date, "date": fix_date(date[found_i:found_i + 4]),
        #                        "type": "generation", "source": SOURCE})
        # else:
        #     newk = ET.Element("eventRef",
        #                       {"wId": "e" + str(cnt), "refersTo": date, "date": fix_date(date[found_i:found_i + 4]),
        #                        "type": "amendment", "source": SOURCE})
        # base.append(newk)
        # cnt += 1

        return base

    def references(self, filename, list_of_concepts: list):
        cnt_concept = 0
        # link ="http://purl.org/vocab/frbr/core#Concept"

        base = ET.Element("references", {"source": SOURCE})

        if len(list_of_concepts) > 0:
            for concept in list_of_concepts[0]:
                concept = Convert.convert_string(concept)
                link = self.translator[concept]
                if '#' not in link:
                    link = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCConcept'
                concept_ref = ET.Element("TLCConcept",
                                         {"eId": "cocnept" + str(cnt_concept), "href": link,
                                          "showAs": concept.capitalize()})
                base.append(concept_ref)
                cnt_concept = cnt_concept + 1
        return base

    def keywords_za_marka(self, list_of_concepts: list,
                          uri="https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#TLCTerm"):
        conceptIri = uri
        base = self.classification
        if len(list_of_concepts) > 0:
            for concept in list_of_concepts[0]:
                lat_con = Convert.convert_string(concept)
                concept_ref = ET.Element("keyword",
                                         {"href": conceptIri, "showAs": lat_con.capitalize(), "value": lat_con.lower(),
                                          "dictionary": "RS"})
                base.append(concept_ref)
        return base

    def notes(self, notes1, notes2):
        base = ET.Element("notes", {"source": SOURCE})
        if notes1 != "":
            newk = ET.Element("note", {"wId": "not1"})
            p = ET.Element("p")
            p.text = notes1
            newk.append(p)
            base.append(newk)
        if notes2 != "":
            if notes1 != "":
                newk = ET.Element("note", {"wId": "not2"})
            else:
                newk = ET.Element("note", {"wId": "not1"})
            p = ET.Element("p")
            p.text = notes1
            newk.append(p)
            base.append(newk)
        return base

    def change_element_by_id(self, uri, i, value):
        temp = uri.split("/")
        temp[i] = value
        temp = "/".join(temp)
        return temp

    def change_subtype_url(self, subtype):
        if len(subtype) < 3:
            return
        subtype_id = 3
        self.uri_expression = self.change_element_by_id(self.uri_expression, subtype_id, subtype).strip()
        self.uri_work = self.change_element_by_id(self.uri_work, subtype_id, subtype).strip()
        self.uri_manifestation = self.change_element_by_id(self.uri_manifestation, subtype_id, subtype).strip()

    def make_urls(self, meta, country_code="rs", lang_code="srp", subtype=None, type_act="act", doc_type="xml"):
        # TODO try automatic
        if meta.broj_akta is None:
            number_act = "nn"
        else:
            number_act = meta.broj_akta
        if hasattr(meta, 'datum_usvajanja'):
            version = meta.datum_usvajanja[:meta.datum_usvajanja.rfind('-') + 1] + number_act
        else:
            exit("No meta info to make url, need: [datum usvajanja]")
        if subtype is None:
            try:
                subtype = Convert.convert_string(meta.vrsta_propisa).lower()
            except:
                subtype = "zakon"  # WIll be changed later anywas
        if meta.verzija_na_snagu_od is not '' and meta.verzija_na_snagu_od is not None:
            current_version = utilities.swap_date(meta.verzija_na_snagu_od)
            if current_version is None:
                current_version = fix_date(meta.datum_usvajanja)
        else:
            current_version = fix_date(meta.datum_usvajanja)
        text_s: str = meta.donosilac
        to = text_s.find("(")
        if to is not -1:
            text_s = text_s[:to]
        actor = Convert.convert_string(text_s.strip()).replace(" ", "_").lower()
        date_got = fix_date(meta.datum_usvajanja)
        self.uri_work = (
            "akn/" + country_code + "/" + type_act + "/" + subtype + "/" + actor + "/" + date_got + "/" + version).strip()
        self.uri_expression = (self.uri_work + "/" + lang_code + "@" + current_version).strip()
        self.number = version
        self.uri_manifestation = (self.uri_expression + "/!main." + doc_type).strip()

    def build(self, filename, akomaroot, skip_tfidf=False, country_code="rs", lang_code="srp", passed_meta=None):
        """
        :param filename: Name which was written in Akoma/data/meta/allmeta.csv when it was scraped
        :param akomaroot: root of new akoma ntoso document
        :param skip_tfidf: boolean if TLCconcepts should be searched for
        :param country_code: which country is this for by ISO 3166-1 standard
        :param lang_code: languge used in document by ISO_639-1 standard
        :param passed_meta: if metainfo is not read from file its should be passed here, type Metadata class from form_akoma/Metadata.py
        :return:
        """
        meta = list(akomaroot)[0].find(PREFIX + "meta")
        if meta is None:
            meta = list(akomaroot)[0].find("meta")

        metainfo = None
        # print(csv.read())
        if passed_meta is None and len(filename) > 2:
            for line in self.csv.readlines():
                values = line.strip().split("#")
                if filename == values[14]:
                    metainfo = Metadata(values)
                    break
        else:
            metainfo = passed_meta
        if metainfo is None:
            print(filename)
            print("Fajl nije pronadjen u metadata.csv")
            return
        self.meta = metainfo
        self.make_urls(metainfo, country_code, lang_code)
        try:
            _ = metainfo.work
            has_work = True
        except AttributeError:
            has_work = False
        if has_work and metainfo.work is not None:
            meta.append(self.identification({"work": metainfo.work, "manifest": metainfo.manifest,
                                             "author": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#Author",
                                             "editor": "somebody"}))
        else:
            print(filename, metainfo.act_name)
            dict = {"date": metainfo.datum_usvajanja, "version": metainfo.version}
            meta.append(self.identification({"work": dict, "manifest": dict,
                                             "author": "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#Author",
                                             "editor": "somebody"}))

        if metainfo.publication != False and metainfo.publication != None:
            meta.append(self.publication(metainfo.publication))
        else:
            pass
        # print(filename, metainfo.publication)
        # SUMA.append(0)#sluzi za brojanje koliko njih ukupno ima neuspesno parsiranu publikaciju, nista vise

        if len(metainfo.classifications) > 0:
            meta.append(self.clssification(metainfo.classifications))

        if metainfo.lifecycle is not None:
            meta.append(self.lifecycle(metainfo.lifecycle))

        if len(metainfo.workflow) > 0:
            meta.append(self.workflow(metainfo.workflow))

        if not skip_tfidf:
            list_of_concept = get_tf_idf_values_document("data/acts", filenames=filename, latin=False,
                                                         with_file_names=False)
            references = self.references(filename, list_of_concepts=list_of_concept)
            self.keywords_za_marka(list_of_concept)
            meta.append(references)

        if metainfo.napomena_izdavaca != "" or metainfo.dodatne_informacije != "":
            meta.append(self.notes(metainfo.napomena_izdavaca, metainfo.dodatne_informacije))


if __name__ == "__main__":
    akoma_root = init_akoma.init_xml("act")

    for fajl in os.listdir("../data/acts"):
        metabuilder = MetadataBuilder("../data/meta/allmeta.csv")
        metabuilder.build(fajl, akoma_root)
# print(len(SUMA))
