from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import UsuariosUsuario
from django.utils import timezone

class UsuarioCreateForm(forms.ModelForm):
    # Campos del User 
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
        help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente."
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.cl'}),
        required=True
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'}),
        required=True
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
        help_text="Mínimo 8 caracteres."
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        help_text="Ingrese la misma contraseña para verificación."
    )

    class Meta:
        model = UsuariosUsuario
        fields = ['rut', 'rol', 'establecimiento', 'telefono']
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9'}),
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'establecimiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Establecimiento de salud'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'})
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError('El nombre de usuario es obligatorio.')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_rut(self):
        rut = self.cleaned_data.get('rut')
        if not rut:
            raise ValidationError('El RUT es obligatorio.')
        if UsuariosUsuario.objects.filter(rut=rut).exists():
            raise ValidationError('Este RUT ya está registrado.')
        return rut

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden.")
            if len(password1) < 8:
                self.add_error('password1', "La contraseña debe tener al menos 8 caracteres.")
        return cleaned_data

    def save(self, commit=True):
        # PRIMERO crear el User de Django correctamente
        user = User(
            username=self.cleaned_data['username'], 
            email=self.cleaned_data['email'], 
            first_name=self.cleaned_data['first_name'], 
            last_name=self.cleaned_data['last_name']
        )
        user.set_password(self.cleaned_data['password1'])
        user.save()

        # LUEGO crear el UsuariosUsuario con fecha_creacion explícita
        usuario = super().save(commit=False)
        usuario.user = user
        usuario.rut = self.cleaned_data['rut']
        usuario.rol = self.cleaned_data['rol']
        usuario.establecimiento = self.cleaned_data['establecimiento']
        usuario.telefono = self.cleaned_data.get('telefono', '')
        
        # FORZAR la fecha_creacion manualmente
        usuario.fecha_creacion = timezone.now()

        if commit:
            usuario.save()

        return usuario

class UsuarioUpdateForm(forms.ModelForm):
    # Campos del User - HACIENDO que readonly en el template, pero con datos
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        help_text="Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente."
    )
    
    # Agregar campo RUT al formulario de edición
    rut = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        required=True
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        required=True
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = UsuariosUsuario
        fields = ['rut', 'rol', 'establecimiento', 'telefono']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-control'}),
            'establecimiento': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'user'):
            # Llena los campos del User con los valores actuales
            self.fields['username'].initial = self.instance.user.username
            self.fields['rut'].initial = self.instance.rut
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def clean_username(self):
        # En edición, no validamos username ya que es readonly
        return self.cleaned_data.get('username')

    def clean_rut(self):
        # En edición, no validamos RUT ya que es readonly
        return self.cleaned_data.get('rut')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('El correo electrónico es obligatorio.')
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)

        # Actualizar el User
        if hasattr(usuario, 'user'):
            user = usuario.user
            user.email = self.cleaned_data['email']
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.save()

        # Actualizar campos de UsuariosUsuario
        usuario.rol = self.cleaned_data['rol']
        usuario.establecimiento = self.cleaned_data['establecimiento']
        usuario.telefono = self.cleaned_data.get('telefono', '')

        if commit:
            usuario.save()
        return usuario

class PasswordChangeCustomForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})