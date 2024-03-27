from datetime import date, datetime
import io
import json
from django.core.files.base import ContentFile
import pymysql
import xlsxwriter
from decimal import Decimal

from django.apps import apps
from django.conf import settings
from django.contrib import messages
from django.contrib.admin import helpers
from django.contrib.auth import logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.models import Session
from django.db import connection
from django.db.models import Q
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.html import format_html
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

from cargos.forms import CargoCapacitacionPostForm, CargoPostForm, FechaAltaForm, FechaBajaCargoForm, Rango
from cargos.models import Cargo, CargoCapacitacion, Departamento, GrupoCapacitacion, Nivel, Rango, RangoCapacitacion
from cargos.utils import convertir_nombre_modelo
from estructura.models import Grupo, Region, Zona
from gestion.forms import ConfirmDeleteForm, DeshacerBajaForm, ReactivarForm
from gestion.models import AltaMiembro, BajaMiembro, Estudio, Member, MiembroGrupo, ExtendedUser

from .forms import MyPasswordChangeForm
from django.conf import settings

def log_out(user):
    [s.delete() for s in Session.objects.all() if s.get_decoded().get("_auth_user_id") == user.id]


def check_expiration(user):
    return user.is_admin or user.has_not_expired

def check_pass_date(user):
    return user.is_almost_expired

@login_required
@user_passes_test(check_expiration)
def regiones(request):
    regiones_list = []
    if request.user.is_nacional:
        regiones_list = [(item.pk, item.nombre) for item in Region.objects.all()]
    elif request.user.is_region or request.user.is_zona:
        regiones_list = [(request.user.region_id, request.user.region)]
    return HttpResponse(json.dumps(regiones_list), content_type="application/json")


@login_required
@user_passes_test(check_expiration)
def get_estructura(request):
    """Llamada ajax desde las vistas para rellenar el sidebar."""
    pk = request.GET.get("id", "")
    field = request.GET.get("field", "")
    child = request.GET.get("child", "").replace("_", "")
    child_class = apps.get_model("estructura", child)
    result = []
    variable_column = field.lower()

    if pk:
        if child.lower() == "zona" and not request.user.is_nacional and not request.user.is_region and request.user.is_zona:
            result = [(request.user.zona_id, request.user.zona)]
        else:
            result = [
                (item.pk, item.nombre)
                for item in child_class.objects.filter(**{variable_column: pk}).order_by("nombre")
            ]
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
@user_passes_test(check_expiration)
def home(request):
    return render(request, "gestion/home.html")


def create_list_from_cursor(cursor):
    rows = cursor.fetchall()
    # DEBUG settings (used to) affect what gets returned.
    if not settings.DEBUG:
        desc = [item[0].lower() for item in cursor.cursor.description]
    else:
        desc = [item[0].lower() for item in cursor.description]
    lista = [dict(zip(desc, item)) for item in rows]
    return lista


def _get_member_query(region_id=None, zona_id=None, solo_activos=None):
    solo_activos_condition = ""
    region_condition = "null"
    zona_condition = "null"
    if region_id:
        region_condition = f"{region_id}"
    if zona_id:
        zona_condition = f"{zona_id}"
    return """
        SELECT M.id, M.nombre, M.apellidos, M.fecha_nacimiento, M.dni, M.baja_lopd, ES.estudio, M.fecha_estudio
            , M.codigo_postal, M.baja, M.fecha_ingreso fechaa, M.alta AS motivo_alta, altaex.fecha_llegada_extranjero
            , altaex.origen AS procedencia, baja.fecha AS fechab, baja.motivo AS motivo_baja, baja.destino
            , M.gohonzon, CD.nombre AS departamento, M.movil, M.email, M.omamori_gohonzon, M.omamori_fecha
            , R.id AS region_id, R.nombre AS region, Z.id AS zona_id, Z.nombre AS zona, DG.id AS distrito_general_id
            , DG.nombre AS distrito_general, D.id AS distrito_id, D.nombre AS distrito, G.id AS grupo_id, G.nombre AS grupo
            , M.fecha_baja, M.localidad
            , (select COUNT(*) from cargos_cargo C WHERE C.member_id = M.id) as num_cargos
            , (select COUNT(*) from cargos_cargocapacitacion C WHERE C.member_id = M.id) as num_cargos_capacitacion

        FROM gestion_member M
        LEFT JOIN cargos_departamento CD ON M.departamento_id=CD.id
        LEFT JOIN gestion_estudio ES ON M.estudio_id=ES.id
        LEFT JOIN (SELECT  A.member_id,
                    A.fecha,
                    A.motivo, A.fecha_llegada_extranjero, A.origen
            FROM    gestion_altamiembro A
            INNER JOIN ( SELECT max(fecha) fecha, member_id from gestion_altamiembro
            where motivo like '%Ingreso%'
            group by member_id
            ) B
            ON A.fecha = B.fecha AND A.member_id=B.member_id
            where motivo like '%Ingreso%') alta
            ON alta.member_id = M.id
        LEFT JOIN (SELECT  A.member_id,
                    A.fecha,
                    A.motivo, A.fecha_llegada_extranjero, A.origen
            FROM    gestion_altamiembro A
            INNER JOIN ( SELECT max(fecha_llegada_extranjero) fecha, member_id from gestion_altamiembro
            where fecha_llegada_extranjero is not null
            group by member_id
            ) B
            ON A.fecha_llegada_extranjero = B.fecha AND A.member_id=B.member_id
            where motivo like '%extranjero%') altaex
            ON altaex.member_id = M.id
        LEFT JOIN (SELECT  A.member_id,
                    A.fecha,
                    A.motivo, A.destino
            FROM    gestion_bajamiembro A
            INNER JOIN ( SELECT max(fecha) fecha, member_id from gestion_bajamiembro
            group by member_id
            ) B
            ON A.fecha = B.fecha AND A.member_id=B.member_id) baja
            ON baja.member_id = M.id
            
        LEFT JOIN (SELECT A.grupo_id, A.member_id, A.fecha_baja, A.fecha_inicio FROM gestion_miembrogrupo A
            INNER JOIN (SELECT member_id, max(fecha_inicio) fecha FROM gestion_miembrogrupo
                    WHERE fecha_baja is null
                    GROUP BY member_id
                ) B
            ON A.member_id = B.member_id AND A.fecha_inicio = B.fecha) MG ON M.id = MG.member_id
        LEFT JOIN estructura_grupo G ON MG.grupo_id = G.id
        LEFT JOIN estructura_distrito D ON G.distrito_id = D.id
        LEFT JOIN estructura_distritogeneral DG ON D.distrito_general_id = DG.id
        LEFT JOIN estructura_zona Z ON DG.zona_id = Z.id
        LEFT JOIN estructura_region R ON Z.region_id = R.id
        WHERE ((CD.fecha_baja IS NULL) OR (CD.fecha_baja >= curdate()))
        AND ((CD.fecha_inicio IS NULL) OR (CD.fecha_inicio <= curdate()))
        AND ((M.baja <> 'Por razones técnicas') OR (M.baja is null))
        {region_condition}
        {zona_condition}
        {solo_activos_condition}
        GROUP by M.id;
    """.format(
        region_condition=region_condition, zona_condition=zona_condition, solo_activos_condition=solo_activos_condition
    )


