# script_usuarios_grupos.py - VERSIÓN CORREGIDA (Pylance compatible)
import os
import django
import sys
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import traceback

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save

def main():
    """
    Script para crear grupos de usuarios, asignar permisos por rol
    y crear usuarios de ejemplo para cada rol del sistema TBC.
    Versión corregida para Pylance.
    """
    
    print("=" * 70)
    print("SCRIPT DE CONFIGURACIÓN DE USUARIOS Y GRUPOS - SISTEMA TBC")
    print("=" * 70)
    
    try:
        # Verificar si ya existen usuarios
        if User.objects.exists():
            print("\n⚠️  ADVERTENCIA: Ya existen usuarios en el sistema.")
            respuesta = input("¿Desea continuar y crear usuarios adicionales? (s/n): ")
            if respuesta.lower() != 's':
                print("Operación cancelada.")
                return
        
        # ======================================================
        # 1. VERIFICAR MODELOS Y APLICACIONES DISPONIBLES
        # ======================================================
        print("\n1. Verificando aplicaciones instaladas...")
        
        # Lista de aplicaciones esperadas
        apps_esperadas = [
            'usuarios', 'pacientes', 'tratamientos', 'examenes',
            'contactos', 'prevencion', 'laboratorio', 'indicadores'
        ]
        
        apps_disponibles: List[str] = []
        for app_label in apps_esperadas:
            try:
                content_type = ContentType.objects.filter(app_label=app_label).first()
                if content_type:
                    apps_disponibles.append(app_label)
                    print(f"  ✓ {app_label}")
                else:
                    print(f"  ✗ {app_label} (sin modelos)")
            except Exception:
                print(f"  ✗ {app_label} (error al verificar)")
        
        if not apps_disponibles:
            print("\n❌ ERROR: No se encontraron aplicaciones configuradas.")
            print("Ejecute primero: python manage.py migrate")
            return
        
        # ======================================================
        # 2. DESCONECTAR SIGNALS TEMPORALMENTE
        # ======================================================
        print("\n2. Configurando entorno...")
        
        try:
            from apps.usuarios.models import create_user_profile, save_user_profile
            post_save.disconnect(create_user_profile, sender=User)
            post_save.disconnect(save_user_profile, sender=User)
            print("  ✓ Signals desconectados")
        except Exception as e:
            print(f"  ⚠️  No se pudieron desconectar signals: {e}")
        
        with transaction.atomic():
            # ======================================================
            # 3. CREACIÓN DE GRUPOS CON PERMISOS ESPECÍFICOS
            # ======================================================
            print("\n3. Creando grupos y asignando permisos...")
            
            # Configuración detallada de permisos por rol
            grupos_config: Dict[str, Dict[str, Any]] = {
                'Administrador': {
                    'descripcion': 'Acceso completo a todos los módulos del sistema',
                    'permisos_generales': [
                        'view_user', 'add_user', 'change_user', 'delete_user',
                        'view_group', 'add_group', 'change_group', 'delete_group',
                    ],
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
                    'permisos_generales': ['view_user', 'view_group'],
                    'permisos_apps': {
                        'pacientes': ['view', 'add', 'change'],
                        'tratamientos': ['view', 'add', 'change'],
                        'examenes': ['view', 'add', 'change'],
                        'contactos': ['view'],
                        'indicadores': ['view'],
                    },
                    'permisos_excluir': [
                        'delete_paciente',
                        'delete_tratamiento',
                        'delete_examen',
                        'delete_contacto'
                    ]
                },
                'Enfermera': {
                    'descripcion': 'Acceso a módulos de cuidados y seguimiento',
                    'permisos_generales': ['view_user'],
                    'permisos_apps': {
                        'pacientes': ['view', 'change'],
                        'tratamientos': ['view', 'change'],
                        'examenes': ['view'],
                        'contactos': ['view'],
                        'prevencion': ['view', 'add', 'change'],
                    },
                    'permisos_especiales': [
                        'add_dosis',
                        'change_dosis',
                        'view_dosis',
                        'add_seguimiento',
                        'change_seguimiento',
                        'view_seguimiento',
                    ]
                },
                'Tecnólogo Médico': {
                    'descripcion': 'Acceso a módulos de laboratorio y exámenes',
                    'permisos_generales': ['view_user'],
                    'permisos_apps': {
                        'examenes': ['view', 'add', 'change'],
                        'laboratorio': ['view', 'add', 'change'],
                        'pacientes': ['view'],
                    },
                    'permisos_especiales': [
                        'add_resultado',
                        'change_resultado',
                        'view_resultado',
                        'add_cultivo',
                        'change_cultivo',
                        'view_cultivo',
                    ]
                },
                'Técnico Paramédico': {
                    'descripcion': 'Acceso a módulos de campo y prevención',
                    'permisos_generales': ['view_user'],
                    'permisos_apps': {
                        'pacientes': ['view', 'add'],
                        'contactos': ['view', 'add'],
                        'prevencion': ['view', 'add'],
                    },
                    'permisos_excluir': [
                        'change_paciente',
                        'delete_paciente',
                        'delete_contacto',
                        'change_contacto',
                    ]
                }
            }
            
            grupos_creados: Dict[str, Group] = {}
            
            for grupo_nombre, config in grupos_config.items():
                print(f"\n  Creando grupo: {grupo_nombre}")
                print(f"  Descripción: {config['descripcion']}")
                
                # Crear o obtener grupo
                grupo, created = Group.objects.get_or_create(name=grupo_nombre)
                permisos_grupo: List[Permission] = []
                
                # Asignar permisos generales
                if 'permisos_generales' in config:
                    for codename in config['permisos_generales']:
                        try:
                            permiso = Permission.objects.get(codename=codename)
                            permisos_grupo.append(permiso)
                        except Permission.DoesNotExist:
                            print(f"    ⚠️ Permiso general no encontrado: {codename}")
                
                # Asignar permisos por aplicación
                for app_name, acciones in config.get('permisos_apps', {}).items():
                    if app_name not in apps_disponibles:
                        print(f"    ⚠️ Aplicación no disponible: {app_name}")
                        continue
                        
                    for accion in acciones:
                        # Buscar permisos que coincidan con el patrón
                        pattern = f"{accion}_{app_name}"
                        permisos = Permission.objects.filter(
                            codename__contains=pattern
                        )
                        
                        permisos_list = list(permisos)
                        if permisos_list:
                            permisos_grupo.extend(permisos_list)
                            print(f"    ✓ {len(permisos_list)} permisos para {app_name}.{accion}")
                        else:
                            # Intentar búsqueda más flexible
                            content_types = list(ContentType.objects.filter(app_label=app_name))
                            if content_types:
                                for ct in content_types:
                                    try:
                                        perm = Permission.objects.get(
                                            content_type=ct,
                                            codename__startswith=accion
                                        )
                                        permisos_grupo.append(perm)
                                    except Permission.DoesNotExist:
                                        pass
                                    except Exception:
                                        pass
                
                # Asignar permisos especiales
                if 'permisos_especiales' in config:
                    for codename in config['permisos_especiales']:
                        try:
                            permiso = Permission.objects.get(codename=codename)
                            permisos_grupo.append(permiso)
                            print(f"    ✓ Permiso especial: {codename}")
                        except Permission.DoesNotExist:
                            print(f"    ⚠️ Permiso especial no encontrado: {codename}")
                
                # Excluir permisos no permitidos
                if 'permisos_excluir' in config:
                    permisos_grupo = [
                        p for p in permisos_grupo 
                        if p.codename not in config['permisos_excluir']
                    ]
                
                    # Eliminar duplicados usando un dict para mantener orden
                    # Eliminar duplicados manteniendo el orden
                    permisos_unicos: List[Permission] = []
                    codenames_vistos = set()
                    
                    for perm in permisos_grupo:
                        # Verificar que sea un objeto Permission válido
                        if not hasattr(perm, 'codename') or not hasattr(perm, 'content_type_id'):
                            continue
                    
                    # Crear clave única
                    perm_key = f"{perm.codename}_{perm.content_type_id}"
                    
                    # Si no hemos visto este permiso, añadirlo
                    if perm_key not in codenames_vistos:
                        codenames_vistos.add(perm_key)
                        permisos_unicos.append(perm)
                
                # Asignar permisos al grupo
                if permisos_unicos:
                    grupo.permissions.set(permisos_unicos)
                    grupos_creados[grupo_nombre] = grupo
                    print(f"  ✅ Grupo '{grupo_nombre}' creado con {len(permisos_unicos)} permisos")
                else:
                    print(f"  ⚠️ Grupo '{grupo_nombre}' sin permisos asignados")
            
            # ======================================================
            # 4. CREACIÓN DE USUARIOS DE EJEMPLO POR ROL
            # ======================================================
            print("\n4. Creando usuarios de ejemplo...")
            
            usuarios_data: List[Dict[str, Any]] = [
                {
                    'username': 'admin',
                    'password': 'AdminTBC2024!',
                    'first_name': 'Carlos',
                    'last_name': 'Administrador',
                    'email': 'admin@minsal.cl',
                    'rol': 'admin',
                    'rut': '12.345.678-9',
                    'establecimiento': 'Ministerio de Salud',
                    'grupo': 'Administrador',
                    'telefono': '+56991234567',
                    'es_superuser': True,
                    'es_staff': True
                },
                {
                    'username': 'medico',
                    'password': 'MedicoTBC2024!',
                    'first_name': 'Ana',
                    'last_name': 'Fernández',
                    'email': 'medico@hospital.cl',
                    'rol': 'medico',
                    'rut': '13.456.789-0',
                    'establecimiento': 'Hospital Regional Metropolitano',
                    'grupo': 'Médico',
                    'telefono': '+56992345678',
                    'es_superuser': False,
                    'es_staff': True
                },
                {
                    'username': 'enfermera',
                    'password': 'EnfermeraTBC2024!',
                    'first_name': 'María',
                    'last_name': 'González',
                    'email': 'enfermera@cesfam.cl',
                    'rol': 'enfermera',
                    'rut': '14.567.890-1',
                    'establecimiento': 'CESFAM Norte',
                    'grupo': 'Enfermera',
                    'telefono': '+56993456789',
                    'es_superuser': False,
                    'es_staff': True
                },
                {
                    'username': 'tecnologo',
                    'password': 'TecnologoTBC2024!',
                    'first_name': 'Pedro',
                    'last_name': 'Rodríguez',
                    'email': 'tecnologo@laboratorio.cl',
                    'rol': 'tecnologo',
                    'rut': '15.678.901-2',
                    'establecimiento': 'Laboratorio Central',
                    'grupo': 'Tecnólogo Médico',
                    'telefono': '+56994567890',
                    'es_superuser': False,
                    'es_staff': True
                },
                {
                    'username': 'paramedico',
                    'password': 'ParamedicoTBC2024!',
                    'first_name': 'Juan',
                    'last_name': 'Martínez',
                    'email': 'tecnico@cesfam.cl',
                    'rol': 'paramedico',
                    'rut': '16.789.012-3',
                    'establecimiento': 'CESFAM Sur',
                    'grupo': 'Técnico Paramédico',
                    'telefono': '+56995678901',
                    'es_superuser': False,
                    'es_staff': True
                }
            ]
            
            usuarios_creados: List[Dict[str, Any]] = []
            
            for user_data in usuarios_data:
                try:
                    # Verificar si el usuario ya existe
                    if User.objects.filter(username=user_data['username']).exists():
                        print(f"  ⚠️ Usuario ya existe: {user_data['username']}")
                        continue
                    
                    # Crear usuario de Django
                    user = User.objects.create_user(
                        username=user_data['username'],
                        password=user_data['password'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        email=user_data['email'],
                        is_staff=user_data['es_staff'],
                        is_active=True,
                        is_superuser=user_data['es_superuser'],
                        date_joined=datetime.now()
                    )
                    
                    # Asignar grupo correspondiente
                    grupo = grupos_creados.get(user_data['grupo'])
                    if grupo:
                        user.groups.add(grupo)
                    
                    # Crear perfil extendido si el modelo existe
                    try:
                        from apps.usuarios.models import UsuariosUsuario
                        
                        perfil = UsuariosUsuario.objects.create(
                            user=user,
                            rut=user_data['rut'],
                            rol=user_data['rol'],
                            establecimiento=user_data['establecimiento'],
                            telefono=user_data['telefono'],
                            fecha_creacion=datetime.now(),
                            fecha_actualizacion=datetime.now()
                        )
                        print(f"  ✅ Usuario con perfil: {user_data['username']}")
                    except ImportError:
                        print(f"  ✅ Usuario básico: {user_data['username']} (modelo UsuariosUsuario no disponible)")
                    except Exception as e:
                        print(f"  ✅ Usuario básico: {user_data['username']} (error en perfil: {e})")
                    
                    usuarios_creados.append({
                        'username': user.username,
                        'password': user_data['password'],
                        'rol': user_data['rol'],
                        'grupo': user_data['grupo'],
                        'email': user_data['email']
                    })
                    
                except Exception as e:
                    print(f"  ❌ Error creando usuario {user_data['username']}: {e}")
                    print(f"  Detalles: {traceback.format_exc()}")
            
            # ======================================================
            # 5. CREAR USUARIO DE TEST PARA APIs
            # ======================================================
            print("\n5. Creando usuario para pruebas de API...")
            
            try:
                if not User.objects.filter(username='api_tester').exists():
                    api_user = User.objects.create_user(
                        username='api_tester',
                        password='ApiTest2024!',
                        first_name='API',
                        last_name='Tester',
                        email='api@test.cl',
                        is_staff=True,
                        is_active=True,
                        is_superuser=False
                    )
                    
                    # Asignar múltiples grupos para pruebas
                    grupos_prueba = ['Médico', 'Enfermera']
                    for grupo_nombre in grupos_prueba:
                        grupo = grupos_creados.get(grupo_nombre)
                        if grupo:
                            api_user.groups.add(grupo)
                    
                    usuarios_creados.append({
                        'username': 'api_tester',
                        'password': 'ApiTest2024!',
                        'rol': 'multi',
                        'grupo': 'Médico+Enfermera',
                        'email': 'api@test.cl'
                    })
                    print("  ✅ Usuario API tester creado")
            except Exception as e:
                print(f"  ⚠️ No se pudo crear usuario API tester: {e}")
        
        # Reconectar signals
        print("\n6. Reconfigurando entorno...")
        try:
            from apps.usuarios.models import create_user_profile, save_user_profile
            post_save.connect(create_user_profile, sender=User)
            post_save.connect(save_user_profile, sender=User)
            print("  ✓ Signals reconectados")
        except ImportError:
            print("  ⚠️ No se encontraron signals para reconectar")
        except Exception as e:
            print(f"  ⚠️ Error reconectando signals: {e}")
        
        # ======================================================
        # 7. RESUMEN DE CREDENCIALES
        # ======================================================
        print("\n" + "=" * 70)
        print("RESUMEN DE CONFIGURACIÓN COMPLETADA")
        print("=" * 70)
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"  • Grupos creados: {len(grupos_creados)}")
        print(f"  • Usuarios creados: {len(usuarios_creados)}")
        print(f"  • Permisos totales en sistema: {Permission.objects.count()}")
        
        print(f"\n👥 GRUPOS DISPONIBLES:")
        for grupo_nombre, grupo in grupos_creados.items():
            perm_count = grupo.permissions.count()
            print(f"  • {grupo_nombre}: {perm_count} permisos")
        
        print(f"\n🔐 CREDENCIALES DE ACCESO:")
        print("  " + "-" * 68)
        
        for usuario in usuarios_creados:
            print(f"\n  👤 Usuario: {usuario['username']}")
            print(f"     Contraseña: {usuario['password']}")
            print(f"     Rol: {usuario['rol']}")
            print(f"     Grupo: {usuario['grupo']}")
            print(f"     Email: {usuario['email']}")
            print("     " + "-" * 40)
        
        print(f"\n🌐 URLS DE ACCESO:")
        print(f"  • Interfaz web: http://localhost:8000/")
        print(f"  • API REST: http://localhost:8000/api/")
        print(f"  • Admin Django: http://localhost:8000/admin/")
        
        print(f"\n📋 NOTAS IMPORTANTES:")
        print(f"  1. Las contraseñas son seguras pero debes cambiarlas en producción")
        print(f"  2. El usuario 'admin' tiene acceso completo al sistema")
        print(f"  3. El usuario 'api_tester' es para pruebas de API")
        print(f"  4. Cada rol tiene permisos específicos según su función")
        
        print(f"\n✅ CONFIGURACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        print(traceback.format_exc())
        print("\nRevise la configuración de Django y la base de datos.")
        sys.exit(1)

def verificar_instalacion() -> bool:
    """Función para verificar la instalación antes de ejecutar"""
    print("🔍 Verificando instalación de Django...")
    
    try:
        # Verificar settings
        from django.conf import settings
        print(f"  ✓ Settings: {settings.SETTINGS_MODULE}")
        
        # Verificar base de datos
        from django.db import connection
        connection.ensure_connection()
        db_engine = connection.settings_dict.get('ENGINE', 'Desconocido')
        print(f"  ✓ Base de datos: {db_engine}")
        
        # Verificar aplicaciones instaladas - CORRECCIÓN DEL ERROR PYLANCE
        from django.apps import apps
        app_configs = apps.get_app_configs()
        
        # Convertir a lista para contar
        app_list = list(app_configs)
        print(f"  ✓ Aplicaciones: {len(app_list)} instaladas")
        
        # Mostrar algunas aplicaciones
        if len(app_list) > 0:
            print(f"  ✓ Ejemplos: {', '.join([app.name for app in app_list[:3]])}")
            if len(app_list) > 3:
                print(f"    ... y {len(app_list) - 3} más")
        
        return True
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        print("\nPosibles soluciones:")
        print("  1. Ejecute: python manage.py migrate")
        print("  2. Verifique su archivo .env")
        print("  3. Asegúrese que MySQL esté corriendo")
        print("  4. Ejecute: pip install -r requirements.txt")
        return False

if __name__ == '__main__':
    # Verificar instalación primero
    if verificar_instalacion():
        main()
    else:
        print("\n❌ No se puede continuar. Corrija los errores primero.")
        sys.exit(1)