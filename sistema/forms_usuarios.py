from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from sistema.models.models import Grupo, Tutor, UsuarioEscolar
import re


class CrearUsuarioForm(forms.Form):
    ROLES = [
        ('Profesor', 'Profesor'),
        ('Tutor', 'Tutor'),
        ('Alumno', 'Alumno'),
        ('Nutricionista', 'Nutricionista'),
        ('Cocinero', 'Cocinero'),
        ('Administrador', 'Administrador'),
    ]

    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9._]+$',
        message='El nombre de usuario solo puede contener letras, números, punto y guion bajo.'
    )

    nombre = forms.CharField(
        label="Nombres",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. Aurora',
            'class': 'campo-input',
            'autocomplete': 'given-name'
        })
    )

    apellido = forms.CharField(
        label="Apellidos",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. Cetina',
            'class': 'campo-input',
            'autocomplete': 'family-name'
        })
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={
            'placeholder': 'ejemplo@correo.com',
            'class': 'campo-input',
            'autocomplete': 'email',
            'pattern': r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
            'title': 'Ingresa un correo válido, por ejemplo: usuario@dominio.com'
        }),
    )

    username = forms.CharField(
        label="Nombre de usuario",
        min_length=4,
        max_length=20,
        required=False,
        validators=[username_validator],
        widget=forms.TextInput(attrs={
            'placeholder': 'Ej. aurora.cetina',
            'class': 'campo-input',
            'autocomplete': 'username'
        }),
        help_text="Debe tener entre 4 y 20 caracteres. Solo letras, números, punto y guion bajo."
    )

    contrasena = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Ingresa una contraseña segura',
            'class': 'campo-input',
            'autocomplete': 'new-password'
        }),
        help_text="Mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial."
    )

    confirmar_contrasena = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repite la contraseña',
            'class': 'campo-input',
            'autocomplete': 'new-password'
        })
    )

    rol = forms.ChoiceField(
        label="Tipo de usuario",
        choices=ROLES,
        required=True,
        widget=forms.Select(attrs={
            'class': 'campo-input'
        })
    )

    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.all(),
        label="Grupo",
        required=False,
        empty_label="Selecciona un grupo",
        widget=forms.Select(attrs={
            'class': 'campo-input'
        })
    )

    tutor = forms.ModelChoiceField(
        queryset=Tutor.objects.all(),
        label="Tutor",
        required=False,
        empty_label="Selecciona un tutor",
        widget=forms.Select(attrs={
            'class': 'campo-input'
        })
    )

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre'].strip()
        if len(nombre) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data['apellido'].strip()
        if len(apellido) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        return apellido

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            return ""
        username = username.strip()
        if ' ' in username:
            raise ValidationError("El nombre de usuario no puede contener espacios.")
        if UsuarioEscolar.objects.filter(username__iexact=username).exists():
            raise ValidationError("Este nombre de usuario ya está registrado.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            return ""

        email = email.strip().lower()

        patron_email = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(patron_email, email):
            raise ValidationError("Ingresa un correo electrónico válido.")

        dominio = email.split('@')[1]

        if '..' in dominio or dominio.startswith('.') or dominio.endswith('.'):
            raise ValidationError("El dominio del correo no es válido.")

        dominios_permitidos = [
            'gmail.com',
            'hotmail.com',
            'outlook.com',
            'yahoo.com',
            'icloud.com',
            'uady.mx',
            'alumnos.uady.mx'
        ]

        if dominio not in dominios_permitidos:
            raise ValidationError("El dominio del correo no está permitido.")

        if UsuarioEscolar.objects.filter(email__iexact=email).exists():
            raise ValidationError("Este correo electrónico ya está registrado.")

        return email

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')

        if not contrasena:
            return ""

        if len(contrasena) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', contrasena):
            raise ValidationError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r'[a-z]', contrasena):
            raise ValidationError("La contraseña debe contener al menos una minúscula.")
        if not re.search(r'\d', contrasena):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[^A-Za-z0-9]', contrasena):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")

        return contrasena

    def clean(self):
        cleaned_data = super().clean()
        rol = cleaned_data.get('rol')
        grupo = cleaned_data.get('grupo')
        tutor = cleaned_data.get('tutor')
        email = cleaned_data.get('email')
        username = cleaned_data.get('username')
        contrasena = cleaned_data.get('contrasena')
        confirmar_contrasena = cleaned_data.get('confirmar_contrasena')

        if rol == 'Profesor':
            if not grupo:
                self.add_error('grupo', 'Debes seleccionar un grupo para el profesor.')
            if not email:
                self.add_error('email', 'Debes ingresar un correo electrónico.')
            if not username:
                self.add_error('username', 'Debes ingresar un nombre de usuario.')
            if not contrasena:
                self.add_error('contrasena', 'Debes ingresar una contraseña.')
            if not confirmar_contrasena:
                self.add_error('confirmar_contrasena', 'Debes confirmar la contraseña.')

            cleaned_data['tutor'] = None

        elif rol == 'Alumno':
            if not tutor:
                self.add_error('tutor', 'Debes seleccionar un tutor para el alumno.')

            cleaned_data['grupo'] = None
            cleaned_data['email'] = ""
            cleaned_data['username'] = ""
            cleaned_data['contrasena'] = ""
            cleaned_data['confirmar_contrasena'] = ""

        else:
            if not email:
                self.add_error('email', 'Debes ingresar un correo electrónico.')
            if not username:
                self.add_error('username', 'Debes ingresar un nombre de usuario.')
            if not contrasena:
                self.add_error('contrasena', 'Debes ingresar una contraseña.')
            if not confirmar_contrasena:
                self.add_error('confirmar_contrasena', 'Debes confirmar la contraseña.')

            cleaned_data['grupo'] = None
            cleaned_data['tutor'] = None

        if rol != 'Alumno' and contrasena and confirmar_contrasena:
            if contrasena != confirmar_contrasena:
                self.add_error('confirmar_contrasena', 'Las contraseñas no coinciden.')

        return cleaned_data


