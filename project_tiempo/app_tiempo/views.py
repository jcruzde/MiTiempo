from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from project_tiempo import settings
from . import parser
from .models import Municipio, Preferencia, Comentario, Municipio_Usuario, Navegador
import datetime
from django.views.generic.base import RedirectView
import random
import string

global filtro_max
filtro_max = None
global filtro_min
filtro_min = None

def logout_user(request):
    print('Voy a hacerle logout')
    logout(request)

def login_user(request):
    usuario = request.POST['usuario']
    contraseña = request.POST['contraseña']
    user = authenticate(username=usuario, password=contraseña)
    if user:
        login(request, user)

def add_seleccion_usuario(request, municipio_inBD):
    print('Voy a ver si lo añado a la selección de este usuario')
    # Compruebo si ya existe esta asignación
    usuario = User.objects.get(username=request.user.username)
    municipio_usuario = Municipio_Usuario.objects.filter(usuario=usuario).filter(municipio=municipio_inBD)
    if not municipio_usuario:
        print('No tiene la asinación hecha, lo añado')
        municipio_usuario = Municipio_Usuario(usuario = usuario,
                                              municipio = municipio_inBD,
                                              fecha = datetime.date.today(),
                                              )
        municipio_usuario.save()
    else:
        print('Ya estaba asignado')


def add_municipio(request):

    municipio = request.POST['municipio']
    print('Nuevo municipio recibido para asignar: ' + municipio)

    try: # Compruebo si existe el municipio
        id = settings.municipios[municipio]['id'][-5:]
        municipio_inBD = Municipio.objects.get(nombre=municipio)
        # mensaje = "El municipio ya existe en la BD de municipios"
        add_seleccion_usuario(request, municipio_inBD)
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
                            dia = info['dia'],
                            maxima = info['maxima'],
                            minima = info['minima'],
                            prob_precipitacion = info['prob_precipitacion'],
                            descripcion = info['estado_cielo'],
                            url = settings.municipios[municipio]['url'],
                            num_comentarios = 0,
                            )
        new_mun.save()
        # mensaje = "Añadido " + municipio + " a su lista de municipios"

        add_seleccion_usuario(request, new_mun)

    # return mensaje

def actualizar_municipio(id):
    print('Actualizo la info del municipio')

    # Sé que va a estar en mi BD porque ya he hecho la
    # comprobación en la view anterior.
    municipio_inBD = Municipio.objects.get(mun_id = id)
    info_nueva = parser.get_info(id)
    print('La info  nueva que recibo: ' + str(info_nueva['estado_cielo']))
    municipio_inBD.maxima = info_nueva['maxima']
    municipio_inBD.minima = info_nueva['minima']
    municipio_inBD.prob_precipitacion = info_nueva['prob_precipitacion']
    municipio_inBD.descripcion = info_nueva['estado_cielo']
    municipio_inBD.dia = info_nueva['dia']


    municipio_inBD.save()

def borrar_municipio(request):
    municipio = request.POST['municipio']
    municipio_inBD = Municipio.objects.get(nombre = municipio)
    usuario = User.objects.get(username=request.user.username)
    municipio_usuario = Municipio_Usuario.objects.filter(usuario = usuario).filter(municipio = municipio_inBD)
    municipio_usuario.delete()
    print('quiere eliminar un municipio: ' + municipio)


def cambiar_titulo(request):
    nuevo_titulo = request.POST['titulo']
    print('El nuevo titulo que quiere es: ' + nuevo_titulo)

    # Este POST me llega solo cuando estoy autenticado si o si.
    usuario = User.objects.get(username=request.user.username)
    print('Voy a cambiarle el titulo a: ' + str(usuario))

    try:
        # Compruebo si ya tiene algo asignado este usuario.
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

    # A este caso nunca va a llegar, porque ya lo controlo antes.
    # Lo pongo por si acaso.
    except Municipio.DoesNotExist:
        print('Recibo un comentario, pero lo no guardo porque' +
              ' ese municipio no ha sido seleccionado por ningun usuario')

def filtro_temp(filtro_max,filtro_min):
    municipios = Municipio.objects.all()
    lista_municipios = []

    print('maxima que recibo: ' + str(filtro_max))
    print('minima que recibo: ' + str(filtro_min))


    if filtro_max and filtro_min:
        print('Recibo maxima y minima')
        for municipio in municipios:
            # Para manejar el caso de que no haya conexión.
            if municipio.maxima == None or municipio.minima == None:
                continue
            if municipio.maxima <= int(filtro_max) and municipio.maxima >= int(filtro_min):
                lista_municipios.append(municipio)
    elif filtro_max:
        print('Recibo solo maxima')
        for municipio in municipios:
            if municipio.maxima == None or municipio.minima == None:
                continue
            if municipio.maxima <= int(filtro_max):
                lista_municipios.append(municipio)
    elif filtro_min:
        print('Recibo solo minima')
        for municipio in municipios:
            if municipio.maxima == None or municipio.minima == None:
                continue
            if municipio.maxima>= int(filtro_min):
                lista_municipios.append(municipio)

    return lista_municipios

