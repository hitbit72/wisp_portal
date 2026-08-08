from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inicio(request):
    """
    Pantalla de inicio tras el login.
    En la fase de núcleo solo confirma que el acceso y los roles funcionan.
    El dashboard real (métricas, alarmas, mapa) llega en la fase de monitorización.
    """
    return render(request, 'accounts/inicio.html', {
        'usuario': request.user,
    })
