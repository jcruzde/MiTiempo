from django.urls import path
from . import views

urlpatterns = [
    path('favicon.ico', views.favicon),
    path('', views.main),
    path('info', views.info),
    path('municipios', views.municipios),
    path('municipios/<int:id>', views.municipiosid),
    path('<str:user_path>', views.usuario)
]