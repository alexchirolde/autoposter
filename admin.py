from django.contrib import admin
from .models import Cliente, Enlace, Servicio, Fichero
# from .forms import EnlaceForm
# Register your models here.


class CustomEnlace(admin.ModelAdmin):
    list_display = ['nombre_enlace','cliente' ]

class CustomService(admin.ModelAdmin):
    list_display = ['nombre_servicio', 'cliente']

admin.site.register(Cliente)
admin.site.register(Enlace , CustomEnlace)
admin.site.register(Servicio, CustomService)
admin.site.register(Fichero)