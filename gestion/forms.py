from django import forms

from gestion.models import AltaMiembro, Member
from django.contrib.auth.forms import PasswordChangeForm

class ConfirmDeleteForm(forms.ModelForm):
    confirm = forms.CharField(label='Confirm your name', max_length=100)

    class Meta:
        model = Member
        fields = []

    def clean(self):
        confirm = super().clean().get('confirm')

        if self.instance.name.lower() != confirm.lower():
            raise forms.ValidationError('Confirmation incorrect')


class ReactivarForm(forms.ModelForm):
    fecha = forms.DateField(widget=forms.HiddenInput(), label="Fecha ingreso SG")
    fecha_llegada_extranjero = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False, label="Fecha incorporación SGEs")

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
        model = AltaMiembro
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].disabled = True


class DeshacerBajaForm(forms.ModelForm):
    pass

class MyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["old_password"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password1"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        self.fields["new_password2"].widget = forms.PasswordInput(attrs={"class": "form-control"})
        #self.fields[""]
