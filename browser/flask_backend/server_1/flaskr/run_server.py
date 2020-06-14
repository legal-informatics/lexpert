import os 
from flask import Flask, request, jsonify, abort
from SPARQLWrapper import SPARQLWrapper, XML, JSON
from SPARQLWrapper.SPARQLExceptions import QueryBadFormed

import xmltodict
import lxml.etree as ET
import pdfkit

import uuid

app = Flask(__name__)

sparql_query = SPARQLWrapper('http://localhost:3030/test/query')
sparql_query.setReturnFormat(JSON)

sparql_update = SPARQLWrapper('http://localhost:3030/test/update')
sparql_update.method = 'POST'

ontology_url = 'https://github.com/legal-informatics/lexpert/blob/master/browser/ontology.owl'
rdf_type = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
named_individual = 'http://www.w3.org/2002/07/owl#NamedIndividual'


def event(document):
    """kreiranje dogadjaja za prosledjeni document (work ili expression)"""

    query = ''

    # Proverava da li u sparql bazi postoji trazena uloga
    role = document['FRBRauthor']['@as'][1:]
    ask_query = f'''
        SELECT ?s {{
            ?s <{ontology_url}#is_role_of> <{ontology_url}{document['FRBRauthor']['@href']}>.
            ?s <{rdf_type}> <{ontology_url}#{role.capitalize()}>.
        }}
    '''

    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()

        author_iri = ''

        if len(response['results']['bindings']) == 0:
            author_iri = f'{ontology_url}#{role}-{str(uuid.uuid1()).split("-")[0]}'

            query += f'''
                <{author_iri}> <{rdf_type}> <{ontology_url}#{role.capitalize()}>.
                <{author_iri}> <{rdf_type}> <{named_individual}>.
                <{author_iri}> <{ontology_url}#is_role_of> <{ontology_url}{document['FRBRauthor']['@href']}>.
            '''
        else:
            author_iri = response['results']['bindings'][0]['s']['value']

        event_iri = f'{ontology_url}#event-{str(uuid.uuid1()).split("-")[0]}'

        event_type = ''
        if (role == 'author'):
            event_type = 'eventtype_001'
        elif (role == 'editor'):
            event_type = 'eventtype_003'
        else:
            abort(400, 'Event is applicable to FRBRWork and FRBRExpression')

        query += f'''
            <{event_iri}> <{rdf_type}> <{named_individual}>.
            <{event_iri}> <{rdf_type}> <{ontology_url}#TLCEvent>.
            <{event_iri}> <{ontology_url}#has_responsible_role> <{author_iri}>.
            <{event_iri}> <{ontology_url}#has_date> "{document['FRBRdate']['@date']}"^^xsd:date.
            <{event_iri}> <{ontology_url}#is_of_event_type> <{ontology_url}#{event_type}>.
            <{ontology_url}#{document['FRBRuri']['@value']}> <{ontology_url}#has_related_event> <{event_iri}>.
            '''
    except Exception as e:
        abort(400, e)

    return query

