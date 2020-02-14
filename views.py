from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
import datetime
from .serializers import EnlaceSerializer
from .models import Enlace
from collections import deque
from datetime import timedelta



# Create your views here.


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def server_time(request):
    tomorrow = datetime.datetime.now()
    # tomorrow.replace(day=22)
    # Enlace.objects.filter(enlace_anuncio='https://www.revolico.com/modificar-anuncio.html?key=EyIFzbHJzicN31645757').update(
    #                              status= 'QUEUED',
    #                              next_published_time= tomorrow,
    #                              # remaining_post=None,
    #                              # sent_to_client= None
    #                              )
    Enlace.objects.all().update(
                                 status= 'QUEUED',
                                 next_published_time= tomorrow,
                                 # remaining_post=2,
                                 sent_to_client= None
                                 )


    # finished = Enlace.objects.filter(status='FINISHED')
    # print(len(finished))

    return Response(datetime.datetime.now())


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def all_links(request):

    return Response(list_all_links())


@api_view(['GET'])
@permission_classes((permissions.IsAuthenticated,))
def get_queued_links(request):
    # Verificar que todos estan procesados
    finished = Enlace.objects.filter(status='FINISHED')
    if len(list_all_links()) == len(finished):
        Enlace.objects.all().update(status='QUEUED')
        return Response('Se terminaron de publicar los enlaces por hoy.', status=404)

    check_link_status_and_requeued_it() # enlaces que queden pendientes regresarlos a la cola con un dia antes
    queryset = Enlace.objects.filter(status='QUEUED').order_by('next_published_time')
    serializer = EnlaceSerializer(queryset,many=True)

    # validacion para multiples publicistas en caso q todos los enlaces esten siendo procesados
    try:
        next_time = datetime.datetime.strptime(serializer.data[0]["next_published_time"], '%Y-%m-%dT%H:%M:%S.%f')
    except:
        return Response('Todos los enlaces estan siendo procesados, intente en unos minutos', status=404)

    if len(serializer.data):
        links = []
        limit = 0
        if next_time <= datetime.datetime.now():
            for i in serializer.data:
                if limit == 3:
                    break
                if (datetime.datetime.strptime(serializer.data[limit]["next_published_time"],'%Y-%m-%dT%H:%M:%S.%f').minute -
                     datetime.datetime.now().minute) <= 1:
                    links.append(i['enlace_anuncio'])
                    limit += 1
                else:
                    limit += 1
            if len(links):
                for i in links:
                    set_processing(i)
                return Response(links, status=200)


    return Response('No hay enlaces disponibles, proximo enlace a las: ' +
                    str(next_time.hour) +':'+ str(next_time.minute)+':'+str(next_time.second)
                    , status=404)



@api_view(['POST'])
@permission_classes((permissions.IsAuthenticated,))
def set_link_queued(request, url):
    queryset = Enlace.objects.filter(status='PROCESSING')
    serializer = EnlaceSerializer(queryset, many=True)
    for i in serializer.data:
        if str(url) in i["enlace_anuncio"]:
            update_enlace_after_published(i["enlace_anuncio"])

    # TODO check q funcione este for loop
    # link = [i["enlace_anuncio"] for i in serializer.data if str(url) in i["enlace_anuncio"] ]
    # update_enlace_after_published(link)
    # implementar las estadisticas usando request.user
    # # print(request.user)

    return Response('Enlace publicado, presione Continuar para seguir publicando.', status=200)



# en la interfaz de admin poner una opcion para modificar los horarios en q el server estara sirviendo enlaces
# default(lunes a sabados de 9am - 6pm)

# con respecto a la frecuencia:

# enviar 3 enlaces a cada cliente de una vez para ser procesados

# ponerle un campo de tiempo a cada enlace que se le entregue a un cliente de maximo 2 minutos, si en ese tiempo
# el cliente no ha devuelto un estado 200 del enlace q se le entrego ponerlo como queued de nuevo

# boton para reportar anuncion invalidos



# metodos auxiliares

def list_all_links():
    enlace =[]
    queryset = Enlace.objects.all()
    serializer = EnlaceSerializer(queryset, many=True)
    for i in serializer.data:
        enlace.append(i["enlace_anuncio"])
    return enlace

# Set processing a los enlances

def set_processing(url):
    processing = Enlace
    processing.objects.filter(enlace_anuncio=url). \
        update(status= 'PROCESSING', sent_to_client=datetime.datetime.now())


# def list_logged_users():
#     sessions = Session.objects.filter(expire_date__gte=timezone.now() )
#     uid_list = []
#     for session in sessions:
#         data = session.get_decoded()
#         uid_list.append(data.get('_auth_user_id', None))
#     return User.objects.filter(id__in=uid_list)

def check_link_status_and_requeued_it():
    processing = Enlace.objects.filter(status='PROCESSING').order_by('sent_to_client')
    serializer = EnlaceSerializer(processing, many=True)
    if len(serializer.data):
        for i in serializer.data:
            # if datetime.datetime.now() - datetime.datetime.strptime(i["sent_to_client"], '%Y-%m-%dT%H:%M:%S.%f'):
                # Enlace.objects.filter(i["enlace_anuncio"]).update(status='QUEUED',
                #                                                   sent_to_client= None
                #                                                   )
            m = datetime.datetime.now() - datetime.datetime.strptime(i["sent_to_client"], '%Y-%m-%dT%H:%M:%S.%f')
            if m.seconds//60 % 60 >= 2:
                Enlace.objects.filter(enlace_anuncio=i["enlace_anuncio"]).update(
                    status= 'QUEUED',
                    sent_to_client= None,
                    next_published_time= datetime.datetime.now()-timedelta(days=1)

                )


def update_enlace_after_published(url):
    frec = Enlace.objects.get(enlace_anuncio=url).frecuencia
    remaining = Enlace.objects.get(enlace_anuncio=url).remaining_post
    frec_minutes = Enlace.objects.get(enlace_anuncio=url)
    if remaining == 1:

        tomorrow = datetime.datetime.now() + timedelta(days=1)
        return Enlace.objects.filter(enlace_anuncio=url).update(
                                     status= 'FINISHED',
                                     next_published_time= tomorrow.replace(hour=9, minute=00, second=00, microsecond=000000),
                                     remaining_post= int(frec),
                                     sent_to_client= None
                                     )
    if remaining is None:

        return Enlace.objects.filter(enlace_anuncio=url).update(
                                     status= 'QUEUED',
                                     next_published_time=datetime.datetime.now() + timedelta(minutes=int(frec_minutes.get_frecuencia_display())),
                                     remaining_post= int(frec) -1,
                                     sent_to_client= None
                                     )

    else:
        return Enlace.objects.filter(enlace_anuncio=url).update(
                                     status= 'QUEUED',
                                     next_published_time=datetime.datetime.now() + timedelta(minutes=int(frec_minutes.get_frecuencia_display())),
                                     remaining_post= int(remaining) -1,
                                     sent_to_client= None
                                     )