from django.urls import path
from . import views

urlpatterns = [
    path('', views.main),
    path('css', views.servir_css),
    path('info', views.info),
    path('municipios', views.municipios),
    path('municipios/<str:id>', views.municipios_id),
    path('<str:user_path>', views.usuario)
]