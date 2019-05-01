from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from .forms import Form_login

# Create your views here.
def main(request):

    form_in = Form_login()

    if request.method == "GET":
        return render(request, './base.html', {'form_in': form_in})
    elif request.method == "POST":
        if len(request.POST.keys()) == 1: # Solo tiene el token
            logout(request)
            return(render(request, './base.html', {'form_in': form_in}))
        else:
            usuario = request.POST['usuario']
            contraseña = request.POST['contraseña']
            user = authenticate(username=usuario, password=contraseña)
            if user:
                login(request, user)
            return(render(request, './base.html', {'form_in': form_in}))

def usuario(request, usuario):
    return HttpResponse('Pagina de un usuario')

def municipios(request):
    return HttpResponse('Pagina de municipios')

def municipios_id(request, id):
    return HttpResponse('Municipios con id')

def info(request):
    return HttpResponse('Pagina de info')