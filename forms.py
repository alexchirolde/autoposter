from django.forms import ModelForm
from .models import Fichero, Enlace
from django.db import models

class FicheroForm(ModelForm):
    class Meta:
        model = Fichero
        exclude = ()

# class EnlaceForm(ModelForm):
#     class Meta:
#         model = Enlace
#         fields =('nombre_enlace', 'enlace_anuncio',)




