from owlready2 import *
onto = get_ontology("../akn_meta_combined.owl").load()
akn_meta = get_namespace("https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl")
uri = "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl#"

# ubacivanje glasila u ontologiju
counter = 1
with open("glasila.txt", "r", encoding="utf-8") as file:
    kljuc = open("../kljuc/glasila.txt", "w", encoding="utf-8")
    glasila = file.readlines()
    for g in glasila:
        iri = "gazette_" + str(counter).zfill(3)
        idividual = onto.Gazette(iri)
        idividual.has_name = [g.strip()]
        counter = counter + 1
        kljuc.write(g.strip() + ',' + uri + iri + '\n')
    kljuc.close()


# ubacivanje formata dokumenata u ontologiju
counter = 1
with open("vrste_formata.txt", "r", encoding="utf-8") as file:
    vrste_formata = file.readlines()
    for g in vrste_formata:
        akn_meta.FRBRformat(g.strip())
        counter = counter + 1

        
# ubacivanje vrsta dokumenata u ontologiju
counter = 1
with open("vrste_dokumenata.txt", "r", encoding="utf-8") as file:
    vrste_dokumneata = file.readlines()
    kljuc = open("../kljuc/podtipovi_dokumenata.txt", "w", encoding="utf-8")
    for g in vrste_dokumneata:
        iri = g.strip()
        idividual = akn_meta.FRBRsubtype(iri)
        #idividual.has_name = [g.strip()]
        counter = counter + 1
        # print(g.strip() + ',' + uri + g.strip())
        kljuc.write(g.strip() + ',' + uri + g.strip() + '\n')
    kljuc.close()

# ubacivanje liste zemalja u ontologiju
# with open("zemlje.txt", "r", encoding="utf-8") as file:
#     zemlje = file.readlines()
#     for g in zemlje:
#         g = g.split('\t')
#         individual = akn_meta.FRBRcountry(g[0])
#         individual.label = [g[1].strip()]

# ubacivanje liste jezika u ontologiju
# with open("jezici.txt", "r", encoding="utf-8") as file:
#     jezici = file.readlines()
#     for g in jezici:
#         g = g.split('\t')
#         individual = akn_meta.FRBRlanguage(g[0])
#         individual.label = [g[2].strip()]

#ubacivanje skupstina u ontologiju
counter = 1
with open("skupstine.txt", "r", encoding="utf-8") as file:
    kljuc = open("../kljuc/skupstine.txt", "w", encoding="utf-8")

    lines = file.readlines()
    first = None
    second = None
    for s in lines:
        tabs_temp = len(s) - len(s.lstrip(' '))
        if first is None:
            iri = "assembly_" + str(counter).zfill(3)
            first = individual = onto.Assembly(iri)
            individual.has_name = [s.strip()]
            counter = counter + 1

        else:
            if tabs_temp == 4:
                iri = "assembly_" + str(counter).zfill(3)
                second = individual = onto.Assembly(iri)
                individual.has_name = [s.strip()]
                individual.has_superior = [first]
                counter = counter + 1

            elif tabs_temp == 8:
                iri = "assembly_" + str(counter).zfill(3)
                individual = onto.Assembly(iri)
                individual.has_name = [s.strip()]
                individual.has_superior = [second]
                counter = counter + 1

        # print(s.strip() + ',' + iri)
        kljuc.write(s.strip() + ',' + uri + iri + '\n')
    kljuc.close()


