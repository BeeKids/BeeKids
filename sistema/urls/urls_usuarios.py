from django.urls import path
from sistema.views import views_administrador, views_cocinero, views_nutricionista, views_profesor, views_tutor



urlpatterns = [
    # --- RUTAS DE ADMINISTRACIÓN DE USUARIOS  ---
    path('crearUsuario/', views_administrador.crearUsuario, name='crearUsuario'),
    path('listaUsuarios/', views_administrador.listarUsuarios, name='listaUsuarios'),
    path('eliminarUsuario/<int:usuarioId>/', views_administrador.eliminarUsuario, name='eliminarUsuario'),    
    path('modificarUsuario/<int:usuarioId>/ <str:rol>', views_administrador.modificarUsuario, name='modificarUsuario'),

    # --- NUEVAS RUTAS: PANELES DE CONTROL POR ROL ---
    # Estas son las URLs a las que el sistema redirigirá tras el login
    path('panel/profesor/', views_profesor.vista_profesor, name='vista_profesor'),
    path('panel/tutor/', views_tutor.vista_tutor, name='vista_tutor'),
    path('panel/nutricionista/', views_nutricionista.vista_nutricionista, name='vista_nutricionista'),
    path('panel/cocinero/', views_cocinero.vista_cocinero, name='vista_cocinero')
]