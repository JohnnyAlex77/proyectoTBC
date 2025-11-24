# Load_indicadores_data_FIXED.py
import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings')
django.setup()

from django.db import transaction
from django.contrib.auth.models import User
from apps.indicadores.models import (
    Establecimiento, IndicadoresCohorte, IndicadoresOperacionales,
    IndicadoresPrevencion, Alerta
)

print("📊 CARGANDO DATOS PARA MÓDULO INDICADORES")
print("=" * 60)

@transaction.atomic
def main():
    # Obtener usuario admin para registros
    admin_user = User.objects.get(username='admin.sistema')
    
    # 1. CREAR ESTABLECIMIENTOS ADICIONALES
    print("\n1. 🏥 CREANDO ESTABLECIMIENTOS")
    
    establecimientos_data = [
        {'nombre': 'Hospital Metropolitano', 'codigo': 'HOSP001', 'tipo': 'Hospital', 'region': 'Metropolitana'},
        {'nombre': 'CESFAM Pudahuel', 'codigo': 'CES001', 'tipo': 'CESFAM', 'region': 'Metropolitana'},
        {'nombre': 'CESFAM Maipú', 'codigo': 'CES002', 'tipo': 'CESFAM', 'region': 'Metropolitana'},
        {'nombre': 'Hospital Sótero del Río', 'codigo': 'HOSP002', 'tipo': 'Hospital', 'region': 'Metropolitana'},
        {'nombre': 'CESFAM La Florida', 'codigo': 'CES003', 'tipo': 'CESFAM', 'region': 'Metropolitana'},
    ]
    
    establecimientos = {}
    for data in establecimientos_data:
        estab, created = Establecimiento.objects.get_or_create(
            codigo=data['codigo'],
            defaults=data
        )
        establecimientos[data['codigo']] = estab
        print(f"   ✅ {data['nombre']}")
    
    # 2. CREAR INDICADORES DE COHORTE (AJUSTADO A LA ESTRUCTURA REAL)
    print("\n2. 📈 CREANDO INDICADORES DE COHORTE")
    
    # Primero verifiquemos la estructura real del modelo
    try:
        # Intentar crear un indicador con campos mínimos para ver la estructura
        cohorte_test = IndicadoresCohorte.objects.create(
            establecimiento=establecimientos['HOSP001'],
            año=2024,
            trimestre=1,
            casos_nuevos=10,
            curados=8,
            abandonos=1,
            fallecidos=1
        )
        print("   ✅ Estructura básica funciona")
        cohorte_test.delete()  # Eliminar el de prueba
    except Exception as e:
        print(f"   ❌ Error en estructura: {e}")
        print("   🔍 Revisando campos disponibles...")
        
        # Mostrar campos disponibles del modelo
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("DESCRIBE indicadores_indicadorescohorte")
            columns = cursor.fetchall()
            print("   Campos disponibles:")
            for column in columns:
                print(f"     - {column[0]} ({column[1]})")
    
    # Crear cohortes con estructura ajustada
    cohortes_data = []
    year = 2024
    
    for trimestre in range(1, 5):  # 4 trimestres 2024
        for estab_codigo in ['HOSP001', 'CES001', 'CES002']:
            total_casos = random.randint(8, 15)
            curados = int(total_casos * random.uniform(0.85, 0.95))
            abandonos = int(total_casos * random.uniform(0.02, 0.08))
            fallecidos = int(total_casos * random.uniform(0.01, 0.04))
            otros = total_casos - curados - abandonos - fallecidos
            
            try:
                # Intentar con estructura mínima primero
                cohorte_data = {
                    'establecimiento': establecimientos[estab_codigo],
                    'año': year,
                    'trimestre': trimestre,
                    'casos_nuevos': total_casos - 2,
                    'curados': curados,
                    'abandonos': abandonos,
                    'fallecidos': fallecidos
                }
                
                # Agregar campos opcionales si existen
                try:
                    cohorte_data['retratamiento'] = 2
                except:
                    pass
                    
                try:
                    cohorte_data['fracasos'] = 0
                except:
                    pass
                    
                try:
                    cohorte_data['trasladados'] = otros
                except:
                    pass
                
                cohorte = IndicadoresCohorte.objects.create(**cohorte_data)
                cohortes_data.append(cohorte)
                
            except Exception as e:
                print(f"   ⚠️ Error creando cohorte {estab_codigo} Q{trimestre}: {e}")
                # Intentar con estructura mínima absoluta
                try:
                    cohorte = IndicadoresCohorte.objects.create(
                        establecimiento=establecimientos[estab_codigo],
                        año=year,
                        trimestre=trimestre,
                        casos_nuevos=total_casos,
                        curados=curados,
                        abandonos=abandonos,
                        fallecidos=fallecidos
                    )
                    cohortes_data.append(cohorte)
                except Exception as e2:
                    print(f"   ❌ Error crítico: {e2}")
    
    # Cohortes 2025 (primer trimestre)
    year = 2025
    for estab_codigo in ['HOSP001', 'CES001', 'CES002']:
        total_casos = random.randint(10, 18)
        curados = int(total_casos * random.uniform(0.88, 0.96))
        abandonos = int(total_casos * random.uniform(0.01, 0.05))
        fallecidos = int(total_casos * random.uniform(0.005, 0.03))
        
        try:
            cohorte = IndicadoresCohorte.objects.create(
                establecimiento=establecimientos[estab_codigo],
                año=year,
                trimestre=1,
                casos_nuevos=total_casos,
                curados=curados,
                abandonos=abandonos,
                fallecidos=fallecidos
            )
            cohortes_data.append(cohorte)
        except Exception as e:
            print(f"   ⚠️ Error cohorte 2025 {estab_codigo}: {e}")
    
    print(f"   ✅ {len(cohortes_data)} cohortes creadas exitosamente")
    
    # 3. CREAR INDICADORES OPERACIONALES (MENSUALES 2025)
    print("\n3. 📊 CREANDO INDICADORES OPERACIONALES")
    
    meses_2025 = [
        ('2025-01', 'Enero 2025'),
        ('2025-02', 'Febrero 2025'), 
        ('2025-03', 'Marzo 2025'),
    ]
    
    operacionales_count = 0
    for periodo, periodo_nombre in meses_2025:
        for estab_codigo in ['HOSP001', 'CES001', 'CES002', 'HOSP002', 'CES003']:
            try:
                sintomaticos = random.randint(50, 120)
                baciloscopias = int(sintomaticos * random.uniform(0.8, 0.95))
                contactos_identificados = random.randint(20, 60)
                contactos_estudiados = int(contactos_identificados * random.uniform(0.85, 0.98))
                pacientes_taes = random.randint(15, 30)
                pacientes_adherentes = int(pacientes_taes * random.uniform(0.90, 0.98))
                
                # Crear con estructura básica
                operacional_data = {
                    'establecimiento': establecimientos[estab_codigo],
                    'periodo': periodo,
                    'sintomaticos_respiratorios': sintomaticos,
                    'baciloscopias_realizadas': baciloscopias,
                    'contactos_identificados': contactos_identificados,
                    'contactos_estudiados': contactos_estudiados,
                    'pacientes_taes': pacientes_taes,
                    'pacientes_adherentes': pacientes_adherentes
                }
                
                # Agregar campos opcionales
                try:
                    operacional_data['periodo_nombre'] = periodo_nombre
                except:
                    pass
                
                operacional = IndicadoresOperacionales.objects.create(**operacional_data)
                operacionales_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Error operacional {estab_codigo} {periodo}: {e}")
    
    print(f"   ✅ {operacionales_count} indicadores operacionales creados")
    
    # 4. CREAR INDICADORES DE PREVENCIÓN
    print("\n4. 🛡️ CREANDO INDICADORES DE PREVENCIÓN")
    
    prevencion_count = 0
    for periodo, periodo_nombre in meses_2025:
        for estab_codigo in ['HOSP001', 'CES001', 'CES002']:
            try:
                contactos_identificados = random.randint(15, 40)
                contactos_iniciaron_qp = int(contactos_identificados * random.uniform(0.7, 0.9))
                contactos_completaron_qp = int(contactos_iniciaron_qp * random.uniform(0.8, 0.95))
                rn_vacunados = random.randint(20, 50)
                rn_establecimiento = random.randint(25, 55)
                
                prevencion_data = {
                    'establecimiento': establecimientos[estab_codigo],
                    'periodo': periodo,
                    'contactos_identificados': contactos_identificados,
                    'contactos_iniciaron_qp': contactos_iniciaron_qp,
                    'contactos_completaron_qp': contactos_completaron_qp,
                    'rn_vacunados': rn_vacunados,
                    'rn_establecimiento': rn_establecimiento
                }
                
                # Agregar campo opcional
                try:
                    prevencion_data['periodo_nombre'] = periodo_nombre
                except:
                    pass
                
                prevencion = IndicadoresPrevencion.objects.create(**prevencion_data)
                prevencion_count += 1
                
            except Exception as e:
                print(f"   ⚠️ Error prevención {estab_codigo} {periodo}: {e}")
    
    print(f"   ✅ {prevencion_count} indicadores de prevención creados")
    
    # 5. CREAR ALERTAS DEL SISTEMA
    print("\n5. 🚨 CREANDO ALERTAS DEL SISTEMA")
    
    alertas_data = [
        {
            'tipo': 'Vencimiento de tratamiento',
            'nivel': 'Alta',
            'descripcion': 'Tratamiento de paciente Juan Pérez vence en 7 días',
            'establecimiento': establecimientos['CES001'],
            'fecha_vencimiento': datetime.now() + timedelta(days=7)
        },
        {
            'tipo': 'Estudio de contactos pendiente', 
            'nivel': 'Media',
            'descripcion': 'Estudio de contactos de caso índice pendiente por 10 días',
            'establecimiento': establecimientos['HOSP001'],
            'fecha_vencimiento': datetime.now() + timedelta(days=3)
        },
        {
            'tipo': 'Indicador fuera de rango',
            'nivel': 'Baja', 
            'descripcion': 'Tasa de pesquisa inferior a meta mensual',
            'establecimiento': establecimientos['CES002'],
            'fecha_vencimiento': datetime.now() + timedelta(days=30)
        },
        {
            'tipo': 'Resultado crítico',
            'nivel': 'Crítica',
            'descripcion': 'Cultivo positivo para MDR-TB en paciente Carlos Rojas',
            'establecimiento': establecimientos['HOSP001'],
            'fecha_vencimiento': datetime.now() + timedelta(days=1)
        }
    ]
    
    alertas_count = 0
    for alerta_data in alertas_data:
        try:
            alerta = Alerta.objects.create(
                tipo=alerta_data['tipo'],
                nivel=alerta_data['nivel'],
                descripcion=alerta_data['descripcion'],
                estado='Pendiente',
                establecimiento=alerta_data['establecimiento'],
                fecha_creacion=datetime.now(),
                fecha_vencimiento=alerta_data['fecha_vencimiento']
            )
            alertas_count += 1
            print(f"   ✅ Alerta: {alerta_data['tipo']} - {alerta_data['nivel']}")
        except Exception as e:
            print(f"   ⚠️ Error creando alerta: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 CARGA DE DATOS PARA INDICADORES COMPLETADA!")
    print("=" * 60)
    
    # RESUMEN FINAL
    print("\n📊 RESUMEN DE DATOS CARGADOS:")
    print(f"   🏥 Establecimientos: {Establecimiento.objects.count()}")
    print(f"   📈 Indicadores Cohorte: {IndicadoresCohorte.objects.count()}")
    print(f"   📊 Indicadores Operacionales: {IndicadoresOperacionales.objects.count()}")
    print(f"   🛡️ Indicadores Prevención: {IndicadoresPrevencion.objects.count()}")
    print(f"   🚨 Alertas: {Alerta.objects.count()}")

if __name__ == '__main__':
    main()