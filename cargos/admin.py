from django import forms
from django.contrib import admin

from cargos.models import *


class CargoForm(forms.ModelForm):

    region = forms.ChoiceField(required=False, label="Región", widget=forms.Select(attrs={"class": "customDropDown"}))
    zona = forms.ChoiceField(required=False, label="Zona", widget=forms.Select(attrs={"class": "customDropDown"}))
    distrito_general = forms.ChoiceField(
        required=False, label="Distrito General", widget=forms.Select(attrs={"class": "customDropDown"})
    )
    distrito = forms.ChoiceField(
        required=False, label="Distrito", widget=forms.Select(attrs={"class": "customDropDown"})
    )
    grupo = forms.ChoiceField(required=False, label="Grupo", widget=forms.Select(attrs={"class": "customDropDown"}))

    class Meta:
        model = Cargo
        fields = "__all__"

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        user = self.current_user
        try:
            if user.is_region:
                NIVEL_CHOICES = [
                    (nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_RER=True).order_by("orden")
                ]
            else:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.all().order_by("orden")]
            NIVEL_CHOICES.insert(0, ("", "----"))
            self.fields["nivel"].choices = NIVEL_CHOICES
        except (AttributeError, KeyError):
            pass
        try:
            if user.is_region:
                RANGO_CHOICES = [
                    (nivel.pk, nivel.nombre) for nivel in Rango.objects.filter(asignable_RER=True).order_by()
                ]
            else:
                RANGO_CHOICES = [(rango.pk, rango.nombre) for rango in Rango.objects.order_by()]
            self.fields["rango"].choices = RANGO_CHOICES
        except (AttributeError, KeyError):
            pass

    def clean_zona(self):
        pass


class CargoAdmin(admin.ModelAdmin):
    form = CargoForm
    list_display = ("member", "activo", "rango", "departamento", "nivel", "get_object_id_name")
    list_filter = ("rango", "departamento", "nivel")
    search_fields = ("member__nombre", "member__apellidos")
    raw_id_fields = ("member",)

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super().get_queryset(request)
        if request.user.is_admin:
            return qs
        if request.user.is_region:
            region = request.user.region
            niveles = Nivel.objects.filter(asignable_RER=True)
            cargos = Cargo.active_objects.filter(nivel__in=niveles)
            cargos_en_region = []
            for cargo in cargos:
                cargo_region = cargo.get_region
                if cargo_region and cargo_region.nombre == region:
                    cargos_en_region.append(cargo.pk)
            return Cargo.active_objects.filter(pk__in=cargos_en_region)
        if request.user.is_zona:
            zona = request.user.zona
            niveles = Nivel.objects.filter(asignable_REZ=True)
            cargos = Cargo.active_objects.filter(nivel__in=niveles)
            cargos_en_zona = []
            for cargo in cargos:
                cargo_zona = cargo.get_zona
                if cargo_zona and cargo_zona.nombre == zona:
                    cargos_en_zona.append(cargo.pk)
            return Cargo.active_objects.filter(pk__in=cargos_en_zona)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_admin:
            self.readonly_fields = ("member",)
        else:
            self.readonly_fields = ("member", "rango", "nivel", "departamento", "object_id")
        return self.readonly_fields

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, **kwargs)
        form.current_user = request.user
        return form


class RangoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "orden")
    ordering = ("orden",)


class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "orden")
    ordering = ("orden",)


class NivelAdmin(admin.ModelAdmin):
    list_display = ("nombre", "codigo", "orden")
    ordering = ("orden",)

    def has_add_permission(self, request, obj=None):
        return False


