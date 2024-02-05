import re

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


DNI_NIE_REGEX = '^[0-9XYZ][0-9]{7}[TRWAGMYFPDXBNJZSQVHLCKE]$'


@deconstructible
class ValidateFileSize:
    def __init__(self, params):
        self.max_file_size = params

    def __call__(self, value):
        filesize = value.size

        if filesize > self.max_file_size:
            raise ValidationError("El archivo seleccionado supera el tamaño máximo")
        else:
            return value


def validate_dni(value):
    # if not re.match(DNI_NIE_REGEX, value):
    #     raise ValidationError(
    #         ('%(value)s no es un DNI/NIE válido'),
    #         params={'value': value},
    #     )
    pass


def validate_movil(value):
    pass
    # from gestion.models import Member
    # members = Member.objects.filter(movil=value).all()
    # if members.count() > 0:
    #     listado_miembros = [f"{member.pk}: {member}" for member in members]
    #     listado_miembros = ";".join(listado_miembros)
    #     raise ValidationError(
    #         (f'El número de móvil {value} ya está registrado en la base de datos. Miembro: {listado_miembros}'),
    #         params={'value': value},
    #     )