class EliminarUsuarioForm(forms.Form):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=UsuarioEscolar.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Selecciona Usuarios para eliminar"
    )


class ModificarUsuarioForm(forms.Form):
    username_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9._]+$',
        message='El nombre de usuario solo puede contener letras, números, punto y guion bajo.'
    )

    nombre = forms.CharField(
        label="Nombres",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'campo-input',
            'autocomplete': 'given-name'
        })
    )

    apellido = forms.CharField(
        label="Apellidos",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'campo-input',
            'autocomplete': 'family-name'
        })
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'campo-input',
            'autocomplete': 'email',
            'pattern': r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$',
            'title': 'Ingresa un correo válido, por ejemplo: usuario@dominio.com'
        })
    )

    username = forms.CharField(
        label="Nombre de usuario",
        max_length=20,
        min_length=4,
        required=False,
        validators=[username_validator],
        widget=forms.TextInput(attrs={
            'class': 'campo-input',
            'autocomplete': 'username'
        })
    )

    contrasena = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'campo-input',
            'autocomplete': 'new-password'
        })
    )

    grupo = forms.ModelChoiceField(
        queryset=Grupo.objects.all(),
        label="Grupo",
        required=False,
        widget=forms.Select(attrs={'class': 'campo-input'})
    )

    tutor = forms.ModelChoiceField(
        queryset=Tutor.objects.all(),
        label="Tutor",
        required=False,
        widget=forms.Select(attrs={'class': 'campo-input'})
    )

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('usuario', None)
        rol = kwargs.pop('rol', None)
        super().__init__(*args, **kwargs)

        self.usuario = usuario
        self.rol = rol

        if usuario:
            self.fields['nombre'].initial = usuario.first_name
            self.fields['apellido'].initial = usuario.last_name
            self.fields['email'].initial = usuario.email
            self.fields['username'].initial = usuario.username
            self.fields['grupo'].initial = getattr(usuario, 'grupo', None)
            self.fields['tutor'].initial = getattr(usuario, 'tutorAlumno', None)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            return username

        username = username.strip()

        if ' ' in username:
            raise ValidationError("El nombre de usuario no puede contener espacios.")

        existe = UsuarioEscolar.objects.filter(username__iexact=username).exclude(id=self.usuario.id).exists()
        if existe:
            raise ValidationError("Este nombre de usuario ya está registrado.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if not email:
            return email

        email = email.strip().lower()

        patron_email = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        if not re.match(patron_email, email):
            raise ValidationError("Ingresa un correo electrónico válido.")

        dominio = email.split('@')[1]

        if '..' in dominio or dominio.startswith('.') or dominio.endswith('.'):
            raise ValidationError("El dominio del correo no es válido.")

        dominios_permitidos = [
            'gmail.com',
            'hotmail.com',
            'outlook.com',
            'yahoo.com',
            'icloud.com',
            'uady.mx',
            'alumnos.uady.mx'
        ]

        if dominio not in dominios_permitidos:
            raise ValidationError("El dominio del correo no está permitido.")

        existe = UsuarioEscolar.objects.filter(email__iexact=email).exclude(id=self.usuario.id).exists()
        if existe:
            raise ValidationError("Este correo electrónico ya está registrado.")

        return email

    def clean_contrasena(self):
        contrasena = self.cleaned_data.get('contrasena')

        if not contrasena:
            return contrasena

        if len(contrasena) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', contrasena):
            raise ValidationError("La contraseña debe contener al menos una mayúscula.")
        if not re.search(r'[a-z]', contrasena):
            raise ValidationError("La contraseña debe contener al menos una minúscula.")
        if not re.search(r'\d', contrasena):
            raise ValidationError("La contraseña debe contener al menos un número.")
        if not re.search(r'[^A-Za-z0-9]', contrasena):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")

        return contrasena

    def clean(self):
        cleaned_data = super().clean()
        grupo = cleaned_data.get('grupo')
        tutor = cleaned_data.get('tutor')

        if self.rol == 'Profesor':
            if not grupo:
                self.add_error('grupo', 'Debes seleccionar un grupo para el profesor.')
            cleaned_data['tutor'] = None

        elif self.rol == 'Alumno':
            if not tutor:
                self.add_error('tutor', 'Debes seleccionar un tutor para el alumno.')
            cleaned_data['grupo'] = None

        else:
            cleaned_data['grupo'] = None
            cleaned_data['tutor'] = None

        return cleaned_data