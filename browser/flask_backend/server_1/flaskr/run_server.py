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

# constants
named_individual = 'http://www.w3.org/2002/07/owl#NamedIndividual'

type_stavec = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' # Nije moglo samo da stoji type

content = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#content'
has_date = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_date'
has_name = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_name'
has_number = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_number'

is_realized_through = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_realized_through'
is_embodied_in = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_embodied_in'

has_related_event = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#{ontology_url}#is_embodied_in'

is_of_type = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_of_type'
is_of_subtype = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_of_subtype'
has_subregister = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_subregister'
has_group = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_group'
has_area = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_area'
has_country = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_country'

has_language = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_language'

is_in_format = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_in_format'

has_responsible_role = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_responsible_role'
is_of_eventtype = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_of_event_type'

is_of_role = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_role_of'

ontology_url = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined'
core_url = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core'
default_lng = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core#srp'

def event(document):
    """kreiranje dogadjaja za prosledjeni document (work ili expression)"""

    query = ''

    # Proverava da li u sparql bazi postoji trazena uloga
    role = document['FRBRauthor']['@as'][1:]
    ask_query = f'''
        SELECT ?s {{
            ?s <{is_of_role}> <{ontology_url}{document['FRBRauthor']['@href']}>.
            ?s <{type}> <{ontology_url}#{role.capitalize()}>.
        }}
    '''

    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()

        author_iri = ''

        if len(response['results']['bindings']) == 0:
            author_iri = f'{ontology_url}#{role}-{str(uuid.uuid1()).split("-")[0]}'

            query += f'''
                <{author_iri}> <{type}> <{ontology_url}#{role.capitalize()}>.
                <{author_iri}> <{type}> <{named_individual}>.
                <{author_iri}> <{is_of_role}> <{ontology_url}{document['FRBRauthor']['@href']}>.
            '''
        else:
            author_iri = response['results']['bindings'][0]['s']['value']

        event_iri = f'{core_url}#event-{str(uuid.uuid1()).split("-")[0]}'

        event_type = ''
        if (role == 'author'):
            event_type = 'eventtype_001'
        elif (role == 'editor'):
            event_type = 'eventtype_003'
        else:
            abort(400, 'Event is applicable to FRBRWork and FRBRExpression')

        query += f'''
            <{event_iri}> <{type}> <{named_individual}>.
            <{event_iri}> <{type}> <{core_url}#TLCEvent>.
            <{event_iri}> <{has_responsible_role}> <{author_iri}>.
            <{event_iri}> <{has_date}> "{document['FRBRdate']['@date']}"^^xsd:date.
            <{event_iri}> <{is_of_eventtype}> <{ontology_url}#{event_type}>.
            <{ontology_url}#{document['FRBRuri']['@value']}> <{has_related_event}> <{event_iri}>.
            '''
    except Exception as e:
        abort(400, e)

    return query

