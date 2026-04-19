from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
# Importamos los modelos necesarios desde tu estructura de carpetas
from sistema.models.models import Profesor, Grupo, Alumno

@login_required
def vista_profesor(request):
    # Seguridad MANT-38: Solo permite el acceso si el usuario es un Profesor
    if not hasattr(request.user, 'profesor'):
        raise PermissionDenied
    

    profesor = request.user.profesor
    contexto = {
        'profesor': profesor,
        'grupoID': profesor.grupo,
        'alumnos': profesor.grupo.alumnos.all() if profesor.grupo else []
    }
    return render(request, 'sistema/Vista_Profesor.html', {'grupo': contexto})