from owlready2 import *
from os import path
try:
    from Akoma.utilities.utilities import get_root_dir
except ModuleNotFoundError:
    try:
        from utilities.utilities import get_root_dir
    except ModuleNotFoundError:
        print("Error in modules")
        exit(-1)
cls_legal_resource = "LegalResource"
cls_legal_resource_sub = "LegalResourceSubdivision"
p_is_about = "is_about"


pather = path.dirname(__file__)
onto_path = get_root_dir() + "\\semanticki\\"


onto = get_ontology(onto_path + "eli.rdf")
onto.load()
skos = onto.get_namespace("http://www.w3.org/2004/02/skos/core")
concept_class = [s for s in onto.Language.ancestors() if s.name == "Concept"][0]


def save():
    onto.save("output.rdf")


def add_instance(class_name, instance_name):
    return eval("onto.{0}('{1}')".format(class_name, instance_name))


def add_concept(name):
    new_concept = eval("skos.{0}('{1}') ".format("Concept", name))
    new_concept.is_a.append(concept_class)
    return new_concept


def add_legal_resource(name):
    return add_instance(cls_legal_resource, name)


def add_legal_sub(name):
    return add_instance(cls_legal_resource_sub, name)

