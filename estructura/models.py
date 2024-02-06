from django.db import models
from django.utils import timezone

from cargos.models import Cargo, Nivel


class Tracker(models.Model):
    class Meta:
        abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tracked_field = self.TRACKED_FIELD
        try:
            original = getattr(self, self._tracked_field)
            self._original_value = original.pk
        except:
            self._original_value = 0

    def save(self, *args, **kwargs):
        if self._original_value != getattr(self, self._tracked_field):
            nivel_nombre = self.__class__._meta.verbose_name.title()
            nivel = Nivel.objects.get(nombre=nivel_nombre.title())
            estructura_anterior = HistoricoEstructura.objects.filter(nivel=nivel, object_id=self.pk).last()
            if estructura_anterior:
                estructura_anterior.fecha_baja = timezone.localtime(timezone.now())
                estructura_anterior.save()
            super().save(*args, **kwargs)
            HistoricoEstructura.objects.create(nivel=nivel, object_id=self.pk,
                fk=getattr(self, self._tracked_field).pk)
        else:
            super().save(*args, **kwargs)

        
class HistoricoEstructura(models.Model):
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    fk = models.PositiveIntegerField()
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField(blank=True, null=True)


class Region(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="región")
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField

    class Meta:
        indexes = [
            models.Index(fields=['nombre',]),
        ]
        ordering = ['nombre']
        verbose_name = 'región'
        verbose_name_plural = 'regiones'

    def __str__(self):
        return str(self.nombre)

    @property
    def cargos(self):
        nivel = Nivel.objects.get(nombre='Región')
        cargos = Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
        return '<p>' + '<br/>'.join(cargo.nombre_cargo for cargo in cargos) + '</p>'

    @property
    def cargos_set(self):
        nivel = Nivel.objects.get(nombre='Región')
        return Cargo.active_objects.filter(nivel=nivel).filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()

    def region(self):
        return self


class Zona(Tracker):
    print("Nombre: ")

    nombre = models.CharField(max_length=50, verbose_name="zona")
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField

    

    TRACKED_FIELD = 'region'

    class Meta:
        indexes = [
            models.Index(fields=['nombre',]),
            models.Index(fields=['nombre', 'region']),
        ]

    def __str__(self):
        return self.nombre

    @property
    def nombre_completo(self):
        return f'{self.region} - {self.nombre}'

    @property
    def cargos(self):
        nivel = Nivel.objects.get(nombre='Zona')
        cargos = Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
        return '<p>' + '<br/>'.join(cargo.nombre_cargo for cargo in cargos) + '</p>'

    @property
    def cargos_set(self):
        nivel = Nivel.objects.get(nombre='Zona')
        return Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()

    def zona(self):
        return self


class DistritoGeneral(Tracker):
    nombre = models.CharField(max_length=50, verbose_name="distrito general")
    zona = models.ForeignKey(Zona, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField

    TRACKED_FIELD = 'zona'

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Distrito General'
        verbose_name_plural = 'Distritos Generales'
        indexes = [
            models.Index(fields=['nombre',]),
            models.Index(fields=['nombre', 'zona']),
        ]

    def __str__(self):
        return str(self.nombre)

    def region(self):
        return self.zona.region
    region.short_description = 'region'

    @property
    def cargos(self):
        nivel = Nivel.objects.get(nombre='Distrito General')
        cargos = Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
        return '<p>' + '<br/>'.join(cargo.nombre_cargo for cargo in cargos) + '</p>'

    @property
    def cargos_set(self):
        nivel = Nivel.objects.get(nombre='Distrito General')
        return Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()


class Distrito(Tracker):
    nombre = models.CharField(max_length=50, verbose_name="distrito")
    distrito_general = models.ForeignKey(DistritoGeneral, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField

    TRACKED_FIELD = 'distrito_general'

    class Meta:
        indexes = [
            models.Index(fields=['nombre',]),
            models.Index(fields=['nombre', 'distrito_general']),
        ]

    def __str__(self):
        return str(self.nombre)

    def zona(self):
        return self.distrito_general.zona
    zona.short_description = 'zona'

    def region(self):
        return self.distrito_general.zona.region
    region.short_description = 'region'

    @property
    def cargos(self):
        nivel = Nivel.objects.get(nombre='Distrito')
        cargos = Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
        return '<p>' + '<br/>'.join(cargo.nombre_cargo for cargo in cargos) + '</p>'

    @property
    def cargos_set(self):
        nivel = Nivel.objects.get(nombre='Distrito')
        return Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()


class Grupo(Tracker):
    nombre = models.CharField(max_length=50)
    distrito = models.ForeignKey(Distrito, on_delete=models.CASCADE)
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_baja = models.DateField
    miembros = models.ManyToManyField('gestion.Member', through='gestion.MiembroGrupo')

    TRACKED_FIELD = 'distrito'

    class Meta:
        indexes = [
            models.Index(fields=['nombre',]),
            models.Index(fields=['nombre', 'distrito']),
        ]

    def __str__(self):
        return str(self.nombre)

    def distrito_general(self):
        return self.distrito.distrito_general
    distrito_general.short_description = 'distrito general'

    def zona(self):
        return self.distrito.distrito_general.zona
    zona.short_description = 'zona'

    def region(self):
        return self.distrito.distrito_general.zona.region
    region.short_description = 'region'

    @property
    def cargos(self):
        nivel = Nivel.objects.get(nombre='Grupo')
        cargos = Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
        return '<p>' + '<br/>'.join(cargo.nombre_cargo for cargo in cargos) + '</p>'

    @property
    def cargos_set(self):
        nivel = Nivel.objects.get(nombre='Grupo')
        return Cargo.active_objects.filter(nivel=nivel) \
            .filter(object_id=self.pk).order_by('departamento__orden', 'rango__orden', 'member').distinct()
