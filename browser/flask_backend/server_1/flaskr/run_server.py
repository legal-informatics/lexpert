import os 
from flask import Flask, url_for, request, jsonify, abort
from SPARQLWrapper import SPARQLWrapper, XML, JSON

import xmltodict
import lxml.etree as ET
import pdfkit

app = Flask(__name__)

sparql_query = SPARQLWrapper('http://localhost:3030/test/query')
sparql_query.setReturnFormat(JSON)

sparql_update = SPARQLWrapper('http://localhost:3030/test/update')
sparql_update.method = 'POST'

# constants
content = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#content'
embodied_in = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_embodied_in'
has_date = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_date'
has_related_event = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_related_event'
is_realized_through = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#is_realized_through'
has_language = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_language'

ontology_url = 'http://www.semanticweb.org/marko/ontologies/2020/3/untitled-ontology-36'
default_lng = 'http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core#srp'

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


def parse_xml(data):
    content_dict = xmltodict.parse(data)

    # TODO parsiranje xml-a i vracanje rdf grafa za ubacivanje u Fuseki

    # INSERT DATA{ <http://example/book3> dc:title "A new book"} primer inserta

    # iz content_dict treba samo izvuci podatke i napraviti sve odgovarajuce triplete, nezaboraviti i triplete kao:
    # <http://www.semanticweb.org/marko/ontologies/2020/3/untitled-ontology-36#/akn/rs/act/zakon/2017-09-27/2017-88-3634> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#NamedIndividual>
    # <http://www.semanticweb.org/marko/ontologies/2020/3/untitled-ontology-36#/akn/rs/act/zakon/2017-09-27/2017-88-3634> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core#FRBRWork>

    return content_dict # moze da vrati i odgovor da li je insertovao ili da vrati string pa u svkom od endpointa da se radi insertovanje


@app.route('/simple_search')
def simple_search():

    # TODO search preko jednog polja, ispod je primer kako sam mislio samo imamo problem cirilice, jer 'Zakon' ne bi nasao posto mu je u imenu 'Закон' videti sta sa tim

    # Select ?s where { ?s <http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_combined#has_name> ?o. FILTER regex(?o, "Закон")}

    # Takodje treba se dogovoriti sta se sve vraca, ocigledno uri, sto je u ovom slucaju (ili mozda samo ono posle # trebalo bi da moze), i sta jos tipa datum, vrstu, nzm ni ja

    return 'Najlepsa!'

@app.route('/search', methods=['POST'])
def search():
    data = request.json

    # TODO search preko forme pretpostavljam da ces slati json te ovde treba sisliti sparql upit koji ce to da hvata i opet sta sve vratiti od podataka za tu te pronadjene
    
    # query = 'SPARQL upit'
    # sparql_query.setQuery(query)

    # try :
    #     response = sparql_query.query().convert()
    #     return response
    # except Exception as e:
    #     abort(400, e)

    return transform(request.data, 'pdf') # trenutno mi je sluzio da testiram konverzije i sada radi sa pdf konverzijom kad mu prosledis akn xml, to je ono od cvejica, mada imaju gresaka ti akn xml-ovi


# exposing Apche Jena Fuseki endpoint for SPARKQL queries
@app.route('/sparql', methods=['POST'])
def sparql():
    query = request.data

    if not query:
        abort(400, 'No sparql query has been pased')
    
    sparql_query.setQuery(query)

    try :
        response = sparql_query.query().convert()
        return response
    except Exception as e:
        abort(400, e)


# endpoint for Manifestations   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634/srp@2017-09-29/2020-03-17.xml
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>/<lng>@<date_2>/<date_3>.<ret_format>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_manifestation(subtype, date_1, number, lng, date_2, date_3, ret_format):
    uri = ontology_url + '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number + '/' + lng + '@' + date_2 + '/' + date_3 + '.xml'
    
    # get only returns data
    if request.method == "GET":
        query = 'JSON {"data": ?data} WHERE { <'+ uri +'> <'+ content +'> ?data.}'
        sparql_query.setQuery(query)

        try :
            response = sparql_query.query().convert()
            return transform(response[0]['data'], ret_format) # only xml format is stored so for any other formats we need to transform them
        except Exception as e:
            abort(400, e)

    # deleting of all connected stuff with individual
    if request.method == "PUT" or request.method == "DELETE":
        query = 'DELETE { ?s ?q ?o } WHERE { ?s ?q ?o. FILTER ( ?s = <'+ uri +'> || ?o = <'+ uri +'>)}'
        sparql_update.setQuery(query)

        try :
            sparql_update.query()
            if request.method == "DELETE":
                return 'Manifestation deleted', 200
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT
    rdf_qraph = parse_xml(request.data)

    return rdf_qraph


