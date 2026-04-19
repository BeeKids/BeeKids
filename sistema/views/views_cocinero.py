from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from sistema.models.models import Nutricionista, Chef, Platillo, MenuSemanal

@login_required
def vista_cocinero(request):
    # En tu models.py la clase se llama 'Chef'
    if not hasattr(request.user, 'chef'):
        raise PermissionDenied
    
    return render(request, 'sistema/Vista_Cocinero.html')