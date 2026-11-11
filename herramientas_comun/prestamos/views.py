from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, HerramientaForm
from .models import Categoria, Herramienta


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
