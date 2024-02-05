import json

from django.apps import apps
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponse

from cargos.models import Nivel
from cargos.utils import convertir_nombre_modelo
from estructura.models import Region
from gestion.models import Member
from gestion.views import check_expiration

@login_required
@user_passes_test(check_expiration)
def get_object_id(request):
    # if request.method == 'GET' and request.is_ajax():
        member_id = int(request.GET.get('member_id'))
        order_id = int(float(request.GET.get('order_id')))
        nivel_id = request.GET.get('nivel_id')
        
        if member_id:
            member = Member.objects.get(id=member_id)
            cargos = member.cargo_set.all()
            nombre_nivel = Nivel.objects.get(pk=nivel_id).nombre
            cargo = cargos[order_id]
            modelo = apps.get_model('estructura', convertir_nombre_modelo(nombre_nivel))
            object_nombre = modelo.objects.get(pk=cargo.object_id).nombre
            return HttpResponse(json.dumps(
                {"pk": cargo.object_id,
                "text": object_nombre,
                "order_id": order_id}
            ), content_type='application/json')
        else:
            return HttpResponse("no-go")

@login_required
@user_passes_test(check_expiration)
def populate_object_id(request):
    # if request.method == 'GET' and request.is_ajax():
        nivel_id = request.GET.get('id', '')
        nivel = Nivel.objects.get(id=nivel_id)
        nombre_nivel = convertir_nombre_modelo(nivel.nombre)
        modelo = apps.get_model('estructura', convertir_nombre_modelo(nombre_nivel))

        result = []
    
        if nivel_id:
            result = [(item.pk, item.nombre) for item in modelo.objects.all()]
            return HttpResponse(json.dumps(result), content_type='application/json')
        else:
            return HttpResponse("no-go")
