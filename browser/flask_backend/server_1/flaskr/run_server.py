import os 
from flask import Flask, url_for, request, jsonify, abort
from SPARQLWrapper import SPARQLWrapper, XML, JSON

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
        return data, 200, {'content-type':'application/xml'}

    # TODO transformacija u ostale formate

    return data


@app.route('/simple_search')
def simple_search():

    # TODO search preko jednog polja

    return 'Najlepsa!'

@app.route('/search')
def search():

    # TODO search preko forme

    return 'Najlepsa!'


# exposing Apche Jena Fuseki endpoint for SPARKQL queries
@app.route('/sparql', methods=['POST'])
def sparql():
    query = request.json['query']

    if not query:
        abort(400, 'No sparql query has been pased')
    
    sparql_query.setQuery(query)

    try :
        response = sparql_query.query().convert()
        return response.toxml()
    except Exception as e:
        abort(400, e)


# endpoint for Manifestations   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634/srp@2017-09-29/2020-03-17.xml
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>/<lng>@<date_2>/<date_3>.<ret_format>', methods=['GET', 'DELETE', 'PUT'])
def fetch_manifestation(subtype, date_1, number, lng, date_2, date_3, ret_format):
    uri = '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number + '/' + lng + '@' + date_2 + '/' + date_3 + '.xml'
    
    # get only returns data
    if request.method == "GET":
        query = 'JSON {"data": ?data} WHERE { <' + ontology_url + uri + '> <' + content + '> ?data.}'
        sparql_query.setQuery(query)

        try :
            response = sparql_query.query().convert()
            return transform(response[0]['data'], ret_format) # only xml format is stored so for any other formats we need to transform them
        except Exception as e:
            abort(400, e)

    # deleting of all connected stuff with individual
    if request.method == "PUT" or request.method == "DELETE":
        query = 'DELETE { ?s ?q ?o } WHERE { ?s ?q ?o. FILTER ( ?s = <'+ ontology_url + uri +'> || ?o = <'+ ontology_url + uri +'>)}'
        sparql_update.setQuery(query)

        try :
            sparql_update.query()
            if request.method == "DELETE":
                return 'Success', 204
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT

    return 'delete'


# endpoint for Expressions   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634/srp@2017-09-29
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>/<lng>@<date_2>', methods=['GET', 'DELETE', 'PUT'])
def fetch_expression(subtype, date_1, number, lng, date_2):
    uri = '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number + '/' + lng + '@' + date_2
    
    # get only returns data
    if request.method == "GET":
        query = 'JSON {"data": ?data} WHERE { <'+ ontology_url + uri +'> <'+ embodied_in +'> ?manifestation. ' \
                                            '?manifestation <' + has_date + '> ?date. ' \
                                            '?manifestation <' + content + '> ?data. } ORDER BY DESC (?date)'
        sparql_query.setQuery(query)

        try :
            response = sparql_query.query().convert()
            return transform(response[0]['data'], 'xml')
        except Exception as e:
            abort(400, e)

    # deleting of all connected stuff wit individual
    if request.method == "PUT" or request.method == "DELETE":
        query = 'DELETE { ?s ?q ?o } WHERE { {?s ?q ?o. FILTER ( ?s = <'+ ontology_url + uri +'> || ?o = <'+ ontology_url + uri +'>)} UNION' \
            '{ ?s ?q ?o. <'+ ontology_url + uri +'> <'+ embodied_in +'> ?manifestation. FILTER ( ?s = ?manifestation || ?o = ?manifestation )} UNION' \
            '{ ?s ?q ?o. <'+ ontology_url + uri +'> <'+ has_related_event +'> ?event. FILTER ( ?s = ?event || ?o = ?event )} }'
        sparql_update.method = 'POST'
        sparql_update.setQuery(query)

        try :
            sparql_update.query()
            if request.method == "DELETE":
                return 'Success', 204
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT

    return 'delete'


# endpoint for Work   -->   #/akn/rs/act/zakon/2017-09-27/2017-88-3634
@app.route('/akn/rs/act/<subtype>/<date_1>/<number>', methods=['GET', 'DELETE', 'PUT'])
def fetch_work(subtype, date_1, number):
    uri = '#/akn/rs/act/' + subtype + '/' + date_1 + '/' + number
    
    # get only returns data
    if request.method == "GET":
        try :
            query = 'JSON {"expression": ?expression} WHERE { <'+ ontology_url + uri +'> <'+ is_realized_through +'> ?expression. ' \
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

    # deleting of all connected stuff wit individual
    if request.method == "PUT" or request.method == "DELETE":

        # TODO brisanje za work

        try :
            sparql_update.query()
            if request.method == "DELETE":
                return 'Success', 204
        except Exception as e:
            abort(400, e)

    # TODO insertovanje posle PUT

    return 'delete'



if __name__ == '__main__':
    app.run(debug = True)