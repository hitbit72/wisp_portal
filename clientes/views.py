from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ClienteForm, ContratoForm
from .models import Cliente, Contrato


@login_required
def lista_clientes(request):
    """
    Listado de clientes con búsqueda y filtros. Si la petición viene de
    HTMX (búsqueda en vivo), devuelve solo la tabla; si es una carga normal
    de página, devuelve la página completa con el formulario de filtros.
    """
    clientes = Cliente.objects.all()
    clientes_totales = clientes.count()
    clientes_activos = clientes.filter(activo=True).count()
    clientes_inactivos = clientes.filter(activo=False).count()

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        clientes = clientes.filter(
            Q(nombre_completo__icontains=busqueda)
            | Q(apodo__icontains=busqueda)
            | Q(numero_documento__icontains=busqueda)
            | Q(telefono__icontains=busqueda)
        )

    poblacion_seleccionada = request.GET.get('poblacion', '').strip()
    if poblacion_seleccionada:
        clientes = clientes.filter(poblacion=poblacion_seleccionada)

    estado_seleccionado = request.GET.get('estado', '').strip()
    if estado_seleccionado == 'activos':
        clientes = clientes.filter(activo=True)
    elif estado_seleccionado == 'inactivos':
        clientes = clientes.filter(activo=False)

    paginator = Paginator(clientes, 25)
    pagina = paginator.get_page(request.GET.get('page'))

    poblaciones = (
        Cliente.objects.exclude(poblacion='')
        .values_list('poblacion', flat=True)
        .distinct()
        .order_by('poblacion')
    )

    contexto = {
        'pagina': pagina,
        'busqueda': busqueda,
        'poblacion_seleccionada': poblacion_seleccionada,
        'estado_seleccionado': estado_seleccionado,
        'poblaciones': poblaciones,
        'clientes_totales': clientes_totales,
        'clientes_activos': clientes_activos,
        'clientes_inactivos': clientes_inactivos,
        'sector': 0,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'clientes/_tabla.html', contexto)
    return render(request, 'clientes/lista.html', contexto)


@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/detalle.html', {'cliente': cliente})


@login_required
def form_cliente(request, pk=None):
    cliente = get_object_or_404(Cliente, pk=pk) if pk else None

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/form_cliente.html', {'form': form, 'cliente': cliente})


@login_required
def alternar_activo_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.activo = not cliente.activo
        cliente.save()
    return redirect('clientes:detalle', pk=cliente.pk)


@login_required
def nuevo_contrato(request, cliente_pk):
    cliente = get_object_or_404(Cliente, pk=cliente_pk)

    if request.method == 'POST':
        form = ContratoForm(request.POST)
        if form.is_valid():
            contrato = form.save(commit=False)
            contrato.cliente = cliente
            contrato.save()
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ContratoForm()

    return render(request, 'clientes/form_contrato.html', {
        'form': form, 'cliente': cliente, 'contrato': None,
    })


@login_required
def editar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    cliente = contrato.cliente

    if request.method == 'POST':
        form = ContratoForm(request.POST, instance=contrato)
        if form.is_valid():
            form.save()
            return redirect('clientes:detalle', pk=cliente.pk)
    else:
        form = ContratoForm(instance=contrato)

    return render(request, 'clientes/form_contrato.html', {
        'form': form, 'cliente': cliente, 'contrato': contrato,
    })


@login_required
def eliminar_contrato(request, pk):
    contrato = get_object_or_404(Contrato, pk=pk)
    cliente_pk = contrato.cliente_id

    if request.method == 'POST':
        contrato.delete()
        return redirect('clientes:detalle', pk=cliente_pk)

    return render(request, 'clientes/confirmar_eliminar_contrato.html', {'contrato': contrato})