@login_required
@user_passes_test(check_expiration)
@user_passes_test(check_pass_date, login_url='/registration/update.html')
def list(request):
    members = []
    context = {}
    regiones = [] 
    if request.user.is_nacional:
        regiones = [region.nombre for region in Region.objects.all()]
        args = (None,None)
    elif request.user.is_region:
        regiones = [request.user.region]
        args = (None,request.user.region_id)
    elif request.user.is_zona:
        regiones = [request.user.region]
        args = (request.user.zona_id, request.user.region_id)
    else:
        log_out(request.user)
        messages.add_message(request, messages.ERROR, "Su usuario no tiene permisos suficientes")
        return

    with connection.cursor() as cursor:
        try:
            cursor.callproc("listado",args)
            members = create_list_from_cursor(cursor)
        except:
            messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")
            render(request, "gestion/list.html", context)

    q = request.GET.get("q", "")
    if q:
        context["nivel"] = q.replace("_", " ").title()
        modelo = apps.get_model("estructura", convertir_nombre_modelo(q))
        q += "_id"
        id = int(request.GET.get("id", ""))
        nombre_nivel = modelo.objects.get(pk=id).nombre.upper()
        context["nombre_nivel"] = nombre_nivel
        members = [member for member in members if member.get(q) == id]
    context["members"] = members
    context["regiones"] = regiones
    context["estudios"] = [estudio.estudio for estudio in Estudio.objects.distinct()]
    context["departamentos"] = [departamento.nombre for departamento in Departamento.objects.distinct()]
    context["motivos_alta"] = [motivo for motivo, _ in Member.REGISTER_CHOICES]
    context["motivos_baja"] = [motivo for motivo, _ in Member.DROP_OUT_CHOICES]

    return render(request, "gestion/list.html", context)


class MemberDetailView(LoginRequiredMixin, DetailView):
    model = Member
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["opts"] = Member._meta
        return context


@login_required
@user_passes_test(check_expiration)
def cargos(request):
    context = {}
    con_fecha_fin = False
    if request.user.is_nacional:
        args = ("t", 0)
        context["regiones"] = Region.objects.all()
        con_fecha_fin = True
    if request.user.is_region:
        args = ("r", request.user.region_id)
        region = Region.objects.get(pk=request.user.region_id)
        context["regiones"] = [region]
    if request.user.is_zona:
        args = ("z", request.user.zona_id)
        region = Region.objects.get(pk=request.user.region_id)
        context["regiones"] = [region]
    with connection.cursor() as cursor:
        try:
            cursor.callproc("Cargos_de_responsabilidad", args)
            cargos = create_list_from_cursor(cursor)
            if not con_fecha_fin:
                cargos = [cargo for cargo in cargos if not cargo.get('fecha_fin')]
            context["cargos"] = cargos
        except KeyError:
            messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")
            render(request, "gestion/cargos.html", context)
    context["departamentos"] = [departamento.nombre for departamento in Departamento.objects.distinct()]
    context["niveles"] = [nivel.nombre for nivel in Nivel.objects.distinct()]
    context["estudios"] = [estudio.estudio for estudio in Estudio.objects.distinct()]
    context["rangos"] = [rango.nombre for rango in Rango.objects.distinct()]

    return render(request, "gestion/cargos.html", context)


@login_required
@user_passes_test(check_expiration)
def cargos_capacitacion(request):
    context = {}
    if request.user.is_nacional:
        args = ("t", 0)
        context["regiones"] = Region.objects.all()
    if request.user.is_region:
        args = ("r", request.user.region_id)
        region = Region.objects.get(pk=request.user.region_id)
        context["regiones"] = [region]
    if request.user.is_zona:
        args = ("z", request.user.zona_id)
        region = Region.objects.get(pk=request.user.region_id)
        context["regiones"] = [region]
    with connection.cursor() as cursor:
        try:
            cursor.callproc("Cargos_de_capacitacion", args)
            context["cargos"] = create_list_from_cursor(cursor)
        except KeyError:
            messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")
            render(request, "gestion/cargos.html", context)
    context["departamentos"] = [departamento.nombre for departamento in Departamento.objects.distinct()]
    context["grupos_capacitacion"] = [
        grupo_capacitacion.nombre for grupo_capacitacion in GrupoCapacitacion.objects.distinct()
    ]
    context["niveles"] = [nivel.nombre for nivel in Nivel.objects.distinct()]
    context["estudios"] = [estudio.estudio for estudio in Estudio.objects.distinct()]
    context["rangos"] = [rango.nombre for rango in RangoCapacitacion.objects.distinct()]

    return render(request, "gestion/cargos_capacitacion.html", context)


@login_required
@user_passes_test(check_expiration)
def organigrama(request):
    if request.user.is_nacional:
        regiones = [region.nombre for region in Region.objects.all()]
    elif request.user.is_region or request.user.is_zona:
        region = request.user.miembro.region
        regiones = [region]
    else:
        log_out(request.user)
        messages.add_message(request, messages.ERROR, "No tiene permisos para ver esta página")
        return
    return render(request, "gestion/organigrama.html", {"regiones": regiones})


