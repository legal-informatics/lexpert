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
    except ModuleNotFoundError:
        print("Error")
        exit(-1)
import os

PREFIX = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
SOURCE = "#somebody"  # "#pravno-informacioni-sistem"
ADDED_DATE = "-01-01"


def valid_date(date,reduce=0):
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
    ret = str(yy)+"-"+str(mm)+"-"+str(dd)
    return fix_date(ret, False)


def fix_date(before,use_extra=True):
    a = before.split("-")
    if len(a) == 1:
        return before.replace(".","") + ADDED_DATE;
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
    Назив прописа  # ELI#Напомена издавача#Додатне информације#Врста прописа#Доносилац#Област#Група#Датум усвајања#Гласило и датум објављивања#Датум ступања на снагу основног текста#Датум примене#Правни претходник#Издавач#filename
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
        self.csv = io.open(csv_file, mode="r", encoding="utf-8")
        self.expressionuri = ""

    def identification(self, metadata):
        base = ET.Element("identification", {"source": SOURCE})
        base.append(self.frbrwork(metadata["work"]["date"], metadata["work"]["version"], metadata["author"]))
        base.append(
            self.frbrexpression(metadata["manifest"]["date"], metadata["manifest"]["version"], metadata["editor"]))
        base.append(
            self.frbrmanifestation(metadata["manifest"]["date"], metadata["manifest"]["version"], metadata["editor"]))
        return base

    def frbrwork(self, date, version, author):
        base = ET.Element("FRBRWork")
        base.append(ET.Element("FRBRthis", {"value": "akn/rs/act/" + date + "/" + version + "/main"}))
        base.append(ET.Element("FRBRuri", {"value": "akn/rs/act/" + date + "/" + version}))
        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {"href": "#" + author, "as": "#author"}))
        base.append(ET.Element("FRBRcountry", {"value": "rs"}))
        return base

    def frbrexpression(self, date, version, editor):
        base = ET.Element("FRBRExpression")

        base.append(ET.Element("FRBRthis", {"value": "akn/rs/act/" + date + "/" + version + "/srp@/main"}))
        base.append(ET.Element("FRBRuri", {"value": "akn/rs/act/" + date + "/" + version + "/srp@"}))
        self.expressionuri = "akn/rs/act/" + date + "/" + version + "/srp@"
        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {"href": "#" + editor, "as": "#editor"}))
        base.append(ET.Element("FRBRlanguage", {"language": "srp"}))

        return base

    def frbrmanifestation(self, date, version, editor):
        base = ET.Element("FRBRManifestation")

        base.append(ET.Element("FRBRthis", {"value": "akn/rs/act/" + date + "/" + version + "/srp@/main.xml"}))
        base.append(ET.Element("FRBRuri", {"value": "akn/rs/act/" + date + "/" + version + "/srp@.akn"}))

        base.append(ET.Element("FRBRdate", {"date": fix_date(date), "name": "Generation"}))
        base.append(ET.Element("FRBRauthor", {"href": "#" + editor, "as": "#editor"}))
        base.append(ET.Element("FRBRformat", {"value": "xml"}))

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
        for dict in clssifications:
            newk = ET.Element("keyword", {"wId": dict["id"], "value": dict["value"].lower(), "showAs": dict["value"],
                                          "dictionary": "/akn/rs/srp@ontology"})  # TODO Andrija Popraviti dictionary
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
        base = ET.Element("lifecycle", {"source": SOURCE})
        cnt = 1
        for date in lifecycles:
            found_i = date.find("/") + 1
            if cnt == 1:
                newk = ET.Element("eventRef",
                                  {"wId": "e" + str(cnt), "refersTo": date, "date": fix_date(date[found_i:found_i + 4]),
                                   "type": "generation", "source": SOURCE})
            else:
                newk = ET.Element("eventRef",
                                  {"wId": "e" + str(cnt), "refersTo": date, "date": fix_date(date[found_i:found_i + 4]),
                                   "type": "amendment", "source": SOURCE})
            base.append(newk)
            cnt += 1
        return base

    def references(self, filename):
        cnt_concept = 0
        conceptIri = "http://purl.org/vocab/frbr/core#Concept"
        base = ET.Element("references", {"source": SOURCE})
        list_of_concept = get_tf_idf_values_document("data/acts", filenames=filename, latin=False,
                                                     with_file_names=False)
        if len(list_of_concept) > 0:
            for concept in list_of_concept[0]:
                concept_ref = ET.Element("TLCConcept",
                                         {"eId": "cocnept" + str(cnt_concept), "href": conceptIri, "showAs": concept})
                base.append(concept_ref)
                cnt_concept = cnt_concept + 1
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

    # SUMA = []
    def build(self, filename, akomaroot, skip_tfidf=False):
        meta = list(akomaroot)[0].find(PREFIX + "meta")
        if meta is None:
            meta = list(akomaroot)[0].find("meta")

        metainfo = None
        # print(csv.read())
        for line in self.csv.readlines():
            values = line.strip().split("#")
            if filename == values[14]:
                metainfo = Metadata(values)
                break
        if metainfo is None:
            print(filename)
            print("Fajl nije pronadjen u metadata.csv")
            return
        try:
            _ = metainfo.work
            has_work = True
        except AttributeError:
            has_work = False
        if has_work and metainfo.work is not None:
            meta.append(self.identification({"work": metainfo.work, "manifest": metainfo.manifest,
                                             "author": "somebody", "editor": "somebody"}))
        else:
            print(filename, metainfo.act_name)
            dict = {"date": metainfo.datum_usvajanja, "version": metainfo.version}
            meta.append(self.identification({"work": dict, "manifest": dict,
                                             "author": "somebody", "editor": "somebody"}))

        if metainfo.publication != False and metainfo.publication != None:
            meta.append(self.publication(metainfo.publication))
        else:
            pass
        # print(filename, metainfo.publication)
        # SUMA.append(0)#sluzi za brojanje koliko njih ukupno ima neuspesno parsiranu publikaciju, nista vise

        if len(metainfo.classifications) > 0:
            meta.append(self.clssification(metainfo.classifications))

        if metainfo.lifecycle is not None and len(metainfo.lifecycle) > 1:
            meta.append(self.lifecycle(metainfo.lifecycle))

        if len(metainfo.workflow) > 0:
            meta.append(self.workflow(metainfo.workflow))

        if not skip_tfidf:
            references = self.references(filename)
            meta.append(references)

        if metainfo.napomena_izdavaca != "" or metainfo.dodatne_informacije != "":
            meta.append(self.notes(metainfo.napomena_izdavaca, metainfo.dodatne_informacije))


if __name__ == "__main__":
    akoma_root = init_akoma.init_xml("act")

    for fajl in os.listdir("../data/acts"):
        metabuilder = MetadataBuilder("../data/meta/allmeta.csv")
        metabuilder.build(fajl, akoma_root)
# print(len(SUMA))
