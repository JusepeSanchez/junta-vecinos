from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import CategoriaForm, HerramientaForm
from .models import Categoria, Herramienta, Prestamo


def encargado_requerido(view):
    return login_required(user_passes_test(lambda user: user.is_staff)(view))


@login_required
def inicio(request):
    return render(request, 'prestamos/inicio.html')


@encargado_requerido
def herramienta_list(request):
    herramientas = Herramienta.objects.select_related('categoria')
    busqueda = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '').strip()
    if busqueda:
        herramientas = herramientas.filter(nombre__icontains=busqueda)
    if categoria.isdigit():
        herramientas = herramientas.filter(categoria_id=int(categoria))
    return render(request, 'prestamos/herramienta_list.html', {
        'herramientas': herramientas,
        'categorias': Categoria.objects.all(),
        'busqueda': busqueda,
        'categoria_seleccionada': categoria,
    })


@encargado_requerido
def herramienta_detail(request, pk):
    herramienta = get_object_or_404(Herramienta.objects.select_related('categoria'), pk=pk)
    return render(request, 'prestamos/herramienta_detail.html', {'herramienta': herramienta})


@encargado_requerido
def herramienta_create(request):
    form = HerramientaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Herramienta creada correctamente.')
        return redirect('herramienta_list')
    if request.method == 'POST':
        messages.error(request, 'No se pudo crear la herramienta. Revisa los campos indicados.')
    return render(request, 'prestamos/herramienta_form.html', {'form': form, 'titulo': 'Crear herramienta'})