# endpoint for Expressions   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634/srp@2017-09-29
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>/<lng>@<date_2>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_expression(subtype, date_1, number, lng, date_2):
    uri = ontology_url + '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number + '/' + lng + '@' + date_2
    
    # get only returns data
    if request.method == "GET":
        query = 'JSON {"data": ?data} WHERE { <'+ uri +'> <'+ embodied_in +'> ?manifestation. ' \
                                            '?manifestation <' + has_date + '> ?date. ' \
                                            '?manifestation <' + content + '> ?data. } ORDER BY DESC (?date)'
        sparql_query.setQuery(query)

        try :
            response = sparql_query.query().convert()
            return transform(response[0]['data'], 'xml')
        except Exception as e:
            abort(400, e)

    # deleting of all connected stuff with individual
    if request.method == "PUT" or request.method == "DELETE":
        query = 'DELETE { ?s ?q ?o } WHERE { {?s ?q ?o.' \
                        ' <'+ uri +'> <'+ has_related_event +'> ?event. ' \
                        'OPTIONAL { <'+ uri +'> <'+ embodied_in +'> ?manifestation. }' \
                        'FILTER ( ?s in ( <'+ uri +'>, ?manifestation,  ?event) || ?o in ( <'+ uri +'>, ?manifestation,  ?event) )} }'
        sparql_update.method = 'POST'
        sparql_update.setQuery(query)

        try :
            sparql_update.query()
            if request.method == "DELETE":
                return 'Expression deleted', 200
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT
    rdf_qraph = parse_xml(request.data)

    return rdf_qraph


# endpoint for Work   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>', methods=['GET', 'DELETE', 'PUT', 'POST'])
def fetch_work(subtype, date_1, number):
    uri = ontology_url  + '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number
    
    # get only returns data
    if request.method == "GET":
        try :
            query = 'JSON {"expression": ?expression} WHERE { <' + uri +'> <'+ is_realized_through +'> ?expression. ' \
                                                '?expression <' + has_date + '> ?date. ' \
                                                '?expression <'+ has_language +'> <'+ default_lng +'>. } ORDER BY DESC (?date)'
            sparql_query.setQuery(query)
            uri = sparql_query.query().convert()[0]['expression']

            query = 'JSON {"data": ?data} WHERE { <'+ uri +'> <'+ embodied_in +'> ?manifestation. ' \
                                                '?manifestation <' + has_date + '> ?date. ' \
                                                '?manifestation <' + content + '> ?data. } ORDER BY DESC (?date)'
            sparql_query.setQuery(query)

            response = sparql_query.query().convert()
            return transform(response[0]['data'], 'xml')
        except Exception as e:
            abort(400, e)

    # deleting of all connected stuff with individual
    if request.method == "PUT" or request.method == "DELETE":

        query = 'DELETE { ?s ?q ?o } WHERE { { ?s ?q ?o.' + \
                        ' <'+ uri +'> <'+ has_related_event +'> ?work_ev. ' + \
                        'OPTIONAL { <'+ uri +'> <'+ is_realized_through +'> ?exp. } ' + \
                        'OPTIONAL {?exp' +' <'+ has_related_event +'> ?exp_ev. } ' + \
                        'OPTIONAL { ?exp' +' <'+ embodied_in +'> ?man. } ' + \
                        'FILTER (?s in ( <'+ uri +'> , ?work_ev, ?exp, ?exp_ev, ?man) || ' + \
                                '?o in ( <'+ uri +'> , ?work_ev, ?exp, ?exp_ev, ?man) )} }'
        sparql_update.method = 'POST'
        sparql_update.setQuery(query)

        try :
            sparql_update.query().convert()
            if request.method == "DELETE":
                return 'Success', 204
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT
    rdf_qraph = parse_xml(request.data)

    return rdf_qraph


if __name__ == '__main__':
    app.run(debug = True)