from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User


# Create your views here.
def main(request):

    if request.method == "GET":
        return render(request, './main.html')
    elif request.method == "POST":
        if len(request.POST.keys()) == 1: # Solo tiene el token
            logout(request)
            return(render(request, './main.html'))
        else:
            usuario = request.POST['usuario']
            contraseña = request.POST['contraseña']
            user = authenticate(username=usuario, password=contraseña)
            if user:
                login(request, user)
            return(render(request, './main.html'))

def usuario(request, usuario):

    # Controlar esto al haber un POST
    try:
        user = User.objects.get(username=usuario)
        print('El usuario existe')
        content = "Mi lista de municipios"
    except User.DoesNotExist:
        print('El usuario no existe')
        content = "Este usuario no está registrado."

    if request.method == "GET":
        return render(request, './usuario.html')
    elif request.method == "POST":
        if len(request.POST.keys()) == 1: # Solo tiene el token
            logout(request)
            return(render(request, './usuario.html'))
        else:
            usuario = request.POST['usuario']
            contraseña = request.POST['contraseña']
            user = authenticate(username=usuario, password=contraseña)
            if user:
                login(request, user)
            return(render(request, './usuario.html'))


def municipios(request):
    return HttpResponse('Pagina de municipios')

def municipios_id(request, id):
    return HttpResponse('Municipios con id')

def info(request):
    return HttpResponse('Pagina de info')