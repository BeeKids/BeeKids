from django import forms
from sistema.models.models_actividades import *
from django.core.exceptions import ValidationError  
from typing import Any, Dict
from datetime import date, time
import re
from sistema.models.models import Grupo

class BaseActividadForm(forms.ModelForm):

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if nombre:
            if not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', nombre):
                raise ValidationError(
                    'El nombre debe contener al menos una letra.'
                )

        return nombre


    def clean_descripcion(self):
        descripcion = self.cleaned_data.get('descripcion')

        if descripcion:
            if not re.search(r'[A-Za-zÁÉÍÓÚáéíóúÑñ]', descripcion):
                raise ValidationError(
                    'La descripción debe contener al menos una letra.'
                )

        return descripcion
    
    @staticmethod
    def validarDatosFormulario(formulario, horaInicio, horaFinal, actividad=None):
        if horaFinal and horaInicio:
            if horaFinal <= horaInicio:
                formulario.add_error(
                    'horaFinal',
                    'La hora de finalización debe ser mayor que la hora de inicio.'
                )
                return

            gestorActividades = GestorActividades()

            if actividad:
                horario = actividad.horario
                grupo = actividad.grupo
                fecha = actividad.fecha
            else:
                horario = formulario.cleaned_data.get('horario')
                grupo = formulario.cleaned_data.get('grupo')
                fecha = formulario.cleaned_data.get('fecha')

            if not horario:
                formulario.add_error("horario", "Debe seleccionar un horario válido.")
                return

            if not grupo:
                formulario.add_error("grupo", "Debe seleccionar un grupo.")
                return

            if not fecha:
                formulario.add_error("fecha", "Debe seleccionar una fecha válida.")
                return

            if not gestorActividades.validarRangoDeActividad(horario, horaInicio, horaFinal):
                formulario.add_error(
                    "horaFinal",
                    "La actividad está fuera del horario permitido."
                )
                return

        actividadesExistentes = Actividad.objects.filter(
            grupo=grupo,
            fecha=fecha
        )

        if actividad:
            actividadesExistentes = actividadesExistentes.exclude(id=actividad.id)

        for actividadExistente in actividadesExistentes:
            if horaInicio < actividadExistente.horaFinal and horaFinal > actividadExistente.horaInicio:
                formulario.add_error(
                    "horaFinal",
                    f"Conflicto de horario con la actividad '{actividadExistente.nombre}', registrada de {actividadExistente.horaInicio} a {actividadExistente.horaFinal} para el mismo grupo y fecha."
                )
                return


class CrearActividadForm(BaseActividadForm):

    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.all(),
        required=True,
        empty_label="Selecciona un grupo",
        label="Grupo Asociado",
        error_messages={
            'required': 'Debes seleccionar un grupo.'
        }
    )

    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'horaInicio', 'horaFinal', 'horario', 'fecha', 'grupo']

        labels = {
                'nombre': 'Nombre de la Actividad',
                'descripcion': 'Descripción',
                'horaInicio': 'Hora de Inicio',
                'horaFinal': 'Hora de Finalización',
                'horario': 'Horario Asociado',
                'fecha': 'Fecha de la Actividad',
                'grupo': 'Grupo Asociado',
        }

        widgets = {
            'nombre': forms.TextInput(attrs={
                'placeholder': 'Ingrese el nombre de la actividad'
            }),

            'descripcion': forms.TextInput(attrs={
                'placeholder': 'Ingrese una descripción'
            }),

            'horaInicio': forms.TimeInput(attrs={'type': 'time'}),
            'horaFinal': forms.TimeInput(attrs={'type': 'time'}),

            'horario': forms.Select(),

            'fecha': forms.DateInput(attrs={
                'type': 'date',
                'value': timezone.localdate()
            }),

            'grupo': forms.Select()
        }

    def clean(self):
        datosValidados = super().clean()
        horaInicio = datosValidados.get('horaInicio')
        horaFinal = datosValidados.get('horaFinal')
        self.validarDatosFormulario(self, horaInicio, horaFinal)
        return datosValidados


class ActualizarActividadForm(BaseActividadForm):
    class Meta:
        model = Actividad
        fields = ['nombre', 'descripcion', 'horaInicio', 'horaFinal']
        labels = {
                'nombre': 'Nombre de la Actividad',
                'descripcion': 'Descripción',
                'horaInicio': 'Hora de Inicio',
                'horaFinal': 'Hora de Finalización',
        }

        widgets = {
            'horaInicio': forms.TimeInput(attrs={'type': 'time'}),
            'horaFinal': forms.TimeInput(attrs={'type': 'time'}),
        }
    def clean(self):
        datosValidados = super().clean()
        horaInicio = datosValidados.get('horaInicio')
        horaFinal = datosValidados.get('horaFinal')
        self.validarDatosFormulario(self, horaInicio, horaFinal, self.instance)
        return datosValidados



class CrearHorarioForm(forms.ModelForm):
    class Meta:
        model = HorarioEscolar
        fields = ['fecha', 'horaEntrada', 'horaSalida']
        labels = {
            'fecha': 'Fecha',
            'horaEntrada': 'Hora de Entrada',
            'horaSalida': 'Hora de Salida',
        }
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'horaEntrada': forms.TimeInput(attrs={'type': 'time'}),
            'horaSalida': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        datosValidados = super().clean()

        fecha = datosValidados.get('fecha')
        horaEntrada = datosValidados.get('horaEntrada')
        horaSalida = datosValidados.get('horaSalida')

        # Validar primero si ya existe horario para esa fecha
        if fecha and HorarioEscolar.objects.filter(fecha=fecha).exists():
            self.add_error(
                'fecha',
                'Ya existe un horario para esta fecha.'
            )

            return datosValidados

        # Solo validar horas si la fecha es válida
        if horaEntrada and horaSalida:
            if horaSalida <= horaEntrada:
                self.add_error(
                    'horaSalida',
                    'La hora de salida debe ser mayor que la hora de entrada.'
                )

        return datosValidados