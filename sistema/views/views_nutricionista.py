from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from sistema.models.models import Nutricionista, Chef, Platillo, MenuSemanal

@login_required
def vista_nutricionista(request):
    if not hasattr(request.user, 'nutricionista'):
        raise PermissionDenied
    
    return render(request, 'sistema/Vista_Nutricionista.html')