# ubacivanje podregistara, oblasti i grupa u ontologiju
with open("podregistar_oblast_grupa.txt", "r", encoding="utf-8") as file:
    kljuc1 = open("../kljuc/podregistri.txt", "w", encoding="utf-8")
    kljuc2 = open("../kljuc/grupe.txt", "w", encoding="utf-8")
    kljuc3 = open("../kljuc/oblasti.txt", "w", encoding="utf-8")

    lines = file.readlines()
    podregistar = None
    counter_p = 1
    oblast = None
    counter_o = 1
    grupa = None
    counter_g = 1
    for g in lines:
        if '\t\t' in g:
            # grupa = onto.Group("s" + str(counter_p-1).zfill(2) + "_g" + str(counter_g).zfill(2))
            # counter_g = counter_g + 1
            # grupa.broader = [oblast]
            # grupa.has_name = [' '.join(g.strip().split(' ')[1:])]

            iri = "s" + str(counter_p - 1).zfill(2) + "_g" + str(counter_g - 1).zfill(2) + "_a" + str(counter_o).zfill(2)
            oblast = onto.Area(iri)
            counter_o = counter_o + 1
            oblast.broader = [grupa]
            # print(g.strip())
            oblast.has_name = [' '.join(g.strip().split(' ')[1:])]
            kljuc3.write(' '.join(g.strip().split(' ')[1:]) + ',' + uri + iri + '\n')
        elif '\t' in g:
            # oblast = onto.Area("s" + str(counter_p-1).zfill(2) + "_g" + str(counter_g-1).zfill(2) + "_a" + str(counter_o).zfill(2))
            # counter_o = counter_o + 1
            # oblast.broader = [podregistar]
            # oblast.has_name = [' '.join(g.strip().split('\t')[1:])]

            iri = "s" + str(counter_p - 1).zfill(2) + "_g" + str(counter_g).zfill(2)
            grupa = onto.Group(iri)
            counter_g = counter_g + 1
            counter_o = 1
            grupa.broader = [podregistar]
            # print(g.strip())
            grupa.has_name = [' '.join(g.strip().split('\t')[1:])]
            kljuc2.write(' '.join(g.strip().split('\t')[1:]) + ',' + uri + iri + '\n')
        else:
            iri = "s" + str(counter_p).zfill(2)
            podregistar = onto.Subregister(iri)
            counter_p = counter_p + 1
            counter_g = 1
            counter_o = 1
            podregistar.has_name = [g.strip()]
            kljuc1.write(g.strip() + ',' + uri + iri + '\n')
    kljuc1.close()
    kljuc2.close()
    kljuc3.close()

with open("event_type.txt", "r", encoding="utf-8") as file:
    kljuc = open("../kljuc/tipovi_dogadjaja.txt", "w", encoding="utf-8")
    lines = file.readlines()
    counter = 1
    for e in lines:
        iri = "eventtype_" + str(counter).zfill(3)
        eventType = onto.EventType(iri)
        counter = counter + 1
        eventType.has_name = [e.strip()]
        kljuc.write(e.strip() + ',' + uri + iri + '\n')
    kljuc.close()

with open("osobe.txt", "r", encoding="utf-8") as file:
    kljuc = open("../kljuc/osobe.txt", "w", encoding="utf-8")
    lines = file.readlines()
    counter = 1
    for o in lines:
        iri = "person_" + str(counter).zfill(3)
        person = akn_meta.TLCPerson(iri)
        counter = counter + 1
        person.has_name = [o.strip()]
        kljuc.write(o.strip() + ',' + uri + iri + '\n')
    kljuc.close()

with open("organizacije.txt", "r", encoding="utf-8") as file:
    kljuc = open("../kljuc/organizacije.txt", "w", encoding="utf-8")
    lines = file.readlines()
    counter = 1
    for o in lines:
        iri = "organization_" + str(counter).zfill(3)
        organization = akn_meta.TLCOrganization(iri)
        counter = counter + 1
        organization.has_name = [o.strip()]
        kljuc.write(o.strip() + ',' + uri + iri + '\n')
    kljuc.close()

with open("tipovi_dokumenata.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    counter = 1
    for t in lines:
        onto.FRBRtype(t.strip())
        counter = counter + 1

        
# with open("role_type.txt", "r", encoding="utf-8") as file:
#     lines = file.readlines()
#     counter = 1
#     for r in lines:
#         roleType = onto.RoleType("rt_" + str(counter).zfill(3))
#         counter = counter + 1
#         roleType.has_name = [r.strip()]

onto.save(file ="../akn_meta_combined_full.owl", format ="rdfxml")