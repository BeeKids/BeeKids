from django.urls import path

from sistema.views import views_actividades
from sistema.views import views_tutor

urlpatterns = [
    #URL generales para actividades
    path('crearActividad/', views_actividades.creacionActividad, name='crearActividad'),
    path('listaActividades/', views_actividades.listaActividades, name='listaActividades'),
    path('actualizar/<int:actividadId>/', views_actividades.actualizacionActividad, name='actualizarActividad'),
    path('detallesActividad/<int:actividadId>/', views_actividades.detallesDeActividad, name='detallesDeActividad'),
    path('crearHorario/', views_actividades.creacionHorario, name='crearHorario'),
    path('listaHorarios/', views_actividades.listaHorarios, name='listaHorarios'),
    path('eliminarHorario/<int:horarioId>/', views_actividades.eliminacionHorario, name='eliminarHorario'),
    path('eliminarActividad/<int:actividadId>', views_actividades.eliminacionActividad, name='eliminarActividad'),

   #URL específicas para tutores

    path('tutor/horarios/', views_tutor.listaHorarios_tutor, name='listaHorarios_tutor'),
    path('tutor/actividades/', views_tutor.listaActividades_tutor, name='listaActividades_tutor'),
    path('tutor/detalles/<int:actividadId>/', views_tutor.detallesActividad_tutor, name='detallesDeActividad_tutor'),
]