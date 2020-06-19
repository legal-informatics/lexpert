import os 
from flask import Flask, request, jsonify, abort
from SPARQLWrapper import SPARQLWrapper, XML, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

from flask_cors import CORS

import xmltodict
import lxml.etree as ET
import pdfkit

import re

app = Flask(__name__)
CORS(app)

sparql_query = SPARQLWrapper('http://localhost:3030/test/query')
sparql_query.setReturnFormat(JSON)

sparql_update = SPARQLWrapper('http://localhost:3030/test/update')
sparql_update.method = 'POST'

ontology_url = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl'
rdf_type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
named_individual = 'http://www.w3.org/2002/07/owl#NamedIndividual'

def parse_xml(request):
    data = request.data.decode('utf-8')

    data = (data[data.find('<?xml version="1.0" ?>'):data.find('</akomaNtoso>')+13])

    print(data)
    
    xml_file = ET.XML(data)
    dir_path = os.path.dirname(os.path.realpath(__file__))                  # xsd validacija ***** pogledati da ne vraca te errore tolike 
    schema = ET.XMLSchema(file=dir_path + '\\static\\akomantoso30.xsd')
    try:
        schema.assertValid(xml_file)
    except ET.DocumentInvalid:
        print("Validation error(s):")
        for error in schema.error_log:
            print("  Line {}: {}".format(error.line, error.message))
        abort(400, 'XML did not pass XSD validation!!!')

    content_dict = xmltodict.parse(data)

    meta = content_dict['akomaNtoso']['act']['meta']
    identification = meta['identification']
    # publication = meta['publication']             # ne koristi se          
    classification = meta['classification']
    lifecycle = meta['lifecycle']['eventRef']

    work = identification['FRBRWork']
    expression = identification['FRBRExpression']
    manifestation = identification['FRBRManifestation']

    manifestation_uri = ontology_url + '#' + manifestation['FRBRuri']['@value']
    expression_uri = ontology_url + '#' + expression['FRBRuri']['@value']
    work_uri = ontology_url + '#' + work['FRBRuri']['@value']

    cont = data
    # .decode("utf-8")
    cont_fix = "".join(cont.splitlines()).replace("\"", "\\\"")

    path_uri = ontology_url + '#' + request.path

    if not (path_uri == work_uri or path_uri == expression_uri or path_uri == manifestation_uri):
        abort(400, 'Path uri does not match document uri!')

    if (not expression_uri.startswith(work_uri)):
        abort(400, 'Expression uri does not start with work uri!')

    if (not manifestation_uri.startswith(expression_uri)):
        abort(400, 'Manifestation uri does not start with expression uri!')    
    
    query = f'PREFIX xsd:<http://www.w3.org/2001/XMLSchema#> INSERT DATA {{'

    # Work
    query += f'''
        <{work_uri}> <{rdf_type}> <{named_individual}>.
        <{work_uri}> <{rdf_type}> <{ontology_url}#FRBRWork>.
        <{work_uri}> <{ontology_url}#has_date> "{work['FRBRdate']['@date']}"^^xsd:date.
        <{work_uri}> <{ontology_url}#has_name> "{work['FRBRname']['@value']}"^^xsd:string.
        <{work_uri}> <{ontology_url}#has_number> "{work['FRBRnumber']['@value']}"^^xsd:string.
        <{work_uri}> <{ontology_url}#is_of_type> <{ontology_url}#act>.
        <{work_uri}> <{ontology_url}#is_of_subtype> <{work['FRBRsubtype']['@refersTo']}>.
        <{work_uri}> <{ontology_url}#has_country> <{work['FRBRcountry']['@refersTo']}>.
    '''                
    # <{ontology_url}#act> paziti posto ne mora uvek biti act uzimati iz urija

    for keyword in classification['keyword']:           # ovde ce biti link ka individui te nece biti potrebe za ovim

        group_regexp = re.compile('s[0-9]{2}_g[0-9]{2}_a[0-9]{2}')
        area_regexp = re.compile('s[0-9]{2}_g[0-9]{2}')
        subregister_regexp = re.compile('s[0-9]{2}')

        if group_regexp.match(keyword['@value']) :
            # print(len(keyword['@value']), keyword['@value'], 'is group')
            query += f'''
                <{work_uri}> <{ontology_url}#has_group> <{keyword['@href']}>.
            '''
        elif area_regexp.match(keyword['@value']):
            # print(len(keyword['@value']), keyword['@value'], 'is area')
            query += f'''
                <{work_uri}> <{ontology_url}#has_area> <{keyword['@href']}>.
            '''
        elif subregister_regexp.match(keyword['@value']):
            # print(len(keyword['@value']), keyword['@value'], 'is subregister')
            query += f'''
                <{work_uri}> <{ontology_url}#has_subregister> <{keyword['@href']}>.
            '''
        else:
            print(len(keyword['@value']), keyword['@value'], 'is keyword')
            # implementirati kljucne reci
            # implementirati notes

    # Expression
    query += f'''
        <{expression_uri}> <{rdf_type}> <{named_individual}>.
        <{expression_uri}> <{rdf_type}> <{ontology_url}#FRBRExpression>.
        <{expression_uri}> <{ontology_url}#has_date> "{expression['FRBRdate']['@date']}"^^xsd:date.
        <{expression_uri}> <{ontology_url}#has_language> <{expression['FRBRlanguage']['@language']}>.
        <{work_uri}> <{ontology_url}#is_realized_through> <{expression_uri}>.
    '''
    
    # Manifestation
    query += f'''
        <{manifestation_uri}> <{rdf_type}> <{named_individual}>.
        <{manifestation_uri}> <{rdf_type}> <{ontology_url}#FRBRManifestation>.
        <{manifestation_uri}> <{ontology_url}#has_date> "{manifestation['FRBRdate']['@date']}"^^xsd:date.
        <{manifestation_uri}> <{ontology_url}#is_in_format> <{manifestation['FRBRformat']['@refersTo']}>.
        <{manifestation_uri}> <{ontology_url}#content> "{cont_fix}"^^xsd:string.
        <{expression_uri}> <{ontology_url}#is_embodied_in> <{manifestation_uri}>.
    '''

    # Event
    authors = []

    for eventRef in lifecycle:
        author_iri = f'{ontology_url}#{work["FRBRauthor"]["@as"][1:]}_{work["FRBRauthor"]["@href"][1:]}'

        if author_iri not in authors:
            # print('kreiram ' + author_iri)
            authors.append(author_iri)
            query += f'''
                <{author_iri}> <{rdf_type}> <{ontology_url}#{work["FRBRauthor"]["@as"][1:].capitalize()}>.
                <{author_iri}> <{rdf_type}> <{named_individual}>.
                <{author_iri}> <{ontology_url}#is_role_of> <{ontology_url}#{work["FRBRauthor"]["@href"][1:]}>.
            '''
        # else:
        #     print('vec postoji ' + author_iri)

        event_iri = f'{ontology_url}#event_{work["FRBRnumber"]["@value"]}_{eventRef["@href"][1:]}_{eventRef["@date"]}'

        query += f'''
            <{event_iri}> <{rdf_type}> <{named_individual}>.
            <{event_iri}> <{rdf_type}> <{ontology_url}#TLCEvent>.
            <{event_iri}> <{ontology_url}#has_responsible_role> <{author_iri}>.
            <{event_iri}> <{ontology_url}#has_date> "{eventRef["@date"]}"^^xsd:date.
            <{event_iri}> <{ontology_url}#is_of_event_type> <{ontology_url}#{eventRef["@href"][1:]}>.
            <{ontology_url}#{work['FRBRuri']['@value']}> <{ontology_url}#has_related_event> <{event_iri}>.
        '''

    query += f'}}'   

    # print(query)

    return query





