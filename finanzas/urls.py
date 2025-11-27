
from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views



urlpatterns = [
    path("", views.inicio_sesion, name="incio_sesion"),
    path("registar_usuario/", views.registrar_usuario, name="registrar_usuario"),
    path("finanzas/",views.finanzas,name="finanzas"),
    path("ingresos/" ,views.registrarIngreso,name="ingresos" ),
    path("gastos/",views.registrarGastos,name='gastos'),
    path("calificacion/",views.calificacion, name='calificacion'),
    path("ver_calificaciones/",views.VerCalificacion.as_view(), name='ver_calificaciones'),
    path('agregar_categoria', views.categoriaNueva,name='agregar_categoria'),
    path('', LogoutView.as_view(), name='logout')
]
