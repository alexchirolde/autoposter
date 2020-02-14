from os import path
from io import BytesIO
from django.core.exceptions import ValidationError
import re




name_enlace=[]
enlace=[]
frecuencia_enlace=[]

def validateExtensionContent(value):
    ext = path.splitext(value.name)[1]
    valid_extension = ['.txt']

    if not ext.lower() in valid_extension:
        raise ValidationError(u'Tipo de archivo no soportado')

    if hasattr(value, 'read'):
        file = BytesIO(value.read()).getvalue().splitlines()
        if not len(file) % 3 == 0:
            raise ValidationError(u'Formato de fichero incorrecto')
            return
        for i in file:
            if file.index(i) == 0:
                for v in file[file.index(i)::3]:
                    name_enlace.append(sanitize(v))

            if file.index(i) == 1:
                for v in file[file.index(i)::3]:
                    if enlace_validator(sanitize(v)) == True:
                        if sanitize(v).startswith('www'):
                            enlace.append('https://'+sanitize(v))
                        else:
                            enlace.append(sanitize(v))

            if file.index(i) == 2:
                for v in file[file.index(i)::3]:
                    if re.fullmatch(r'(108|135|180|270|540|60|45|30|15|10|5){1}', sanitize(v)) == None:
                        raise ValidationError(u'Frecuencia del anuncio incorrecta: '+sanitize(v)+'. Asegúrese de usar solo números y que sea uno'
                                                                                                 'de los siguiente: 108,135,180,270,540,60,45,'
                                                                                                 '30,15,10,5')
                    else:
                        frecuencia_enlace.append(v)


def sanitize(arg):

    return str(arg).lstrip().replace('\n','').replace('b','',1).replace('\'','')


def enlace_validator(link):
    if re.fullmatch("((w){3}|(https:\/\/www){1}){1}\.revolico\.com\/modificar-anuncio\.html\?key\=[A-Za-z0-9]+", link) == None:
        raise ValidationError(u'Enlace del anuncio incorrecto: '+sanitize(link))
    else:

        return True

def name_validator(name):
    if re.fullmatch('[^0-9]+', name) == None:
        raise ValidationError(u'Nombre del anuncio incorrecto: '+ sanitize(name)+ '. Asegúrese de no usar números')
    else:
        return True

def links_listed():
    return name_enlace, enlace, frecuencia_enlace




# validator for Servicios model

def user_validator(user):
    if re.fullmatch('\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+',user) ==None:
        raise ValidationError(u'El usuario debe ser un correo electrónico válido')
    else:
        return True



