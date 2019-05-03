from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from project_tiempo import settings


def logout_user(request):
    print('Voy a hacerle logout')
    logout(request)

def login_user(request):
    usuario = request.POST['usuario']
    contraseña = request.POST['contraseña']
    user = authenticate(username=usuario, password=contraseña)
    if user:
        login(request, user)

def add_municipio(request):

    municipio = request.POST['municipio']
    print('Nuevo municipio: ' + municipio)

    try:
        id = settings.municipios[municipio]['id'][-5:]
        print('Este es su id: ' + id)
    except KeyError:
        print('Este municipio no existe')

# Create your views here.
def main(request):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    return(render(request, './main.html'))

def usuario(request, user_path):

    if request.method == "GET":
        try:
            user = User.objects.get(username=user_path)
            print('El usuario existe')
            content = "Mi lista de municipios"
        except User.DoesNotExist:
            print('El usuario no está registrado, no tendrá contenido')
            content = "Este usuario no está registrado."

    elif request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)
        elif form_type == 'css':
            print('Quiere cambiar el css')
        elif form_type == 'titulo':
            print('Quiere cambiar su titulo')
        elif form_type == 'municipio':
            add_municipio(request)

    return render(request, './usuario.html', {'path': user_path})


def municipios(request):
    return HttpResponse('Pagina de municipios')

def municipios_id(request, id):
    return HttpResponse('Municipios con id')

def info(request):
    return HttpResponse('Pagina de info')

def favicon(request):
    return HttpResponseRedirect('/')