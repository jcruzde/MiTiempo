from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json

# Create your views here.
def main(request):
    return HttpResponse('Pagina de inicio')

def usuario(request, usuario):
    return HttpResponse('Pagina de un usuario')

def municipios(request):
    return HttpResponse('Pagina de municipios')

def municipios_id(request, id):
    return HttpResponse('Municipios con id')

def info(request):
    return HttpResponse('Pagina de info')