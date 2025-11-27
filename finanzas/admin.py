from django.contrib import admin

from .models import Gasto, Ingreso,Categoria

admin.site.register(Gasto)
admin.site.register(Ingreso)
admin.site.register(Categoria)
# Register your models here.
