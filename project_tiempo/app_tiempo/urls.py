from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('info', views.info),
    path('municipios', views.municipios),
    path('municipios/<int:id>', views.municipios_id),
    path('<str:usuario>', views.usuario)
]