from owlready2 import *
onto = get_ontology("../akn_meta_combined.owl").load()
akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")

# ubacivanje glasila u ontologiju
counter = 1
with open("glasila.txt", "r", encoding="utf-8") as file:
    glasila = file.readlines()
    for g in glasila:
        iri = "gazette_" + str(counter).zfill(3)
        idividual = onto.Gazette(iri)
        idividual.has_name = [g.strip()]
        counter = counter + 1


# ubacivanje formata dokumenata u ontologiju
counter = 1
with open("vrste_formata.txt", "r", encoding="utf-8") as file:
    vrste_formata = file.readlines()
    for g in vrste_formata:
        iri = "format_" + str(counter).zfill(3)
        idividual = akn_meta.FRBRformat(iri)
        idividual.has_name = [g.strip()]
        counter = counter + 1

        
# ubacivanje vrsta dokumenata u ontologiju
counter = 1
with open("vrste_dokumenata.txt", "r", encoding="utf-8") as file:
    vrste_dokumneata = file.readlines()
    for g in vrste_dokumneata:
        iri = "subtype_" + str(counter).zfill(3)
        idividual = akn_meta.FRBRsubtype(iri)
        idividual.has_name = [g.strip()]
        counter = counter + 1


# ubacivanje liste zemalja u ontologiju
with open("zemlje.txt", "r", encoding="utf-8") as file:
    zemlje = file.readlines()
    for g in zemlje:
        g = g.split('\t')
        individual = akn_meta.FRBRcountry(g[0])
        individual.label = [g[1].strip()]

# ubacivanje liste jezika u ontologiju
with open("jezici.txt", "r", encoding="utf-8") as file:
    jezici = file.readlines()
    for g in jezici:
        g = g.split('\t')
        individual = akn_meta.FRBRlanguage(g[0])
        individual.label = [g[2].strip()]

#ubacivanje skupstina u ontologiju
counter = 1
with open("skupstine.txt", "r", encoding="utf-8") as file:
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


# ubacivanje podregistara, oblasti i grupa u ontologiju
with open("podregistar_oblast_grupa.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    podregistar = None
    counter_p = 1
    oblast = None
    counter_o = 1
    grupa = None
    counter_g = 1
    for g in lines:
        if '\t\t' in g:
            grupa = onto.Group("group_" + str(counter_g).zfill(3))
            counter_g = counter_g + 1
            grupa.broader = [oblast]
            grupa.has_name = [' '.join(g.strip().split(' ')[1:])]
        elif '\t' in g:
            oblast = onto.Field("field_" + str(counter_o).zfill(3))
            counter_o = counter_o + 1
            oblast.broader = [podregistar]
            oblast.has_name = [' '.join(g.strip().split('\t')[1:])]
        else:
            podregistar = onto.Subregister("subregister_" + str(counter_p).zfill(3))
            counter_p = counter_p + 1
            podregistar.has_name = [g.strip()]

with open("event_type.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    counter = 1
    for e in lines:
        eventType = onto.EventType("eventtype_" + str(counter).zfill(3))
        counter = counter + 1
        eventType.has_name = [e.strip()]

with open("osobe.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    counter = 1
    for o in lines:
        person = akn_meta.TLCPerson("person_" + str(counter).zfill(3))
        counter = counter + 1
        person.has_name = [o.strip()]

with open("organizacije.txt", "r", encoding="utf-8") as file:
    lines = file.readlines()
    counter = 1
    for o in lines:
        organization = akn_meta.TLCOrganization("organization_" + str(counter).zfill(3))
        counter = counter + 1
        organization.has_name = [o.strip()]
        
# with open("role_type.txt", "r", encoding="utf-8") as file:
#     lines = file.readlines()
#     counter = 1
#     for r in lines:
#         roleType = onto.RoleType("rt_" + str(counter).zfill(3))
#         counter = counter + 1
#         roleType.has_name = [r.strip()]

onto.save(file = "akn_meta_combined_full.owl", format = "rdfxml")