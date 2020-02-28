from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
# from rest_framework import authentication, permissions
from owlready2 import *
import json


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
            data['ime'] = str(e).split('.')[-1]
            res.append(data)

        # res = json.dumps(res)
        return Response(res)
