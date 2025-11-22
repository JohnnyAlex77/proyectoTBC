# load_complete_data.py
import os
import django
from datetime import datetime, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from apps.usuarios.models import UsuariosUsuario
from apps.pacientes.models import PacientesPaciente as Paciente
from apps.contactos.models import ContactosContacto as Contacto
from apps.tratamientos.models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from apps.examenes.models import ExamenesExamenbacteriologico as ExamenBacteriologico, ExamenPPD as PPD, ExamenRadiologico as Radiologico
from apps.prevencion.models import PrevencionQuimioprofilaxis as Quimioprofilaxis, PrevencionVacunacionBCG as VacunacionBCG, PrevencionSeguimiento as Seguimiento
from apps.laboratorio.models import LaboratorioRedLaboratorios as RedLaboratorios, LaboratorioControlCalidad as ControlCalidad, LaboratorioIndicadores as Indicadores, LaboratorioTarjetero as Tarjetero
from apps.indicadores.models import (
    IndicadoresCohorte, IndicadoresOperacionales, 
    IndicadoresPrevencion, Alerta, ReportePersonalizado, Establecimiento
)

from django.utils import timezone

print("🚀 INICIANDO CARGA COMPLETA DE DATOS - SISTEMA TBC")
print("=" * 60)

@transaction.atomic
def main():
    """Función principal para cargar todos los datos"""
    
    print("🧹 Creando base de datos desde cero...")
    
    # 1. CREAR GRUPOS Y PERMISOS
    print("\n1. 👥 CREANDO GRUPOS Y PERMISOS")
    grupos = {}
    
    grupos_data = [
        ('Administrador', 'Acceso completo al sistema'),
        ('Médico', 'Gestión clínica de pacientes y tratamientos'),
        ('Enfermera', 'Seguimiento y administración de tratamientos'),
        ('Tecnólogo Médico', 'Gestión de laboratorio y exámenes'),
        ('Técnico Paramédico', 'Tareas básicas de apoyo')
    ]
    
    for nombre, descripcion in grupos_data:
        grupo, created = Group.objects.get_or_create(name=nombre)
        grupos[nombre] = grupo
        print(f"   ✅ Grupo: {nombre}")
    
    # 2. CREAR ESTABLECIMIENTOS
    print("\n2. 🏥 CREANDO ESTABLECIMIENTOS")
    establecimientos = {}
    
    establecimientos_data = [
        ('Hospital Regional Metropolitano', 'HRM001', 'Hospital', 'Metropolitana'),
        ('CESFAM Norte', 'CFN001', 'Centro de Salud Familiar', 'Metropolitana'),
        ('CESFAM Sur', 'CFS001', 'Centro de Salud Familiar', 'Metropolitana'),
        ('Laboratorio Central de Salud Pública', 'LABCEN001', 'Laboratorio', 'Metropolitana'),
        ('Hospital San José', 'HSJ001', 'Hospital', 'Metropolitana'),
        ('CESFAM Oriente', 'CFO001', 'Centro de Salud Familiar', 'Metropolitana'),
        ('SAPU Emergencia', 'SAPU001', 'Servicio de Urgencia', 'Metropolitana'),
        ('Hospital Sótero del Río', 'HSR001', 'Hospital', 'Metropolitana'),
    ]
    
    for nombre, codigo, tipo, region in establecimientos_data:
        establecimiento = Establecimiento.objects.create(
            nombre=nombre,
            codigo=codigo,
            tipo=tipo,
            region=region
        )
        establecimientos[codigo] = establecimiento
        print(f"   ✅ Establecimiento: {nombre}")
    
    # 3. CREAR USUARIOS (CON RUTs MÁS CORTOS)
    print("\n3. 👤 CREANDO USUARIOS")
    usuarios = {}
    
    usuarios_data = [
        {
            'username': 'admin.saludcentral',
            'password': 'AdminTBC2025*',
            'first_name': 'Carlos',
            'last_name': 'Administrador',
            'email': 'carlos.admin@minsal.cl',
            'is_superuser': True,
            'is_staff': True,
            'rol': 'admin',
            'rut': '12345678-9',  # RUT más corto
            'establecimiento': 'Ministerio de Salud',
            'telefono': '+56912345678',
            'grupo': 'Administrador'
        },
        {
            'username': 'dra.fernandez',
            'password': 'MedicoTBC2025*',
            'first_name': 'Ana',
            'last_name': 'Fernández',
            'email': 'ana.fernandez@hospital.cl',
            'is_superuser': False,
            'is_staff': True,
            'rol': 'medico',
            'rut': '13456789-0',  # RUT más corto
            'establecimiento': 'Hospital Regional Metropolitano',
            'telefono': '+56923456789',
            'grupo': 'Médico'
        },
        {
            'username': 'enf.gonzalez',
            'password': 'EnfermeraTBC2025*',
            'first_name': 'María',
            'last_name': 'González',
            'email': 'maria.gonzalez@cesfam.cl',
            'is_superuser': False,
            'is_staff': True,
            'rol': 'enfermera',
            'rut': '14567890-1',  # RUT más corto
            'establecimiento': 'CESFAM Norte',
            'telefono': '+56934567890',
            'grupo': 'Enfermera'
        },
        {
            'username': 'tm.rodriguez',
            'password': 'TecnologoTBC2025*',
            'first_name': 'Pedro',
            'last_name': 'Rodríguez',
            'email': 'pedro.rodriguez@laboratorio.cl',
            'is_superuser': False,
            'is_staff': True,
            'rol': 'tecnologo',
            'rut': '15678901-2',  # RUT más corto
            'establecimiento': 'Laboratorio Central de Salud Pública',
            'telefono': '+56945678901',
            'grupo': 'Tecnólogo Médico'
        },
        {
            'username': 'tens.martinez',
            'password': 'TensTBC2025*',
            'first_name': 'Juan',
            'last_name': 'Martínez',
            'email': 'juan.martinez@cesfam.cl',
            'is_superuser': False,
            'is_staff': True,
            'rol': 'paramedico',
            'rut': '16789012-3',  # RUT más corto
            'establecimiento': 'CESFAM Sur',
            'telefono': '+56956789012',
            'grupo': 'Técnico Paramédico'
        }
    ]
    
    # Desactivar el signal temporalmente para evitar el error
    from django.db.models.signals import post_save
    from apps.usuarios.models import create_user_profile
    
    post_save.disconnect(create_user_profile, sender=User)
    
    for user_data in usuarios_data:
        user = User.objects.create_user(
            username=user_data['username'],
            password=user_data['password'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            is_superuser=user_data['is_superuser'],
            is_staff=user_data['is_staff'],
            is_active=True,
            date_joined=timezone.now()
        )
        
        # Asignar grupo
        grupo = grupos[user_data['grupo']]
        user.groups.add(grupo)
        
        # Crear perfil extendido MANUALMENTE
        perfil = UsuariosUsuario.objects.create(
            user=user,
            rut=user_data['rut'],
            rol=user_data['rol'],
            establecimiento=user_data['establecimiento'],
            telefono=user_data['telefono'],
            fecha_creacion=timezone.now(),
            fecha_actualizacion=timezone.now()
        )
        
        usuarios[user_data['username']] = user
        print(f"   ✅ Usuario: {user_data['username']} - {user_data['rol']}")
    

if __name__ == '__main__':
    main()