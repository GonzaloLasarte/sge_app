from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from estructura.models import Zona, DistritoGeneral, DistritoGeneral, Grupo, HistoricoEstructura
from cargos.models import Nivel

class Command(BaseCommand):
    help = 'Registra en el histórico la estructura actual'

    def handle(self, *args, **options):
        modelos_estructura = ('Zona', 'DistritoGeneral', 'Distrito', 'Grupo')
        for modelo_estructura in modelos_estructura:
            modelo = apps.get_model('estructura', modelo_estructura)
            elementos = modelo.objects.all()
            nivel_nombre = modelo._meta.verbose_name.title()
            nivel = Nivel.objects.get(nombre=nivel_nombre.title())
            for elemento in elementos:
                estructura_anterior = HistoricoEstructura.objects.filter(nivel=nivel, object_id=elemento.pk).last()
                if estructura_anterior:
                    estructura_anterior.fecha_baja = timezone.localtime(timezone.now())
                    estructura_anterior.save()
                HistoricoEstructura.objects.create(nivel=nivel, object_id=elemento.pk,
                    fk=getattr(elemento, elemento._tracked_field).pk)
        