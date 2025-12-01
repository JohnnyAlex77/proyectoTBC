# script_usuarios_grupos.py
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from apps.usuarios.models import UsuariosUsuario
from django.db.models.signals import post_save

def main():
    """
    Script para crear grupos de usuarios, asignar permisos por rol
    y crear usuarios de ejemplo para cada rol del sistema TBC.
    """
    
    # Desconectar signals temporales para evitar conflictos
    print("Desconectando signals temporales...")
    from apps.usuarios.models import create_user_profile, save_user_profile
    post_save.disconnect(create_user_profile, sender=User)
    post_save.disconnect(save_user_profile, sender=User)
    
    with transaction.atomic():
        # ======================================================
        # 1. CREACIÓN DE GRUPOS CON PERMISOS ESPECÍFICOS POR ROL
        # ======================================================
        print("\n1. Creando grupos y asignando permisos...")
        
        grupos_config = {
            'Administrador': {
                'descripcion': 'Acceso completo a todos los módulos del sistema',
                'permisos_apps': {
                    'usuarios': ['view', 'add', 'change', 'delete'],
                    'pacientes': ['view', 'add', 'change', 'delete'],
                    'tratamientos': ['view', 'add', 'change', 'delete'],
                    'examenes': ['view', 'add', 'change', 'delete'],
                    'contactos': ['view', 'add', 'change', 'delete'],
                    'prevencion': ['view', 'add', 'change', 'delete'],
                    'laboratorio': ['view', 'add', 'change', 'delete'],
                    'indicadores': ['view', 'add', 'change', 'delete'],
                }
            },
            'Médico': {
                'descripcion': 'Acceso a módulos clínicos (pacientes, tratamientos, exámenes)',
                'permisos_apps': {
                    'pacientes': ['view', 'add', 'change'],
                    'tratamientos': ['view', 'add', 'change'],
                    'examenes': ['view', 'add', 'change'],
                    'contactos': ['view'],
                    'indicadores': ['view'],
                },
                'permisos_excluir': [
                    'delete_pacientespaciente',
                    'delete_tratamiento',
                    'delete_examenesexamenbacteriologico'
                ]
            },
            'Enfermera': {
                'descripcion': 'Acceso a módulos de cuidados y seguimiento',
                'permisos_apps': {
                    'pacientes': ['view', 'change'],
                    'tratamientos': ['view', 'change'],
                    'examenes': ['view'],
                    'contactos': ['view'],
                    'prevencion': ['view', 'add', 'change'],
                },
                'permisos_especiales': [
                    'add_dosisadministrada',
                    'change_dosisadministrada',
                    'view_dosisadministrada',
                ]
            },
            'Tecnólogo Médico': {
                'descripcion': 'Acceso a módulos de laboratorio y exámenes',
                'permisos_apps': {
                    'examenes': ['view', 'add', 'change'],
                    'laboratorio': ['view', 'add', 'change'],
                    'pacientes': ['view'],
                },
                'permisos_especiales': [
                    'add_laboratoriotarjetero',
                    'change_laboratoriotarjetero',
                    'view_laboratoriotarjetero',
                ]
            },
            'Técnico Paramédico': {
                'descripcion': 'Acceso a módulos de campo y prevención',
                'permisos_apps': {
                    'pacientes': ['view', 'add'],
                    'contactos': ['view', 'add'],
                    'prevencion': ['view', 'add'],
                },
                'permisos_excluir': [
                    'change_pacientespaciente',
                    'delete_pacientespaciente',
                    'delete_contactoscontacto'
                ]
            }
        }
        
        grupos_creados = {}
        
        for grupo_nombre, config in grupos_config.items():
            # Crear o obtener grupo
            grupo, created = Group.objects.get_or_create(name=grupo_nombre)
            permisos_grupo = []
            
            # Asignar permisos por aplicación
            for app_name, acciones in config['permisos_apps'].items():
                for accion in acciones:
                    # Buscar permisos que coincidan con el patrón accion_app
                    permisos = Permission.objects.filter(
                        codename__startswith=f"{accion}_{app_name}"
                    )
                    permisos_grupo.extend(permisos)
            
            # Asignar permisos especiales
            if 'permisos_especiales' in config:
                for codename in config['permisos_especiales']:
                    try:
                        permiso = Permission.objects.get(codename=codename)
                        permisos_grupo.append(permiso)
                    except Permission.DoesNotExist:
                        print(f"  Permiso no encontrado: {codename}")
            
            # Excluir permisos no permitidos
            if 'excluir' in config:
                permisos_grupo = [
                    p for p in permisos_grupo 
                    if p.codename not in config['excluir']
                ]
            
            # Eliminar duplicados
            permisos_grupo = list(set(permisos_grupo))
            
            # Asignar permisos al grupo
            grupo.permissions.set(permisos_grupo)
            grupos_creados[grupo_nombre] = grupo
            
            print(f"  Grupo creado: {grupo_nombre} ({len(permisos_grupo)} permisos)")
        
        # ======================================================
        # 2. CREACIÓN DE USUARIOS DE EJEMPLO POR ROL
        # ======================================================
        print("\n2. Creando usuarios de ejemplo...")
        
        usuarios_data = [
            {
                'username': 'admin.sistema',
                'password': 'Admin.1234',
                'first_name': 'Carlos',
                'last_name': 'Administrador',
                'email': 'admin@minsal.cl',
                'rol': 'admin',
                'rut': '12345678-9',
                'establecimiento': 'Ministerio de Salud',
                'grupo': 'Administrador'
            },
            {
                'username': 'medico.principal',
                'password': 'Medico.1234',
                'first_name': 'Ana',
                'last_name': 'Fernández',
                'email': 'medico@hospital.cl',
                'rol': 'medico',
                'rut': '13456789-0',
                'establecimiento': 'Hospital Regional Metropolitano',
                'grupo': 'Médico'
            },
            {
                'username': 'enfermera.jefe',
                'password': 'Enfermera.1234',
                'first_name': 'María',
                'last_name': 'González',
                'email': 'enfermera@cesfam.cl',
                'rol': 'enfermera',
                'rut': '14567890-1',
                'establecimiento': 'CESFAM Norte',
                'grupo': 'Enfermera'
            },
            {
                'username': 'tecnologo.lab',
                'password': 'Tecnologo.1234',
                'first_name': 'Pedro',
                'last_name': 'Rodríguez',
                'email': 'tecnologo@laboratorio.cl',
                'rol': 'tecnologo',
                'rut': '15678901-2',
                'establecimiento': 'Laboratorio Central',
                'grupo': 'Tecnólogo Médico'
            },
            {
                'username': 'tecnico.terreno',
                'password': 'Tecnico.1234',
                'first_name': 'Juan',
                'last_name': 'Martínez',
                'email': 'tecnico@cesfam.cl',
                'rol': 'paramedico',
                'rut': '16789012-3',
                'establecimiento': 'CESFAM Sur',
                'grupo': 'Técnico Paramédico'
            }
        ]
        
        usuarios_creados = []
        
        for user_data in usuarios_data:
            # Crear usuario de Django
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=user_data['email'],
                is_staff=True,
                is_active=True,
                is_superuser=(user_data['rol'] == 'admin')
            )
            
            # Asignar grupo correspondiente
            grupo = grupos_creados[user_data['grupo']]
            user.groups.add(grupo)
            
            # Crear perfil extendido
            perfil = UsuariosUsuario.objects.create(
                user=user,
                rut=user_data['rut'],
                rol=user_data['rol'],
                establecimiento=user_data['establecimiento'],
                telefono='+56912345678',
                fecha_creacion=datetime.now()
            )
            
            usuarios_creados.append({
                'username': user.username,
                'password': user_data['password'],
                'rol': user_data['rol'],
                'grupo': user_data['grupo']
            })
            
            print(f"  Usuario creado: {user_data['username']} ({user_data['rol']})")
    
    # Reconectar signals
    print("\nReconectando signals...")
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)
    
    # ======================================================
    # 3. RESUMEN DE CREDENCIALES
    # ======================================================
    print("\n" + "=" * 60)
    print("RESUMEN DE USUARIOS CREADOS")
    print("=" * 60)
    
    for usuario in usuarios_creados:
        print(f"\nUsuario: {usuario['username']}")
        print(f"Contraseña: {usuario['password']}")
        print(f"Rol: {usuario['rol']}")
        print(f"Grupo: {usuario['grupo']}")
        print("-" * 40)
    
    print("\n¡Configuración completada exitosamente!")
    print("=" * 60)

if __name__ == '__main__':
    main()