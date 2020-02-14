from django.db import models
from datetime import date
import datetime
from .validator import validateExtensionContent, enlace_validator, name_validator, links_listed, sanitize, user_validator
from django.contrib.auth.hashers import make_password
from .encyption_utils import *
from django.shortcuts import redirect
# Create your models here.

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    fecha_contrato = models.DateField(default=date.today)
    correo = models.EmailField(unique=True)
    direccion = models.CharField(max_length=100, blank=True)
    website = models.CharField(max_length=100, blank=True)
    notas = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.nombre

class Fichero(models.Model):

    # def user_directory_path(instance, filename):
    #     return 'user_{0}/{1}'.format(instance.cliente.nombre, filename)

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fichero = models.FileField(validators=[validateExtensionContent],
                               help_text='Tipo admitido: .txt <br> <strong>Formato:</strong> <br> Nombre <br> '
                                         'www.revolico.com/enlace.html?key=asdkJHSADO9<br> Frecuencia en base a la hora. Ej: 3', )
    def save(self, **kwargs):
        for (i,j,k) in zip(links_listed()[0], links_listed()[1], links_listed()[2]):
            """
            Validar que el enlace en caso de que exista, el nombre tiene que ser el mismo pero la frecuencia
            tiene q ser diferente para poder insertarlo en la dB
            """
            if Enlace.objects.filter(enlace_anuncio = j, frecuencia=sanitize(k)).exists():
                pass
            else:

                Enlace.objects.create(cliente=self.cliente, nombre_enlace=i, enlace_anuncio=j,
                                      frecuencia=sanitize(k))




class Enlace(models.Model):

    FREQUENCY_CHOICES=(
        ('5','108'),
        ('4','135'),
        ('3','180'),
        ('2','270'),
        ('1','540'),
        ('9','60'),
        ('12','45'),
        ('18','30'),
        ('36','15'),
        ('54','10'),
        ('108','5'),

    )

    STATUS_CHOICES=(
        ('QUEUED', 'QUEUED'),
        ('PROCESSING', 'PROCESSING'),
        ('FINISHED', 'FINISHED'),
    )


    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre_enlace = models.CharField(max_length=100)
    enlace_anuncio = models.CharField(max_length=255, validators=[enlace_validator], unique=True)
    frecuencia = models.CharField(max_length=5 , choices=FREQUENCY_CHOICES, help_text='Frecuencia de publicación, cada cuantos minutos')
    # settear editable false a status
    status = models.CharField(max_length=10 , choices=STATUS_CHOICES, default='QUEUED', editable=False, blank=True, null=True)
    next_published_time = models.DateTimeField(blank=True, null=True, editable=False, default=datetime.datetime.now)
    sent_to_client = models.DateTimeField(blank=True, null=True, editable=False, default=None)
    remaining_post = models.PositiveIntegerField(blank=True, null=True, editable=False)



    def __str__(self):
        return self.nombre_enlace



class Servicio(models.Model):

    SERVICE_CHOICES=(
        ('BC', 'BacheCubano'),
        # ('CS', 'Cubisima'),
        ('PL', 'PorlaLivre'),
        ('TB', 'Timbirichi'),
        # ('OC', '1CUC')
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre_servicio = models.CharField(max_length=100, choices=SERVICE_CHOICES)
    usuario = models.CharField(max_length=50, help_text='El valor de este campo '
                                                                             'debe ser un correo electronico valido',
                               validators=[user_validator], unique=True)
    contrasena = models.CharField(max_length=150, null=False )

    def __str__(self):
        return self.nombre_servicio
    def save(self, *args, **kwargs):
        self.contrasena = encrypt(self.contrasena)
        super(Servicio, self).save(*args, **kwargs)

