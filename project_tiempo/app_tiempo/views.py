from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from project_tiempo import settings
from . import parser
from .models import Municipio, Preferencia


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
        info = parser.get_info(id)
        print('Este es su id: ' + id)
        # Añadir este Municipio a la Base de datos municipio

        new_mun = Municipio(nombre = info['nombre'],
                            mun_id = id,
                            altitud = settings.municipios[municipio]['altitud'],
                            latitud = settings.municipios[municipio]['latitud'],
                            longitud = settings.municipios[municipio]['longitud'],
                            maxima = info['maxima'],
                            minima = info['minima'],
                            prob_precipitacion = info['prob_precipitacion'],
                            descripcion = info['estado_cielo'],
                            url = settings.municipios[municipio]['url'],
                            num_comentarios = 0,
                            )
        new_mun.save()

    except KeyError:
        print('Este municipio no existe')

def cambiar_titulo(request):
    nuevo_titulo = request.POST['titulo']
    print('El nuevo titulo que quiere es: ' + nuevo_titulo)

    # Este POST me llega solo cuando estoy autenticado si o si.
    usuario = User.objects.get(username=request.user.username)
    print('Voy a cambiarle el titulo a: ' + str(usuario))

    try:
        preferencia = Preferencia.objects.get(usuario=usuario)
    except Preferencia.DoesNotExist:
        print('Aún no existe, creo el  nuevo modelo')
        preferencia = Preferencia(usuario=usuario)

    preferencia.titulo = nuevo_titulo
    preferencia.save()


# Create your views here.

def main(request):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    usuarios = User.objects.all()
    titulos = {}
    for usuario in usuarios:
        try:
            preferencia = Preferencia.objects.get(usuario=usuario)
            titulos[usuario] = preferencia.titulo
        except Preferencia.DoesNotExist:
            titulos[usuario] = "Página de " + str(usuario)


    return(render(request, './main.html', {'usuarios': usuarios, 'titulos': titulos}))

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
            cambiar_titulo(request)
        elif form_type == 'municipio':
            add_municipio(request)

    return render(request, './usuario.html', {'path': user_path})


def municipios(request):

    lista_municipios = Municipio.objects.all()

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    return render(request, './municipios.html', {'lista_municipios': lista_municipios})

def municipiosid(request, id):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    try:
        info = parser.get_info(id)
        url = settings.municipios[info['nombre']]['url']
        # Actualizar esta info en la BD.
        # Comprobar que ese id exista
    except:
        info = {}
        url = ""
        print('Este ID no existe')

    return render(request, './municipiosID.html', {'info': info, 'url': url})

def info(request):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    return render(request, './info.html')

def favicon(request):
    return HttpResponseRedirect('/')