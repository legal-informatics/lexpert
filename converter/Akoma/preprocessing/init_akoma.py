import xml.etree.ElementTree as ET
import re

"""
    Used to fix parts of a html file that are unreadable to ElementTree; if needed.
"""


def trash(stringo):
    # tree = ET.parse('../aktovi/1.html')
    # print(stringo)
    stringo = close_html_token("meta", stringo)
    stringo = close_html_token("link", stringo)
    stringo = close_html_token("img", stringo)
    stringo = close_html_token_exact("col", stringo)
    stringo = add_fake_root_node(stringo)
    # print(stringo)
    root = ET.fromstring(stringo)

    # for child in root:
    #   print(child.tag, child.attrib)


def close_html_token(token, stringo):
    m = re.search('(<' + token + ')(.*?)(>)', stringo)
    if m:
        return stringo[:m.end()] + u"</" + token + ">" + stringo[m.end():]
    return stringo


def close_html_token_exact(token, stringo):
    m = re.search('(<' + token + '>)', stringo)
    if m:
        return stringo[:m.end()] + u"</" + token + ">" + stringo[m.end():]
    return stringo


def add_fake_root_node(stringo):
    return u"<article>" + stringo + u"</article>"


def init_xml(type):
    akoma = ET.Element("akomaNtoso", {"xmlns": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0",
                                     "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                                     "xsi:schemaLocation": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0 ../../schema/akoma30.xsd"})
    typeNode = ET.Element(type)
    akoma.insert(0,typeNode)
    typeNode.insert(0,ET.Element("body"))
    typeNode.insert(0,ET.Element("meta"))
    #ET.register_namespace('', "http://docs.oasis-open.org/legaldocml/ns/akn/3.0")
    return akoma
