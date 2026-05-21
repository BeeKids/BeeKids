from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404 
from django.contrib import messages
import re
from datetime import datetime

from sistema.models.models import Chef, Platillo, MenuSemanal, Nutricionista, MenuPlatillo


def contiene_letras(texto):
    return bool(re.search(r"[A-Za-zÁÉÍÓÚáéíóúÑñ]", texto or ""))

def opcionesMenu(request):
    return render(request, "sistema/Vista_OpcionesMenu.html")

def gestionarRecomendaciones(request):
    platillos = Platillo.objects.all() 
    return render(request, "sistema/Vista_GestionarRecomendaciones.html", {'platillos': platillos})

def crearRecomendacion(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        consideraciones = request.POST.get("consideraciones", "").strip()

        if not contiene_letras(nombre):
            messages.error(request, "El nombre del platillo debe contener al menos una letra.")
            return render(request, "sistema/Vista_CrearRecomendacion.html")

        if Platillo.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, "Ya existe un platillo con ese nombre.")
            return render(request, "sistema/Vista_CrearRecomendacion.html")

        if not contiene_letras(descripcion):
            messages.error(request, "La descripción debe contener al menos una letra.")
            return render(request, "sistema/Vista_CrearRecomendacion.html")

        if not contiene_letras(consideraciones):
            messages.error(request, "Las consideraciones deben contener al menos una letra.")
            return render(request, "sistema/Vista_CrearRecomendacion.html")

        try:
            Platillo.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                consideraciones=consideraciones
            )

            messages.success(request, "Recomendación creada con éxito.")
            return redirect("gestionarRecomendaciones")

        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return render(request, "sistema/Vista_CrearRecomendacion.html")

    return render(request, "sistema/Vista_CrearRecomendacion.html")

def editarRecomendacion(request, platillo_id):
    platillo = get_object_or_404(Platillo, id=platillo_id)

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        descripcion = request.POST.get("descripcion", "").strip()
        consideraciones = request.POST.get("consideraciones", "").strip()

        if not contiene_letras(nombre):
            messages.error(request, "El nombre del platillo debe contener al menos una letra.")
            return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

        if Platillo.objects.filter(nombre__iexact=nombre).exclude(id=platillo.id).exists():
            messages.error(request, "Ya existe un platillo con ese nombre.")
            return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

        if not contiene_letras(descripcion):
            messages.error(request, "La descripción debe contener al menos una letra.")
            return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

        if not contiene_letras(consideraciones):
            messages.error(request, "Las consideraciones deben contener al menos una letra.")
            return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

        try:
            platillo.nombre = nombre
            platillo.descripcion = descripcion
            platillo.consideraciones = consideraciones
            platillo.save()

            messages.success(request, "Platillo actualizado con éxito.")
            return redirect("gestionarRecomendaciones")

        except Exception as e:
            messages.error(request, f"Ocurrió un error al actualizar: {e}")
            return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

    return render(request, "sistema/Vista_EditarRecomendacion.html", {"recomendacion": platillo})

def eliminarRecomendacion(request, platillo_id):
    
    platillo = get_object_or_404(Platillo, id=platillo_id)
    
    if request.method == "POST":
        try:
            platillo.delete()
            messages.success(request, "Recomendación eliminada con éxito.")
            return redirect("gestionarRecomendaciones") 
        except Exception as e:
            messages.error(request, f"Ocurrió un error: {e}")
            return render(request, "sistema/error.html", {"message": str(e)})
    
    return render(request, "sistema/Vista_GestionarRecomendaciones.html")

def crearMenu(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        fecha_inicio = request.POST.get("fecha_inicio")
        fecha_fin = request.POST.get("fecha_fin")

        if not contiene_letras(nombre):
            messages.error(request, "El nombre del menú debe contener al menos una letra.")
            return render(request, "sistema/Vista_CrearMenuSemanal.html")

        if MenuSemanal.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, "Ya existe un menú semanal con ese nombre.")
            return render(request, "sistema/Vista_CrearMenuSemanal.html")

        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if fecha_fin_dt <= fecha_inicio_dt:
                messages.error(request, "La fecha de fin debe ser mayor a la fecha de inicio.")
                return render(request, "sistema/Vista_CrearMenuSemanal.html")

            Chef.crearMenuSemanal(nombre, fecha_inicio_dt, fecha_fin_dt)
            messages.success(request, "Menú semanal creado con éxito.")
            return render(request, "sistema/Vista_CrearMenuSemanal.html")

        except ValueError:
            messages.error(request, "Las fechas ingresadas no son válidas.")
            return render(request, "sistema/Vista_CrearMenuSemanal.html")

        except Exception as e:
            messages.error(request, f"Error al crear el menú: {str(e)}")
            return render(request, "sistema/Vista_CrearMenuSemanal.html")

    return render(request, "sistema/Vista_CrearMenuSemanal.html")


