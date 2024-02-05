from gestion.views import cargos_capacitacion
import urllib.parse as urlparse
from urllib.parse import parse_qs

from django import forms
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.db.models import Q
from django.forms import TextInput
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, resolve

from cargos.forms import FechaAltaForm
from cargos.models import Cargo, CargoCapacitacion, Departamento
from estructura.models import Distrito, DistritoGeneral, Grupo, Region, Zona
from gestion.models import (Documento, Estudio, ExtendedUser, Member, MiembroDepartamento,
                            MiembroGrupo, AltaMiembro, BajaMiembro)


estructura = ('region', 'zona', 'distrito_general', 'distrito', 'grupo')


class ServerInlineAdminForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['rango', 'departamento', 'nivel', 'object_id']

    def __init__(self, *args, **kwargs):
        super(ServerInlineAdminForm, self).__init__(*args, **kwargs)
        self.fields['object_id'] = forms.CharField(widget=forms.Select)


class CustomModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%d %s" % (obj.id, obj.nombre)


class CargoInline(admin.TabularInline):
    model = Cargo
    fields = ('rango', 'nivel', 'get_object_id_name', 'fecha_inicio', 'fecha_fin')
    template = "admin/member/cargo/edit_inline/tabular.html"

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        resolved = resolve(request.path_info)
        member = self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        if request.user.is_admin:
            return member.cargo_set.all()
        else:
            cargos_pk = []
            for cargo in member.cargo_set.filter(fecha_fin__isnull=True).all():
                if cargo.nivel.nombre.lower() == "sin nivel" or cargo.get_region and cargo.get_region.pk == request.user.region_id:
                    cargos_pk.append(cargo.pk)
            return member.cargo_set.filter(fecha_fin__isnull=True, pk__in=cargos_pk)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            self.readonly_fields += ('rango', 'nivel', 'get_object_id_name')
        else:
            self.readonly_fields += ('rango', 'nivel', 'get_object_id_name', 'fecha_inicio', 'fecha_fin')
        return self.readonly_fields


class CargoCapacitacionInline(admin.TabularInline):
    model = CargoCapacitacion
    fields = ('rango', 'grupo_capacitacion', 'nivel', 'get_object_id_name', 'fecha_inicio', 'fecha_fin')
    readonly_fields = ('rango', 'grupo_capacitacion', 'nivel', 'get_object_id_name')
    template = "admin/member/cargo_capacitacion/edit_inline/tabular.html"

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            self.readonly_fields += ('rango', 'grupo_capacitacion', 'nivel', 'get_object_id_name')
        else:
            self.readonly_fields += ('rango', 'grupo_capacitacion', 'nivel', 'get_object_id_name', 'fecha_inicio', 'fecha_fin')
        return self.readonly_fields

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        resolved = resolve(request.path_info)
        member = self.parent_model.objects.get(pk=resolved.kwargs['object_id'])
        if request.user.is_admin:
            return member.cargocapacitacion_set.all()
        else:
            cargos_capacitacion_pk = []
            for cargo_capacitacion in member.cargocapacitacion_set.filter(fecha_fin__isnull=True).all():
                if cargo_capacitacion.nivel.nombre.lower() == "sin nivel" or cargo_capacitacion.get_region and cargo_capacitacion.get_region.pk == request.user.region_id:
                    cargos_capacitacion_pk.append(cargo_capacitacion.pk)
            return member.cargocapacitacion_set.filter(fecha_fin__isnull=True, pk__in=cargos_capacitacion_pk)


class MiembroGrupoInline(admin.TabularInline):
    model = MiembroGrupo
    fields = ('grupo', 'fecha_inicio', 'fecha_baja')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_nacional:
            return qs
        return qs.filter(fecha_baja__isnull=True)


class MiembroDepartamentoInline(admin.TabularInline):
    model = MiembroDepartamento
    fields = ('departamento', 'fecha_inicio', 'fecha_baja')

    def has_add_permission(self, request, obj=None):
        return False