@login_required
@user_passes_test(check_expiration)
def exportar_organigrama(request, region):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    # Even though the final file will be in memory the module uses temp
    # files during assembly for efficiency. To avoid this on servers that
    # don't allow temp files, for example the Google APP Engine, set the
    # 'in_memory' Workbook() constructor option as shown in the docs.
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Get some data to write to the spreadsheet.

    headers = ["Nombre", "Desde", "Cargo", "Nivel", "Rango", "Grupo", "Distrito", "Distrito General", "Zona", "Región"]

    selected_region = Region.objects.get(nombre=region.lower())
    nivel = Nivel.objects.get(nombre="Nacional")
    if request.user.is_nacional:
        cargos_nacionales = (
            Cargo.active_objects.filter(nivel=nivel).order_by("departamento__orden", "rango__orden", "member").distinct()
        )
        cargos_nacionales_data = [[
            f"{cargo.member.nombre} {cargo.member.apellidos}",
            cargo.fecha_inicio,
            cargo.codigo,
            cargo.nivel.nombre,
            cargo.rango.nombre,
            "-",
            "-",
            "-",
            "-",
            "-"
        ] for cargo in cargos_nacionales]
    else:
        cargos_nacionales_data = []
    cargos_region = selected_region.cargos_set  # if request.user.is_region or request.user.is_nacional else []
    cargos_region_data = [[
        f"{cargo.member.nombre} {cargo.member.apellidos}",
        cargo.fecha_inicio,
        cargo.codigo,
        cargo.nivel.nombre,
        cargo.rango.nombre,
        "-",
        "-",
        "-",
        "-",
        selected_region.nombre
        ] for cargo in cargos_region]
    data = cargos_nacionales_data + cargos_region_data
    if request.user.is_zona:
        zonas = []
        zona_id = request.user.miembro.zona_id
        zonas.append(Zona.objects.get(pk=zona_id))
    elif request.user.is_region or request.user.is_nacional:
        zonas = selected_region.zona_set.all().order_by("nombre")
    else:
        log_out(request.user)
        messages.add_message(request, messages.ERROR, "No tiene permisos para ver esta página")
        return

    cargos_zonas_data = []
    for zona in zonas:
        for cargo in zona.cargos_set:
            cargos_zonas_data.append([
                f"{cargo.member.nombre} {cargo.member.apellidos}",
                cargo.fecha_inicio,
                cargo.codigo,
                cargo.nivel.nombre,
                cargo.rango.nombre,
                "-",
                "-",
                "-",
                zona.nombre,
                selected_region.nombre
            ])
        for distritogeneral in zona.distritogeneral_set.all().order_by("nombre"):
            for cargo in distritogeneral.cargos_set:
                cargos_zonas_data.append([
                    f"{cargo.member.nombre} {cargo.member.apellidos}",
                    cargo.fecha_inicio,
                    cargo.codigo,
                    cargo.nivel.nombre,
                    cargo.rango.nombre,
                    "-",
                    "-",
                    distritogeneral.nombre,
                    zona.nombre,
                    selected_region.nombre
                ])
            for distrito in distritogeneral.distrito_set.all().order_by("nombre"):
                for cargo in distrito.cargos_set:
                    cargos_zonas_data.append([
                        f"{cargo.member.nombre} {cargo.member.apellidos}",
                        cargo.fecha_inicio,
                        cargo.codigo,
                        cargo.nivel.nombre,
                        cargo.rango.nombre,
                        "-",
                        distrito.nombre,
                        distritogeneral.nombre,
                        zona.nombre,
                        selected_region.nombre
                    ])
                for grupo in distrito.grupo_set.all().order_by("nombre"):
                    for cargo in grupo.cargos_set:
                        cargos_zonas_data.append([
                            f"{cargo.member.nombre} {cargo.member.apellidos}",
                            cargo.fecha_inicio,
                            cargo.codigo,
                            cargo.nivel.nombre,
                            cargo.rango.nombre,
                            grupo.nombre,
                            distrito.nombre,
                            distritogeneral.nombre,
                            zona.nombre,
                            selected_region.nombre
                        ])

    data = cargos_nacionales_data + cargos_region_data + cargos_zonas_data
    data.insert(0, headers)

    # Write some test data.
    for row_num, columns in enumerate(data):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num, col_num, cell_data)

    # Apply format
    bold = workbook.add_format({'bold': True})
    header = workbook.add_format({'bold': True, 'bg_color': '#752936', 'color': 'white'})
    dates = workbook.add_format()
    dates.set_num_format('dd/mm/yyyy')
    worksheet.set_row(0, 18, bold)
    worksheet.set_row(0, 18, header)
    worksheet.set_column(0, 0, 30, bold)
    worksheet.set_column(1, 1, 11, dates)
    worksheet.set_column(2, 2, 10)
    worksheet.set_column(3, 3, 15)
    worksheet.set_column(4, 4, 20)
    worksheet.set_column(5, 9, 15)

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    filename = 'organigrama.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=%s' % filename

    return response