# function to transform data to wanted format
def transform(data, ret_format):

    if ret_format == 'xml':
        return data, 200, {'content-type': 'application/xml'}

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dom = ET.XML(data)
    xslt = ET.parse(dir_path + '/static/akoma_to_xhtml.xsl')
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    xhtml = ET.tostring(newdom, pretty_print=True, encoding='utf-8')

    if ret_format == 'xhtml':
        return xhtml, 200, {'content-type': 'application/xhtml+xml'}

    if ret_format == 'pdf':
        conf = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
        options = {'encoding': "UTF-8"}
        data = pdfkit.from_string(xhtml.decode("utf-8"), False, options = options, configuration = conf)
        return data, 200, {'content-type': 'application/pdf'}

    return data

# function that sends queries to Apache Jena Server
def crud_operations(request, get_query, del_query, ret_format):
    if request.method == "GET":
        print('\nGET sending sparql to Jena: ', get_query, '\n')
        sparql_query.setQuery(get_query)
        
        try :
            response = sparql_query.query().convert()
            return transform(response[0]['data'], ret_format)
        except Exception as e:
            if type(e) is QueryBadFormed:
                abort(400, e)
            elif len(response) == 0:
                abort(404, 'Individual with that URI was not found')
            else:
                abort(500, e)
    
    if request.method == "DELETE":
        print('\nDELETE sending sparql to Jena: ', del_query, '\n')
        sparql_update.setQuery(del_query)
        try:
            sparql_update.query()
            return 'Deleted', 200
        except Exception as e:
            abort(500, e)

    if request.method == "PUT":
        insert_query = parse_xml(request)
        try:
            sparql_update.setQuery(del_query)
            sparql_update.query()

            sparql_update.setQuery(insert_query)
            sparql_update.query()
            return 'Individual successfully updated', 200
        except Exception as e:
            abort(400, e)

    if request.method == "POST":
        insert_query = parse_xml(request)
        sparql_update.setQuery(insert_query)
        try:
            sparql_update.query()
            return 'Individual successfully added', 200
        except Exception as e:
            abort(400, e) 


