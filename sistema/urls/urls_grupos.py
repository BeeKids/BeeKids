from django.urls import path
from sistema.views.views_actividades import *
from sistema.views import views_actividades
from sistema.views import views_administrador
from sistema.views import views_tutor



urlpatterns = [
    path("administrar", views_administrador.administrar, name="administrar"),
    path('crearGrupo/', views_administrador.crearGrupo, name='crearGrupo'),
    path('listaGrupos/', views_administrador.listar_grupos, name='listaGrupos'),
    path('eliminarGrupo/<int:grupoId>/', views_administrador.eliminarGrupo, name='eliminarGrupo'),
    path('actualizarGrupo/<int:grupoId>/', views_administrador.modificarGrupo, name='modificarGrupo'),
    path('paseDeLista/<int:grupoId>/', views_actividades.paseDeLista, name='paseDeLista'),
    path('registroDeAsistencia/<int:grupoId>/', views_actividades.registroDeAsistencia, name='registroDeAsistencia'),
    path('asignarCalificaciones/<int:grupoId>/', views_actividades.asignacionCalificaciones, name='asignarCalificaciones'),

    #URL específicas para tutores
    
    path('listaGruposTutor/', views_tutor.listaGrupos_tutor, name='listaGrupos_tutor'),
    path('asistenciaTutor/', views_tutor.registroAsistencia_tutor, name='registroAsistencia_tutor'),
    
]