@login_required
@user_passes_test(check_expiration)
def get_data(request):
    region_name = request.GET.get("region", "")
    if region_name:
        selected_region = Region.objects.get(nombre=region_name)
        nivel = Nivel.objects.get(nombre="Nacional")
        if request.user.is_nacional:
            cargos_nacionales = (
                Cargo.active_objects.filter(nivel=nivel).order_by("departamento__orden", "rango__orden", "member").distinct()
            )
            cargos_nacionales = "<p>" + "<br/>".join(cargo.nombre_cargo for cargo in cargos_nacionales) + "</p>"
        else:
            cargos_nacionales = ""
        result = {
            "name": "SGEs",
            "title": "SGEs",
            "className": "nacional",
            "title": cargos_nacionales,
        }
        cargos_region = selected_region.cargos if request.user.is_region or request.user.is_nacional else ""
        region = {
            "url": f"region&id={selected_region.id}",
            "name": f"Región {selected_region.nombre}",
            "title": cargos_region,
            "className": "middle-level",
        }
        region_children = []
        if request.user.is_zona:
            zonas = []
            zona_id = request.user.miembro.zona_id
            zonas.append(Zona.objects.get(pk=zona_id))
        elif request.user.is_region or request.user.is_nacional:
            zonas = selected_region.zona_set.all().order_by("nombre")
        else:
            log_out(request.user)
            messages.add_message(request, messages.ERROR, "No tiene permisos para ver esta página")
            return
        for zona in zonas:
            zona_json = {
                "url": f"zona&id={zona.id}",
                "name": f"Zona {zona.nombre}",
                "title": zona.cargos,
                "className": "product-dept",
                "collapsed": "true",
            }
            zona_children = []
            for distritogeneral in zona.distritogeneral_set.all().order_by("nombre"):
                distritogeneral_json = {
                    "url": f"distrito_general&id={distritogeneral.id}",
                    "name": f"Distrito General { distritogeneral.nombre }",
                    "title": distritogeneral.cargos,
                    "className": "pipeline1 slide-up",
                    "collapsed": "true",
                }
                distritogeneral_children = []
                for distrito in distritogeneral.distrito_set.all().order_by("nombre"):
                    distrito_json = {
                        "url": f"distrito&id={distrito.id}",
                        "name": f"Distrito { distrito.nombre }",
                        "title": distrito.cargos,
                        "className": "rd-dept slide-up",
                        "collapsed": "true",
                    }
                    distrito_children = []
                    for grupo in distrito.grupo_set.all().order_by("nombre"):
                        grupo_json = {
                            "url": f"grupo&id={grupo.id}",
                            "name": f"Grupo { grupo.nombre }",
                            "title": grupo.cargos,
                            "className": "frontend1 slide-up",
                        }
                        distrito_children.append(grupo_json)
                    distrito_json["children"] = distrito_children
                    distritogeneral_children.append(distrito_json)
                distritogeneral_json["children"] = distritogeneral_children
                zona_children.append(distritogeneral_json)
                zona_json["children"] = zona_children
            region_children.append(zona_json)
        region["children"] = region_children
        result["children"] = [region]
    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
@user_passes_test(check_expiration)
def get_list(request):
    from django.core import serializers
    from django.http import JsonResponse

    members = Member.objects.select_related("departamento")

    result = [
        (
            item.nombre,
            item.apellidos,
            str(item.fecha_ingreso),
            str(item.fecha_gohonzon),
            item.departamento.nombre,
            item.region,
            item.zona,
            item.distrito_general,
            item.distrito,
            item.grupo,
            item.localidad,
            str(item.fecha_baja),
        )
        for item in members
    ]

    return HttpResponse(json.dumps(result), content_type="application/json")


@login_required
@user_passes_test(check_expiration)
def añadir_cargo(request, pk):
    if request.POST:
        form = CargoPostForm(request.POST)
        member = Member.objects.get(pk=pk)
        rango_id = request.POST.get("rango", None)
        rango = Rango.objects.get(pk=rango_id)
        departamento_id = request.POST.get("departamento", None)
        departamento = Departamento.objects.get(pk=departamento_id)
        nivel_id = request.POST.get("nivel", None)
        nivel = Nivel.objects.get(pk=nivel_id)
        object_id = request.POST.get("object_id", None) or None
        fecha_inicio = request.POST.get("fecha_inicio", None)

        try:
            cargo = (
                Cargo.active_objects.filter(
                    member_id=pk,
                    departamento_id=departamento_id,
                    nivel_id=nivel_id,
                    rango_id=rango_id,
                    object_id=object_id,
                )
                .filter(Q(fecha_fin__gt=fecha_inicio) | Q(fecha_fin__isnull=True))
                .exists()
            )

            if cargo:
                messages.error(
                    request,
                    format_html("<b>El cargo a añadir coincide en el tiempo con un mismo cargo ya existente.</b>"),
                )
            else:
                cargo = Cargo.objects.create(
                    member=member,
                    rango=rango,
                    departamento=departamento,
                    nivel=nivel,
                    object_id=object_id,
                    fecha_inicio=fecha_inicio,
                )
        except IntegrityError:
            messages.error(request, format_html("<b>Este miembro ya tiene este cargo.</b>"))
        else:
            # When post imported, go to edition page
            return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change/")
        # else:
        #     return render_to_response('admin/cargo/add_cargo.html', {'form': form})

    return render(
        request,
        "admin/cargo/add_cargo.html",
        {"form": CargoPostForm(user=request.user)},
    )


@login_required
@user_passes_test(check_expiration)
def reactivar(request, pk):
    member = Member.objects.get(pk=pk)
    if request.POST:
        motivo = request.POST.get("motivo", None)
#        fecha = request.POST.get("fecha", None)
        origen = request.POST.get("origen", None)
        fecha_llegada_extranjero = request.POST.get("fecha_llegada_extranjero", None)

        member.alta = motivo
#        member.fecha_ingreso = fecha
        member.origen = origen
        member.fecha_llegada_extranjero = fecha_llegada_extranjero
        member.baja = None
        member.fecha_baja = None
        member.destino = None
        member.save()

        AltaMiembro.objects.create(
            member=member,
            motivo=motivo,
            fecha=fecha_llegada_extranjero if fecha_llegada_extranjero else None,
            origen=origen if origen else None,
            fecha_llegada_extranjero=fecha_llegada_extranjero if fecha_llegada_extranjero else None
        )

        grupo_pk = request.POST.get("grupo", None)
        grupo = Grupo.objects.get(pk=grupo_pk)
        MiembroGrupo.objects.create(
            member=member,
            grupo=grupo,
            fecha_inicio=fecha_llegada_extranjero if fecha_llegada_extranjero else None
        )

        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change/")
    return render(
        request,
        "admin/member/reactivar.html",
        {"form": ReactivarForm(initial={'member': member})},
    )


@login_required
@user_passes_test(check_expiration)
@user_passes_test(lambda u: u.is_admin)
def deshacer_baja(request, pk):
    member = Member.objects.get(pk=pk)
    if request.POST:
        if member.fecha_baja:
            ultima_baja_miembro = BajaMiembro.objects.filter(member=member).order_by('-fecha').first()
            if ultima_baja_miembro:
                ultima_baja_miembro.delete()
            member.baja = None
            member.fecha_baja = None
            member.destino = None
            member.save()

        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change/")

    return render(
        request,
        "admin/member/deshacer_baja.html",
        {"form": ReactivarForm(initial={'member': member})},
    )


