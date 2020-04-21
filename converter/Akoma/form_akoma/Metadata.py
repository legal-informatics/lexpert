import re

class Metadata():
    """
        0 Назив прописа
        1 ELI
        2 Напомена издавача
        3 Додатне информације
        4 Врста прописа
        5 Доносилац
        6 Област
        7 Група
        8 Датум усвајања
        9 Гласило и датум објављивања
        10 Датум ступања на снагу основног текста
        11 Датум примене
        12 Правни претходник
        13 Издавач
        14 filename
    """
    def __init__(self, list):
        self.act_name = list[0]
        self.eli = list[1]
        self.napomena_izdavaca = list[2]
        self.dodatne_informacije = list[3]
        self.vrsta_propisa = list[4]
        self.donosilac = list[5]
        self.oblast = list[6]
        self.grupa = list[7]
        self.datum_usvajanja = self.convert_date(list[8]) #datum
        self.glasilo_i_datum = list[9]
        self.datum_stupanja = self.convert_date(list[10]) #datum
        self.datum_primene = self.convert_date(list[11]) #datum
        self.pravni_prethodnik = list[12]
        self.izdavac = list[13]
        self.filename = list[14]
        try:
            self.publication = self.parse_publication(list[9])
        except:
            print("Metadata.py ,Greska u parsiranju publikacije:", list[9])
            self.publication = False
        self.workflow = self.parse_workflow(self.datum_usvajanja, self.datum_stupanja, self.datum_primene)
        self.classifications = self.parse_classifications(list[4], list[6], list[7])
        self.version = "1"
        self.lifecycle = self.parse_lifecycle(list[0])

    def convert_date(self, date):
        unknown = "0001-01-01"
        if date is None:
            return unknown
        if date == "":
            return unknown
        if date == unknown:
            return unknown
        els = date.split(".")
        if len(els) == 1:
            els = date.split("-")
        if len(els[0]) == 4:
            return date
        return els[2]+"-"+els[1]+"-"+els[0]

    def parse_lifecycle(self, title):
        list1 = title.split(":")
        if len(list1) < 2:
            return None
        else:
            izdanja = list1[1].split(",")
            self.version = str(len(izdanja))
            retval = []
            for i in range(0, len(izdanja)):
                stringo = izdanja[i].strip()
                m = re.search("([0-9]+)/([0-9]+)-([0-9]+)", stringo)
                if m:
                    retval.append(m.group(0).strip())
            if len(retval)>0:
                m = re.match("([0-9]+)\/([0-9]+)\-([0-9]+)", retval[0])
                self.work = {"date": m.group(2), "version": m.group(1)+"-"+m.group(3)}
                m = re.match("([0-9]+)\/([0-9]+)\-([0-9]+)", retval[-1])
                self.manifest = {"date": m.group(2), "version": m.group(1) + "-" + m.group(3)}
            else:
                self.work = None
                self.manifest = None
                print(izdanja)
            return retval



    def parse_workflow(self, usvajanje, stupanje, primena):
        retval = []

        if usvajanje != "":
            retval.append({"id": "usvajanje", "date":  self.convert_date(usvajanje)})
        if usvajanje != "":
            retval.append({"id": "stupanje_na_snagu", "date":  self.convert_date(stupanje)})
        if usvajanje != "":
            retval.append({"id": "primena", "date":  self.convert_date(primena)})
        return retval

    def parse_classifications(self, vrsta, oblast, grupa):
        retval = []
        if vrsta != "":
            retval.append({"id": "vrsta", "value": vrsta})
        if oblast != "":
            retval.append({"id": "oblast", "value": oblast})
        if grupa != "":
            retval.append({"id": "grupa", "value": grupa})
        return retval

    def parse_publication(self, string):
        if string == "":
            return None
        if ',' in string:
            lis = string.strip().split(",")
            journal, numdate = lis[0], lis[1]
            els = numdate.strip().split(" ")
        else:
            journal, numdate = string.strip().split("број")
            els1 = numdate.strip().split(" ")
            els = ["број"]
            els.extend(els1)

        retval = {}
        journal = journal.strip()
        if journal[0] == u'„' or journal[0] ==u'”':
            journal = journal[1:]
        if journal[-1] == u'„' or journal[-1] ==u'”':
            journal = journal[:-1]
        retval["journal"] = journal
        retval["number"] = els[1]

        if len(els)<5: #ako je datum formata 21.12.1995
            retval["date"] = self.convert_date(els[-1])
            return retval


        # inace ako je datum formata 21. decembra 1995.
        day = els[3]
        month = els[4].strip()
        year = els[5]

        if day[-1] == ".":
            day = day[:-1]
        if year[-1] == ".":
            year = year[:-1]
        #kod "октобра" i "децембра" je u par propisa rec napisana sa latinicnim slovom a, zbog nekog razloga... Broj ovakvih je zanemarljivo mali
        #npr: oктобра, децембрa XD
        meseci = ["јануара", "фебруара", "марта", "априла", "маја", "јуна", "јула", "августа", "септембра", "октобра", "новембра", "децембра"]
        found = False
        for i in range(0, len(meseci)):
            if month.lower() == meseci[i] or meseci[i].startswith(month.lower()):
                month = str(i+1)
                found = True
                break
        if not found:
            print("Greska, mesec datuma objave glasnika nije ispravno napisan:", month)
            return False
        retval["date"] = year+"-"+month+"-"+day
        return retval
