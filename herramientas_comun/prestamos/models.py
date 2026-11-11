from django.conf import settings
from django.db import models


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'categorías'

    def __str__(self):
        return self.nombre


class Herramienta(models.Model):
    class Estado(models.TextChoices):
        BUENO = 'Bueno', 'Bueno'
        REGULAR = 'Regular', 'Regular'
        REPARACION = 'En reparación', 'En reparación'

    codigo = models.CharField(max_length=7, unique=True)
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='herramientas'
    )
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.BUENO)
    disponible = models.BooleanField(default=True)
    fecha_ingreso = models.DateField()

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'


class Prestamo(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = 'Pendiente', 'Pendiente'
        ACTIVO = 'Activo', 'Activo'
        DEVUELTO = 'Devuelto', 'Devuelto'
        CANCELADO = 'Cancelado', 'Cancelado'

    socio = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='prestamos'
    )
    herramienta = models.ForeignKey(
        Herramienta, on_delete=models.PROTECT, related_name='prestamos'
    )
    fecha_solicitud = models.DateField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=10, choices=Estado.choices, default=Estado.PENDIENTE
    )

    class Meta:
        ordering = ['-fecha_solicitud', '-pk']

    def __str__(self):
        return f'{self.herramienta} - {self.socio} ({self.estado})'
