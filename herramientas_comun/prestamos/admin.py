from django.contrib import admin

from .models import Categoria, Herramienta, Prestamo


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre', 'descripcion')


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'estado', 'disponible', 'fecha_ingreso')
    list_filter = ('categoria', 'estado', 'disponible')
    search_fields = ('codigo', 'nombre')


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        'socio', 'herramienta', 'fecha_solicitud', 'fecha_devolucion_esperada',
        'fecha_devolucion_real', 'estado',
    )
    list_filter = ('estado', 'fecha_solicitud', 'fecha_devolucion_esperada')
    search_fields = ('socio__username', 'herramienta__codigo', 'herramienta__nombre')