def parse_xml(request):
    data = request.data
    content_dict = xmltodict.parse(data)

    meta = content_dict['meta']
    identification = meta['identification']
    publication = meta['publication']
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

    # ne dozvoljava dodavanje dokumenta ukoliko se path uri razlikuje od manifestation uri-ja u dokumentu
    if (path_uri != manifestation_uri):
        abort(400, 'Path uri does not match document uri!')

    # ne dozvoljava dodavanje dokumenta ukoliko expression uri ne pocinje work uri-jem
    if (not expression_uri.startswith(work_uri)):
        abort(400, 'Expression uri does not start with work uri!')

    # ne dozvoljava dodavanje dokumenta ukoliko manifestation uri ne pocinje expression uri-jem
    if (not manifestation_uri.startswith(expression_uri)):
        abort(400, 'Manifestation uri does not start with expression uri!')

    # ne dozvoljava se dodavanje dokumenta ukoliko u bazi vec postoji dokument sa istim urijem
    if request.method == 'POST':
        ask_query = f'''
            ASK {{
                <{manifestation_uri}> <{type}> <{core_url}#FRBRManifestation>
            }}
        '''

        sparql_query.setQuery(ask_query)

        try:
            response = sparql_query.query().convert()

            if response['boolean']:
                abort(400, 'Document with same IRI already exists!')
        except Exception as e:
            abort(400, e)

    query = f'''
        PREFIX xsd:<http://www.w3.org/2001/XMLSchema#>
        INSERT DATA {{
    '''

    # proverava postoji li vec u bazi work uri iz dokumenta, kako bi se sprecilo dupliranje podataka
    # pre svega dogadjaja ciji se nazivi dobijaju na osnovu trenutnog vremena
    ask_query = f'''
            SELECT ?s {{
                <{work_uri}> <{type}> <{core_url}#FRBRWork>.
            }}
        '''

    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()

        author_iri = ''

        if len(response['results']['bindings']) == 0:
            query += f'''
                <{work_uri}> <{type}> <{named_individual}>.
                <{work_uri}> <{type}> <{core_url}#FRBRWork>.
                <{work_uri}> <{has_date}> "{work['FRBRdate']['@date']}"^^xsd:date.
                <{work_uri}> <{has_name}> "{work['FRBRname']['@value']}"^^xsd:string.
                <{work_uri}> <{has_number}> "{work['FRBRnumber']['@value']}"^^xsd:string.
                <{work_uri}> <{is_of_type}> <http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#act>.
                <{work_uri}> <{is_of_subtype}> <{core_url}#{work['FRBRsubtype']['@value']}>.
                <{work_uri}> <{has_country}> <{core_url}#{work['FRBRcountry']['@value']}>.
            '''

            for keyword in classification['keyword']:
                if 'subregister' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{has_subregister}> <{ontology_url}#{keyword['@value']}>.
                    '''
                elif 'group' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{has_group}> <{ontology_url}#{keyword['@value']}>.
                    '''
                if 'area' in keyword['@value']:
                    query += f'''
                        <{work_uri}> <{has_area}> <{ontology_url}#{keyword['@value']}>.
                    '''
            query += event(work)
    except Exception as e:
        abort(400, e)

    # proverava postoji li vec u bazi expression uri iz dokumenta, kako bi se sprecilo dupliranje podataka
    # pre svega dogadjaja ciji se nazivi dobijaju na osnovu trenutnog vremena
    ask_query = f'''
        SELECT ?s {{
            <{expression_uri}> <{type}> <{core_url}#FRBRExpression>.
        }}
    '''

    sparql_query.setQuery(ask_query)

    try:
        response = sparql_query.query().convert()

        author_iri = ''

        if len(response['results']['bindings']) == 0:
            query += f'''
                        <{expression_uri}> <{type}> <{named_individual}>.
                        <{expression_uri}> <{type}> <{core_url}#FRBRExpression>.
                        <{expression_uri}> <{has_date}> "{expression['FRBRdate']['@date']}"^^xsd:date.
                        <{expression_uri}> <{has_language}> <{core_url}#{expression['FRBRlanguage']['@language']}>.
                        <{work_uri}> <{is_realized_through}> <{expression_uri}>.
                    '''
            query += event(expression)
    except Exception as e:
        abort(400, e)

    query += f'''
        <{manifestation_uri}> <{type}> <{named_individual}>.
        <{manifestation_uri}> <{type}> <{core_url}#FRBRManifestation>.
        <{manifestation_uri}> <{has_date}> "{manifestation['FRBRdate']['@date']}"^^xsd:date.
        <{manifestation_uri}> <{is_in_format}> <{core_url}#{manifestation['FRBRformat']['@value']}>.
        <{manifestation_uri}> <{content}> "{cont_fix}"^^xsd:string.
        <{expression_uri}> <{is_embodied_in}> <{manifestation_uri}>.
    '''

    query += f'''}}'''

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
        sparql_update.setQuery(insert_query)
        try:
            sparql_update.query()
            return 'Individual successfully added', 200
        except Exception as e:
            abort(400, e) 


# endpoint for Manifestations   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634/xml
@app.route('/akn/<country>/<type_>/<subtype>/<work_id>/<lng>@<exp_id>/<ret_format>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_manifestation(country, type_, subtype, work_id, lng, exp_id, ret_format):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{work_id}/{lng}@{exp_id}/{ret_format}'
    get_query = f'JSON {{ "data": ?data }} WHERE {{ <{uri}> <{ontology_url}#content> ?data.}}'
    del_query = f'DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. FILTER ( ?s = <{uri}> || ?o = <{uri}>) }}'
    
    return crud_operations(request, get_query, del_query, ret_format)

# endpoint for Expressions   -->   #/akn/rs/act/zakon/2017-88-3634/srp@2017-09-3634
@app.route('/akn/<country>/<type_>/<subtype>/<work_id>/<lng>@<exp_id>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_expression(country, type_, subtype, work_id, lng, exp_id):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{work_id}/{lng}@{exp_id}'
    get_query = f'''JSON {{ "data": ?data}} WHERE {{ <{uri}> <{ontology_url}#is_embodied_in> ?manifestation. 
                                                    ?manifestation <{ontology_url}#has_date> ?date. 
                                                    ?manifestation <{ontology_url}#content> ?data. }} ORDER BY DESC (?date)'''
    
    del_query = f'''DELETE {{ ?s ?q ?o }} WHERE {{ ?s ?q ?o. 
                                                    <{uri}> <{ontology_url}#has_related_event> ?event.
                                                    OPTIONAL {{ <{uri}> <{ontology_url}#is_embodied_in> ?manifestation. }}
                                                    FILTER ( ?s in ( <{uri}>, ?manifestation,  ?event) || ?o in ( <{uri}>, ?manifestation,  ?event) )}}'''
    
    return crud_operations(request, get_query, del_query, 'xml')

# endpoint for Work   -->   #/akn/rs/act/zakon/2017-88-3634
@app.route('/akn/<country>/<type_>/<subtype>/<work_id>.<ret_format>', methods=['GET'])
@app.route('/akn/<country>/<type_>/<subtype>/<work_id>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_work(country, type_, subtype, work_id, ret_format='xml'):
    uri = f'{ontology_url}#/akn/{country}/{type_}/{subtype}/{work_id}'
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