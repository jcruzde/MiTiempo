from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from project_tiempo import settings
from . import parser
from .models import Municipio, Preferencia, Comentario
import datetime


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

    try: # Compruebo si existe el municipio
        id = settings.municipios[municipio]['id'][-5:]
        municipio_inBD = Municipio.objects.get(nombre=municipio)
        mensaje = "El municipio ya existe en la BD de municipios"
    except KeyError: # No es un municipio válido.
        mensaje = "Disculpe, el municipio introducido no existe"
    except Municipio.DoesNotExist: # Es un municipio válido y nuevo.
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
        mensaje = "Añadido " + municipio + " a su lista de municipios"

        # Añadir a la selección de un usuario

    return mensaje

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
    mensaje = "Enhorabuena! Has cambiado el título de tu página"
    return mensaje

def add_comentario(request, id):
    comentario = request.POST['mensaje']
    print('Añado el comentario: ' + comentario)

    try:
        municipio = Municipio.objects.get(mun_id = id)
        usuario = User.objects.get(username=request.user.username)

        new_coment = Comentario(municipio = municipio,
                                comentario = comentario,
                                usuario = usuario,
                                fecha = datetime.date.today(),
                                )
        new_coment.save()
        print('Comentario guardado')

        num_comentarios = municipio.num_comentarios
        print('Comentarios que tiene actualmente: ' + str(num_comentarios))
        num_comentarios = num_comentarios + 1
        municipio.num_comentarios = num_comentarios
        municipio.save()

    except Municipio.DoesNotExist:
        print('Recibo un comentario, pero lo no guardo porque' +
              ' ese municipio no ha sido seleccionado por ningun usuario')

    # Sumar el contador de comentarios.


########################################################################
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
    mensaje = ""

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
            mensaje = cambiar_titulo(request)
        elif form_type == 'municipio':
            mensaje = add_municipio(request)

    return render(request, './usuario.html', {'path': user_path,
                                              'mensaje': mensaje})


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
        elif form_type == 'comentario':
            add_comentario(request, id)

    try: # Comprobar que exista ese municipio, si no está en la BD lo descarto.
        info = parser.get_info(id) # Añadirle la longitud y latitud.
        url = settings.municipios[info['nombre']]['url']
        municipio = Municipio.objects.get(mun_id=id)
        lista_comentarios = Comentario.objects.filter(municipio = municipio)
        # Actualizar esta info en la BD.
        # Comprobar que ese id exista
    except:
        info = {}
        url = ""
        lista_comentarios = {}
        print('Este ID no existe')

    return render(request, './municipiosID.html', {'info': info,
                                                   'url': url,
                                                   'lista_comentarios': lista_comentarios})

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