def parse_xml(request):
    data = request.data

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
    publication = meta['publication']             # ne koristi se          
    classification = meta['classification']
    work = identification['FRBRWork']
    expression = identification['FRBRExpression']
    manifestation = identification['FRBRManifestation']

    manifestation_uri = ontology_url + '#' + manifestation['FRBRuri']['@value']
    expression_uri = ontology_url + '#' + expression['FRBRuri']['@value']
    work_uri = ontology_url + '#' + work['FRBRuri']['@value']

    cont = data.decode("utf-8")
    cont_fix = "".join(cont.splitlines()).replace("\"", "\\\"")

    path_uri = ontology_url + '#' + request.path
    print(path_uri, '\n' + manifestation_uri, '\n' +  work_uri, '\n' + expression_uri)

    # # ne dozvoljava dodavanje dokumenta ukoliko se path uri razlikuje od manifestation uri-ja u dokumentu
    # if (path_uri != manifestation_uri):
    #     abort(400, 'Path uri does not match document uri!')
    # # ne dozvoljava dodavanje dokumenta ukoliko expression uri ne pocinje work uri-jem
    # if (not expression_uri.startswith(work_uri)):
    #     abort(400, 'Expression uri does not start with work uri!')
    # # ne dozvoljava dodavanje dokumenta ukoliko manifestation uri ne pocinje expression uri-jem
    # if (not manifestation_uri.startswith(expression_uri)):
    #     abort(400, 'Manifestation uri does not start with expression uri!')

    # ne dozvoljava se dodavanje dokumenta ukoliko u bazi vec postoji dokument sa istim urijem
    # if request.method == 'POST':
    #     ask_query = f'''
    #         ASK {{
    #             <{manifestation_uri}> <{rdf_type}> <{ontology_url}#FRBRManifestation>
    #         }}
    #     '''

    #     sparql_query.setQuery(ask_query)

    #     try:
    #         response = sparql_query.query().convert()

    #         if response['boolean']:
    #             abort(400, 'Document with same IRI already exists!')
    #     except Exception as e:
    #         abort(400, e)

    query = f'PREFIX xsd:<http://www.w3.org/2001/XMLSchema#> INSERT DATA {{'

    # proverava postoji li vec u bazi work uri iz dokumenta, kako bi se sprecilo dupliranje podataka
    # pre svega dogadjaja ciji se nazivi dobijaju na osnovu trenutnog vremena
    ask_query = f'SELECT ?s {{ <{work_uri}> <{rdf_type}> <{ontology_url}#FRBRWork>. }}'
    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()
        author_iri = ''

        if len(response['results']['bindings']) == 0:
            query += f'''
                <{work_uri}> <{rdf_type}> <{named_individual}>.
                <{work_uri}> <{rdf_type}> <{ontology_url}#FRBRWork>.
                <{work_uri}> <{ontology_url}#has_date> "{work['FRBRdate']['@date']}"^^xsd:date.
                <{work_uri}> <{ontology_url}#has_name> "{work['FRBRname']['@value']}"^^xsd:string.
                <{work_uri}> <{ontology_url}#has_number> "{work['FRBRnumber']['@value']}"^^xsd:string.
                <{work_uri}> <{ontology_url}#is_of_type> <{ontology_url}#act>.
                <{work_uri}> <{ontology_url}#is_of_subtype> <{ontology_url}#{work['FRBRsubtype']['@value']}>.
                <{work_uri}> <{ontology_url}#has_country> <{ontology_url}#{work['FRBRcountry']['@value']}>.
            '''                 # <{ontology_url}#act> paziti posto ne mora uvek biti act uzimati iz urija

            for keyword in classification['keyword']:           # ovde ce biti link ka individui te nece biti potrebe za ovim
                if 'subregister' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{ontology_url}#has_subregister> <{ontology_url}#{keyword['@value']}>.
                    '''
                elif 'group' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{ontology_url}#has_group> <{ontology_url}#{keyword['@value']}>.
                    '''
                if 'area' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{ontology_url}#has_area> <{ontology_url}#{keyword['@value']}>.
                    '''
            query += event(work)
    except Exception as e:
        abort(400, e)

    # proverava postoji li vec u bazi expression uri iz dokumenta, kako bi se sprecilo dupliranje podataka
    # pre svega dogadjaja ciji se nazivi dobijaju na osnovu trenutnog vremena
    ask_query = f'''
        SELECT ?s {{
            <{expression_uri}> <{rdf_type}> <{ontology_url}#FRBRExpression>.
        }}
    '''

    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()

        author_iri = ''

        if len(response['results']['bindings']) == 0:
            query += f'''
                        <{expression_uri}> <{rdf_type}> <{named_individual}>.
                        <{expression_uri}> <{rdf_type}> <{ontology_url}#FRBRExpression>.
                        <{expression_uri}> <{ontology_url}#has_date> "{expression['FRBRdate']['@date']}"^^xsd:date.
                        <{expression_uri}> <{ontology_url}#has_language> <{ontology_url}#{expression['FRBRlanguage']['@language']}>.
                        <{work_uri}> <{ontology_url}#is_realized_through> <{expression_uri}>.
                    '''
            query += event(expression)
    except Exception as e:
        abort(400, e)

    query += f'''
        <{manifestation_uri}> <{rdf_type}> <{named_individual}>.
        <{manifestation_uri}> <{rdf_type}> <{ontology_url}#FRBRManifestation>.
        <{manifestation_uri}> <{ontology_url}#has_date> "{manifestation['FRBRdate']['@date']}"^^xsd:date.
        <{manifestation_uri}> <{ontology_url}#is_in_format> <{ontology_url}#{manifestation['FRBRformat']['@value']}>.
        <{manifestation_uri}> <{ontology_url}#content> "{cont_fix}"^^xsd:string.
        <{expression_uri}> <{ontology_url}#is_embodied_in> <{manifestation_uri}>.
    '''

    query += f'}}'
    print(query)

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
        print('\nsending sparql to Jena: ', get_query)
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
        print('\nsending sparql to Jena: ', del_query)
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


# endpoint for Manifestations   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634/xml
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>/<lng>@<exp_id>/<ret_format>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_manifestation(country, type_, subtype, autor, date, work_id, lng, exp_id, ret_format):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{autor}/{date}/{work_id}/{lng}@{exp_id}/{ret_format}'
    get_query = f'JSON {{ "data": ?data }} WHERE {{ <{uri}> <{ontology_url}#content> ?data.}}'
    del_query = f'DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. FILTER ( ?s = <{uri}> || ?o = <{uri}>) }}'
    
    return crud_operations(request, get_query, del_query, ret_format)

# endpoint for Expressions   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634
@app.route('/akn/<country>/<type_>/<subtype>/<autor>/<date>/<work_id>/<lng>@<exp_id>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_expression(country, type_, subtype, autor, date, work_id, lng, exp_id):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{autor}/{date}/{work_id}/{lng}@{exp_id}'
    get_query = f'''JSON {{ "data": ?data}} WHERE {{ <{uri}> <{ontology_url}#is_embodied_in> ?manifestation. 
                                                    ?manifestation <{ontology_url}#has_date> ?date. 
                                                    ?manifestation <{ontology_url}#content> ?data. }} ORDER BY DESC (?date)'''
    
    del_query = f'''DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. 
                                                    <{uri}> <{ontology_url}#has_related_event> ?event.
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
                                                    ?expression <{ontology_url}#has_language> <{ontology_url}#srp>. }} ORDER BY DESC (?date) LIMIT 1'''
    
    get_query = f'''JSON {{ "data": ?data }} WHERE {{ {{ {get_subquery} }}
                                                    ?expression <{ontology_url}#is_embodied_in> ?manifestation.
                                                    ?manifestation <{ontology_url}#has_date> ?date.
                                                    ?manifestation <{ontology_url}#content> ?data. }} ORDER BY DESC (?date)'''

    del_query = f'''DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o.
                                                    <{uri}> <{ontology_url}#has_related_event> ?work_ev.
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
    if data['split'] is True:
        data = data['search'].split()

    search = '|'.join(data)

    get_query = f'''JSON {{ "o":?o, "subtype":?subtype, "area":?area, "group":?group, "s":?s }} WHERE {{ ?s a <{ontology_url}#FRBRWork>.
                                                    ?s <{ontology_url}#has_name> ?o. FILTER regex(?o, "{search}")
                                                    ?s <{ontology_url}#FRBRsubtype> ?subtype.
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

    search_name = data['search'] if 'search' in data else '?search'
    if data['split'] is True:
        search = '|'.join(search_name.split())

    keywords = data['keywords'].split() if 'keywords' in data else '?keywords'
    subtype = data['subtype'] if 'subtype' in data else '?subtype'
    subregister = data['subregister'] if 'subregister' in data else '?subregister'
    area = data['area'] if 'area' in data else '?area'
    group = data['group'] if 'group' in data else '?group'

    #fali za keywords
    get_query = f'''JSON {{ "o":?o, "subtype":?subtype, "area":?area, "group":?group, "s":?s }} WHERE {{ ?s a <{ontology_url}#FRBRWork>.
                                                    ?s <{ontology_url}#has_name> ?o. FILTER regex(?o, "{search}")
                                                    ?s <{ontology_url}#FRBRsubtype> {subtype}.
                                                    ?s <{ontology_url}#has_subregister> ?subregister_uri.
                                                    ?subregister_uri <{ontology_url}#has_name> {subregister}.
                                                    ?s <{ontology_url}#has_group> ?group_uri.
                                                    ?group_uri <{ontology_url}#has_name> {group}.
                                                    ?s <{ontology_url}#has_area> ?area_uri.
                                                    ?area_uri <{ontology_url}#has_name> {area}. }}'''
    
    try:
        sparql_query.setQuery(get_query)
        response = sparql_query.query().convert()
        return jsonify(response)
    except Exception as e:
        abort(500, e)

    return 