import re

try:
    from Akoma.tokenizer.patterns import is_vrsta_akta, eng_tags
    from Akoma.tokenizer.TokenType import TokenType
except ModuleNotFoundError:
    try:
        from tokenizer.patterns import is_vrsta_akta, eng_tags
        from tokenizer.TokenType import TokenType
    except ModuleNotFoundError:
        print("Error")
        exit()

import xml.etree.ElementTree as ET

PREFIX = "{http://docs.oasis-open.org/legaldocml/ns/akn/3.0}"
STOPWORD = "!STOP!"

def remove_double_space(string_input: str):
    return re.sub(' +', ' ', string_input)


class AkomaBuilder():

    def __init__(self, akomaroot):
        ET.register_namespace('', "http://www.akomantoso.org/2.0")
        self.akomaroot = akomaroot
        self.current = list(akomaroot)[0].find(PREFIX + "body")
        if self.current is None:
            self.current = list(akomaroot)[0].find("body")
        self.stack = [self.current]
        # print(self.result_str())
        # print(self.stack, list(akomaroot)[0].tag)

    def build_preface(self, tokens):
        counter = 0
        preamble = None
        preface = None
        name = ""
        act = list(self.akomaroot)[0]
        longTitle = ET.Element("longTitle")
        title = ET.Element("p")
        longTitle.insert(0, title)
        for token in tokens[::-1]:
            if preface is None:
                preface = ET.Element("preface")
            counter += 1
            if "напомена" in token.value.lower():
                counter -= 1
            elif counter == 1:
                title.text = token.value
            elif counter == 2:
                title.text = token.value.capitalize() + " " + remove_double_space(title.text)
                name += token.value
            elif is_vrsta_akta(token.value):
                title.text = token.value.capitalize() + " " + title.text
                name = token.value.capitalize() + " " + name
                counter -= 1
            elif counter == 3:
                authority = ET.Element("p")  # authority
                authority.text = token.value
                preface.insert(0, authority)
            elif counter > 3:
                if preamble is None:
                    preamble = ET.Element("preamble")
                p = ET.Element("p")
                p.text = token.value
                preamble.insert(0, p)
            else:
                counter -= 1
        if preface is not None:
            preface.insert(0, longTitle)
            act.insert(1, preface)
        if preamble is not None:
            to = 1
            if preface is not None:
                to = 2
            act.insert(to, preamble)
        act.set("name", name.replace("\"", "'"))

    def add_special(self, token):
        parent = self.stack[-1]
        parent.append(token)

    def add_token(self, token, identification):
        if identification == STOPWORD:
            return
        if token.special is not None:
            token.special.tail = ""
            token.special.text = ""
        # print(token.name, identification, token.value)
        if token.type == TokenType.TACKA and token.name == 'тачка':  # QUICK FIX
            token.name = eng_tags[TokenType.TACKA]
        novi = self.create_element(token, identification)
        if token.type >= TokenType.TACKA:
            no_content = True
        else:
            no_content = False

        parent = self.current_parent(identification, no_content)
        # if identification == "gla2-clan7-stav1":
            # ff = 5
            # print("token")
        # from tokenizer import patterns # TODO MAIN FUNCTION ADD TOKEN, TO FIX wrong hir adding ANDRIJA 8.xml proba
        # new_token = None
        # new_parent = None
        # for token, name in patterns.eng_tags.items():  # for name, age in dictionary.iteritems():  (for Python 2.x)
        #     if name == novi.tag:
        #         new_token = token
        #     if name == parent.tag:
        #         new_parent = token
        # if new_parent and new_token:
        #     raz = new_token - new_parent
        #if token.type - parent.type
        parent.append(novi)
        self.stack.append(novi)

    def change(self, node):
        found = node.find('content')
        if found is not None:
            found.tag = "intro"
        # print(found)

    def clean_table(self, el):
        for element in el.iter():
            if element.tag == 'td':
                p = element.find('p')
                if p is None:
                    new_el = ET.Element('p')
                    if element.text is not None:
                        new_el.text = element.text.replace("<", "&lt;").replace("\"", "").replace(">", "&gt;")
                    element.text = ""
                    element.append(new_el)
                else:
                    for p in element.iter(tag="p"):
                        if p.text is not None:
                            p.text = p.text.replace("<", "&lt;").replace("\"", "").replace(">", "&gt;")
            element.attrib = dict()
        return el

    def current_parent(self, identification, no_content=False):
        if "od2-clan13-stav1" == identification:
            print("JEJ")
        for i in range(len(self.stack) - 1, -1, -1):
            node = self.stack[i]
            # print(i, self.stack)
            if node.tag == PREFIX + "body" or node.tag == "body":
                return node

            id = node.attrib["wId"]
            check = re.search("[0-9]+(?=\.)",identification)

            if id in identification:
                if no_content:
                    self.change(node)
                    return node
                if check is not None: #TODO QUICKFIX FOR .a

                    if 'stav' in identification:
                        return node
                    else:
                        return self.stack[i-1]

                content = node.find("content")
                # print('TEXT', list(node))
                if content is not None:
                    return content
                else:
                    return node
            self.stack.pop()
        return False

    def create_element(self, token, identification):
        base = ET.Element(token.name, {"wId": identification})

        if token.type == TokenType.PODTACKA:
            base.attrib['name'] = 'subpoint'

        if token.numberstr is not None:
            num = ET.Element("num")
            num.text = token.numberstr
            base.append(num)

        content = ET.Element("content")
        if token.type <= TokenType.CLAN and token.value is not None:
            heading = ET.Element("heading")
            heading.text = token.value
            base.append(heading)
        elif token.type == TokenType.STAV and token.special is not None:
            base.tag = eng_tags[TokenType.STAV]  # TODO OVDE JE RADNJA ANDRIJA
            base.attrib['class'] = 'special'
            base.append(content)
            if token.special.tag == 'table':
                content.append(self.clean_table(token.special))
            elif token.special.tag == 'img':
                block = ET.Element('block', {'name': 'image'})
                block.append(token.special)
                content.append(block)
        elif token.value is not None:
            p = ET.Element("p")
            p.text = token.value.replace(">", "~vece;").replace("<", "~manje;").replace("\"", "~navod;").replace("&gt;", "~vece;").replace("&lt;", "~manje;").replace("\"", "~navod;")
            content.append(p)
            base.append(content)

        return base

    def result_str(self):
        import xml.dom.minidom

        dom = xml.dom.minidom.parseString(ET.tostring(self.akomaroot, encoding='UTF-8',
                                                      method="xml").decode())  # or xml.dom.minidom.parseString(xml_string)
        pretty_xml_as_string = dom.toprettyxml()

        return pretty_xml_as_string  # str(ET.tostring(self.akomaroot,encoding='UTF-8', method="xml").decode())
