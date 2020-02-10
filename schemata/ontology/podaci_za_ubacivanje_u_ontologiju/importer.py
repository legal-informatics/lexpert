from owlready2 import *
onto = get_ontology("../akn_meta_combined.owl").load()
akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")

# ubacivanje glasila u ontologiju
with open("glasila.txt", "r", encoding="utf-8") as file:
    glasila = file.readlines()
    for g in glasila:
        g = g.strip()
        g = g.replace(' ', '_')
        onto.Glasila(g)

# ubacivanje formata dokumenata u ontologiju
with open("vrste_formata.txt", "r", encoding="utf-8") as file:
    vrste_formata = file.readlines()
    for g in vrste_formata:
        g = g.strip()
        akn_meta.FRBRformat(g)
        
# ubacivanje vrsta dokumenata u ontologiju
with open("vrste_dokumenata.txt", "r", encoding="utf-8") as file:
    vrste_dokumneata = file.readlines()
    for g in vrste_dokumneata:
        g = g.strip()
        g = g.replace(' ', '_')
        akn_meta.FRBRsubtype(g)

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
    oblast = None
    grupa = None
    for g in lines:
        if '\t\t' in g:
            grupa = onto.Grupa(g.strip().replace(' ', '_'))
            grupa.broader = [oblast]
        elif '\t' in g:
            oblast = onto.Oblast(g.strip().replace(' ', '_'))
            oblast.broader = [podregistar]
        else:
            podregistar = onto.Podregistar(g.strip().replace(' ', '_'))
        

onto.save(file = "akn_meta_combined_full.owl", format = "rdfxml")