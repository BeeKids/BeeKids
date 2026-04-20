from django.http import HttpRequest
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse

from sistema.models import UsuarioEscolar


def indice(request: HttpRequest):
    return render(request, "sistema/Vista_Indice.html")


def iniciarSesion(request: HttpRequest):
    if request.method == "POST":
        identificador = request.POST.get("nombre_usuario", "").strip()
        contrasena = request.POST.get("contrasena", "")

        if not identificador or not contrasena:
            return render(request, "sistema/Vista_IniciarSesion.html", {
                "mensaje": "Ingresa tu usuario o correo electrónico y tu contraseña."
            })

        username_para_autenticacion = identificador

        if "@" in identificador:
            usuario_por_correo = UsuarioEscolar.objects.filter(
                email__iexact=identificador
            ).first()

            if usuario_por_correo:
                username_para_autenticacion = usuario_por_correo.username

        usuario = authenticate(
            request,
            username=username_para_autenticacion,
            password=contrasena
        )

        if usuario is not None:
            login(request, usuario)

            # Logica de redirección basada en el rol del usuario

            # 1. Superusuario / Administrador
            if usuario.is_superuser:
                return HttpResponseRedirect(reverse("administrar"))
            
            # 2. Profesor
            if hasattr(usuario, 'profesor'):
                return HttpResponseRedirect(reverse("vista_profesor"))
            
            # 3. Tutor
            if hasattr(usuario, 'tutor'):
                return HttpResponseRedirect(reverse("vista_tutor"))
            
            # 4. Nutricionista
            if hasattr(usuario, 'nutricionista'):
                return HttpResponseRedirect(reverse("vista_nutricionista"))
            
            # 5. Cocinero (Chef)
            if hasattr(usuario, 'chef'):
                return HttpResponseRedirect(reverse("vista_cocinero"))

            # Redirección por defecto si no hay un rol específico asignado
            return HttpResponseRedirect(reverse("indice"))

        return render(request, "sistema/Vista_IniciarSesion.html", {
            "mensaje": "Usuario, correo o contraseña incorrectos."
        })

    return render(request, "sistema/Vista_IniciarSesion.html")


def cerrarSesion(request: HttpRequest):
    logout(request)
    return HttpResponseRedirect(reverse("indice"))