@encargado_requerido
def herramienta_edit(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    form = HerramientaForm(request.POST or None, instance=herramienta)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Herramienta actualizada correctamente.')
        return redirect('herramienta_list')
    if request.method == 'POST':
        messages.error(request, 'No se pudo actualizar la herramienta. Revisa los campos indicados.')
    return render(request, 'prestamos/herramienta_form.html', {'form': form, 'titulo': 'Editar herramienta'})


@encargado_requerido
def herramienta_delete(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == 'POST':
        herramienta.delete()
        messages.success(request, 'Herramienta eliminada correctamente.')
        return redirect('herramienta_list')
    return render(request, 'prestamos/confirmar_eliminacion.html', {
        'objeto': herramienta, 'volver': 'herramienta_list',
    })


@encargado_requerido
def categoria_list(request):
    return render(request, 'prestamos/categoria_list.html', {'categorias': Categoria.objects.all()})


@encargado_requerido
def categoria_create(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría creada correctamente.')
        return redirect('categoria_list')
    if request.method == 'POST':
        messages.error(request, 'No se pudo crear la categoría. Revisa los campos indicados.')
    return render(request, 'prestamos/categoria_form.html', {'form': form, 'titulo': 'Crear categoría'})


@encargado_requerido
def categoria_edit(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    form = CategoriaForm(request.POST or None, instance=categoria)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Categoría actualizada correctamente.')
        return redirect('categoria_list')
    if request.method == 'POST':
        messages.error(request, 'No se pudo actualizar la categoría. Revisa los campos indicados.')
    return render(request, 'prestamos/categoria_form.html', {'form': form, 'titulo': 'Editar categoría'})


@encargado_requerido
def categoria_delete(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoría eliminada correctamente.')
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: la categoría tiene herramientas asociadas.')
        return redirect('categoria_list')
    return render(request, 'prestamos/confirmar_eliminacion.html', {
        'objeto': categoria, 'volver': 'categoria_list',
    })


@login_required
def catalogo(request):
    herramientas = Herramienta.objects.filter(
        disponible=True
    ).exclude(estado=Herramienta.Estado.REPARACION).select_related('categoria')
    return render(request, 'prestamos/catalogo.html', {'herramientas': herramientas})


@login_required
@require_POST
def agregar_solicitud(request, pk):
    solicitud = request.session.get('solicitud', [])
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if not herramienta.disponible or herramienta.estado == Herramienta.Estado.REPARACION:
        messages.error(request, 'La herramienta ya no está disponible.')
    elif str(pk) in solicitud or pk in solicitud:
        messages.error(request, 'La herramienta ya está en tu solicitud.')
    elif len(solicitud) >= 3:
        messages.error(request, 'Puedes solicitar hasta 3 herramientas.')
    else:
        solicitud.append(str(pk))
        request.session['solicitud'] = solicitud
        messages.success(request, 'Herramienta agregada a tu solicitud.')
    return redirect('catalogo')


@login_required
def ver_solicitud(request):
    ids = request.session.get('solicitud', [])
    herramientas = Herramienta.objects.filter(pk__in=ids).select_related('categoria')
    return render(request, 'prestamos/solicitud.html', {'herramientas': herramientas})


@login_required
@require_POST
def quitar_solicitud(request, pk):
    solicitud = request.session.get('solicitud', [])
    request.session['solicitud'] = [item for item in solicitud if str(item) != str(pk)]
    request.session.modified = True
    messages.success(request, 'Herramienta quitada de tu solicitud.')
    return redirect('ver_solicitud')


@login_required
@require_POST
def confirmar_solicitud(request):
    ids = request.session.get('solicitud', [])
    if not ids:
        messages.error(request, 'Tu solicitud está vacía.')
        return redirect('ver_solicitud')

    creados = 0
    no_disponibles = 0
    with transaction.atomic():
        herramientas = Herramienta.objects.select_for_update().filter(pk__in=ids)
        for herramienta in herramientas:
            if not herramienta.disponible or herramienta.estado == Herramienta.Estado.REPARACION:
                no_disponibles += 1
                continue
            Prestamo.objects.create(
                socio=request.user,
                herramienta=herramienta,
                fecha_devolucion_esperada=timezone.localdate() + timedelta(days=7),
                estado=Prestamo.Estado.PENDIENTE,
            )
            herramienta.disponible = False
            herramienta.save(update_fields=['disponible'])
            creados += 1

    request.session.pop('solicitud', None)
    if creados:
        messages.success(request, f'Solicitud enviada: {creados} préstamo(s) pendiente(s).')
    if no_disponibles:
        messages.warning(request, f'{no_disponibles} herramienta(s) ya no estaban disponibles.')
    return redirect('mis_prestamos')


@login_required
def mis_prestamos(request):
    prestamos = Prestamo.objects.filter(socio=request.user).select_related('herramienta')
    return render(request, 'prestamos/mis_prestamos.html', {'prestamos': prestamos})


@login_required
@require_POST
def cancelar_prestamo(request, pk):
    with transaction.atomic():
        prestamo = get_object_or_404(
            Prestamo.objects.select_for_update(), pk=pk, socio=request.user
        )
        if prestamo.estado != Prestamo.Estado.PENDIENTE:
            messages.error(request, 'Solo puedes cancelar préstamos pendientes.')
        else:
            prestamo.estado = Prestamo.Estado.CANCELADO
            prestamo.save(update_fields=['estado'])
            herramienta = Herramienta.objects.select_for_update().get(pk=prestamo.herramienta_id)
            herramienta.disponible = True
            herramienta.save(update_fields=['disponible'])
            messages.success(request, 'Préstamo cancelado; la herramienta está disponible.')
    return redirect('mis_prestamos')


@encargado_requerido
def todos_prestamos(request):
    prestamos = Prestamo.objects.select_related('socio', 'herramienta')
    return render(request, 'prestamos/todos_prestamos.html', {'prestamos': prestamos})


@encargado_requerido
@require_POST
def activar_prestamo(request, pk):
    with transaction.atomic():
        prestamo = get_object_or_404(Prestamo.objects.select_for_update(), pk=pk)
        if prestamo.estado != Prestamo.Estado.PENDIENTE:
            messages.error(request, 'Solo se pueden activar préstamos pendientes.')
        else:
            prestamo.estado = Prestamo.Estado.ACTIVO
            prestamo.save(update_fields=['estado'])
            messages.success(request, 'Préstamo activado correctamente.')
    return redirect('todos_prestamos')


@encargado_requerido
@require_POST
def registrar_devolucion(request, pk):
    with transaction.atomic():
        prestamo = get_object_or_404(Prestamo.objects.select_for_update(), pk=pk)
        if prestamo.estado != Prestamo.Estado.ACTIVO:
            messages.error(request, 'Solo se puede registrar la devolución de un préstamo activo.')
        else:
            prestamo.estado = Prestamo.Estado.DEVUELTO
            prestamo.fecha_devolucion_real = timezone.localdate()
            prestamo.save(update_fields=['estado', 'fecha_devolucion_real'])
            herramienta = Herramienta.objects.select_for_update().get(pk=prestamo.herramienta_id)
            herramienta.disponible = True
            herramienta.save(update_fields=['disponible'])
            messages.success(request, 'Devolución registrada; la herramienta está disponible.')
    return redirect('todos_prestamos')