class CargoCapacitacionForm(forms.ModelForm):

    region = forms.ChoiceField(required=False, label="Región", widget=forms.Select(attrs={"class": "customDropDown"}))
    zona = forms.ChoiceField(required=False, label="Zona", widget=forms.Select(attrs={"class": "customDropDown"}))
    distrito_general = forms.ChoiceField(
        required=False, label="Distrito General", widget=forms.Select(attrs={"class": "customDropDown"})
    )
    distrito = forms.ChoiceField(
        required=False, label="Distrito", widget=forms.Select(attrs={"class": "customDropDown"})
    )
    grupo = forms.ChoiceField(required=False, label="Grupo", widget=forms.Select(attrs={"class": "customDropDown"}))

    class Meta:
        model = CargoCapacitacion
        fields = "__all__"

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        user = self.current_user
        try:
            if user.is_region:
                NIVEL_CHOICES = [
                    (nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_RER=True).order_by("orden")
                ]
            elif user.is_zona:
                NIVEL_CHOICES = [
                    (nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_REZ=True).order_by("orden")
                ]
            else:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.all().order_by("orden")]
            NIVEL_CHOICES.insert(0, ("", "----"))
            self.fields["nivel"].choices = NIVEL_CHOICES
        except (AttributeError, KeyError):
            pass
        try:
            if user.is_region:
                RANGO_CHOICES = [
                    (nivel.pk, nivel.nombre)
                    for nivel in RangoCapacitacion.objects.filter(asignable_RER=True).order_by()
                ]
            elif user.is_zona:
                RANGO_CHOICES = [
                    (nivel.pk, nivel.nombre)
                    for nivel in RangoCapacitacion.objects.filter(nombre="Miembro integrante").order_by()
                ]
            else:
                RANGO_CHOICES = [(rango.pk, rango.nombre) for rango in RangoCapacitacion.objects.order_by()]
            self.fields["rango"].choices = RANGO_CHOICES
        except (AttributeError, KeyError):
            pass


class CargoCapacitacionAdmin(admin.ModelAdmin):
    form = CargoCapacitacionForm
    list_display = (
        "member",
        "activo",
        "rango",
        "departamento",
        "nivel",
        "grupo_capacitacion",
        "fecha_inicio",
        "fecha_fin",
    )
    list_filter = ("rango", "departamento", "nivel", "grupo_capacitacion")
    search_fields = ("member__nombre", "member__apellidos")
    raw_id_fields = ("member",)

    def get_queryset(self, request):
        """
        Filter the objects displayed in the change_list to only
        display those for the currently signed in user.
        """
        qs = super().get_queryset(request)
        if request.user.is_admin:
            return qs
        if request.user.is_region:
            region = request.user.region
            niveles = Nivel.objects.filter(asignable_RER=True)
            cargos = CargoCapacitacion.active_objects.filter(nivel__in=niveles)
            cargos_en_region = []
            for cargo in cargos:
                cargo_region = cargo.get_region
                if cargo_region and cargo_region.nombre == region:
                    cargos_en_region.append(cargo.pk)
            return CargoCapacitacion.active_objects.filter(pk__in=cargos_en_region)
        if request.user.is_zona:
            zona = request.user.zona
            niveles = Nivel.objects.filter(asignable_REZ=True)
            cargos = CargoCapacitacion.active_objects.filter(nivel__in=niveles)
            cargos_en_zona = []
            for cargo in cargos:
                cargo_zona = cargo.get_zona
                if cargo_zona and cargo_zona.nombre == zona:
                    cargos_en_zona.append(cargo.pk)
            return CargoCapacitacion.active_objects.filter(pk__in=cargos_en_zona)
        return qs

    def has_add_permission(self, request, obj=None):
        return False

    def get_form(self, request, *args, **kwargs):
        form = super().get_form(request, **kwargs)
        form.current_user = request.user
        return form

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            if request.user.is_admin:
                self.readonly_fields = ("member",)
            else:
                self.readonly_fields = ("member", "nivel", "rango", "departamento", "object_id", "grupo_capacitacion")
        return self.readonly_fields


class CustomContentTypeChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "Pretty name for #%d" % obj.id


admin.site.register(Cargo, CargoAdmin)
admin.site.register(Rango, RangoAdmin)
admin.site.register(Departamento, DepartamentoAdmin)
admin.site.register(Nivel, NivelAdmin)
admin.site.register(GrupoCapacitacion)
admin.site.register(RangoCapacitacion)
admin.site.register(CargoCapacitacion, CargoCapacitacionAdmin)
