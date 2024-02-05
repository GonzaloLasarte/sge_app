from django.contrib import admin

from estructura.models import Region, Zona, DistritoGeneral, Distrito, Grupo


class EventAdminSite(admin.AdminSite):
    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        ordering = {
            "Regiones": 1,
            "Zonas generales": 2,
            "Zonas": 3,
            "Distritos generales": 4
        }
        app_dict = self._build_app_dict(request)
        # a.sort(key=lambda x: b.index(x[0]))
        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: ordering[x['name']])

        return app_list


class RegionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    ordering = ('nombre',)


class ZonaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region')
    search_fields = ('nombre', 'region__nombre')
    list_filter = ('region',)
    ordering = ('nombre',)

    raw_id_fields = ('region',)


class DistritoGeneralAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'zona')
    search_fields = (
        'zona__region__nombre',
        'zona__nombre',
        'nombre'
        )
    list_filter = (
        'zona__region',
        'zona',
        )
    ordering = ('nombre',)

    raw_id_fields = ('zona',)


class DistritoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'zona', 'distrito_general')
    search_fields = (
        'distrito_general__zona__region__nombre',
        'distrito_general__zona__nombre',
        'distrito_general__nombre',
        'nombre'
        )
    list_filter = (
        'distrito_general__zona__region',
        'distrito_general__zona',
        'distrito_general',
        )
    ordering = ('nombre',)

    raw_id_fields = ('distrito_general',)


class GrupoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'region', 'zona', 'distrito_general', 'distrito')
    search_fields = (
        'distrito__distrito_general__zona__region__nombre',
        'distrito__distrito_general__zona__nombre',
        'distrito__distrito_general__nombre',
        'distrito__nombre',
        'nombre'
        )
    list_filter = (
        'distrito__distrito_general__zona__region',
        'distrito__distrito_general__zona',
        'distrito__distrito_general',
        'distrito',
        )
    ordering = ('nombre',)

    raw_id_fields = ('distrito',)

    def get_list_filter(self, request):
        return (RegionFilter, ZonaFilter, DistritoGeneralFilter, DistritoFilter)

    def get_queryset(self, request):
        if request.user.is_admin or request.user.is_nacional:
            return super().get_queryset(request).all()
        else:
            if request.user.is_region:
                return super().get_queryset(request).filter(
                    distrito__distrito_general__zona__region__nombre=request.user.miembro.region).distinct()
            elif request.user.is_zona:
                return super().get_queryset(request).filter(
                    distrito__distrito_general__zona__nombre=request.user.miembro.zona).distinct()
            else:
                return


class RegionFilter(admin.SimpleListFilter):
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
                distrito__distrito_general__zona__region__pk=value).distinct()
        return queryset


class ZonaFilter(admin.SimpleListFilter):
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
            return queryset.filter(distrito__distrito_general__zona__pk=value)
        return queryset


class DistritoGeneralFilter(admin.SimpleListFilter):
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
                distrito__distrito_general__pk=value)
        return queryset


class DistritoFilter(admin.SimpleListFilter):
    title = 'distrito'
    parameter_name = 'distrito'

    def lookups(self, request, model_admin):
        distrito_general = request.GET.get('distrito_general')
        if distrito_general:
            return Distrito.objects.filter(distrito_general_id=distrito_general).values_list('pk', 'nombre').order_by(
                'nombre')
        else:
            return

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(
                distrito__pk=value)
        return queryset


admin.site.register(Region, RegionAdmin)
admin.site.register(Zona, ZonaAdmin)
admin.site.register(DistritoGeneral, DistritoGeneralAdmin)
admin.site.register(Distrito, DistritoAdmin)
admin.site.register(Grupo, GrupoAdmin)
