from django import forms
from django.conf import settings
from django.utils.timezone import datetime

from cargos.models import Nivel, Departamento, Rango, GrupoCapacitacion, RangoCapacitacion, Cargo, CargoCapacitacion
from estructura.models import Region
from gestion.models import MiembroGrupo


class CargoPostForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    rango = forms.ChoiceField(required=True)
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.order_by(),
        required=True)
    nivel = forms.ChoiceField(required=True)
    region = forms.ChoiceField(required=False, label='Región', widget=forms.Select(attrs={'class':'customDropDown'}))
    zona = forms.ChoiceField(required=False, label='Zona', widget=forms.Select(attrs={'class':'customDropDown'}))
    distrito_general = forms.ChoiceField(required=False, label='Distrito General', widget=forms.Select(attrs={'class':'customDropDown'}))
    distrito = forms.ChoiceField(required=False, label='Distrito', widget=forms.Select(attrs={'class':'customDropDown'}))
    grupo = forms.ChoiceField(required=False, label='Grupo', widget=forms.Select(attrs={'class':'customDropDown'}))
    object_id = forms.IntegerField(required=False)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if user.is_region:
                RANGO_CHOICES = [(rango.pk, rango.nombre) for rango in Rango.objects.filter(asignable_RER=True).order_by('orden')]
            else:
                RANGO_CHOICES = [(rango.pk, rango.nombre) for rango in Rango.objects.all().order_by('orden')]
            RANGO_CHOICES.insert(0, ('', '----'))
            self.fields['rango'].choices = RANGO_CHOICES
        except AttributeError:
            pass
        try:
            if user.is_region:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_RER=True).order_by('orden')]
            elif user.is_zona:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_REZ=True).order_by('orden')]
            else:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.all().order_by('orden')]
            NIVEL_CHOICES.insert(0, ('', '----'))
            self.fields['nivel'].choices = NIVEL_CHOICES
        except AttributeError:
            pass
    
    def clean_region(self):
        return None


class CargoCapacitacionPostForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    rango = forms.ChoiceField(required=True)
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.order_by(),
        required=True)
    grupo_capacitacion = forms.ModelChoiceField(
        queryset=GrupoCapacitacion.objects.order_by(),
        required=True)
    nivel = forms.ChoiceField(required=True)
    region = forms.ChoiceField(required=False, label='Región', widget=forms.Select(attrs={'class':'customDropDown'}))
    zona = forms.ChoiceField(required=False, label='Zona', widget=forms.Select(attrs={'class':'customDropDown'}))
    distrito_general = forms.ChoiceField(required=False, label='Distrito General', widget=forms.Select(attrs={'class':'customDropDown'}))
    distrito = forms.ChoiceField(required=False, label='Distrito', widget=forms.Select(attrs={'class':'customDropDown'}))
    grupo = forms.ChoiceField(required=False, label='Grupo', widget=forms.Select(attrs={'class':'customDropDown'}))
    object_id = forms.IntegerField(required=False)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if user.is_region:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_RER=True).order_by('orden')]
            elif user.is_zona:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.filter(asignable_REZ=True).order_by('orden')]
            else:
                NIVEL_CHOICES = [(nivel.pk, nivel.nombre) for nivel in Nivel.objects.all().order_by('orden')]
            NIVEL_CHOICES.insert(0, ('', '----'))
            self.fields['nivel'].choices = NIVEL_CHOICES
        except AttributeError:
            pass
        try:
            if user.is_region:
                RANGO_CHOICES = [(nivel.pk, nivel.nombre) for nivel in RangoCapacitacion.objects.filter(asignable_RER=True).order_by()]
            elif user.is_zona:
                RANGO_CHOICES = [(nivel.pk, nivel.nombre) for nivel in RangoCapacitacion.objects.filter(nombre="Miembro integrante").order_by()]
            else:
                RANGO_CHOICES = [(rango.pk, rango.nombre) for rango in RangoCapacitacion.objects.order_by()]                
            self.fields['rango'].choices = RANGO_CHOICES
        except AttributeError:
            pass


class DateInput(forms.DateInput):
    input_type = 'date'
    value = datetime.now().strftime("%d-%m-%Y"),


class FechaAltaForm(forms.ModelForm):

    class Meta:
       model = MiembroGrupo
       fields = ['fecha_inicio']
       widgets = {
           'fecha_inicio': DateInput(),
       }


class FechaBajaCargoForm(forms.ModelForm):

    class Meta:
       model = Cargo
       fields = ['fecha_fin']
       widgets = {
           'fecha_baja': DateInput(),
       }