# endpoint for Manifestations   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634.xml
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>/<lng>@<exp_id>.<ret_format>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_manifestation(country, type_, subtype, autor, date, work_id, lng, exp_id, ret_format):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{autor}/{date}/{work_id}/{lng}@{exp_id}.xml'
    get_query = f'JSON {{ "data": ?data }} WHERE {{ <{uri}> <{ontology_url}#content> ?data.}}'
    del_query = f'DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. FILTER ( ?s = <{uri}> || ?o = <{uri}>) }}'
    print(get_query)
    
    return crud_operations(request, get_query, del_query, ret_format)

# endpoint for Expressions   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>/<lng>@<exp_id>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_expression(country, type_, subtype, autor, date, work_id, lng, exp_id):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{autor}/{date}/{work_id}/{lng}@{exp_id}'
    get_query = f'''JSON {{ "data": ?data}} WHERE {{ <{uri}> <{ontology_url}#is_embodied_in> ?manifestation. 
                                                    ?manifestation <{ontology_url}#has_date> ?date. 
                                                    ?manifestation <{ontology_url}#content> ?data. }} ORDER BY DESC (?date) LIMIT 1'''
    
    del_query = f'''DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. 
                                                    OPTIONAL {{ <{uri}> <{ontology_url}#has_related_event> ?event. }}
                                                    OPTIONAL {{ <{uri}> <{ontology_url}#is_embodied_in> ?manifestation. }}
                                                    FILTER ( ?s in ( <{uri}>, ?manifestation,  ?event) || ?o in ( <{uri}>, ?manifestation,  ?event) )}}'''
    
    return crud_operations(request, get_query, del_query, 'xml')

# endpoint for Work   -->   #/akn/rs/act/zakon/a001/2013-02-06/2013-104-4477
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>.<ret_format>', methods=['GET'])
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_work(country, type_, subtype, autor, date, work_id, ret_format='xml'):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{autor}/{date}/{work_id}'
    get_subquery = f'''SELECT ?expression WHERE {{ <{uri}> <{ontology_url}#is_realized_through> ?expression.
                                                    ?expression <{ontology_url}#has_date> ?date.
                                                    ?expression <{ontology_url}#has_language> <http://dbpedia.org/page/Serbian_language>. }} ORDER BY DESC (?date) LIMIT 1'''
    
    get_query = f'''JSON {{ "data": ?data }} WHERE {{ {{ {get_subquery} }}
                                                    ?expression <{ontology_url}#is_embodied_in> ?manifestation.
                                                    ?manifestation <{ontology_url}#has_date> ?date.
                                                    ?manifestation <{ontology_url}#content> ?data. }} ORDER BY DESC (?date)'''

    del_query = f'''DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o.
                                                    OPTIONAL {{ <{uri}> <{ontology_url}#has_related_event> ?work_ev. }}
                                                    OPTIONAL {{ <{uri}> <{ontology_url}#is_realized_through> ?exp. }}
                                                    OPTIONAL {{ ?exp <{ontology_url}#has_related_event> ?exp_ev. }}
                                                    OPTIONAL {{ ?exp <{ontology_url}#is_embodied_in> ?man. }}
                                                    FILTER (?s in (<{uri}>, ?work_ev, ?exp, ?exp_ev, ?man) || ?o in (<{uri}>, ?work_ev, ?exp, ?exp_ev, ?man) ) }}'''

    return crud_operations(request, get_query, del_query, ret_format)


