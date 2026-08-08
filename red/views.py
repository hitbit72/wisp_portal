from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import DispositivoForm, EnlaceForm, InterfazForm, SectorForm
from .models import Dispositivo, Enlace, Interfaz, Sector


# --- Sectores ---------------------------------------------------------------

@login_required
def lista_sectores(request):
    """Listado de sectores con búsqueda HTMX y paginación."""
    sectores = Sector.objects.all()

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        sectores = sectores.filter(
            Q(nombre__icontains=busqueda) | Q(poblacion__icontains=busqueda)
        )

    paginator = Paginator(sectores, 25)
    pagina = paginator.get_page(request.GET.get('page'))

    contexto = {'pagina': pagina, 'busqueda': busqueda}

    if request.headers.get('HX-Request'):
        return render(request, 'red/_tabla.html', contexto)
    return render(request, 'red/lista.html', contexto)


@login_required
def detalle_sector(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    return render(request, 'red/detalle_sector.html', {'sector': sector})


@login_required
def form_sector(request, pk=None):
    sector = get_object_or_404(Sector, pk=pk) if pk else None

    if request.method == 'POST':
        form = SectorForm(request.POST, instance=sector)
        if form.is_valid():
            sector = form.save()
            return redirect('red:detalle_sector', pk=sector.pk)
    else:
        form = SectorForm(instance=sector)

    return render(request, 'red/form_sector.html', {'form': form, 'sector': sector})


@login_required
def eliminar_sector(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    if request.method == 'POST':
        sector.delete()
        return redirect('red:lista')
    return render(request, 'red/confirmar_eliminar_sector.html', {'sector': sector})


# --- Dispositivos -----------------------------------------------------------

@login_required
def nuevo_dispositivo(request, sector_pk):
    sector = get_object_or_404(Sector, pk=sector_pk)

    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save(commit=False)
            dispositivo.sector = sector
            dispositivo.save()
            return redirect('red:detalle_sector', pk=sector.pk)
    else:
        form = DispositivoForm()

    return render(request, 'red/form_dispositivo.html', {
        'form': form, 'sector': sector, 'dispositivo': None,
    })


@login_required
def detalle_dispositivo(request, pk):
    dispositivo = get_object_or_404(
        Dispositivo.objects.prefetch_related('interfaces', 'enlaces_origen', 'enlaces_destino'),
        pk=pk,
    )
    return render(request, 'red/detalle_dispositivo.html', {'dispositivo': dispositivo})


@login_required
def editar_dispositivo(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    sector_pk = dispositivo.sector_id

    if request.method == 'POST':
        form = DispositivoForm(request.POST, instance=dispositivo)
        if form.is_valid():
            form.save()
            return redirect('red:detalle_sector', pk=sector_pk)
    else:
        form = DispositivoForm(instance=dispositivo)

    return render(request, 'red/form_dispositivo.html', {
        'form': form, 'sector': dispositivo.sector, 'dispositivo': dispositivo,
    })


@login_required
def eliminar_dispositivo(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    sector_pk = dispositivo.sector_id

    if request.method == 'POST':
        dispositivo.delete()
        return redirect('red:detalle_sector', pk=sector_pk)

    return render(request, 'red/confirmar_eliminar_dispositivo.html', {'dispositivo': dispositivo})


# --- Interfaces -------------------------------------------------------------

@login_required
def nueva_interfaz(request, dispositivo_pk):
    dispositivo = get_object_or_404(Dispositivo, pk=dispositivo_pk)

    if request.method == 'POST':
        form = InterfazForm(request.POST)
        if form.is_valid():
            interfaz = form.save(commit=False)
            interfaz.dispositivo = dispositivo
            interfaz.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo.pk)
    else:
        form = InterfazForm()

    return render(request, 'red/form_interfaz.html', {
        'form': form, 'dispositivo': dispositivo, 'interfaz': None,
    })


@login_required
def editar_interfaz(request, pk):
    interfaz = get_object_or_404(Interfaz, pk=pk)
    dispositivo_pk = interfaz.dispositivo_id

    if request.method == 'POST':
        form = InterfazForm(request.POST, instance=interfaz)
        if form.is_valid():
            form.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo_pk)
    else:
        form = InterfazForm(instance=interfaz)

    return render(request, 'red/form_interfaz.html', {
        'form': form, 'dispositivo': interfaz.dispositivo, 'interfaz': interfaz,
    })


@login_required
def eliminar_interfaz(request, pk):
    interfaz = get_object_or_404(Interfaz, pk=pk)
    dispositivo_pk = interfaz.dispositivo_id

    if request.method == 'POST':
        interfaz.delete()
        return redirect('red:detalle_dispositivo', pk=dispositivo_pk)

    return render(request, 'red/confirmar_eliminar_interfaz.html', {'interfaz': interfaz})


# --- Enlaces ----------------------------------------------------------------

@login_required
def nuevo_enlace(request, dispositivo_pk):
    """Crea un enlace cuyo origen es el dispositivo actual."""
    dispositivo = get_object_or_404(Dispositivo, pk=dispositivo_pk)

    if request.method == 'POST':
        form = EnlaceForm(request.POST, dispositivo_origen=dispositivo)
        if form.is_valid():
            enlace = form.save(commit=False)
            enlace.dispositivo_origen = dispositivo
            enlace.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo.pk)
    else:
        form = EnlaceForm(dispositivo_origen=dispositivo)

    return render(request, 'red/form_enlace.html', {
        'form': form, 'dispositivo': dispositivo, 'enlace': None,
    })


@login_required
def editar_enlace(request, pk):
    enlace = get_object_or_404(Enlace, pk=pk)
    dispositivo_pk = enlace.dispositivo_origen_id

    if request.method == 'POST':
        form = EnlaceForm(request.POST, instance=enlace, dispositivo_origen=enlace.dispositivo_origen)
        if form.is_valid():
            form.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo_pk)
    else:
        form = EnlaceForm(instance=enlace, dispositivo_origen=enlace.dispositivo_origen)

    return render(request, 'red/form_enlace.html', {
        'form': form, 'dispositivo': enlace.dispositivo_origen, 'enlace': enlace,
    })


@login_required
def eliminar_enlace(request, pk):
    enlace = get_object_or_404(Enlace, pk=pk)
    dispositivo_pk = enlace.dispositivo_origen_id

    if request.method == 'POST':
        enlace.delete()
        return redirect('red:detalle_dispositivo', pk=dispositivo_pk)

    return render(request, 'red/confirmar_eliminar_enlace.html', {'enlace': enlace})