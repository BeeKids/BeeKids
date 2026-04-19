from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from sistema.models.models import Tutor, Alumno
from django.contrib import messages
from datetime import date

# Imports de tus modelos (ajustados a tu estructura de archivos)
from sistema.models.models import Alumno, Grupo, Tutor, UsuarioEscolar, RegistroAsistencia
from sistema.models.models_actividades import Actividad, HorarioEscolar, GestorActividades

# Si vas a usar algún formulario específico para el tutor en el futuro
# from sistema.forms_usuarios import ...

@login_required
def vista_tutor(request):
    # Seguridad MANT-38: Solo permite el acceso si el usuario es un Tutor
    if not hasattr(request.user, 'tutor'):
        raise PermissionDenied
    
    tutor = request.user.tutor
    # Obtenemos los alumnos asociados a este tutor específico
    tutorados = tutor.tutorAlumno.all() 
    
    return render(request, 'sistema/Vista_Tutor.html', {'tutorados': tutorados})



@login_required
def listaGrupos_tutor(request):
    if not hasattr(request.user, 'tutor'):
        raise PermissionDenied
    
    # Obtenemos los alumnos asignados a este tutor
    mis_tutorados = Alumno.objects.filter(tutorAlumno=request.user.tutor)
    
    # Extraemos los grupos únicos de esos alumnos
    grupos = Grupo.objects.filter(alumnos__in=mis_tutorados).distinct().prefetch_related('alumnos')
    
    return render(request, "sistema/Vista_ListaGrupos_Tutor.html", {'grupos': grupos})


@login_required
def listaActividades_tutor(request):
    if not hasattr(request.user, 'tutor'):
        raise PermissionDenied
    
    # Identificamos los grupos de sus tutorados
    grupos_ids = Alumno.objects.filter(tutorAlumno=request.user.tutor).values_list('grupo_id', flat=True)
    
    # Filtramos actividades que pertenezcan a esos grupos
    actividades = Actividad.objects.filter(grupo_id__in=grupos_ids).distinct()
    
    return render(request, "sistema/Vista_ListaActividades_Tutor.html", {"actividades": actividades})


@login_required
def detallesActividad_tutor(request, actividadId):
    actividad = get_object_or_404(Actividad, id=actividadId)
    
    # Verificación de seguridad: ¿Esta actividad pertenece a un grupo de sus tutorados?
    grupos_del_tutor = Alumno.objects.filter(tutorAlumno=request.user.tutor).values_list('grupo_id', flat=True)
    
    if actividad.grupo.id not in grupos_del_tutor:
        raise PermissionDenied("No tienes permiso para ver esta actividad.")

    return render(request, "sistema/Vista_DetallesActividad_Tutor.html", {'actividad': actividad})


@login_required
def listaHorarios_tutor(request):
    if not hasattr(request.user, 'tutor'):
        raise PermissionDenied
        
    # El horario escolar suele ser general, pero lo vinculamos a la visibilidad del tutor
    horarios = HorarioEscolar.objects.all() # O filtrar por relación si el modelo lo permite
    return render(request, "sistema/Vista_ListaHorarios_Tutor.html", {'horarios': horarios})



@login_required
def registroAsistencia_tutor(request):
    if not hasattr(request.user, 'tutor'):
        raise PermissionDenied
    
    mis_tutorados = Alumno.objects.filter(tutorAlumno=request.user.tutor)
    
    # Obtenemos todos los registros de asistencia de sus hijos
    asistencias = RegistroAsistencia.objects.filter(alumno__in=mis_tutorados).order_by('-fecha')
    
    return render(request, "sistema/Vista_Asistencia_Tutor.html", {
        'asistencias': asistencias,
        'tutorados': mis_tutorados
    })