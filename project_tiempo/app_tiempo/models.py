from django.db import models

# Create your models here.
class Municipio(models.Model):
    nombre = models.CharField(max_length = 100, null=True)
    mun_id = models.CharField(max_length = 32, null=True)
    altitud = models.CharField(max_length = 100, null=True)
    latitud = models.CharField(max_length = 100, null=True)
    longitud = models.CharField(max_length = 100, null=True)
    maxima = models.IntegerField(null=True)
    minima = models.IntegerField(null=True)
    prob_precipitacion = models.IntegerField(null=True)
    descripcion = models.TextField(null=True)
    url = models.CharField(max_length = 100, null=True)
    num_comentarios = models.IntegerField(default = 0)

    def __str__(self):
        return self.nombre
