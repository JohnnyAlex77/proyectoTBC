# scripts/load_test_data.py
"""
Script para cargar datos de prueba en el sistema TBC
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC.settings')
django.setup()

from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import date, timedelta
import random

def crear_grupos():
    """Crear grupos de usuarios si no existen"""
    grupos = [
        ('Administrador', 'Acceso completo a todos los módulos'),
        ('Medico', 'Acceso clínico completo'),
        ('Enfermera', 'Acceso para seguimiento y administración'),
        ('Tecnologo_Medico', 'Acceso para procesamiento de exámenes'),
        ('Tecnico_Paramedico', 'Acceso para actividades comunitarias'),
    ]
    
    for nombre, descripcion in grupos:
        grupo, creado = Group.objects.get_or_create(
            name=nombre,
            defaults={'name': nombre}
        )
        if creado:
            print(f"Grupo creado: {nombre}")

def crear_usuarios_prueba():
    """Crear usuarios de prueba para cada rol"""
    usuarios = [
        ('admin', 'admin@sistematbc.cl', 'AdminTBC2024!', ['Administrador']),
        ('medico', 'medico@sistematbc.cl', 'MedicoTBC2024!', ['Medico']),
        ('enfermera', 'enfermera@sistematbc.cl', 'EnfermeraTBC2024!', ['Enfermera']),
        ('tecnologo', 'tecnologo@sistematbc.cl', 'TecnologoTBC2024!', ['Tecnologo_Medico']),
        ('paramedico', 'paramedico@sistematbc.cl', 'ParamedicoTBC2024!', ['Tecnico_Paramedico']),
    ]
    
    for username, email, password, grupos in usuarios:
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_staff=True,
                is_active=True
            )
            
            # Asignar grupos
            for grupo_nombre in grupos:
                grupo = Group.objects.get(name=grupo_nombre)
                user.groups.add(grupo)
            
            print(f"Usuario creado: {username} ({', '.join(grupos)})")

def crear_pacientes_prueba():
    """Crear pacientes de prueba"""
    from apps.pacientes.models import PacientesPaciente
    
    comunas_chile = [
        'Santiago', 'Puente Alto', 'Maipú', 'La Florida', 'Las Condes',
        'Ñuñoa', 'San Bernardo', 'Peñalolén', 'El Bosque', 'La Pintana'
    ]
    
    establecimientos = [
        'Hospital San Juan de Dios',
        'Hospital Salvador',
        'Hospital Sótero del Río',
        'Hospital San José',
        'Hospital El Pino'
    ]
    
    enfermedades = [
        'Diabetes, Hipertensión',
        'VIH, Hepatitis B',
        'Asma, Alergias',
        'EPOC, Tabaquismo',
        'Ninguna'
    ]
    
    alergias = [
        'Penicilina, Sulfas',
        'Ibuprofeno, Naproxeno',
        'Mariscos, Maní',
        'Polvo, Ácaros',
        'Ninguna'
    ]
    
    for i in range(1, 21):
        rut = f"{random.randint(10000000, 25000000)}-{random.randint(0,9)}"
        
        if not PacientesPaciente.objects.filter(rut=rut).exists():
            paciente = PacientesPaciente.objects.create(
                rut=rut,
                nombre=f"Paciente Prueba {i}",
                fecha_nacimiento=date.today() - timedelta(days=random.randint(18*365, 80*365)),
                sexo=random.choice(['M', 'F', 'O']),
                domicilio=f"Calle {random.randint(1, 9999)} #{random.randint(1, 999)}",
                comuna=random.choice(comunas_chile),
                telefono=f"+569{random.randint(10000000, 99999999)}",
                establecimiento_salud=random.choice(establecimientos),
                fecha_diagnostico=date.today() - timedelta(days=random.randint(1, 365)),
                tipo_tbc=random.choice(['pulmonar', 'extrapulmonar', 'mixta']),
                baciloscopia_inicial=random.choice(['Positiva', 'Negativa', 'ND']),
                cultivo_inicial=random.choice(['Positivo', 'Negativo', 'Pendiente']),
                poblacion_prioritaria=random.choice(['', 'migrante', 'indígena', 'vih', 'diabetes']),
                enfermedades_preexistentes=random.choice(enfermedades),
                alergias=random.choice(alergias),
                estado=random.choice(['activo', 'suspendido', 'egresado', 'abandono']),
                usuario_registro=User.objects.get(username='admin')
            )
            print(f"Paciente creado: {paciente.nombre}")

def crear_tratamientos_prueba():
    """Crear tratamientos de prueba"""
    from apps.pacientes.models import PacientesPaciente
    from apps.tratamientos.models import Tratamiento, EsquemaMedicamento
    
    pacientes = PacientesPaciente.objects.all()[:10]
    
    for i, paciente in enumerate(pacientes, 1):
        tratamiento = Tratamiento.objects.create(
            paciente=paciente,
            esquema=random.choice(['HRZE', 'HRE', 'HR', 'Personalizado']),
            fecha_inicio=date.today() - timedelta(days=random.randint(30, 180)),
            fecha_termino_estimada=date.today() + timedelta(days=random.randint(30, 180)),
            peso_kg=random.uniform(50, 90),
            resultado_final=random.choice([None, 'Curación', 'En Tratamiento', 'Abandono']),
            observaciones=f"Tratamiento de prueba #{i}",
            usuario_registro=User.objects.get(username='medico')
        )
        
        # Crear esquema de medicamentos
        medicamentos = ['Isoniazida (H)', 'Rifampicina (R)', 'Pirazinamida (Z)', 'Etambutol (E)']
        for medicamento in random.sample(medicamentos, random.randint(2, 4)):
            EsquemaMedicamento.objects.create(
                tratamiento=tratamiento,
                medicamento=medicamento,
                dosis_mg=random.choice([300, 600, 750, 1000]),
                frecuencia=random.choice(['Diaria', '3 veces por semana']),
                fase=random.choice(['Fase Intensiva', 'Fase Continuación']),
                duracion_semanas=random.randint(4, 24),
                fecha_inicio=tratamiento.fecha_inicio,
                fecha_termino=tratamiento.fecha_termino_estimada
            )
        
        print(f"Tratamiento creado para: {paciente.nombre}")

def main():
    """Función principal"""
    print("=" * 50)
    print("CARGANDO DATOS DE PRUEBA - SISTEMA TBC API")
    print("=" * 50)
    
    print("\n1. Creando grupos...")
    crear_grupos()
    
    print("\n2. Creando usuarios de prueba...")
    crear_usuarios_prueba()
    
    print("\n3. Creando pacientes de prueba...")
    crear_pacientes_prueba()
    
    print("\n4. Creando tratamientos de prueba...")
    crear_tratamientos_prueba()
    
    print("\n" + "=" * 50)
    print("DATOS DE PRUEBA CARGADOS EXITOSAMENTE")
    print("=" * 50)
    print("\nResumen:")
    print(f"  • Grupos: {Group.objects.count()}")
    print(f"  • Usuarios: {User.objects.count()}")
    print(f"  • Pacientes: {PacientesPaciente.objects.count()}")
    print(f"  • Tratamientos: {Tratamiento.objects.count()}")

if __name__ == "__main__":
    main()