@login_required
@user_passes_test(check_expiration)
@user_passes_test(lambda u: u.is_admin)
def dar_baja_lopd(request, pk):
    member = Member.objects.get(pk=pk)
    if request.POST:
        member.dar_baja_lopd()

        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change/")

    return render(
        request,
        "admin/member/dar_baja_lopd.html",
        {"form": ReactivarForm(initial={'member': member})},
    )


@login_required
@user_passes_test(check_expiration)
def añadir_cargo_capacitacion(request, pk):
    if request.POST:
        form = CargoCapacitacionPostForm(request.POST)
        member = Member.objects.get(pk=pk)
        rango_id = request.POST.get("rango", None)
        rango = RangoCapacitacion.objects.get(pk=rango_id)
        grupo_capacitacion_id = request.POST.get("grupo_capacitacion", None)
        grupo_capacitacion = GrupoCapacitacion.objects.get(pk=grupo_capacitacion_id)
        departamento_id = request.POST.get("departamento", None)
        departamento = Departamento.objects.get(pk=departamento_id)
        nivel_id = request.POST.get("nivel", None)
        nivel = Nivel.objects.get(pk=nivel_id)
        object_id = request.POST.get("object_id", None) or None
        fecha_inicio = request.POST.get("fecha_inicio", None)

        try:
            cargo = (
                CargoCapacitacion.objects.filter(
                    member_id=pk,
                    departamento_id=departamento_id,
                    nivel_id=nivel_id,
                    grupo_capacitacion_id=grupo_capacitacion_id,
                    rango_id=rango_id,
                    object_id=object_id,
                )
                .filter(Q(fecha_fin__gt=fecha_inicio) | Q(fecha_fin__isnull=True))
                .exists()
            )

            if cargo:
                messages.error(
                    request,
                    format_html("<b>El cargo a añadir coincide en el tiempo con un mismo cargo ya existente.</b>"),
                )
            else:
                cargo = CargoCapacitacion.objects.create(
                    member=member,
                    rango=rango,
                    departamento=departamento,
                    grupo_capacitacion=grupo_capacitacion,
                    nivel=nivel,
                    object_id=object_id,
                    fecha_inicio=fecha_inicio,
                )
        except IntegrityError:
            messages.error(
                request,
                format_html("<b>Este miembro ya tiene este cargo de capacitación.</b>"),
            )
        else:
            return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change/")

    return render(
        request,
        "admin/cargo/add_cargo.html",
        {"form": CargoCapacitacionPostForm(user=request.user)},
    )


@login_required
@user_passes_test(check_expiration)
def update_grupo(request, pk):
    member = Member.objects.get(pk=pk)

    if "apply" in request.POST:
        grupo_id = request.POST.get("id_grupo")
        grupo = Grupo.objects.get(pk=grupo_id)
        fecha_inicio = request.POST.get("fecha_inicio")
        result = member.cambiar_grupo(grupo, fecha_inicio)
        if result:
            messages.success(request, f"Cambiado el grupo del miembro {pk}")
        else:
            messages.error(
                request,
                f"La fecha de inicio es anterior a la fecha de inicio del anterior grupo",
            )
        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change")
    elif "cancel" in request.POST:
        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change")

    fecha_alta_form = FechaAltaForm()
    return render(
        request,
        "admin/estructura/estructura/grupo_intermediate.html",
        context={"member": member, "opts": Grupo._meta, "form": fecha_alta_form},
    )


def logout_view(request, **kwargs):
    expired_user = kwargs.get("expired_user", False)
    request.session["expired_user"] = expired_user
    logout(request)
    return redirect("login")


def show_message(sender, user, request, **kwargs):
    try:
        expired_user = request.session["expired_user"]
        messages.info(request, "Su usuario ha caducado. Contacte con su administrador.")
    except:
        pass


user_logged_out.connect(show_message)


class MemberDeleteView(LoginRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy("member-list")

    def get_context_data(self, **kwargs):
        """
        Overridden to add a confirmation form to the context.
        """
        context = super().get_context_data(**kwargs)

        if "form" not in kwargs:
            context["form"] = ConfirmDeleteForm()

        return context

    def post(self, request, *args, **kwargs):
        """
        Overridden to process the confirmation form before deleting
        the object.
        """
        self.object = self.get_object()
        form = ConfirmDeleteForm(request.POST, instance=self.object)

        if form.is_valid():
            return self.delete(request, *args, **kwargs)
        else:
            return self.render_to_response(
                self.get_context_data(form=form),
            )


@login_required
@user_passes_test(check_expiration)
def get_motivos_baja(request):
    return HttpResponse(json.dumps(Member.DROP_OUT_CHOICES), content_type="application/json")


@login_required
@user_passes_test(check_expiration)
def delete_member(request, pk):
    post = request.POST.get("post", "")
    if post:
        fecha_baja = request.POST.get("date", date.today())
        motivo_baja = request.POST.get("motivosBaja", "")
        destino = request.POST.get("destino", "")
        member = Member.objects.get(pk=pk)
        member.dar_de_baja(fecha_baja, motivo_baja, destino)

    if motivo_baja != 'Por razones técnicas':
        return HttpResponseRedirect(f"/admin/gestion/member/{pk}/change")
    else:
        return HttpResponseRedirect(f"/admin/gestion/member/")


@login_required
@user_passes_test(check_expiration)
def panel(request):
    return render(request, "gestion/panel.html")


@login_required
@user_passes_test(check_expiration)
def dar_baja_cargo(request, pk):
    post = request.POST.get("post", "")
    cargo = Cargo.active_objects.get(pk=pk)
    if post:
        fecha_fin = request.POST.get("date", date.today())
        fecha_fin_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        if cargo.fecha_inicio and fecha_fin_date < cargo.fecha_inicio:
            messages.add_message(
                request,
                messages.ERROR,
                "La fecha de baja es anterior a la fecha de inicio",
            )
        else:
            cargo.fecha_fin = fecha_fin
            cargo.save()
        return HttpResponseRedirect(f"/admin/gestion/member/{cargo.member.pk}/change")
    else:
        fecha_baja_cargo_form = FechaBajaCargoForm()
        return render(
            request,
            "admin/cargos/cargo/delete_confirmation.html",
            context={
                "cargo": cargo,
                "opts": Cargo._meta,
                "form": fecha_baja_cargo_form,
            },
        )


@login_required
@user_passes_test(check_expiration)
def dar_baja_cargo_capacitacion(request, pk):
    post = request.POST.get("post", "")
    cargo = CargoCapacitacion.objects.get(pk=pk)
    if post:
        fecha_fin = request.POST.get("date", date.today())
        fecha_fin_date = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        if cargo.fecha_inicio and fecha_fin_date < cargo.fecha_inicio:
            messages.add_message(
                request,
                messages.ERROR,
                "La fecha de baja es anterior a la fecha de inicio",
            )
        else:
            cargo.fecha_fin = fecha_fin
            cargo.save()
        return HttpResponseRedirect(f"/admin/gestion/member/{cargo.member.pk}/change")
    else:
        fecha_baja_cargo_form = FechaBajaCargoForm()
        return render(
            request,
            "admin/cargos/cargo/delete_confirmation.html",
            context={
                "cargo": cargo,
                "opts": CargoCapacitacion._meta,
                "form": fecha_baja_cargo_form,
            },
        )

@login_required
def cambiaPass(request):
    if request.method == 'POST':
        contraseña1 = request.POST.get("password1")
        contraseña2 = request.POST.get("password2")
        if contraseña1==contraseña2:
            pass
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Las contraseñas no coinciden",
            )
            messages.add_message(request, messages.WARNING, "")
    else:
        context = {}
        context["Nombre"] = "Hala a cascala"
        return render(request, "registration/update.html", context)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Se ha actualizado la contraseña correctamente.')
            return redirect("/")
        else:
            messages.error(request, 'Por favor, corrige los errores indicados.')
    else:
        form = MyPasswordChangeForm(request.user)
    return render(request, 'registration/update.html', {
        'form': form
    })
