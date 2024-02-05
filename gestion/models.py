import unicodedata
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group
from django.db import connection, models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .validators import ValidateFileSize, validate_dni, validate_movil


def user_directory_path(instance, filename):
    sanitized_filename = unicodedata.normalize("NFKD", filename).encode("ascii","ignore").decode("ascii")
    return '{}/{}'.format(instance.pk, sanitized_filename)

def document_directory_path(instance, filename):
    sanitized_filename = unicodedata.normalize("NFKD", filename).encode("ascii","ignore").decode("ascii")
    return '{}/{}'.format(instance.member.pk, sanitized_filename)

def return_date_time():
    now = timezone.localtime(timezone.now())
    return now + timezone.timedelta(days=365)


class ExtendedUser(AbstractUser):
    miembro = models.ForeignKey('gestion.Member', on_delete=models.CASCADE)
    caducidad = models.DateField(default=return_date_time)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.caducidad = date.today() + relativedelta(months=+12)
        super(ExtendedUser, self).save(*args, **kwargs)

    @property
    def has_not_expired(self):
        if self.is_admin:
            return True
        return self.caducidad > date.today()

    @property
    def is_almost_expired(self):
        if self.is_admin:
            return True
        return self.caducidad > date.today() + timedelta(days=15)

    @property
    def zona(self):
        return self.miembro.zona

    @property
    def zona_id(self):
        return self.miembro.zona_id

    @property
    def region(self):
        return self.miembro.region

    @property
    def region_id(self):
        return self.miembro.region_id

    @property
    def is_nacional(self):
        return self.is_superuser or self.groups.filter(name__in=["Admin", "Consultor Nacional"]).exists()

    @property
    def is_region(self):
        return self.groups.filter(name__in=["RER", "Consultor Región"]).exists()

    @property
    def is_zona(self):
        return self.groups.filter(name__in=["REZ", "Consultor Zona"]).exists()

    @property
    def is_admin(self):
        return self.is_superuser or self.groups.filter(name=["Admin"]).exists()

    @property
    def is_responsable(self):
        return self.is_superuser or self.groups.filter(name__in=["Admin", "RER", "REZ"]).exists()

    @property
    def is_consultor(self):
        return not self.is_responsable and self.groups.filter(name__in=["Consultor Nacional", "Consultor Región", "Consultor Zona"]).exists()
    
    # @property
    # def is_staff(self):
    #     return self.is_staff == True or self.groups.filter(name="staff").exists()


class ActiveMemberManager(models.Manager):
    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs.filter(fecha_baja__isnull=True)


class ActiveLopdMemberManager(models.Manager):
    def get_queryset(self, request):
        qs = self.model.objects.get_queryset()
        return qs.filter(baja_lopd=False)


