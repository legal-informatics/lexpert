from owlready2 import *
onto = get_ontology("../akn_meta_combined.owl").load()
akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")

# ubacivanje glasila u ontologiju
counter = 1
with open("glasila.txt", "r", encoding="utf-8") as file:
    glasila = file.readlines()
    for g in glasila:
        iri = "gl_" + str(counter).zfill(3)
        idividual = onto.Glasila(iri)
        idividual.ima_ime = [g.strip()]
        counter = counter + 1


# ubacivanje formata dokumenata u ontologiju
counter = 1
with open("vrste_formata.txt", "r", encoding="utf-8") as file:
    vrste_formata = file.readlines()
    for g in vrste_formata:
        iri = "vf_" + str(counter).zfill(3)
        idividual = akn_meta.FRBRformat(iri)
        idividual.ima_ime = [g.strip()]
        counter = counter + 1

        
# ubacivanje vrsta dokumenata u ontologiju
counter = 1
with open("vrste_dokumenata.txt", "r", encoding="utf-8") as file:
    vrste_dokumneata = file.readlines()
    for g in vrste_dokumneata:
        iri = "vd_" + str(counter).zfill(3)
        idividual = akn_meta.FRBRsubtype(iri)
        idividual.ima_ime = [g.strip()]
        counter = counter + 1


# ubacivanje liste zemalja u ontologiju
with open("zemlje.txt", "r", encoding="utf-8") as file:
    zemlje = file.readlines()
    for g in zemlje:
        g = g.split('\t')
        akn_meta.FRBRcountry(g[0])


# ubacivanje liste jezika u ontologiju
with open("jezici.txt", "r", encoding="utf-8") as file:
    jezici = file.readlines()
    for g in jezici:
        g = g.split('\t')
        akn_meta.FRBRlanguage(g[0])


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
            grupa = onto.Grupa("grupa_" + str(counter_g).zfill(3))
            counter_g = counter_g + 1
            grupa.broader = [oblast]
            grupa.ima_ime = [' '.join(g.strip().split(' ')[1:])]
        elif '\t' in g:
            oblast = onto.Oblast("oblast_" + str(counter_o).zfill(3))
            counter_o = counter_o + 1
            oblast.broader = [podregistar]
            oblast.ima_ime = [' '.join(g.strip().split('\t')[1:])]
        else:
            podregistar = onto.Podregistar("podregistar_" + str(counter_p).zfill(3))
            counter_p = counter_p + 1
            podregistar.ima_ime = [g.strip()]
        
#ubacivanje skupstina u ontologiju
counter = 1
with open("skupstine.txt", "r", encoding="utf-8") as file:
    skupstine = file.readlines()
    for s in skupstine:
        iri = "sk_" + str(counter).zfill(3)
        individual = onto.Skupstine(iri)
        individual.ima_ime = [s.strip()]
        counter = counter + 1

onto.save(file = "akn_meta_combined_full.owl", format = "rdfxml")