@login_required
@user_passes_test(check_expiration)
def data_subcriptions(request):
    members= []
    dataBase = pymysql.connect(
        host= 'localhost',#settings.DB_WOOCOMMERCE_HOST,
        user = 'root',#settings.DB_WOOCOMMERCE_USER,
        #password = '',#settings.DB_WOOCOMMERCE_PASSWORD,
        database = 'edicion7_sgsfscwq20w'#settings.DB_WOOCOMMERCE_DATABASE
    )
    cursor2 = dataBase.cursor()
    cursor2.execute("""SELECT
                        p.ID,
                        p.post_title AS subscription_id,
                        MAX(CASE WHEN m.meta_key = '_billing_email' THEN m.meta_value END) AS billing_email,
                        MAX(CASE WHEN m.meta_key = '_billing_first_name' THEN m.meta_value END) AS billing_first_name,
                        MAX(CASE WHEN m.meta_key = '_billing_last_name' THEN m.meta_value END) AS billing_last_name
                    FROM kt_posts p
                    JOIN kt_postmeta m ON p.ID = m.post_id
                    WHERE p.post_type = 'shop_subscription'
                    AND p.post_status = 'wc-active'
                    AND (m.meta_key = '_billing_email'
                        OR m.meta_key = '_billing_first_name'
                        OR m.meta_key = '_billing_last_name')
                    GROUP BY p.ID
                    ORDER BY p.ID;"""
                    )
    data = cursor2.fetchall()
  
    cursor2.close()
    keys_member2 =[
        'id',
        'subscription_id',
        'email',
        'first_name',
        'last_name',
    ]
    regiones = [region.nombre for region in Region.objects.all()]
    estudios = [estudio.estudio for estudio in Estudio.objects.distinct()]
    departamentos = [departamento.nombre for departamento in Departamento.objects.distinct()]
     
    if request.user.is_nacional:
        regiones = [region.nombre for region in Region.objects.all()]
        args = (None,None)
    elif request.user.is_region:
        regiones = [request.user.region]
        args = (None,request.user.region_id)
    elif request.user.is_zona:
        regiones = [request.user.region]
        args = (request.user.zona_id, request.user.region_id)
    else:
        log_out(request.user)
        messages.add_message(request, messages.ERROR, "Su usuario no tiene permisos suficientes")
        return

    with connection.cursor() as cursor:
        try:
            cursor.callproc("listado",args)
            members = create_list_from_cursor(cursor)
        except:
            messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")
   
    def convertir_datetimes_a_string(diccionario):
        for clave, valor in diccionario.items():
            if isinstance(valor, date):
                diccionario[clave] = valor.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según tus necesidades
            elif valor is None:
                diccionario[clave] = ""
        return diccionario
    new_members = [convertir_datetimes_a_string(member) for member in members]   
    
    def convertir_a_string(valor):
            if valor is None:
                return ""
            elif isinstance(valor, date):
                return valor.strftime('%Y-%m-%d')  # Ajusta el formato según tus necesidades
            return valor
    
    dataFilter = []
    if(request.user.is_superuser!=True or request.user.is_admin!=True):
        if(request.user.is_consultor and request.user.is_nacional):
            dataFilter = new_members
            list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
            emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
            total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
            total_suscriptors = len(total_memebers_suscriptors)
        elif(request.user.is_consultor and request.user.is_region):
            print("entro")
            dataFilter = [x for x in new_members if x['region_id'] == request.user.region_id]
            print(dataFilter)
            list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
            emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
            total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
            total_suscriptors = len(total_memebers_suscriptors)
        else:
            dataFilter = [x for x in new_members if x['region_id'] == request.user.region_id and x['zona_id'] == request.user.zona_id]
            regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        
            list_data_woocomerce = [
            dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
            for tupla in data]

            emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
       
            total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
            total_suscriptors = len(total_memebers_suscriptors)
    else:
        dataFilter = new_members

        list_data_woocomerce = [
            dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
            for tupla in data]
        #esto calcula el total que coinciden entre los dos listados por el campo email
        emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
        total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
       
        total_suscriptors = len(total_memebers_suscriptors)

     
    return render(request, "gestion/data_subcriptions.html", {"total_members_suscriptors": total_memebers_suscriptors,"list_client": list_data_woocomerce, "members": dataFilter, "regiones": regiones, "estudios": estudios, "departamentos": departamentos, "total_suscriptors": total_suscriptors})