# exposing Apche Jena Fuseki endpoint for SPARKQL queries
@app.route('/sparql', methods=['POST'])
def sparql():
    query = request.data
    if not query:
        abort(400, 'No sparql query has been pased')
    
    try :
        sparql_query.setQuery(query)
        response = sparql_query.query().convert()
        return response
    except Exception as e:
        abort(400, e)

# simple search only by document name
@app.route('/simple_search', methods=['POST'])
def simple_search():
    data = request.json

    search = ''

    if data['split'] is True:
        data = data['query'].split()
        search = '|'.join(data)
    else:
        data = data['query']
        search = data

    get_query = f'''JSON {{ "o":?o, "subtype":?subtype, "area":?area, "group":?group, "s":?s }} WHERE {{ ?s a <{ontology_url}#FRBRWork>.
                                                    ?s <{ontology_url}#has_name> ?o. FILTER regex(?o, "{search}")
                                                    ?s <{ontology_url}#is_of_subtype> ?subtype.
                                                    ?s <{ontology_url}#has_group> ?group_uri.
                                                    ?group_uri <{ontology_url}#has_name> ?group.
                                                    ?s <{ontology_url}#has_area> ?area_uri.
                                                    ?area_uri <{ontology_url}#has_name> ?area. }}'''

    try:
        sparql_query.setQuery(get_query)
        response = sparql_query.query().convert()
        return jsonify(response)
    except Exception as e:
        abort(500, e)

#advanced search by dosument atributes
@app.route('/search', methods=['POST'])
def search():
    data = request.json

    search = data['search'] if 'search' in data else '.*'
    if data['split'] is True:
        search = '|'.join(search.split())

    subtype = '<' + data['subtype'] + '>' if 'subtype' in data else '?subtype'
    subregister = '<' + data['subregister'] + '>' if 'subregister' in data else '?subregister_uri'
    area = '<' + data['area'] + '>' if 'area' in data else '?area_uri'
    group = '<' + data['group'] + '>' if 'group' in data else '?group_uri'
    date_from = data['date_from'] if 'date_from' in data else '0001-01-01'
    date_to = data['date_to'] if 'date_to' in data else '9999-12-31'

    keywords = data['keywords'].split() if 'keywords' in data else '?keywords'

    #fali za keywords
    get_query = f'''PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
                JSON {{ "o":?o, "subtype":?subtype, "area":?area, "group":?group, "exp":?exp, "lng":?lng, "date":?date }} WHERE {{ ?s a <{ontology_url}#FRBRWork>.
                                                    ?s <{ontology_url}#has_name> ?o. FILTER regex(?o, "{search}")
                                                    ?s <{ontology_url}#is_of_subtype> {subtype}.
                                                    ?s <{ontology_url}#is_of_subtype> ?subtype.
                                                    ?s <{ontology_url}#has_subregister> {subregister}.
                                                    {subregister} <{ontology_url}#has_name> ?subregister.
                                                    ?s <{ontology_url}#has_group> {group}.
                                                    {group} <{ontology_url}#has_name> ?group.
                                                    ?s <{ontology_url}#has_area> {area}.
                                                    {area} <{ontology_url}#has_name> ?area. 
                                                    ?s <{ontology_url}#is_realized_through> ?exp.
                                                    ?exp <{ontology_url}#has_language> ?lng. 
                                                    ?exp <{ontology_url}#has_date> ?date.
                                                    FILTER( "{date_from}"^^xsd:date <= ?date && "{date_to}"^^xsd:date >= ?date)
                                                    }}'''
    

    print(get_query)
    try:
        sparql_query.setQuery(get_query)
        response = sparql_query.query().convert()
        return jsonify(response)
    except Exception as e:
        abort(500, e)

    return 