def cambiar_css(request):
    print('Voy a actualziar su css')
    usuario = User.objects.get(username=request.user)
    color_letra = request.POST['letra']
    tamaño_letra = request.POST['tamaño']
    color_fondo = request.POST['fondo']

    preferencia = Preferencia.objects.get(usuario=usuario)

    if tamaño_letra:
        print('Nuevo tamaño de letra: ' + tamaño_letra)
        preferencia.tamaño_letra = tamaño_letra
    if color_fondo:
        print('Nuevo color de fondo: ' + color_fondo)
        preferencia.color_fondo = color_fondo
    if color_letra:
        print('Nuevo color de letra: ' + color_letra)
        preferencia.color_letra = color_letra

    preferencia.save()

def generate_cookie_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def seleccion_municipios(municipios_comentados,estado):
    print('Estado por el que voy: ' +  str(estado))
    if estado == 0:
        seleccion_municipios = municipios_comentados
        title = ""
    elif estado == 1:
        # Solo los que prob_precip > 0
        seleccion_municipios = []
        for municipio in municipios_comentados:
            if municipio.prob_precipitacion > 0:
                seleccion_municipios.append(municipio)
        title = "Municipios con probabilidad de precipitación > 0"
    elif estado == 2:
        # Solo los que prob_precip == 0
        seleccion_municipios = []
        for municipio in municipios_comentados:
            if municipio.prob_precipitacion == 0:
                seleccion_municipios.append(municipio)
        title = "Municipios con probabilidad de precipitación = 0"

    return seleccion_municipios, title


def gestion_boton(request,usuarios,titulos,municipios_comentados):

    envio_cookie = False

    # Solo aquí es cuando me interesa enviar o detectar cookie de navegador
    if request.COOKIES.get('cookie_id'):
        cookie_id = request.COOKIES.get('cookie_id')
        navegador = Navegador.objects.get(cookie_id=cookie_id)
        print('Este navegador ya tiene una cookie de navegador: ' + navegador.cookie_id)
        print('Su estado es: ' + str(navegador.estado))
        if navegador.estado == 2:
            navegador.estado = 0
        else:
            navegador.estado += 1

        navegador.save()

    else:
        print('Este navegador todavía no lo he fichado')
        envio_cookie = True
        cookie_id = generate_cookie_id()
        print('Le asigno una cookie_id: ' + str(cookie_id))
        navegador = Navegador(cookie_id= cookie_id,
                                  estado = 1)
        navegador.save()

    municipios_mostrados,title = seleccion_municipios(municipios_comentados, navegador.estado)

    response = (render(request, './main.html', {'usuarios': usuarios,
                                                'titulos': titulos,
                                                'municipios_comentados': municipios_mostrados,
                                                'title': title}))
    if envio_cookie:
        # Seguro que tengo la cookie_id inicializada
        response.set_cookie('cookie_id', cookie_id)

    return response

def like(request):
    municipio = request.POST['municipio']
    print('Recibo un like para: ' + str(municipio))
    municipio_in_DB = Municipio.objects.get(nombre = municipio)
    print(str(municipio_in_DB.nombre) + ' ya tiene ' + str(municipio_in_DB.num_likes))
    municipio_in_DB.num_likes = municipio_in_DB.num_likes + 1
    municipio_in_DB.save()

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

    municipios = Municipio.objects.all()
    municipios_comentados = [] # Lista de municipios que tienen algún comentario
    for municipio in municipios:
        if municipio.num_comentarios:
            municipios_comentados.append(municipio)

    # Lista de municipios solo que tienen comentarios, en orden decreciente.
    municipios_comentados.sort(key=lambda Municipio: Municipio.num_comentarios, reverse=True)
    if len(municipios_comentados) > 10:
        print('Hay más de 10 en la lista')
        municipios_comentados = municipios_comentados[0:10]

    # Si veo solo los que salen del boton, el xml me debería mostrar solo esos.
    # Si veo una seleccion y hago login/logout me vuelve a mostrar todos.

    if request.method == "GET" and 'format' in request.GET:
        print('Me piden el xml')
        response = (render(request, './main.xml', {'lista_municipios': municipios_comentados}, content_type='text/xml'))
        return response
    elif request.method == "POST" and request.POST['form_type'] == 'boton':
        print('Boton pulsado')
        response = gestion_boton(request,usuarios,titulos,municipios_comentados)
        return response
    else:
        response = (render(request, './main.html', {'usuarios': usuarios,
                                               'titulos': titulos,
                                               'municipios_comentados': municipios_comentados}))
        return response

