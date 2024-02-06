from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils import timezone

from cargos.utils import convertir_nombre_modelo
from gestion.models import Member


class Rango(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=5, blank=True, null=True)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True, editable=False)
    orden = models.IntegerField(blank=True, null=True)
    asignable_RER = models.BooleanField(default=False, verbose_name='asignable por RER')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'rango de responsabilidad'
        verbose_name_plural = 'rangos de responsabilidad'


class Departamento(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True, editable= False)
    orden = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return str(self.nombre)


class Nivel(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=50)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True, editable=False)
    orden = models.IntegerField(blank=True, null=True)
    asignable_RER = models.BooleanField(default=False, verbose_name='asignable por RER')
    asignable_REZ = models.BooleanField(default=False, verbose_name='asignable por REZ')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'nivel'
        verbose_name_plural = 'niveles'


class CargosActivosManager(models.Manager):
    def get_queryset(self):
        return super(CargosActivosManager, self).get_queryset().filter(fecha_fin__isnull=True).filter(member__fecha_baja__isnull=True)


class Cargo(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='miembro')
    rango = models.ForeignKey(Rango, on_delete=models.SET_NULL, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, blank=True, null=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    objects = models.Manager()
    active_objects = CargosActivosManager()

    class Meta:
        # ordering = ['fecha_inicio']
        verbose_name = 'cargo de responsabilidad'
        verbose_name_plural = 'cargos de responsabilidad'

    def delete(self, fecha_baja=None, razones_tecnicas=False):
        if not fecha_baja:
            fecha_baja = timezone.localtime(timezone.now())
        self.fecha_fin = fecha_baja
        self.save()

    @property
    def get_nivel_codigo(self):
        try:
            return Nivel.objects.get(pk=self.nivel.pk).codigo
        except:
            return ""

    def get_object_id_name_method(self):
        try:
            modelo = apps.get_model('estructura', convertir_nombre_modelo(self.nivel.nombre))
            instancia = modelo.objects.get(pk=self.object_id)
            return instancia.nombre
        except (LookupError, ObjectDoesNotExist):
            return ""
    get_object_id_name_method.short_description = "A cargo de"
    get_object_id_name = property(get_object_id_name_method)

    @property
    def rango_codigo(self):
        try:
            return self.rango.codigo
        except AttributeError:
            return ""

    @property
    def codigo(self):
        departamento = '' if self.departamento.nombre == 'Sin departamento' else self.departamento.nombre
        rango_codigo = '' if self.rango_codigo == 'R' and departamento else self.rango_codigo
        nivel_codigo = self.get_nivel_codigo or "N"
        guion = '' if nivel_codigo == 'N' else ' - '
        return f'{rango_codigo}{departamento}{guion}{nivel_codigo}'

    def __str__(self):
        return f'{self.codigo}{self.get_object_id_name} - {self.member}'

    @property
    def nombre_cargo(self):
        departamento = '' if self.departamento.nombre == 'Sin departamento' else self.departamento.nombre
        rango_codigo = '' if self.rango_codigo == 'R' and departamento else self.rango_codigo
        return "{}{}{} - {}".format(rango_codigo,
                                    departamento,
                                    self.get_nivel_codigo or "N",
                                    self.member,)

    @property
    def get_region(self):
        nombre_clase = self.nivel.nombre.replace(" ", "")
        try:
            Clase = apps.get_model(app_label='estructura', model_name=nombre_clase)
        except LookupError:
            return None
        try:
            objeto = Clase.objects.get(pk=self.object_id)
        except Clase.DoesNotExist:
            return None
        try:
            return objeto.region()
        except TypeError:
            return objeto.region

    @property
    def get_zona(self):
        nombre_clase = self.nivel.nombre.replace(" ", "")
        try:
            Clase = apps.get_model(app_label='estructura', model_name=nombre_clase)
        except LookupError:
            return None
        try:
            objeto = Clase.objects.get(pk=self.object_id)
            print("aqui si que si")
        except (Clase.DoesNotExist, AttributeError):
            return None
        try:
            return objeto.zona()
        except TypeError:
            return objeto.zona

    def activo(self):
        if not self.fecha_fin:
            return True
        else:
            return False
    activo.boolean = True


class GrupoCapacitacion(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True, editable= False)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'grupo de capacitación'
        verbose_name_plural = 'grupos de capacitación'


class RangoCapacitacion(models.Model):
    nombre = models.CharField(max_length=50)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True, editable=False)
    asignable_RER = models.BooleanField(default=False, verbose_name='asignable por RER')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'rango de capacitación'
        verbose_name_plural = 'rangos de capacitación'


class CargoCapacitacion(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, verbose_name='miembro')
    rango = models.ForeignKey(RangoCapacitacion, on_delete=models.SET_NULL, blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, blank=True, null=True)
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    grupo_capacitacion = models.ForeignKey(GrupoCapacitacion, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

    objects = models.Manager()
    active_objects = CargosActivosManager()

    class Meta:
        # ordering = ['fecha_inicio']
        verbose_name = 'cargo de capacitación'
        verbose_name_plural = 'cargos de capacitación'

    def delete(self, fecha_baja=None):
        if not fecha_baja:
            fecha_baja = timezone.localtime(timezone.now())
        self.fecha_fin = fecha_baja
        self.save()

    @property
    def get_nivel_codigo(self):
        try:
            return Nivel.objects.get(pk=self.nivel.pk).codigo
        except:
            return ""

    def get_object_id_name_method(self):
        try:
            modelo = apps.get_model('estructura', convertir_nombre_modelo(self.nivel.nombre))
            instancia = modelo.objects.get(pk=self.object_id)
            return instancia.nombre
        except LookupError:
            return ""
    get_object_id_name_method.short_description = "A cargo de"
    get_object_id_name = property(get_object_id_name_method)
    
    @property
    def rango_codigo(self):
        
        try:
            return self.rango.codigo
        except AttributeError:
            return ""

    @property
    def nombre_cargo(self):
        departamento = '' if self.departamento.nombre == 'Sin departamento' else self.departamento.nombre
        rango_codigo = '' if self.rango_codigo == 'R' and departamento else self.rango_codigo
        return "{}{}{} - {}".format (rango_codigo,
                                departamento,
                                self.get_nivel_codigo or "N",
                                self.member,)

    @property
    def get_region(self):
        nombre_clase = self.nivel.nombre.replace(" ", "")
        try:
            Clase = apps.get_model(app_label='estructura', model_name=nombre_clase)
        except LookupError:
            return None
        try:
            objeto = Clase.objects.get(pk=self.object_id)
        except Clase.DoesNotExist:
            return None
        try:
            return objeto.region()
        except TypeError:
            return objeto.region

    @property
    def get_zona(self):
        nombre_clase = self.nivel.nombre.replace(" ", "")
        try:
            Clase = apps.get_model(app_label='estructura', model_name=nombre_clase)
        except LookupError:
            return None
        try:
            objeto = Clase.objects.get(pk=self.object_id)
        except (Clase.DoesNotExist, AttributeError):
            return None
        try:
            return objeto.zona()
        except TypeError:
            return objeto.zona

    def activo(self):
        if not self.fecha_fin:
            return True
        else:
            return False
    activo.boolean = True