class MiembroRegionFilter(admin.SimpleListFilter):
    title = 'region'
    parameter_name = 'region'

    def lookups(self, request, model_admin):       
        if request.user.is_admin or request.user.is_nacional:
            regiones = Region.objects.all().order_by('nombre')
        else:
            regiones = Region.objects.filter(id=request.user.region_id)
        return ((region.pk, region.nombre) for region in regiones)

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrogrupo__fecha_baja__isnull=True,
                miembrogrupo__grupo__distrito__distrito_general__zona__region__pk=value)
        return queryset


class MiembroZonaFilter(admin.SimpleListFilter):
    title = 'zona'
    parameter_name = 'zona'

    def lookups(self, request, model_admin):
        if request.user.is_zona:
            return Zona.objects.filter(id=request.user.zona_id).values_list('pk', 'nombre')
        region = request.GET.get('region')
        if region:
            return Zona.objects.filter(region_id=region).values_list('pk', 'nombre').order_by('nombre')

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrogrupo__fecha_baja__isnull=True,
                miembrogrupo__grupo__distrito__distrito_general__zona__pk=value)
        return queryset


class MiembroDistritoGeneralFilter(admin.SimpleListFilter):
    title = 'distrito general'
    parameter_name = 'distrito_general'

    def lookups(self, request, model_admin):
        zona = request.GET.get('zona')
        if zona:
            return DistritoGeneral.objects.filter(zona_id=zona).values_list('pk', 'nombre').order_by('nombre')
        else:
            return

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrogrupo__fecha_baja__isnull=True,
                miembrogrupo__grupo__distrito__distrito_general__pk=value)
        return queryset


class MiembroDistritoFilter(admin.SimpleListFilter):
    title = 'distrito'
    parameter_name = 'distrito'

    def lookups(self, request, model_admin):
        distrito_general = request.GET.get('distrito_general')
        if distrito_general:
            return Distrito.objects.filter(distrito_general_id=distrito_general).values_list('pk', 'nombre').order_by('nombre')
        else:
            return

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrogrupo__fecha_baja__isnull=True,
                miembrogrupo__grupo__distrito__pk=value)
        return queryset


class MiembroGrupoFilter(admin.SimpleListFilter):
    title = 'grupo'
    parameter_name = 'grupo'

    def lookups(self, request, model_admin):
        distrito = request.GET.get('distrito')
        if distrito:
            return Grupo.objects.filter(distrito_id=distrito).values_list('pk', 'nombre').order_by('nombre')
        else:
            return

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrogrupo__fecha_baja__isnull=True,
                miembrogrupo__grupo__pk=value)
        return queryset


class MiembroDepartamentoFilter(admin.SimpleListFilter):
    title = 'departamento'
    parameter_name = 'departamento'

    def lookups(self, request, model_admin):
        return Departamento.objects.all()

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                miembrodepartamento__fecha_baja__isnull=True,
                miembrodepartamento__departamento__pk=value)
        return queryset


