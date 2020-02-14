from rest_framework import serializers
from .models import Enlace, Cliente


class EnlaceSerializer(serializers.Serializer):
    nombre_enlace = serializers.CharField(max_length=100)
    enlace_anuncio = serializers.CharField(max_length=255)
    frecuencia = serializers.CharField(max_length=5)
    status= serializers.CharField(max_length=10)
    next_published_time= serializers.DateTimeField()
    remaining_post = serializers.CharField(max_length=5)
    sent_to_client = serializers.DateTimeField()