def seleccionarMenuSemanal(request):
    menu_id = request.GET.get('menu_id')
    if menu_id:
        if request.GET.get('ver'):
            return vizualizarMenuSemanal(request, menu_id)
        else:
            return gestionarMenuSemanal(request, menu_id)

    menus = MenuSemanal.objects.all()
    return render(request, "sistema/Vista_SeleccionarMenuSemanal.html", {
        'menus': menus
    })

        
def vizualizarMenuSemanal(request, menu_id):
    try:
        menu = MenuSemanal.objects.get(id=menu_id)

        platillosPorDia = {dia: [] for dia in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']}

        menu_platillos = MenuPlatillo.objects.filter(menu=menu)

        for menu_platillo in menu_platillos:
            platillosPorDia[menu_platillo.dia].append(menu_platillo.platillo)

        return render(request, 'sistema/Vista_VerMenuSemanal.html', {
            'menu': menu,
            'platillos_por_dia': platillosPorDia,
        })
    except MenuSemanal.DoesNotExist:
        messages.error(request, "El menú solicitado no existe.")
        return redirect("seleccionarMenuSemanal")



def gestionarMenuSemanal(request, menu_id): 
    menu = get_object_or_404(MenuSemanal, id=menu_id)
    platillosPorDia = {}

    diasDeLaSemana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    for dia in diasDeLaSemana:
        platillosPorDia[dia] = Platillo.objects.filter(platillo_menus__menu=menu, platillo_menus__dia=dia)

    return render(request, 'sistema/Vista_GestionarMenuSemanal.html', {
        'menu': menu,
        'dias': diasDeLaSemana,
        'platillos_por_dia': platillosPorDia.items(),
    })


def agregarPlatilloDelDia(request, menu_id):
    menu = get_object_or_404(MenuSemanal, id=menu_id)
    dia = request.GET.get('dia')
    platillos = Platillo.objects.all()

    if request.method == "POST":
        platillo_id = request.POST.get('platillo_id')
        try:
            Chef.agregarPlatilloAlMenu(menu, platillo_id, dia)
            messages.success(request, "Platillo agregado con éxito.")
        except Exception as e:
            messages.error(request, f"Error al agregar el platillo: {str(e)}")
        return redirect('gestionarMenuSemanal', menu_id=menu.id)

    return render(request, 'sistema/Vista_EditarPlatillo.html', {
        'accion': 'add',
        'menu': menu,
        'platillos': platillos,
        'dia': dia,
    })


def modificarPlatilloDelDia(request, menu_id): 
    menu = get_object_or_404(MenuSemanal, id=menu_id)
    dia = request.GET.get('dia')

    platillos = Platillo.objects.filter(platillo_menus__menu=menu, platillo_menus__dia=dia)

    if request.method == 'POST':
        platillo_id = request.POST.get('platillo_id')
        try:
            Nutricionista.modificarRecomendaciones(
                menu,
                platillo_id=platillo_id,
                nombre=request.POST.get('nombre'),
                descripcion=request.POST.get('descripcion'),
                consideraciones=request.POST.get('consideraciones')
            )
            messages.success(request, "Recomendación modificada con éxito.")
            return redirect('gestionarMenuSemanal', menu_id=menu.id)
        except Exception as e:
            messages.error(request, f"Error al modificar la recomendación: {str(e)}")
            return redirect('gestionarMenuSemanal', menu_id=menu.id)

    return render(request, 'sistema/Vista_EditarPlatillo.html', {
        'accion': 'edit',
        'menu': menu,
        'platillos': platillos,
        'dia': dia,
    })


def eliminarPlatilloDelDia(request, menu_id):  
    menu = get_object_or_404(MenuSemanal, id=menu_id)
    dia = request.GET.get('dia')
    platillos = Platillo.objects.filter(platillo_menus__menu=menu, platillo_menus__dia=dia)

    if request.method == 'POST':
        platillo_id = request.POST.get('platillo_id')
        try:
            
            Chef.eliminarPlatilloDelMenu(menu, platillo_id, dia) 
            messages.success(request, "Platillo eliminado con éxito.")
            return redirect('gestionarMenuSemanal', menu_id=menu.id)
        except Exception as e:
            messages.error(request, f"Error al eliminar el platillo: {str(e)}")
            return redirect('gestionarMenuSemanal', menu_id=menu.id)

    return render(request, 'sistema/Vista_EditarPlatillo.html', {
        'accion': 'delete',
        'menu': menu,
        'platillos': platillos,
        'dia': dia,
    })


def eliminarMenu(request, menu_id): 
    Chef.eliminarMenuSemanal(menu_id)

    return redirect('seleccionarMenuSemanal')