class AddMiembroGrupoInlineFormset(forms.models.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        field = self.form.base_fields['grupo']
        if self.user.is_region:
            field.queryset = Grupo.objects.filter(
                distrito__distrito_general__zona__region__id__exact=self.user.region_id)
            field.widget.rel.limit_choices_to = {
                'distrito__distrito_general__zona__region__id__exact': self.user.region_id}
        elif self.user.is_zona:
            field.queryset = Grupo.objects.filter(distrito__distrito_general__zona__id__exact=self.user.zona_id)
            field.widget.rel.limit_choices_to = {'distrito__distrito_general__zona__id__exact': self.user.zona_id}

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            instance.save()
        pass


class AddMiembroGrupoInline(admin.TabularInline):
    model = MiembroGrupo
    formset = AddMiembroGrupoInlineFormset
    fields = ['fecha_inicio', 'grupo']
    raw_id_fields = ('grupo',)
    max_num = 1

    def get_queryset(self, request):
        if request.user.is_admin or request.user.is_nacional:
            super().get_queryset(request)
        if request.user.is_region:
            return Grupo.objects.filter(distrito__distrito_general__zona__region__id=request.user.region_id)
        if request.user.is_zona:
            return Grupo.objects.filter(distrito__distrito_general__zona__id=request.user.zona_id)

    def get_formset(self, request, obj=None, **kwargs):
        form = super().get_formset(request, obj, **kwargs)
        form.user = request.user
        field = form.form.base_fields['grupo']
        if request.user.is_region:
            field.widget.rel.limit_choices_to = {
                'distrito__distrito_general__zona__region__id__exact': request.user.region_id}
        elif request.user.is_zona:
            field.widget.rel.limit_choices_to = {'distrito__distrito_general__zona__id__exact': request.user.zona_id}
        return form

    def get_min_num(self, request, obj):
        return 1 if (request.user.is_region or request.user.is_zona) else 0

    def get_extra(self, request, obj):
        return 1 if (request.user.is_region or request.user.is_zona) else 0


class ChangeMiembroGrupoInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        non_empty_forms = 0
        for form in self:
            if form.cleaned_data:
                non_empty_forms += 1
        formulario_vacio = non_empty_forms - len(self.deleted_forms) < 1

        for form in self.forms:
            try:
                form.instance.member.grupo
            except ObjectDoesNotExist:
                if formulario_vacio:
                    raise ValidationError("Asigne un grupo.")

            if form.cleaned_data != {}:
                if not hasattr(form, 'cleaned_data'):
                    continue
                cleaned_data = form.cleaned_data
                fecha_inicio = cleaned_data.get('fecha_inicio', '')
                grupo = cleaned_data.get('grupo', '')
                member = cleaned_data.get('member', '')

                if not (fecha_inicio and grupo):
                    raise forms.ValidationError(
                        "Rellene todos los campos para realizar el cambio de grupo"
                    )

                last_miembro_grupo = member.miembrogrupo_set.filter(fecha_baja__isnull=True).order_by('fecha_inicio').last()
                if last_miembro_grupo:
                    if last_miembro_grupo.fecha_inicio > fecha_inicio:
                        raise forms.ValidationError(
                            "La fecha de inicio es anterior a la del grupo anterior"
                        )

                    if last_miembro_grupo.grupo == grupo:
                        raise forms.ValidationError(
                            "El grupo seleccionado es el mismo que el grupo actual"
                        )

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            miembro_grupos = instance.member.miembrogrupo_set.filter(fecha_baja__isnull=True).all()
            for miembro_grupo in miembro_grupos:
                miembro_grupo.fecha_baja = instance.fecha_inicio
                miembro_grupo.save()
            instance.save()
        pass

    def get_queryset(self):
        # See get_queryset method of django.forms.models.BaseModelFormSet
        if not hasattr(self, '_queryset'):
            self._queryset = MiembroGrupo.objects.none()       
        return self._queryset


class ChangeMiembroGrupoInline(admin.TabularInline):
    """ Notes edit field """
    model = MiembroGrupo
    extra = 1
    max_num = 1
    fields = ('fecha_inicio', 'grupo')
    raw_id_fields = ('grupo',)
    verbose_name = 'Asignar nuevo de grupo'
    verbose_name_plural = 'Asignar nuevo de grupo'
    can_delete = False
    template = "admin/member/miembrogrupo/edit_inline/tabular.html"
    formset = ChangeMiembroGrupoInlineFormset


class ChangeMiembroDepartamentoInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        non_empty_forms = 0
        for form in self:
            if form.cleaned_data:
                non_empty_forms += 1
        formulario_vacio = non_empty_forms - len(self.deleted_forms) < 1

        for form in self.forms:
            try:
                form.instance.member.departamento
            except ObjectDoesNotExist:
                if formulario_vacio:
                    raise ValidationError("Asigne un departamento.")
            if form.cleaned_data != {}:
                if not hasattr(form, 'cleaned_data'):
                    continue
                cleaned_data = form.cleaned_data
                fecha_inicio = cleaned_data.get('fecha_inicio', '')
                departamento = cleaned_data.get('departamento', '')
                member = cleaned_data.get('member', '')

                if not (fecha_inicio and departamento):
                    raise forms.ValidationError(
                        "Rellene todos los campos para realizar el cambio de departamento"
                    )

                last_miembro_departamento = member.miembrodepartamento_set.filter(fecha_baja__isnull=True).order_by('fecha_inicio').last()
                if last_miembro_departamento:
                    if last_miembro_departamento.fecha_inicio and last_miembro_departamento.fecha_inicio > fecha_inicio:
                        raise forms.ValidationError(
                            "La fecha de inicio es anterior a la del departamento anterior"
                        )

                    if last_miembro_departamento.departamento == departamento:
                        raise forms.ValidationError(
                            "El departamento seleccionado es el mismo que el departamento actual"
                        )

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            miembro_departamentos = instance.member.miembrodepartamento_set.filter(fecha_baja__isnull=True).all()
            for miembro_departamento in miembro_departamentos:
                miembro_departamento.fecha_baja = instance.fecha_inicio
                miembro_departamento.save()
            instance.save()
            instance.member.departamento = instance.departamento
            instance.member.save()
        pass

    def get_queryset(self):
        # See get_queryset method of django.forms.models.BaseModelFormSet
        if not hasattr(self, '_queryset'):
            self._queryset = MiembroDepartamento.objects.none()
        return self._queryset


class ChangeMiembroDepartamentoInline(admin.TabularInline):
    """ Notes edit field """
    model = MiembroDepartamento
    extra = 1
    max_num = 1
    fields = ('fecha_inicio', 'departamento')
    raw_id_fields = ('grupo',)
    verbose_name = 'Asignar nuevo departamento'
    verbose_name_plural = 'Asignar nuevo departamento'
    can_delete = False
    template = "admin/member/miembrogrupo/edit_inline/tabular.html"
    formset = ChangeMiembroDepartamentoInlineFormset


class DocumentoInline(admin.TabularInline):
    model = Documento
    extra = 1


class AltaMiembroAdmin(admin.ModelAdmin):
    readonly_fields = ('member',)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        member = obj.member
        ultima_alta = member.altamiembro_set.order_by("fecha").last()
        member.fecha_ingreso = ultima_alta.fecha
        member.alta = ultima_alta.motivo
        member.save()


class BajaMiembroAdmin(admin.ModelAdmin):
    readonly_fields = ('member',)


class AddAltaMiembroInlineFormset(forms.models.BaseInlineFormSet):

    def save(self, commit=True):
        instances = super().save(commit=False)
        for instance in instances:
            instance.save()
            instance.member.fecha_ingreso = self.cleaned_data[0]['fecha']
            instance.member.alta = self.cleaned_data[0]['motivo']
        pass


class AddAltaMiembroInline(admin.TabularInline):
    model = AltaMiembro
    formset = AddAltaMiembroInlineFormset
    extra = 1
    max_num = 1
    verbose_name = 'Datos de alta'
    verbose_name_plural = 'Datos de alta'
    can_delete = False
    template = "admin/member/alta_miembro/edit_inline/tabular.html"

    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return True
    

class AltaMiembroInline(admin.TabularInline):
    model = AltaMiembro
    extra = 0

    readonly_fields = ('fecha', 'motivo', 'origen', 'fecha_llegada_extranjero')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class BajaMiembroInline(admin.TabularInline):
    model = BajaMiembro
    extra = 0

    readonly_fields = ('fecha', 'motivo', 'destino')
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class NullListFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('1', 'Activos', ),
            ('0', 'Dados de baja', ),
        )

    def queryset(self, request, queryset):
        if self.value() in ('0', '1'):
            kwargs = {'{0}__isnull'.format(self.parameter_name) : self.value() == '1' }
            return queryset.filter(**kwargs)
        return queryset


