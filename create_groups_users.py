import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from apps.usuarios.models import UsuariosUsuario
from django.db.models.signals import post_save

print("🚀 CREANDO GRUPOS, USUARIOS Y PERMISOS - SISTEMA TBC")
print("=" * 60)

@transaction.atomic
def main():
    # 1. DESCONECTAR SIGNAL TEMPORALMENTE
    print("\n🔧 DESCONECTANDO SIGNALS TEMPORALES")
    from apps.usuarios.models import create_user_profile, save_user_profile
    post_save.disconnect(create_user_profile, sender=User)
    post_save.disconnect(save_user_profile, sender=User)
    
    # 2. CREAR GRUPOS CON PERMISOS ESPECÍFICOS
    print("\n1. 👥 CREANDO GRUPOS CON PERMISOS")
    
    grupos_config = {
        'Administrador': {
            'permisos': ['add', 'change', 'delete', 'view'],
            'apps': ['usuarios', 'pacientes', 'tratamientos', 'examenes', 'contactos', 
                    'prevencion', 'laboratorio', 'indicadores', 'auth']
        },
        'Médico': {
            'permisos': ['add', 'change', 'view'],
            'apps': ['pacientes', 'tratamientos', 'examenes', 'contactos'],
            'excluir': ['delete_pacientespaciente', 'delete_tratamiento']
        },
        'Enfermera': {
            'permisos': ['view', 'change'],
            'apps': ['pacientes', 'tratamientos', 'examenes', 'contactos', 'prevencion'],
            'permisos_especiales': [
                'add_dosisadministrada', 'change_dosisadministrada', 'view_dosisadministrada',
                'add_prevencionquimioprofilaxis', 'change_prevencionquimioprofilaxis'
            ]
        },
        'Tecnólogo Médico': {
            'permisos': ['view', 'change'],
            'apps': ['examenes', 'laboratorio', 'pacientes'],
            'permisos_especiales': [
                'change_examenesexamenbacteriologico', 'view_examenesexamenbacteriologico',
                'add_laboratoriotarjetero', 'change_laboratoriotarjetero'
            ]
        },
        'Técnico Paramédico': {
            'permisos': ['view', 'add'],
            'apps': ['pacientes', 'contactos', 'prevencion'],
            'excluir': ['change_pacientespaciente', 'delete_pacientespaciente', 'delete_contactoscontacto']
        }
    }
    
    grupos = {}
    for grupo_nombre, config in grupos_config.items():
        grupo, created = Group.objects.get_or_create(name=grupo_nombre)
        permisos_grupo = []
        
        # Permisos por app
        for app in config['apps']:
            for accion in config['permisos']:
                permisos = Permission.objects.filter(
                    codename__startswith=f"{accion}_{app}"
                )
                permisos_grupo.extend(permisos)
        
        # Permisos especiales
        if 'permisos_especiales' in config:
            for codename in config['permisos_especiales']:
                try:
                    permiso = Permission.objects.get(codename=codename)
                    permisos_grupo.append(permiso)
                except Permission.DoesNotExist:
                    print(f"   ⚠️ Permiso no encontrado: {codename}")
        
        # Excluir permisos
        if 'excluir' in config:
            permisos_grupo = [p for p in permisos_grupo if p.codename not in config['excluir']]
        
        # Eliminar duplicados y asignar
        permisos_grupo = list(set(permisos_grupo))
        grupo.permissions.set(permisos_grupo)
        grupos[grupo_nombre] = grupo
        print(f"   ✅ Grupo: {grupo_nombre} - {len(permisos_grupo)} permisos")
    
    # 3. CREAR USUARIOS (CON RUTs MÁS CORTOS)
    print("\n2. 👤 CREANDO USUARIOS")
    
    usuarios_data = [
        {
            'username': 'admin.sistema',
            'password': 'Admin.1234',
            'first_name': 'Carlos',
            'last_name': 'Administrador',
            'email': 'admin@minsal.cl',
            'rol': 'admin',
            'rut': '12345678-9',  # RUT más corto
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
            'rut': '13456789-0',  # RUT más corto
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
            'rut': '14567890-1',  # RUT más corto
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
            'rut': '15678901-2',  # RUT más corto
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
            'rut': '16789012-3',  # RUT más corto
            'establecimiento': 'CESFAM Sur',
            'grupo': 'Técnico Paramédico'
        }
    ]
    
    usuarios = {}
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
            is_superuser=(user_data['rol'] == 'admin')  # Solo admin es superuser
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
            telefono='+56912345678',
            fecha_creacion=datetime.now()
        )
        
        usuarios[user_data['username']] = user
        print(f"   ✅ Usuario: {user_data['username']} - {user_data['rol']}")
    
    # 4. RECONECTAR SIGNALS
    print("\n🔧 RECONECTANDO SIGNALS")
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)
    
    print("\n" + "=" * 60)
    print("🎉 CONFIGURACIÓN DE USUARIOS Y PERMISOS COMPLETADA!")
    print("=" * 60)
    
    # Mostrar credenciales
    print("\n🔐 CREDENCIALES DE ACCESO:")
    for user_data in usuarios_data:
        print(f"   👤 Usuario: {user_data['username']}")
        print(f"   🔑 Contraseña: {user_data['password']}")
        print(f"   🏥 Rol: {user_data['rol']}")
        print(f"   📧 Email: {user_data['email']}")
        print(f"   🏢 Establecimiento: {user_data['establecimiento']}")
        print()

if __name__ == '__main__':
    main()