def usuario(request, user_path):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)
        elif form_type == 'css':
            print('Quiere cambiar el css')
            cambiar_css(request)
        elif form_type == 'titulo':
            print('Quiere cambiar su titulo')
            cambiar_titulo(request)
        elif form_type == 'municipio':
            add_municipio(request)
        elif form_type == 'quitar':
            borrar_municipio(request)
    try:
        user = User.objects.get(username=user_path)
    except User.DoesNotExist:
        user = None
    lista_municipios_user = Municipio_Usuario.objects.filter(usuario=user).order_by('-id')
    # order_by es para que aparezca primero el último que ha seleccionado. El id es el
    # campo que siempre se añade en las BD (que está implícito en el admin site).
    # El - es para que lo ordene de manera descendente.
    try:
        preferencias = Preferencia.objects.filter(usuario=user)[0]
    except:
        # Maneja el caso de que el usuario aún no haya establecido ninguna preferencia.
        preferencias = []

    # El filtro me devuelve una lista. Me quedo con el primer elemento,
    # que será el único que corresponda con ese nombre.
    if request.method == "GET" and 'format' in request.GET:
        print('Me piden el xml')
        return (render(request, './usuario.xml', {'lista_municipios_user': lista_municipios_user}, content_type='text/xml'))
    else:
        return render(request, './usuario.html', {'path': user_path,
                                                  'lista_municipios_user': lista_municipios_user,
                                                  'preferencias': preferencias})

def municipios(request):

    global filtro_max
    global filtro_min

    lista_municipios = Municipio.objects.all()

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)
        elif form_type == 'filtro_temp':
            print('Quiere filtrar la temperatura')
            filtro_max = request.POST['maxima']
            filtro_min = request.POST['minima']

    elif request.method == "GET":
        # Para que cualdo vuelvo a pinchar en 'Todos' del menu, aparezcan
        # todos otra vez, y no la selección.
        filtro_max = None
        filtro_min = None
        lista_municipios = Municipio.objects.all()


    # Para evitar que al hacer el logout sobre un filtrado
    # me vuelvan a aparecer todos los municipios
    if filtro_max or filtro_min:
        lista_municipios = filtro_temp(filtro_max,filtro_min)

    if request.method == "GET" and 'format' in request.GET:
        print('Me piden el xml')
        return (render(request, './main.xml', {'lista_municipios': lista_municipios}, content_type='text/xml'))
    else:
        return render(request, './municipios.html', {'lista_municipios': lista_municipios,
                                                     'filtro_max': filtro_max,
                                                     'filtro_min': filtro_min})

def municipios_id(request, id):


    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)
        elif form_type == 'comentario':
            add_comentario(request, id)
        elif form_type == 'like':
            print('Recibe un like')
            like(request)

    try:
        print('Voy a comprobar si tengo en mi BD el municipio con id: ' + str(id))
        municipio = Municipio.objects.get(mun_id=id)

        # Si me hacen un GET actualizo la info.
        if request.method == "GET":
            actualizar_municipio(id)

        # Tras haber actualizado la info en la BD, recupero
        # la info actualizada
        municipio = Municipio.objects.get(mun_id=id)

        # Sea GET o POST, muestro la info.
        url = settings.municipios[municipio.nombre]['url']
        lista_comentarios = Comentario.objects.filter(municipio=municipio)
        print('Está en mi BD')
    except Municipio.DoesNotExist:
        # /municipio/id => Ese id no lo tengo en mi BD (nadie lo ha seleccionado)
        municipio = ""
        lista_comentarios = {}
        print('No está en mi BD')

    return render(request, './municipiosID.html', {'municipio': municipio,
                                                   'lista_comentarios': lista_comentarios})


def info(request):

    if request.method == "POST":
        form_type = request.POST['form_type']
        if form_type == 'logout':
            logout_user(request)
        elif form_type == 'login':
            login_user(request)

    return render(request, './info.html')

def servir_css(request):
    if request.method == "GET" and request.user.is_authenticated:
        print('Sirvo un css personalizado')
        user = User.objects.get(username=request.user)
        try:
            # Al crear un usuario nuevo, no se crean sus preferencias.
            # Si nada más crearlo quiero hago esto de abajo, no lo encuentra.
            # Solo cuando envío algo del formulario (o vacío) es cuando se crea
            # la entrada en la BD con los valores por defecto.
            preferencia = Preferencia.objects.get(usuario=user)
            print('Sus preferencias son: ' + str(preferencia.color_letra) + str(preferencia.color_fondo) + str(preferencia.tamaño_letra))
            color_letra = preferencia.color_letra
            tamaño_letra = preferencia.tamaño_letra
            color_fondo = preferencia.color_fondo
        except:
            # Para un usuario que se acaba de crear y no ha hecho POST del
            # formulario de preferencias.
            color_letra = 'black'
            tamaño_letra = 'normal'
            color_fondo = 'white'
    else:
        color_letra = 'black'
        tamaño_letra = 'normal'
        color_fondo = ''


    return render(request, './main.css',{'color_letra': color_letra,
                                         'tamaño_letra': tamaño_letra,
                                         'color_fondo': color_fondo},
                                        content_type='text/css')