@login_required
@user_passes_test(check_expiration)
def data_subcriptions_cargo(request):
        dataBase = pymysql.connect(
        host= 'localhost',#settings.DB_WOOCOMMERCE_HOST,
        user = 'root',#settings.DB_WOOCOMMERCE_USER,
        #password = '',#settings.DB_WOOCOMMERCE_PASSWORD,
        database = 'edicion7_sgsfscwq20w'#settings.DB_WOOCOMMERCE_DATABASE
    )
        cursor2 = dataBase.cursor()
        cursor2.execute("""SELECT
                            p.ID,
                            p.post_title AS subscription_id,
                            MAX(CASE WHEN m.meta_key = '_billing_email' THEN m.meta_value END) AS billing_email,
                            MAX(CASE WHEN m.meta_key = '_billing_first_name' THEN m.meta_value END) AS billing_first_name,
                            MAX(CASE WHEN m.meta_key = '_billing_last_name' THEN m.meta_value END) AS billing_last_name
                        FROM kt_posts p
                        JOIN kt_postmeta m ON p.ID = m.post_id
                        WHERE p.post_type = 'shop_subscription'
                        AND p.post_status = 'wc-active'
                        AND (m.meta_key = '_billing_email'
                            OR m.meta_key = '_billing_first_name'
                            OR m.meta_key = '_billing_last_name')
                        GROUP BY p.ID
                        ORDER BY p.ID;"""
                        )
        data = cursor2.fetchall()
    
        cursor2.close()
        keys_member2 =[
            'id',
            'subscription_id',
            'email',
            'first_name',
            'last_name',
        ]

        estudios = [estudio.estudio for estudio in Estudio.objects.distinct()]
        departamentos = [departamento.nombre for departamento in Departamento.objects.distinct()]
        rangos = [rango.nombre for rango in Rango.objects.distinct()]
        nivel = [nivel.nombre for nivel in Nivel.objects.distinct()]
        
        regiones = []
        con_fecha_fin = False
        if request.user.is_nacional:
            args = ("t", 0)
            regiones = [region.nombre for region in Region.objects.all()]
            con_fecha_fin = True
        if request.user.is_region:
            args = ("r", request.user.region_id)
            regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        if request.user.is_zona:
            args = ("z", request.user.zona_id)
            regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        with connection.cursor() as cursor:
            try:
                cursor.callproc("Cargos_de_responsabilidad", args)
                cargos = create_list_from_cursor(cursor)
                if not con_fecha_fin:
                    cargos = [cargo for cargo in cargos if not cargo.get('fecha_fin')]
            except KeyError:
                messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")
    
    
        def convertir_datetimes_a_string(diccionario):
            for clave, valor in diccionario.items():
                if isinstance(valor, date):
                    diccionario[clave] = valor.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según tus necesidades
                elif valor is None:
                    diccionario[clave] = ""
                elif isinstance(valor, Decimal):
                    diccionario[clave] = str(valor)    
            return diccionario
        new_members = [convertir_datetimes_a_string(member) for member in cargos]
        
        def convertir_a_string(valor):
            if valor is None:
                return ""
            elif isinstance(valor, date):
                return valor.strftime('%Y-%m-%d')  # Ajusta el formato según tus necesidades
            return valor
        
        dataFilter = []
        if(request.user.is_superuser!=True or request.user.is_admin!=True):
            if(request.user.is_consultor and request.user.is_nacional):
                dataFilter = new_members
                list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
                emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
                total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
                emails_set = set()
                # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                total_members_suscriptors_unique = []
                for diccionario in total_memebers_suscriptors:
                    if diccionario['email'] not in emails_set:
                        emails_set.add(diccionario['email'])
                        total_members_suscriptors_unique.append(diccionario)

                
                total_suscriptors = len(total_members_suscriptors_unique)
            elif(request.user.is_consultor and request.user.is_region):
                print("entro", request.user.region_id)
                dataFilter = [x for x in new_members if x['id_region_cargo'] == request.user.region_id]
                list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
                emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
                total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
                emails_set = set()
                # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                total_members_suscriptors_unique = []
                for diccionario in total_memebers_suscriptors:
                    if diccionario['email'] not in emails_set:
                        emails_set.add(diccionario['email'])
                        total_members_suscriptors_unique.append(diccionario)

                
                total_suscriptors = len(total_members_suscriptors_unique)
            else:
                print("entro2", request.user.region_id)
                dataFilter = [x for x in new_members if x['id_region'] == request.user.region_id and x['id_zona'] == request.user.zona_id]
                regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        
                
                list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
            
                emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
        
                total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
                emails_set = set()
                # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                total_members_suscriptors_unique = []
                for diccionario in total_memebers_suscriptors:
                    if diccionario['email'] not in emails_set:
                        emails_set.add(diccionario['email'])
                        total_members_suscriptors_unique.append(diccionario)

                
                total_suscriptors = len(total_members_suscriptors_unique)
        else:
           
            dataFilter = new_members
            list_data_woocomerce = [
            dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
            for tupla in data]
            #esto calcula el total que coinciden entre los dos listados por el campo email
            emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
            total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
            emails_set = set()
            # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
            total_members_suscriptors_unique = []
            for diccionario in total_memebers_suscriptors:
                if diccionario['email'] not in emails_set:
                    emails_set.add(diccionario['email'])
                    total_members_suscriptors_unique.append(diccionario)

            
            total_suscriptors = len(total_members_suscriptors_unique)
        
        return render(request, "gestion/data_subcriptions_cargo.html", {"total_members_suscriptors": total_members_suscriptors_unique,"list_client": list_data_woocomerce, "members": dataFilter, "regiones": regiones, "estudios": estudios, "departamentos": departamentos, "rangos": rangos, "niveles": nivel, "total_suscriptors": total_suscriptors})
