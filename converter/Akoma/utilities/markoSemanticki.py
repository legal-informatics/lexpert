import re

from convertToLatin import Convert
from tokenizer import patterns
from form_akoma.Metadata import Metadata
import os
from utilities import utilities


class MarkovaIngenioznost:
    possible_names = []
    load_data = {}

    def __init__(self):
        self.path = utilities.get_root_dir() + "/data/kljuc"
        self.list_files = os.listdir(self.path)
        for one_file in self.list_files:
            # f = open(self.path + "/" + one_file, mode="r")
            name = one_file.split(".")[0]
            self.possible_names.append(name)
            self.load_data[name] = {}
            with open(self.path + "/" + one_file, mode="r", encoding="utf-8") as f:
                for line in f:
                    http_split = line.split("http")
                    first_part = http_split[0].strip()
                    uri_link = "http" + http_split[1].strip()
                    self.load_data[name][str(first_part)] = str(uri_link)

    def __getitem__(self, item):
        for elem_dict in self.possible_names:
            curr_dict = self.load_data[elem_dict]
            for key in curr_dict:
                items = [i[:-1] for i in item.split(" ")]
                for char_item in items:
                    if char_item.lower() in key.lower():
                        return curr_dict[key]
        return "https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl"


if __name__ == "__main__":
    ovaj = MarkovaIngenioznost()
    print("Geniuznost")
    nesto = ovaj["Србија"]
    print("Geniuznost")
