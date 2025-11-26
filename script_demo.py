# script_demo.py
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User, Group, Permission
from apps.usuarios.models import UsuariosUsuario
from apps.pacientes.models import PacientesPaciente as Paciente
from apps.contactos.models import ContactosContacto as Contacto
from apps.tratamientos.models import Tratamiento, EsquemaMedicamento, DosisAdministrada
from apps.examenes.models import ExamenesExamenbacteriologico as ExamenBacteriologico
from django.db.models.signals import post_save

print("🚀 CREANDO GRUPOS, USUARIOS Y DATOS DE DEMOSTRACIÓN - SISTEMA TBC")
print("=" * 70)

@transaction.atomic
def main():
    # 1. DESCONECTAR SIGNALS TEMPORALMENTE
    print("\n🔧 DESCONECTANDO SIGNALS TEMPORALES")
    from apps.usuarios.models import create_user_profile, save_user_profile
    post_save.disconnect(create_user_profile, sender=User)
    post_save.disconnect(save_user_profile, sender=User)
    
    # Desconectar signal problemático de indicadores
    try:
        from apps.indicadores.signals import actualizar_indicadores_paciente
        post_save.disconnect(actualizar_indicadores_paciente, sender=Paciente)
        print("   ✅ Signal de indicadores desconectado temporalmente")
    except Exception as e:
        print(f"   ℹ️  No se pudo desconectar signal de indicadores: {e}")
    
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
    
    # 3. CREAR USUARIOS
    print("\n2. 👤 CREANDO USUARIOS")
    
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
            is_superuser=(user_data['rol'] == 'admin')
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
    
    # 4. CREAR PACIENTE DE DEMOSTRACIÓN - CARLOS ROJAS
    print("\n3. 👨‍⚕️ CREANDO PACIENTE DE DEMOSTRACIÓN")
    
    # Usar objetos date en lugar de strings
    from datetime import date
    
    paciente = Paciente.objects.create(
        rut='17654321-0',  # RUT sin puntos
        nombre='Carlos Antonio Rojas Mendoza',
        fecha_nacimiento=date(1982, 3, 15),  # ← OBJETO DATE, no string
        sexo='M',
        domicilio='Av. Los Constructores 2345, Pudahuel',
        comuna='Pudahuel',
        telefono='+56987654321',
        establecimiento_salud='CESFAM Pudahuel',
        fecha_diagnostico=date(2025, 1, 18),  # ← OBJETO DATE
        tipo_tbc='Pulmonar',
        baciloscopia_inicial='Positivo',
        cultivo_inicial='Positivo',
        poblacion_prioritaria='Trabajador con exposición a sílice',
        estado='En tratamiento',
        fecha_registro=datetime.now(),
        usuario_registro=usuarios['medico.principal']
    )
    print(f"   ✅ Paciente: {paciente.nombre}")
    
    # 5. CREAR CONTACTO PARA DEMOSTRACIÓN
    print("\n4. 👥 CREANDO CONTACTO")
    
    contacto = Contacto.objects.create(
        rut_contacto='18765432-1',  # RUT sin puntos
        nombre_contacto='Elena María Rojas Pérez',
        parentesco='Esposa',
        tipo_contacto='Convivencia',
        fecha_registro=datetime.now(),
        telefono='+56976543210',
        estado_estudio='Estudiado - Sin TB',
        paciente_indice=paciente
    )
    print(f"   ✅ Contacto: {contacto.nombre_contacto}")
    
    # 6. CREAR TRATAMIENTO
    print("\n5. 💊 CREANDO TRATAMIENTO")
    
    tratamiento = Tratamiento.objects.create(
        paciente=paciente,
        esquema='HRZE',
        fecha_inicio=date(2025, 1, 20),  # ← OBJETO DATE
        fecha_termino_estimada=date(2025, 7, 20),  # ← OBJETO DATE
        peso_kg=68.0,
        observaciones='Paciente con buena adherencia inicial. Trabajador construcción.',
        fecha_registro=datetime.now(),
        usuario_registro=usuarios['medico.principal']
    )
    print(f"   ✅ Tratamiento: {tratamiento.esquema}")
    
    # 7. CREAR ESQUEMA DE MEDICAMENTOS
    print("\n6. 🧪 CREANDO ESQUEMAS DE MEDICAMENTOS")
    
    esquemas_data = [
        {
            'medicamento': 'Isoniazida (H)',
            'dosis_mg': 300,
            'frecuencia': 'Diaria',
            'fase': 'Fase Intensiva',
            'duracion_semanas': 8,
            'fecha_inicio': date(2025, 1, 20),
            'fecha_termino': date(2025, 3, 16)
        },
        {
            'medicamento': 'Rifampicina (R)',
            'dosis_mg': 600, 
            'frecuencia': 'Diaria',
            'fase': 'Fase Intensiva',
            'duracion_semanas': 8,
            'fecha_inicio': date(2025, 1, 20),
            'fecha_termino': date(2025, 3, 16)
        }
    ]
    
    for esquema_data in esquemas_data:
        esquema = EsquemaMedicamento.objects.create(
            tratamiento=tratamiento,
            medicamento=esquema_data['medicamento'],
            dosis_mg=esquema_data['dosis_mg'],
            frecuencia=esquema_data['frecuencia'],
            fase=esquema_data['fase'],
            duracion_semanas=esquema_data['duracion_semanas'],
            fecha_inicio=esquema_data['fecha_inicio'],
            fecha_termino=esquema_data['fecha_termino']
        )
        print(f"   ✅ Medicamento: {esquema.medicamento} {esquema.dosis_mg}mg")
    
    # 8. CREAR DOSIS PENDIENTES PARA DEMOSTRACIÓN
    print("\n7. ⏰ CREANDO DOSIS PENDIENTES")
    
    esquema_isoniazida = EsquemaMedicamento.objects.get(medicamento='Isoniazida (H)')
    
    # Crear dosis para hoy y mañana (pendientes)
    hoy = datetime.now().date()
    manana = hoy + timedelta(days=1)
    
    dosis_hoy = DosisAdministrada.objects.create(
        esquema_medicamento=esquema_isoniazida,
        fecha_dosis=hoy,
        administrada=False,  # ← PENDIENTE PARA DEMOSTRAR
        hora_administracion='08:00:00',
        observaciones='Dosis pendiente para hoy',
        fecha_registro=datetime.now(),
        usuario_administracion=usuarios['enfermera.jefe']
    )
    
    dosis_manana = DosisAdministrada.objects.create(
        esquema_medicamento=esquema_isoniazida,
        fecha_dosis=manana,
        administrada=False,  # ← PENDIENTE PARA MAÑANA
        hora_administracion='08:00:00',
        observaciones='Dosis programada para mañana',
        fecha_registro=datetime.now(),
        usuario_administracion=usuarios['enfermera.jefe']
    )
    
    print(f"   ✅ Dosis pendiente para: {hoy}")
    print(f"   ✅ Dosis programada para: {manana}")
    
    # 9. CREAR EXÁMENES DE LABORATORIO
    print("\n8. 🔬 CREANDO EXÁMENES")
    
    examenes_data = [
        {
            'tipo_examen': 'Baciloscopia',
            'tipo_muestra': 'Esputo',
            'fecha_toma_muestra': date(2025, 1, 13),
            'fecha_resultado': date(2025, 1, 13),
            'resultado': 'Positivo',
            'resultado_cuantitativo': '3+',
            'laboratorio': 'Laboratorio Central',
            'numero_muestra_lab': 'BAC2025001'
        },
        {
            'tipo_examen': 'Baciloscopia',
            'tipo_muestra': 'Esputo',
            'fecha_toma_muestra': date(2025, 3, 15),
            'fecha_resultado': date(2025, 3, 15),
            'resultado': 'Negativo',
            'resultado_cuantitativo': 'Negativo',
            'laboratorio': 'Laboratorio Central',
            'numero_muestra_lab': 'BAC2025002'
        }
    ]
    
    for examen_data in examenes_data:
        examen = ExamenBacteriologico.objects.create(
            tipo_examen=examen_data['tipo_examen'],
            tipo_muestra=examen_data['tipo_muestra'],
            fecha_solicitud=examen_data['fecha_toma_muestra'],
            fecha_toma_muestra=examen_data['fecha_toma_muestra'],
            fecha_ingreso_laboratorio=examen_data['fecha_toma_muestra'],
            fecha_resultado=examen_data['fecha_resultado'],
            resultado=examen_data['resultado'],
            resultado_cuantitativo=examen_data['resultado_cuantitativo'],
            sensibilidad='Sensible',
            laboratorio=examen_data['laboratorio'],
            numero_muestra_lab=examen_data['numero_muestra_lab'],
            estado_examen='Completado',
            fecha_registro=datetime.now(),
            fecha_actualizacion=datetime.now(),
            paciente=paciente,
            usuario_registro=usuarios['medico.principal'],
            usuario_toma_muestra=usuarios['tecnologo.lab']
        )
        print(f"   ✅ Examen: {examen_data['tipo_examen']} - {examen_data['resultado']}")
    
    # 10. RECONECTAR SIGNALS
    print("\n🔧 RECONECTANDO SIGNALS")
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)
    
    # Intentar reconectar signal de indicadores
    try:
        from apps.indicadores.signals import actualizar_indicadores_paciente
        post_save.connect(actualizar_indicadores_paciente, sender=Paciente)
        print("   ✅ Signal de indicadores reconectado")
    except Exception as e:
        print(f"   ℹ️  No se pudo reconectar signal de indicadores: {e}")
    
    print("\n" + "=" * 70)
    print("🎉 CONFIGURACIÓN COMPLETA - SISTEMA LISTO PARA DEMOSTRACIÓN!")
    print("=" * 70)
    
    # MOSTRAR DATOS PARA LA DEMOSTRACIÓN
    print("\n🔍 DATOS CREADOS PARA DEMOSTRACIÓN:")
    print(f"   👤 Paciente: Carlos Antonio Rojas Mendoza")
    print(f"   📍 RUT: 17654321-0")
    print(f"   💊 Tratamiento: HRZE (Activo)")
    print(f"   ⏰ Dosis pendientes: 2 (hoy y mañana)")
    print(f"   🔬 Exámenes: 2 baciloscopias")
    print(f"   👥 Contacto: Elena Rojas (esposa)")
    
    print("\n🔐 CREDENCIALES DE ACCESO:")
    for user_data in usuarios_data:
        print(f"   👤 {user_data['username']} | 🔑 {user_data['password']} | 🏥 {user_data['rol']}")
    
    print("\n💡 PARA LA DEMOSTRACIÓN:")
    print("   1. Login con 'enfermera.jefe' / 'Enfermera.1234'")
    print("   2. Ir a Módulo Tratamientos → Dosis Pendientes")
    print("   3. Administrar dosis del día de hoy")
    print("   4. Verificar cambio de estado a 'Administrada'")
    print("   5. Explorar otros módulos con diferentes usuarios")

if __name__ == '__main__':
    main()