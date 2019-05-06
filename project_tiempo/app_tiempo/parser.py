from xml.sax.handler import ContentHandler
from xml.sax import make_parser
import sys
import string
import urllib.request
from datetime import datetime, date, time, timedelta

def get_info(id):
    # id = 28065
    hoy = datetime.today() # Es un objeto con info de la fecha, hora, ...
    mañana = hoy + timedelta(days=1)  # Suma a fecha actual 1 día
    mañana = int(mañana.strftime("%d")) # Me quedo solo con el día
    info = {'dia': mañana}


    class CounterHandler(ContentHandler):

        def __init__(self):
            self.es_mañana = False
            self.in_temperatura = False
            self.in_content = False
            self.theContent = ""
            self.dia = 0

        def startElement(self, name, attrs):
            if name == 'nombre':
                self.in_content = True
            if name == 'dia':
                self.dia = int(attrs.get('fecha')[-2:])
                if self.dia == mañana:
                    print('Día: ' + str(self.dia))
                    self.es_mañana = True

            if self.es_mañana:
                if name == 'prob_precipitacion':
                    self.periodo = attrs.get('periodo')
                    if self.periodo == "00-24":
                        self.in_content = True
                if name == 'temperatura':
                    self.in_temperatura = True
                if name == 'maxima' and self.in_temperatura:
                    self.in_content = True
                if name == 'minima' and self.in_temperatura:
                    self.in_content = True
                if name == 'estado_cielo':
                    self.periodo = attrs.get('periodo')
                    if self.periodo == "00-24":
                        self.descripcion = attrs.get('descripcion')
                        print('Descripcion: ' + self.descripcion)
                        info['estado_cielo'] = self.descripcion

        def endElement(self, name):
            if name == 'nombre':
                print('Nombre: ' + self.theContent)
                info['nombre'] = self.theContent
                self.in_content = False
                self.theContent = ""
            if name == 'prob_precipitacion' and self.in_content:
                print('Prob de precipitación: ' + self.theContent)
                info['prob_precipitacion'] = self.theContent
                self.in_content = False
                self.theContent = ""
            if name == 'temperatura':
                self.in_temperatura = False
            if name == 'maxima' and self.in_temperatura:
                print('Temperatura máxima: ' + self.theContent)
                info['maxima'] = self.theContent
                self.in_content = False
                self.theContent = ""
            if name == 'minima' and self.in_temperatura:
                print('Temperatura minima: ' + self.theContent)
                info['minima'] = self.theContent
                self.in_content = False
                self.theContent = ""
            if name == 'dia' and self.es_mañana:
                self.es_mañana = False

        def characters(self, chars):
            if self.in_content:
                self.theContent = self.theContent + chars

    print('EMPIEZO A PARSEAR' + '\n')

    NewsParser = make_parser()  # Parser genérico de sax
    NewsHandler = CounterHandler()  # Me quedo con las cosas que me interesan
    NewsParser.setContentHandler(NewsHandler)

    xmlPueblo = urllib.request.urlopen("http://www.aemet.es/xml/municipios/localidad_" + str(id) + ".xml")
    NewsParser.parse(xmlPueblo)

    print('\n' + 'FIN DE PARSEAR')

    return info

''' Info es un diccionario con:
dia
nombre
prob_precipitacion
maxima
minima
estado_cielo
'''