@login_required
@user_passes_test(check_expiration)
def data_subcriptions_capacitacion(request):
        dataBase = pymysql.connect(
        host= 'localhost',#settings.DB_WOOCOMMERCE_HOST,
        user = 'root',#settings.DB_WOOCOMMERCE_USER,
        #password = '',#settings.DB_WOOCOMMERCE_PASSWORD,
        database = 'edicion7_sgsfscwq20w'#settings.DB_WOOCOMMERCE_DATABASE
    )
        cursor2 = dataBase.cursor()
        cursor2.execute("""SELECT
                            p.ID,
                            p.post_title AS subscription_id,
                            MAX(CASE WHEN m.meta_key = '_billing_email' THEN m.meta_value END) AS billing_email,
                            MAX(CASE WHEN m.meta_key = '_billing_first_name' THEN m.meta_value END) AS billing_first_name,
                            MAX(CASE WHEN m.meta_key = '_billing_last_name' THEN m.meta_value END) AS billing_last_name
                        FROM kt_posts p
                        JOIN kt_postmeta m ON p.ID = m.post_id
                        WHERE p.post_type = 'shop_subscription'
                        AND p.post_status = 'wc-active'
                        AND (m.meta_key = '_billing_email'
                            OR m.meta_key = '_billing_first_name'
                            OR m.meta_key = '_billing_last_name')
                        GROUP BY p.ID
                        ORDER BY p.ID;"""
                        )
        data = cursor2.fetchall()
    
        cursor2.close()
        keys_member2 =[
            'id',
            'subscription_id',
            'email',
            'first_name',
            'last_name',
        ]
        regiones = [region.nombre for region in Region.objects.all()]
        estudios = [estudio.estudio for estudio in Estudio.objects.distinct()]
        departamentos = [departamento.nombre for departamento in Departamento.objects.distinct()]
    
        if request.user.is_nacional:
            args = ("t", 0)
            regiones = [region.nombre for region in Region.objects.all()]
        if request.user.is_region:
            args = ("r", request.user.region_id)
            regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        if request.user.is_zona:
            args = ("z", request.user.zona_id)
            regiones = [region.nombre for region in Region.objects.all() if region.id == request.user.region_id]
        with connection.cursor() as cursor:
            try:
                cursor.callproc("Cargos_de_capacitacion", args)
                cargos = create_list_from_cursor(cursor)
            except KeyError:
                messages.add_message(request, messages.ERROR, "Se ha producido un error al conectar con la base de datos")

        def convertir_datetimes_a_string(diccionario):
            for clave, valor in diccionario.items():
                if isinstance(valor, date):
                    diccionario[clave] = valor.strftime('%Y-%m-%d %H:%M:%S')  # Ajusta el formato según tus necesidades
                elif valor is None:
                    diccionario[clave] = ""
                elif isinstance(valor, Decimal):
                    diccionario[clave] = str(valor)     
            return diccionario
        new_members = [convertir_datetimes_a_string(member) for member in cargos]
        
        def convertir_a_string(valor):
            if valor is None:
                return ""
            elif isinstance(valor, date):
                return valor.strftime('%Y-%m-%d')  # Ajusta el formato según tus necesidades
            return valor
        
        dataFilter = []
        if(request.user.is_superuser!=True or request.user.is_admin!=True):
            if(request.user.is_consultor and request.user.is_nacional):
                    print('asdasdasdas adsdasdsdsads')
                    dataFilter = new_members
                    list_data_woocomerce = [
                    dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                    for tupla in data]
                    #esto calcula el total que coinciden entre los dos listados por el campo email
                    emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
                    total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
                
                    emails_set = set()
                    # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                    total_members_suscriptors_unique = []
                    for diccionario in total_memebers_suscriptors:
                        if diccionario['email'] not in emails_set:
                            emails_set.add(diccionario['email'])
                            total_members_suscriptors_unique.append(diccionario)

                    
                    total_suscriptors = len(total_members_suscriptors_unique)
            elif(request.user.is_consultor and request.user.is_region):
                dataFilter = [x for x in new_members if x['id_region_cargo'] == request.user.region_id]
                list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
                #esto calcula el total que coinciden entre los dos listados por el campo email
                emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
                total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
            
                emails_set = set()
                # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                total_members_suscriptors_unique = []
                for diccionario in total_memebers_suscriptors:
                    if diccionario['email'] not in emails_set:
                        emails_set.add(diccionario['email'])
                        total_members_suscriptors_unique.append(diccionario)

                
                total_suscriptors = len(total_members_suscriptors_unique)
            else:
                dataFilter = [x for x in new_members if x['id_region_cargo'] == request.user.region_id and x['id_zona'] == request.user.zona_id]

                
                list_data_woocomerce = [
                dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
                for tupla in data]
            
                emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
        
                total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
                emails_set = set()
                # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
                total_members_suscriptors_unique = []
                for diccionario in total_memebers_suscriptors:
                    if diccionario['email'] not in emails_set:
                        emails_set.add(diccionario['email'])
                        total_members_suscriptors_unique.append(diccionario)

                
                total_suscriptors = len(total_members_suscriptors_unique)
        else:
            dataFilter = new_members
            list_data_woocomerce = [
            dict(zip(keys_member2, [convertir_a_string(valor) for valor in tupla]))
            for tupla in data]
            #esto calcula el total que coinciden entre los dos listados por el campo email
            emailsWoocomerce = {diccionario['email'] for diccionario in list_data_woocomerce}
            total_memebers_suscriptors = [diccionario for diccionario in new_members if diccionario['email'] in emailsWoocomerce]
        
            emails_set = set()
            # Filtrar la lista total_memebers_suscriptors eliminando elementos duplicados por correo electrónico
            total_members_suscriptors_unique = []
            for diccionario in total_memebers_suscriptors:
                if diccionario['email'] not in emails_set:
                    emails_set.add(diccionario['email'])
                    total_members_suscriptors_unique.append(diccionario)

            
            total_suscriptors = len(total_members_suscriptors_unique)
           
        
        return render(request, "gestion/data_subcriptions_capacitacion.html", {"total_members_suscriptors": total_members_suscriptors_unique,"list_client": list_data_woocomerce, "members": dataFilter, "regiones": regiones, "estudios": estudios, "departamentos": departamentos, "total_suscriptors": total_suscriptors}) 
