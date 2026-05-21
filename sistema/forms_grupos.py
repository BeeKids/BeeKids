from django import forms

from sistema.models.models import Alumno, Grupo
from .models import *
from django.core.exceptions import ValidationError 
from sistema.models.models import *


        
class CrearGrupoForm(forms.ModelForm):

    alumnos = forms.ModelMultipleChoiceField(
        queryset=Alumno.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Alumnos disponibles"
    )

    class Meta:
        model = Grupo
        fields = ['nombre', 'alumnos']
        labels = {
            'nombre': 'Nombre del grupo',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej. Grupo A',
                'class': 'campo-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['alumnos'].queryset = Alumno.objects.filter(
            grupo__isnull=True
        ).order_by('first_name', 'last_name')

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if nombre:
            nombre = nombre.strip()

            if Grupo.objects.filter(nombre__iexact=nombre).exists():
                raise ValidationError(
                    "Ya existe un grupo con este nombre. Escribe otro nombre."
                )

        return nombre

    def clean_alumnos(self):
        alumnos = self.cleaned_data.get('alumnos')

        if not alumnos:
            raise ValidationError(
                "Debes seleccionar al menos un alumno para crear el grupo."
            )

        alumnosAsignados = alumnos.exclude(grupo__isnull=True)

        if alumnosAsignados.exists():
            raise ValidationError(
                "Uno o más alumnos seleccionados ya pertenecen a otro grupo."
            )

        return alumnos

class EliminarGrupoForm(forms.Form):
    grupos = forms.ModelMultipleChoiceField(
        queryset=Grupo.objects.all(),  
        widget=forms.CheckboxSelectMultiple,  # Usa checkboxes para selección múltiple
        required=True,  # Obliga a seleccionar al menos un grupo
        label="Selecciona Grupos para eliminar"
    )

class ActualizarGrupoForm(forms.ModelForm):

    alumnos = forms.ModelMultipleChoiceField(
        queryset=Alumno.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona los alumnos para el grupo"
    )

    class Meta:
        model = Grupo
        fields = ['nombre', 'alumnos']

        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ej. Grupo A',
                'class': 'campo-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        grupoActual = self.instance

        alumnosDisponibles = Alumno.objects.filter(
            grupo__isnull=True
        )

        alumnosDelGrupo = grupoActual.alumnos.all()

        self.fields['alumnos'].queryset = (
            alumnosDisponibles | alumnosDelGrupo
        ).distinct().order_by(
            'first_name',
            'last_name'
        )

        self.fields['alumnos'].initial = alumnosDelGrupo

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if nombre:
            nombre = nombre.strip()

            existeGrupo = Grupo.objects.filter(
                nombre__iexact=nombre
            ).exclude(
                id=self.instance.id
            )

            if existeGrupo.exists():
                raise ValidationError(
                    "Ya existe un grupo con este nombre."
                )

        return nombre

    def clean_alumnos(self):
        alumnos = self.cleaned_data.get('alumnos')

        if not alumnos:
            raise ValidationError(
                "Debes seleccionar al menos un alumno."
            )

        alumnosInvalidos = alumnos.exclude(
            grupo__isnull=True
        ).exclude(
            grupo=self.instance
        )

        if alumnosInvalidos.exists():
            raise ValidationError(
                "Uno o más alumnos seleccionados ya pertenecen a otro grupo."
            )

        return alumnos

class PaseDeListaForm(forms.Form):
    def __init__(self, grupo, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for alumno in grupo.alumnos.all():
            self.fields[f'asistencias_{alumno.id}'] = forms.BooleanField(
                label=f"{alumno.getNombre()}",
                required=False
            )

class AsignarCalificacionForm(forms.ModelForm):
    class Meta:
        model = RegistroCalificaciones
        fields = ['alumno', 'calificacion', 'comentario']

    calificacion = forms.ChoiceField(choices=[(i, str(i)) for i in range(1, 6)], label="Calificación")
    comentario = forms.CharField(required=False, widget=forms.Textarea, label="Comentario")
