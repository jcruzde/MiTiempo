from django.urls import path
from . import views

urlpatterns = [
    path('favicon.ico', views.favicon),
    path('', views.main),
    path('info', views.info),
    path('municipios', views.municipios),
    path('municipios/<str:id>', views.municipios_id),
    path('<str:user_path>', views.usuario)
]