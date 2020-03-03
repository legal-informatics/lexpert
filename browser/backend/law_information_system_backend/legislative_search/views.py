from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
# from rest_framework import authentication, permissions
from owlready2 import *
import json
import os 


class Glasila(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        lista = onto.search(type = onto.Glasila)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['ime'] = str(e.ima_ime[0])
            res.append(data)

        return Response(res)


class Formati(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")
        lista = onto.search(type = akn_meta.FRBRformat)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['format'] = str(e.ima_ime[0])
            res.append(data)

        return Response(res)


class Dokumenti(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")
        lista = onto.search(type = akn_meta.FRBRsubtype)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['tip'] = str(e.ima_ime[0])
            res.append(data)

        return Response(res)


class Jezici(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")
        lista = onto.search(type = akn_meta.FRBRlanguage)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['kod'] = str(e).split('.')[-1]
            res.append(data)

        return Response(res)


class Zemlje(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        akn_meta = get_namespace("http://www.semanticweb.org/filip/ontologies/2020/1/akn_meta_core")
        lista = onto.search(type = akn_meta.FRBRcountry)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['kod'] = str(e).split('.')[-1]
            res.append(data)

        return Response(res)


class Podregistri(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        lista = onto.search(type = onto.Podregistar)

        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['ime'] = str(e.ima_ime[0])
            oblasti = []
            for o in e.narrower:
                oblasti.append(o.ima_ime[0])
            data['oblasti'] = oblasti
            res.append(data)

        return Response(res)


class Oblasti(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        lista = onto.search(type = onto.Oblast)
        
        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['ime'] = str(e.ima_ime[0])
            data['podregistar'] = str(e.broader[0].ima_ime[0])
            grupe = []
            for o in e.narrower:
                grupe.append(o.ima_ime[0])
            data['grupe'] = grupe
            res.append(data)

        return Response(res)


class Grupe(ViewSet):
    # authentication_classes = [authentication.TokenAuthentication]
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly ]

    def list(self, request, format=None):
        onto = get_ontology("./akn_meta_combined_full.owl").load()
        lista = onto.search(type = onto.Grupa)
        
        res = []
        for e in lista:
            data = {}
            data['iri'] = str(e.iri)
            data['ime'] = str(e.ima_ime[0])
            data['oblast'] = str(e.broader[0].ima_ime[0])
            data['podregistar'] = str(e.broader[0].broader[0].ima_ime[0])
            res.append(data)

        return Response(res)