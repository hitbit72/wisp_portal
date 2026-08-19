#import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente

from .forms import DispositivoForm, EnlaceForm, InterfazForm, SectorForm
from .models import Dispositivo, Enlace, Interfaz, Sector

from eventos.models import Evento
from metricas.models import DeviceMetrics
from eventos.services import registrar_evento
MODULO = 'red'

def http_ruta(ruta):
    """
    Funcion para obtener la ruta de retorno a partir de la URL anterior. Se usa para
    evitar que al editar o crear un router/plan, la página de detalle redirija
    correctamente a la lista de routers en lugar de volver a la página de edición.
    """
    if any(palabra in ruta for palabra in ['editar', 'nuevo', 'eliminar']):
        return '/red/dispositivos'
    
    return ruta # Devuelve la ruta original

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
        return render(request, 'red/sector/_tabla.html', contexto)
    return render(request, 'red/sector/lista.html', contexto)


@login_required
def detalle_sector(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    router_total = sector.routers_mikrotik.count()
    return render(request, 'red/sector/detalle_sector.html', {'sector': sector, 'routers': router_total})


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

    return render(request, 'red/sector/form_sector.html', {'form': form, 'sector': sector})


@login_required
def eliminar_sector(request, pk):
    sector = get_object_or_404(Sector, pk=pk)
    if request.method == 'POST':
        registrar_evento(
	        MODULO,
	        f'Sector {sector.nombre} eliminado',
	        f'Sector #{sector.pk} - {sector.nombre} {sector.poblacion}.',
	        nivel=Evento.Nivel.INFO,
        )
        sector.delete()
        return redirect('red:lista')
    return render(request, 'red/sector/confirmar_eliminar_sector.html', {'sector': sector})


# --- Dispositivos -----------------------------------------------------------

@login_required
def lista_dispositivos(request):
    """Listado global de dispositivos (sin pasar por sectores), con búsqueda
    y filtros. Es una segunda vía de acceso: los dispositivos también se ven
    desde el detalle de su sector."""
    dispositivos = Dispositivo.objects.select_related('sector', 'cliente')
    
    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        dispositivos = dispositivos.filter(
            Q(nombre__icontains=busqueda)
            | Q(modelo__icontains=busqueda)
            | Q(ip_gestion__icontains=busqueda)
            | Q(mac_address__icontains=busqueda)
        )

    tipo_seleccionado = request.GET.get('tipo', '').strip()
    if tipo_seleccionado:
        dispositivos = dispositivos.filter(tipo=tipo_seleccionado)

    estado_seleccionado = request.GET.get('estado', '').strip()
    if estado_seleccionado:
        dispositivos = dispositivos.filter(estado=estado_seleccionado)

    sector_seleccionado = request.GET.get('sector', '').strip()
    if sector_seleccionado:
        dispositivos = dispositivos.filter(sector_id=sector_seleccionado)

    dis_totales = dispositivos.count()
    dis_activos = dispositivos.filter(estado='activo').count()
    dis_inactivos = dispositivos.filter(estado='inactivo').count()
    dis_mantenimiento = dispositivos.filter(estado='mantenimiento').count()
    dis_instalacion = dispositivos.filter(estado='instalacion').count()
    dis_retirados = dispositivos.filter(estado='retirado').count()

    paginator = Paginator(dispositivos, 25)
    pagina = paginator.get_page(request.GET.get('page'))

    contexto = {
        'pagina': pagina,
        'busqueda': busqueda,
        'tipo_seleccionado': tipo_seleccionado,
        'estado_seleccionado': estado_seleccionado,
        'tipos_dispositivo': Dispositivo.Tipo.choices,
        'tipos_estado': Dispositivo.Estado.choices,
        'sector_seleccionado': sector_seleccionado,
        'todos_sectores': Sector.objects.all().values_list('pk', 'nombre').order_by('nombre'),
        'totales': {
            'total': dis_totales,
            'activos': dis_activos,
            'inactivos': dis_inactivos,
            'mantenimiento': dis_mantenimiento,
            'instalacion': dis_instalacion,
            'retirados': dis_retirados,
        },
    }

    if request.headers.get('HX-Request'):
        return render(request, 'red/dispositivo/_tabla_dispositivos.html', contexto)
    return render(request, 'red/dispositivo/lista_dispositivos.html', contexto)


@login_required
def nuevo_dispositivo(request, sector_pk):
    sector = get_object_or_404(Sector, pk=sector_pk)

    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save()
            return redirect('red:detalle_sector', pk=dispositivo.sector_id or sector.pk)
    else:
        form = DispositivoForm(initial={'sector': sector})

    return render(request, 'red/dispositivo/form_dispositivo.html', {
        'form': form, 'sector': sector, 'dispositivo': None,
    })

@login_required
def nuevo_dispositivo_solo(request):

    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save()
            return redirect('red:lista_dispositivos')
    else:
        form = DispositivoForm()

    return render(request, 'red/dispositivo/form_dispositivo_solo.html', {
        'form': form, 'dispositivo': None,
    })

@login_required
def nuevo_dispositivo_cliente(request, cliente_pk):
    cliente = get_object_or_404(Cliente, pk=cliente_pk)

    if request.method == 'POST':
        form = DispositivoForm(request.POST)
        if form.is_valid():
            dispositivo = form.save()
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = DispositivoForm(initial={'cliente': cliente})

    return render(request, 'red/dispositivo/form_dispositivo_cliente.html', {
        'form': form, 'cliente': cliente, 'dispositivo': None,
    })

@login_required
def detalle_dispositivo(request, pk):
    # Obtiene la URL anterior, o asigna una ruta por defecto si no existe
    url_anterior = request.META.get('HTTP_REFERER', 'red:lista_dispositivos')
    url_anterior = http_ruta(url_anterior)  # Cambia la ruta si es necesario

    dispositivo = get_object_or_404(
        Dispositivo.objects.prefetch_related('interfaces', 'enlaces_origen', 'enlaces_destino'),
        pk=pk,
    )
    metricas = get_object_or_404(DeviceMetrics, device = pk)
    # procesar los datos tipo json antes de enviarlos a la platilla
    #if isinstance(metricas.puertos, str):
    #    metricas.puertos = json.loads(metricas.puertos)

    enlaces = sorted(
        (*dispositivo.enlaces_origen.all(), *dispositivo.enlaces_destino.all()),
        key=lambda e: e.pk,
    )
    return render(request, 'red/dispositivo/detalle_dispositivo.html', {
        'dispositivo': dispositivo,
        'enlaces': enlaces,
        'url_anterior': url_anterior,
        'metricas': metricas,
    })


@login_required
def editar_dispositivo(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    sector_pk = dispositivo.sector_id
    # Obtiene la URL anterior, o asigna una ruta por defecto si no existe
    url_anterior = request.META.get('HTTP_REFERER', 'red:lista_dispositivos')

    if request.method == 'POST':
        form = DispositivoForm(request.POST, instance=dispositivo)
        url_anterior = request.POST.get('urlanterior')
        if form.is_valid():
            dispositivo = form.save()
            if '/red/' in url_anterior:
                return redirect('red:detalle_dispositivo', pk=pk)
            return redirect('red:detalle_sector', pk=dispositivo.sector_id or sector_pk)
    else:
        form = DispositivoForm(instance=dispositivo)

    return render(request, 'red/dispositivo/form_dispositivo.html', {
        'form': form, 
        'sector': dispositivo.sector, 
        'dispositivo': dispositivo,
        'url_anterior': url_anterior,
    })

@login_required
def editar_dispositivo_cliente(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    cliente = get_object_or_404(Cliente, pk=dispositivo.cliente.pk)
    cliente_pk = cliente.pk

    if request.method == 'POST':
        form = DispositivoForm(request.POST, instance=dispositivo)
        if form.is_valid():
            dispositivo = form.save()
            return redirect('clientes:detalle', pk=dispositivo.cliente.pk or cliente_pk)
    else:
        form = DispositivoForm(instance=dispositivo)

    return render(request, 'red/dispositivo/form_dispositivo_cliente.html', {
        'form': form, 'sector': dispositivo.sector, 'dispositivo': dispositivo, 'cliente': cliente
    })

@login_required
def eliminar_dispositivo(request, pk):
    dispositivo = get_object_or_404(Dispositivo, pk=pk)
    sector_pk = dispositivo.sector_id

    if request.method == 'POST':
        registrar_evento(
	        MODULO,
	        f'Dipositivo {dispositivo.nombre} eliminado',
	        f'Dispositivo #{dispositivo.pk} - {dispositivo.marca} {dispositivo.modelo|""} {dispositivo.ip_gestion}.',
	        nivel=Evento.Nivel.INFO,
        )
        dispositivo.delete()
        return redirect('red:detalle_sector', pk=sector_pk)

    return render(request, 'red/dispositivo/confirmar_eliminar_dispositivo.html', {'dispositivo': dispositivo})


# --- Interfaces -------------------------------------------------------------

@login_required
def nueva_interfaz(request, dispositivo_pk):
    dispositivo = get_object_or_404(Dispositivo, pk=dispositivo_pk)
    error_msg = ""

    if request.method == 'POST':
        form = InterfazForm(request.POST)
        if form.is_valid():
            interfaz = form.save(commit=False)
            interfaz.dispositivo = dispositivo
            interfaz.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo.pk)
        else:
            # si el formlario no es válido.
            error_msg = "Por favor, corrige los errores en el formulario: " + form.errors.as_text()
    else:
        form = InterfazForm()

    return render(request, 'red/interfaz/form_interfaz.html', {
        'form': form, 'dispositivo': dispositivo, 'interfaz': None, 'error_msg': error_msg
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

    return render(request, 'red/interfaz/form_interfaz.html', {
        'form': form, 'dispositivo': interfaz.dispositivo, 'interfaz': interfaz,
    })


@login_required
def eliminar_interfaz(request, pk):
    interfaz = get_object_or_404(Interfaz, pk=pk)
    dispositivo_pk = interfaz.dispositivo_id

    if request.method == 'POST':
        interfaz.delete()
        return redirect('red:detalle_dispositivo', pk=dispositivo_pk)

    return render(request, 'red/interfaz/confirmar_eliminar_interfaz.html', {'interfaz': interfaz})


# --- Enlaces ----------------------------------------------------------------

@login_required
def opciones_interfaces_dispositivo(request):
    """Fragmento HTMX con las opciones de interfaz_destino del dispositivo
    elegido en el formulario de enlaces."""
    destino_id = request.GET.get('dispositivo_destino', '').strip()
    if destino_id.isdigit():
        interfaces = Interfaz.objects.filter(
            dispositivo_id=destino_id
        ).order_by('nombre')
    else:
        interfaces = Interfaz.objects.none()
    return render(request, 'red/enlace/_opciones_interfaz.html', {'interfaces': interfaces})


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

    return render(request, 'red/enlace/form_enlace.html', {
        'form': form, 'dispositivo': dispositivo, 'enlace': None,
    })


@login_required
def editar_enlace(request, pk):
    enlace = get_object_or_404(Enlace, pk=pk)
    dispositivo_pk = enlace.dispositivo_origen_id
    error_msg = ""

    if request.method == 'POST':
        form = EnlaceForm(request.POST, instance=enlace, dispositivo_origen=enlace.dispositivo_origen)
        if form.is_valid():
            form.save()
            return redirect('red:detalle_dispositivo', pk=dispositivo_pk)
        else:
            # si el formlario no es válido.
            error_msg = "Por favor, corrige los errores en el formulario: " + form.errors.as_text()
    else:
        form = EnlaceForm(instance=enlace, dispositivo_origen=enlace.dispositivo_origen)

    return render(request, 'red/enlace/form_enlace.html', {
        'form': form, 'dispositivo': enlace.dispositivo_origen, 'enlace': enlace, 'error_msg': error_msg,
    })


@login_required
def eliminar_enlace(request, pk):
    enlace = get_object_or_404(Enlace, pk=pk)
    dispositivo_pk = enlace.dispositivo_origen_id

    if request.method == 'POST':
        enlace.delete()
        return redirect('red:detalle_dispositivo', pk=dispositivo_pk)

    return render(request, 'red/enlace/confirmar_eliminar_enlace.html', {'enlace': enlace})