class FechaBajaNullListFilter(NullListFilter):
    title = u'activo'
    parameter_name = u'fecha_baja'


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member
        fields = '__all__'

    def clean(self):
        pk = self.instance.pk

        dni = self.cleaned_data['dni']
        if dni:
            members = [str(member.pk) for member in Member.objects.filter(dni=dni).filter(~Q(pk=pk)).all()]
            if members:
                members_list = ', '.join(members)
                self.add_error('dni', f"El DNI {dni} ya está registrado en la base de datos. Miembro: {members_list}")

        movil = self.cleaned_data['movil']
        if movil:
            members = [str(member.pk) for member in Member.objects.filter(movil=movil).filter(~Q(pk=pk)).all()]
            if members:
                members_list = ', '.join(members)
                self.add_error('movil', f"El número de móvil {movil} ya está registrado en la base de datos. Miembro: {members_list}")

        return self.cleaned_data


class MemberAdmin(admin.ModelAdmin):
    form = MemberForm
    search_fields = ('nombre', 'apellidos', 'dni', 'email')
    ordering = ('nombre',)
    exclude = ('subscripcion', 'fecha_ingreso', 'fecha_baja', 'alta', 'baja', 'baja_lopd')
    readonly_fields = ("departamento",)

    raw_id_fields = ['recomendado_por_1', 'recomendado_por_2', 'gohonzon_familiar']
    actions = ['update_grupo']
    formfield_overrides = {
        models.IntegerField: {'widget': TextInput(attrs={'size': '15', 'autocomplete': 'off'})},
        models.CharField: {'widget': TextInput(attrs={'size': '50', 'autocomplete': 'off'})},
    }
    omamori_gohonzon = forms.BooleanField(initial=False, required=False)

    def get_list_display(self, request):
        if request.user.is_admin or request.user.is_nacional:
            return ('nombre', 'apellidos', 'activo', 'departamento', 'movil', 'email', 'region', 'zona', 'distrito_general', 'distrito', 'grupo', 'localidad')
        else:
            return ('nombre', 'apellidos', 'departamento', 'movil', 'email', 'region', 'zona', 'distrito_general', 'distrito', 'grupo', 'localidad')

    def get_list_filter(self, request):
        if request.user.is_admin or request.user.is_nacional:
            return (FechaBajaNullListFilter, 'departamento', MiembroRegionFilter, MiembroZonaFilter,
                    MiembroDistritoGeneralFilter, MiembroDistritoFilter, MiembroGrupoFilter)
        else:
            return ('departamento', MiembroRegionFilter, MiembroZonaFilter, MiembroDistritoGeneralFilter,
                    MiembroDistritoFilter, MiembroGrupoFilter)

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super(MemberAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name in ('observaciones', 'observaciones_al_estudio'):
            formfield.widget = forms.Textarea(attrs={'rows': 3, 'cols': 100})
        return formfield

    def add_view(self, request, form_url='', extra_context={}):
        self.inlines = [AddAltaMiembroInline, ChangeMiembroGrupoInline, ChangeMiembroDepartamentoInline]
        return super(MemberAdmin, self).add_view(request, form_url, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context={}):
        member = Member.objects.get(pk=object_id)
        if not member.fecha_baja:
            self.inlines = [AltaMiembroInline, BajaMiembroInline, DocumentoInline, MiembroDepartamentoInline,
                            ChangeMiembroDepartamentoInline, MiembroGrupoInline, ChangeMiembroGrupoInline,
                            CargoInline, CargoCapacitacionInline]
        else:
            self.inlines = [AltaMiembroInline, BajaMiembroInline, DocumentoInline, MiembroDepartamentoInline]
        return super(MemberAdmin, self).change_view(request, object_id, form_url, extra_context)

    def has_delete_permission(self, request, obj=None):
        try:
            if not obj.fecha_baja:
                return True
        except:
            return True

    def get_queryset(self, request):
        if request.user.is_nacional:
            return super().get_queryset(request).filter(baja_lopd=False).distinct()
        if request.user.is_region:
            id = request.user.miembro.region_id
            return super().get_queryset(request).filter(
                baja_lopd=False,
                fecha_baja__isnull=True,
                grupo__distrito__distrito_general__zona__region__pk=id).distinct()
        if request.user.is_zona:
            id = request.user.miembro.zona_id
            return super().get_queryset(request).filter(
                baja_lopd=False,
                fecha_baja__isnull=True,
                grupo__distrito__distrito_general__zona__pk=id).distinct()

    def update_grupo(self, request, queryset):
        if 'apply' in request.POST:
            grupo_id = request.POST.get('id_grupo')
            grupo = Grupo.objects.get(pk=grupo_id)
            fecha_inicio = request.POST.get('fecha_inicio')
            errores = 0
            for member in queryset:
                result = member.cambiar_grupo(grupo, fecha_inicio)
                if not result:
                    self.message_user(request, f"Error en {member}, fecha incorrecta", level=messages.ERROR)
                    errores += 1
            self.message_user(request, f"Cambiado el grupo de {queryset.count() - errores} miembros")
            return HttpResponseRedirect(request.get_full_path())
        elif 'cancel' in request.POST:
            self.message_user(request, "Acción cancelada")
            return HttpResponseRedirect(request.get_full_path())

        fecha_alta_form = FechaAltaForm()
        return render(request,
                      'admin/estructura/estructura/grupo_intermediate.html',
                      context={'members':queryset,
                               'opts': Grupo._meta,
                               'form': fecha_alta_form}
                      )

    update_grupo.short_description = "Cambiar de grupo"

    def changelist_view(self, request, extra_context=None):
        estructura_actual = {}
        estructura_anterior = {}
        referer_url = request.META.get('HTTP_REFERER')
        parsed = urlparse.urlparse(referer_url)
        for campo in estructura:
            try:
                estructura_actual[campo] = request.GET[campo]
            except KeyError:
                pass
            try:
                estructura_anterior[campo] = parse_qs(parsed.query).get(campo)[0]
            except TypeError:
                pass
        cambios_estructura = [k for k in estructura_actual if k in estructura_anterior and estructura_anterior[k] != estructura_actual[k]]
        if len(cambios_estructura) == 1:
            args = str(self.opts).split('.')
            url = reverse('admin:%s_%s_changelist' % (args[0], args[1]))
            campo_index = estructura.index(cambios_estructura[0])
            # Con esto se detecta que antes había un nivel más de estructura y se ha cambiado un nivel superior
            try:
                campos_estructura = estructura[:campo_index + 1]
                if estructura_actual.get(estructura[campo_index + 1]):
                    query = ''
                    for campo in campos_estructura:
                        query += f'&{campo}={estructura_actual[campo]}'
                    return HttpResponseRedirect(f'{url}?{query[1:]}')
            except:
                pass
        return super(MemberAdmin,self).changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class ExtendedUserAdmin(UserAdmin):

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser',
                                    'groups')}),
        (None, {'fields': ('caducidad', 'miembro',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Permissions', {'fields': ('is_active', 'is_superuser',
                                    'groups')}),
        (None, {'fields': ('miembro',)}),
    )
    list_display = ('username', 'miembro', 'is_active', 'is_superuser', 'grupo', 'caducidad')
    raw_id_fields = ('miembro',)
    ordering = ('username',)

    def grupo(self, obj):
        if obj.groups.all():
            return ' - '.join([group.name for group in obj.groups.all()])
        else:
            return ' - '


class MiembroGrupoAdmin(admin.ModelAdmin):
    search_fields = ('member__nombre', 'member__apellidos', 'grupo__nombre',)
    raw_id_fields = ('member', 'grupo',)


class MiembroDepartamentoAdmin(admin.ModelAdmin):
    search_fields = ('member__nombre', 'member__apellidos', 'departamento__nombre',)
    raw_id_fields = ('member', 'departamento',)


admin.site.register(Member, MemberAdmin)
admin.site.register(ExtendedUser, ExtendedUserAdmin)
admin.site.register(MiembroGrupo, MiembroGrupoAdmin)
admin.site.register(MiembroDepartamento, MiembroDepartamentoAdmin)

admin.site.register(Estudio)
admin.site.register(AltaMiembro, AltaMiembroAdmin)
admin.site.register(BajaMiembro, BajaMiembroAdmin)