class Member(models.Model):
    # Gender choices
    HOMBRE = 'H'
    MUJER = 'M'
    GENDER_CHOICES = [
        (HOMBRE, 'Hombre'),
        (MUJER, 'Mujer'),
    ]
    # Region choices
    REGION_CHOICES = [
        ('CENTRO','CENTRO'),
        ('ESTE', 'ESTE'),
        ('NORTE', 'NORTE'),
        ('SUR', 'SUR'),
        ('CANARIAS', 'CANARIAS')
    ]
    # Department choices
    DEPARTMENT_CHOICES = [
        ('DH', 'DH'),
        ('DM', 'DM'),
        ('DHJ', 'DHJ'),
        ('DMJ', 'DMJ'),
        ('DF', 'DF')
    ]
    # Charge choices
    RESP_TITULAR = 'R'
    VICE_TITULAR = 'V-'
    RESP_DH = 'H'
    VICE_RESP_DH = 'V-H'
    RESP_DM = 'M'
    VICE_RESP_DM = 'V-M'
    RESP_DHJ = 'HJ'
    VICE_RESP_DJH = 'V-HJ'
    RES_DMJ = 'MJ'
    VICE_RESP_DMJ = 'V-MJ'
    CHARGE_CHOICES = [
        (RESP_TITULAR, 'Resp. Titular'),
        (VICE_TITULAR, 'Vice. Titular'),
        (RESP_DH, 'Resp. DH'),
        (VICE_RESP_DH, 'Vice-Resp. DH'),
        (RESP_DM, 'Resp. DM'),
        (VICE_RESP_DM, 'Vice-Resp. DM'),
        (RESP_DHJ, 'Resp. DHJ'),
        (VICE_RESP_DJH, 'Vice-Resp. DHJ'),
        (RES_DMJ, 'Resp. DMJ'),
        (VICE_RESP_DMJ, 'Vice-Resp. DMJ'),
    ]
    GRUPO = 'G'
    DISTRITO = 'D'
    DIST_GRAL = 'DG'
    ZONA = 'Z'
    REGION = 'R'
    NACIONAL = 'N'
    # In charge of choices
    IN_CHARGE_OF_CHOICES = [
        (GRUPO, 'GRUPO'),
        (DISTRITO, 'DISTRITO'),
        (DIST_GRAL, 'DIST. GRAL'),
        (ZONA, 'ZONA'),
        (REGION, 'REGION'),
        (NACIONAL, 'NACIONAL')
    ]
    # Study choices
    STUDY_CHOICES = [
        ('Grado 1', 'Grado 1'),
        ('Grado 2', 'Grado 2'),
        ('Grado 3', 'Grado 3'),
        ('Grado 4', 'Grado 4'),
    ]
    # Register choices
    REGISTER_CHOICES = [
        ('Ingreso con entrega de Gohonzon', 'Ingreso con entrega de Gohonzon'),
        ('Ingreso sin entrega de Gohonzon', 'Ingreso sin entrega de Gohonzon'),
        ('Llegada desde el extranjero', 'Llegada desde el extranjero'),
        ('Siendo miembro recibir Gohonzon', 'Siendo miembro recibir Gohonzon')
    ]
    #Drop out choices
    DROP_OUT_CHOICES = [
        ('Por solicitud', 'Por solicitud'),
        ('Por traslado a otro país', 'Por traslado a otro país'),
        ('Por fallecimiento', 'Por fallecimiento'),
        ('Por razones técnicas', 'Por razones técnicas')
    ]

    TITLE_FIELDS = ('nombre', 'apellidos', 'direccion', 'localidad', 'provincia')

    # Fields
    nombre = models.CharField(max_length=255, verbose_name='nombre', null=True, blank=True)
    apellidos = models.CharField(max_length=255, verbose_name='apellidos', null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name='fecha de nacimiento')
    fecha_ingreso = models.DateField(null=True, blank=True, verbose_name='fecha ingreso SG')
    dni = models.CharField(max_length=10, null=True, blank=True, unique=True, verbose_name='DNI/NIE/PASAPORTE', validators=[validate_dni])
    direccion = models.CharField(max_length=500, null=True, blank=True, verbose_name='dirección')
    localidad = models.CharField(max_length=255, null=True, blank=True, verbose_name='población')
    provincia = models.CharField(max_length=100, null=True, blank=True, verbose_name='provincia')
    codigo_postal = models.CharField(max_length=5, null=True, blank=True, verbose_name='código postal')
    telefono = models.IntegerField(null=True, blank=True, verbose_name='teléfono fijo')
    movil = models.IntegerField(null=True, blank=True, verbose_name='móvil', validators=[validate_movil])
    email = models.EmailField(max_length=200, null=True, blank=True, verbose_name='e-mail')
    recomendado_por_1 = models.ForeignKey('self', null=True, blank=True, related_name='recomendador_uno', on_delete=models.SET_NULL)
    recomendado_por_2 = models.ForeignKey('self', null=True, blank=True, related_name='recomendador_dos', on_delete=models.SET_NULL)
    observaciones = models.CharField(max_length=200, blank=True, null=True)
    departamento = models.ForeignKey('cargos.Departamento', on_delete=models.CASCADE)
    estudio = models.ForeignKey('gestion.estudio', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='estudio')
    fecha_estudio = models.DateField(null=True, blank=True)
    observaciones_al_estudio = models.CharField(max_length=100, blank=True, null=True)
    subscripcion = models.BooleanField(default=0, verbose_name='suscripción')
    gohonzon = models.DateField(null=True, blank=True, verbose_name = "Fecha Gohonzon")
    gohonzon_familiar = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    omamori_gohonzon = models.BooleanField(default=False, verbose_name='Omamori Gohonzon')
    omamori_fecha = models.DateField(null=True, blank=True, verbose_name='Fecha Omamori')
    alta = models.CharField(max_length=50, blank=True, null=True, choices=REGISTER_CHOICES, verbose_name='alta')
    baja = models.CharField(max_length=50, blank=True, null=True, choices=DROP_OUT_CHOICES, verbose_name='baja')
    fecha_baja = models.DateField(null=True, blank=True)
    foto = models.ImageField(upload_to=user_directory_path, null=True, blank=True, verbose_name='foto',
                             validators=[ValidateFileSize(419430)], help_text='La imagen debe tener un tamaño máximo de 400 kb')
    baja_lopd = models.BooleanField(default=False, verbose_name='Baja por LOPD')

    objects = models.Manager()  # The default manager.
    active_objects = ActiveMemberManager()

    class Meta:
        ordering = ['nombre']
        verbose_name = 'miembro'
        verbose_name_plural = 'miembros'

        indexes = [
            models.Index(fields=['id', 'nombre', 'apellidos', 'movil', 'email', 'fecha_baja'],
                         name='full_index'),
        ]

    class Admin:
        manager = ActiveLopdMemberManager()

    def __str__(self):
        return "%s %s" % (self.nombre, self.apellidos)

    def save(self, *args, **kwargs):
        for field_name in self.TITLE_FIELDS:
            val = getattr(self, field_name, False)
            if val:
                setattr(self, field_name, val.title())
        if self.omamori_fecha and not self.omamori_gohonzon:
            self.omamori_gohonzon = True
        super().save(*args, **kwargs)

    def delete(self):
        if self.baja != 'Por razones técnicas':
            self.save()
        else:
            super().delete()

    @property
    def grupo(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.nombre
        except:
            return None
    
    @property
    def distrito(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.nombre
        except:
            return None
    
    @property
    def distrito_general(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.distrito_general.nombre
        except:
            return None
        
    @property
    def zona(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.distrito_general.zona.nombre
        except:
            return None
    
    @property
    def zona_id(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.distrito_general.zona.pk
        except:
            return None
    
    @property
    def region(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.distrito_general.zona.region.nombre
        except:
            return None

    @property
    def region_id(self):
        try:
            return self.miembrogrupo_set.filter(fecha_baja__isnull=True).last().grupo.distrito.distrito_general.zona.region.pk
        except:
            return None

    @property
    def get_foto(self):
        return self.foto or 'sin-foto.jpg'

    @property
    def cargos_activos(self):
        return self.cargo_set.filter(fecha_fin__isnull=True).all()

    @property
    def cargos_capacitacion_activos(self):
        return self.cargocapacitacion_set.filter(fecha_fin__isnull=True).all()

    def dar_de_baja(self, fecha_baja=None, motivo_baja=None, destino=None):
        if not fecha_baja:
            fecha_baja = timezone.localtime(timezone.now())
        self.fecha_baja = fecha_baja
        self.baja = motivo_baja
        self.delete()
        if motivo_baja != 'Por razones técnicas':
            BajaMiembro.objects.create(
                fecha=fecha_baja,
                motivo=motivo_baja,
                destino=destino,
                member=self
            )

            for cargo in self.cargos_activos:
                cargo.delete(fecha_baja)
            for cargo in self.cargos_capacitacion_activos:
                cargo.delete(fecha_baja)

            miembrogrupos_activos = self.miembrogrupo_set.filter(fecha_baja__isnull=True).all()
            for miembrogrupo in miembrogrupos_activos:
                miembrogrupo.dadebaja(fecha_baja)
#TODO: Falta eliminar todo lo que le cuelga (cargos, altas, bajas, etc.)

    def dar_baja_lopd(self):
        self.nombre = None
        self.apellidos = None
        self.fecha_nacimiento = None
        self.dni = None
        self.direccion = None
        self.telefono = None
        self.movil = None
        self.email = None
        self.observaciones_al_estudio = None
        self.foto = None
        self.recomendado_por_1 = None
        self.recomendado_por_2 = None
        self.observaciones = None
        self.gohonzon_familiar = None
        self.baja_lopd = True
        for documento in self.documento_set.all():
            documento.delete()
        self.save()

    def get_absolute_url(self):
        """
        Devuelve la url para acceder a una instancia particular del modelo.
        """
        return "/member/%i" % self.id

    @property
    def fecha_gohonzon(self):
        if self.gohonzon:
            return self.gohonzon
        elif self.gohonzon_familiar:
            return self.gohonzon_familiar.gohonzon

    def cambiar_grupo(self, grupo, fecha_inicio):
        fecha_inicio_con_formato = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        miembrogrupos_activos = self.miembrogrupo_set.filter(fecha_baja__isnull=True).order_by('fecha_inicio').all()
        if miembrogrupos_activos.last().fecha_inicio > fecha_inicio_con_formato:
            return False
        for miembrogrupo in miembrogrupos_activos:
            miembrogrupo.dadebaja(fecha_inicio)
        self.miembrogrupo_set.create(grupo=grupo, fecha_inicio=fecha_inicio)
        return True
    
    def activo(self):
        if not self.fecha_baja:
            return True
        else:
            return False
    activo.boolean = True

    def eventos(self):
        with connection.cursor() as cursor:
            try:
                cursor.callproc("ListaFechas", (self.pk,))
                return create_list_from_cursor(cursor)
            except Exception:
                return []

    def origen(self):
        return AltaMiembro.objects.filter(member_id=self.pk).order_by("pk").last().origen
    
    def fecha_llegada_extranjero(self):
        return AltaMiembro.objects.filter(member_id=self.pk).order_by("pk").last().fecha_llegada_extranjero

    def destino(self):
        return BajaMiembro.objects.filter(member_id=self.pk).order_by("pk").last().destino


def create_list_from_cursor(cursor):
    rows = cursor.fetchall()
    # DEBUG settings (used to) affect what gets returned. 
    if settings.DEBUG:
        desc = [item[0] for item in cursor.cursor.description]
    else:
        desc = [item[0] for item in cursor.description]
    eventos = [Evento(**dict(zip(desc, item))) for item in rows]
    return eventos[1:]


class Evento:
    
    ICONOS = {
        'A': 'card_travel',
        'B': 'face',
        'C': 'group',
        'D': 'supervisor_account',
        'E': 'local_florist'
    }

    COLORES = {
        'A': 'primary',  # eventos organización
        'B': 'primary',  # eventos vitales
        'C': 'secondary',  # eventos grupos
        'D': 'secondary',  # eventos cargos de responsabilidad
        'E': 'secondary'  # eventos cargos de capacitación
    }

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    
    def icono(self):
        return self.ICONOS.get(self.ICO)
    
    def color(self):
        return self.COLORES.get(self.ICO)
    
    @property
    def fecha_format(self):
        return datetime.strptime(self.FECHA, "%Y-%m-%d")


class MiembroGrupo(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    grupo = models.ForeignKey('estructura.Grupo', on_delete=models.CASCADE)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('pertenencia a grupo')
        verbose_name_plural = _('pertenencias a grupo')

        indexes = [
            models.Index(fields=['member',]),
            models.Index(fields=['member', 'grupo']),
        ]

    def dadebaja(self, fecha_baja=None):
        if not fecha_baja:
            fecha_baja = timezone.localtime(timezone.now())
        self.fecha_baja = fecha_baja
        self.save()

    def __str__(self):
        return (
            f'{self.grupo} - {self.grupo.distrito} - {self.grupo.distrito.distrito_general}'
            f' - {self.grupo.distrito.distrito_general.zona}'
            f' - {self.grupo.distrito.distrito_general.zona.region}')


class AltaMiembro(models.Model):
    # Register choices
    REGISTER_CHOICES = [
        ('Ingreso con entrega de Gohonzon', 'Ingreso con entrega de Gohonzon'),
        ('Ingreso sin entrega de Gohonzon', 'Ingreso sin entrega de Gohonzon'),
        ('Llegada desde el extranjero', 'Llegada desde el extranjero'),
        ('Siendo miembro recibir Gohonzon', 'Siendo miembro recibir Gohonzon')
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    fecha = models.DateField(null=True, blank=True, verbose_name = "Fecha ingreso SG")
    motivo = models.CharField(max_length=50, blank=True, null=True, choices=REGISTER_CHOICES)
    origen = models.CharField(max_length=50, blank=True, null=True)
    fecha_llegada_extranjero = models.DateField(null=True, blank=True, verbose_name = "Fecha incorporación SGEs")

    class Meta:
        ordering = ['fecha']
        verbose_name = 'alta'
        verbose_name_plural = 'altas'

    def __str__(self):
        return f"{self.member} - {self.fecha or 'Sin fecha'} - {self.motivo}"


class BajaMiembro(models.Model):

    # Drop out choices
    DROP_OUT_CHOICES = [
        ('Por solicitud', 'Por solicitud'),
        ('Por traslado a otro país', 'Por traslado a otro país'),
        ('Por fallecimiento', 'Por fallecimiento'),
        ('Por razones técnicas', 'Por razones técnicas')
    ]

    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    fecha = models.DateField(null=True, blank=True)
    motivo = models.CharField(max_length=50, blank=True, null=True, choices=DROP_OUT_CHOICES)
    destino = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['fecha']
        verbose_name = 'baja'
        verbose_name_plural = 'bajas'

    def __str__(self):
        return f"{self.member} - {self.fecha or 'Sin fecha'} - {self.motivo}"


class Estudio(models.Model):
    estudio = models.CharField(max_length=50)

    def __str__(self):
        return self.estudio


DESCRIPCION_CHOICES = [
        ('Solicitud de Ingreso', 'Solicitud de Ingreso'),
        ('Propuesta de Nombramiento', 'Propuesta de Nombramiento'),
        ('Solicitud de Entrega de Omamori', 'Solicitud de Entrega de Omamori'),
        ('Gohonzon', 'Gohonzon'),
        ('Autorización a menores', 'Autorización a menores'),
        ('Carta de Presentación', 'Carta de Presentación'),
        ('Formulario de Visita a Centro Cultural', 'Formulario de Visita a Centro Cultural'),
        ('Solicitud de baja', 'Solicitud de baja'),
        ('Otros', 'Otros'),
    ]

#TODO
class Documento(models.Model):
    descripcion = models.CharField(
        max_length=50, verbose_name='descripcion', db_index=True,
        help_text='Descripción corta del archivo (max 50 caracteres)', choices=DESCRIPCION_CHOICES
    )
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    archivo = models.FileField(
        upload_to=document_directory_path, null=True, blank=True, verbose_name='archivo',
        validators=[ValidateFileSize(2097152)], help_text='El archivo debe tener un tamaño máximo de 2 Mb'
    )

    def __str__(self):
        return f'{self.descripcion} - {self.archivo}'

class MiembroDepartamento(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    departamento = models.ForeignKey('cargos.Departamento', on_delete=models.CASCADE)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_baja = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('pertenencia a departamento')
        verbose_name_plural = _('pertenencias a departamento')

        indexes = [
            models.Index(fields=['member']),
            models.Index(fields=['member', 'departamento']),
        ]

    def delete(self, fecha_baja=None):
        if not fecha_baja:
            fecha_baja = timezone.localtime(timezone.now())
        self.fecha_baja = fecha_baja
        self.save()

    def __str__(self):
        return f"{self.member} - {self.departamento}"

    def save(self):
        super().save()
        if self.fecha_baja is None:
            self.member.departamento = self.departamento
            self.member.save()
