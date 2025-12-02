# scripts/test_apis.py
"""
Script para probar las APIs del sistema TBC
"""
import os
import sys
import django
import requests
import json
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sistemaTBC_demo.settings.development')
django.setup()

BASE_URL = "http://localhost:8000/api/"

def test_api_status():
    """Probar endpoint de estado"""
    print("1. Probando endpoint de estado...")
    
    response = requests.get(f"{BASE_URL}status/")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Estado: {response.status_code}")
        print(f"   ✓ API REST: {data.get('api_rest', False)}")
        print(f"   ✓ Base de datos: {data.get('base_datos', False)}")
        return True
    else:
        print(f"   ✗ Error: {response.status_code}")
        return False

def test_autenticacion():
    """Probar autenticación"""
    print("\n2. Probando autenticación...")
    
    # Obtener token
    auth_data = {
        'username': 'admin',
        'password': 'AdminTBC2024!'
    }
    
    response = requests.post(f"{BASE_URL}auth/token/", data=auth_data)
    
    if response.status_code == 200:
        token = response.json().get('token')
        print(f"   ✓ Token obtenido: {token[:20]}...")
        return token
    else:
        print(f"   ✗ Error de autenticación: {response.status_code}")
        return None

def test_api_pacientes(token):
    """Probar API de pacientes"""
    print("\n3. Probando API de pacientes...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Listar pacientes
    response = requests.get(f"{BASE_URL}pacientes/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Listado: {len(data.get('results', data))} pacientes")
        
        # Obtener estadísticas
        response = requests.get(f"{BASE_URL}pacientes/estadisticas/", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✓ Estadísticas: {stats.get('total', 0)} pacientes totales")
        
        return True
    else:
        print(f"   ✗ Error: {response.status_code}")
        return False

def test_api_tratamientos(token):
    """Probar API de tratamientos"""
    print("\n4. Probando API de tratamientos...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Listar tratamientos activos
    response = requests.get(f"{BASE_URL}tratamientos/activos/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Tratamientos activos: {len(data.get('results', data))}")
        return True
    else:
        print(f"   ✗ Error: {response.status_code}")
        return False

def test_api_dashboard(token):
    """Probar API del dashboard"""
    print("\n5. Probando API del dashboard...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Obtener estadísticas del dashboard
    response = requests.get(f"{BASE_URL}dashboard/estadisticas/", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Dashboard: {len(data)} métricas obtenidas")
        print(f"   ✓ Pacientes: {data.get('pacientes', {}).get('total', 0)}")
        print(f"   ✓ Tratamientos: {data.get('tratamientos', {}).get('total', 0)}")
        return True
    else:
        print(f"   ✗ Error: {response.status_code}")
        return False

def test_api_externas(token):
    """Probar APIs externas"""
    print("\n6. Probando APIs externas...")
    
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }
    
    # Probar geocodificación
    geo_data = {
        'direccion': 'Av. Libertador Bernardo O Higgins 123',
        'comuna': 'Santiago'
    }
    
    response = requests.post(
        f"{BASE_URL}external/geocodificar/", 
        headers=headers, 
        json=geo_data
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Geocodificación: {data.get('exitoso', False)}")
        print(f"   ✓ Dirección: {data.get('direccion', '')[:30]}...")
    else:
        print(f"   ✗ Error geocodificación: {response.status_code}")
    
    # Probar clima
    response = requests.get(
        f"{BASE_URL}external/clima/?ciudad=Santiago", 
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ Clima: {data.get('exitoso', False)}")
        print(f"   ✓ Temperatura: {data.get('temperatura', 0)}°C")
    else:
        print(f"   ✗ Error clima: {response.status_code}")
    
    return True

def generar_reporte(results):
    """Generar reporte de pruebas"""
    print("\n" + "=" * 50)
    print("REPORTE DE PRUEBAS - SISTEMA TBC API")
    print("=" * 50)
    
    total_tests = len(results)
    tests_exitosos = sum(results.values())
    
    for test, resultado in results.items():
        status = "✓" if resultado else "✗"
        print(f"{status} {test}")
    
    print("\n" + "=" * 50)
    print(f"RESUMEN: {tests_exitosos}/{total_tests} pruebas exitosas")
    
    if tests_exitosos == total_tests:
        print("✅ TODAS LAS APIS FUNCIONAN CORRECTAMENTE")
    else:
        print(f"⚠️  {total_tests - tests_exitosos} pruebas fallaron")
    
    print("=" * 50)

def main():
    """Función principal de pruebas"""
    print("=" * 50)
    print("INICIANDO PRUEBAS DEL SISTEMA TBC API")
    print("=" * 50)
    
    results = {}
    
    # Ejecutar pruebas
    results['API Status'] = test_api_status()
    
    token = test_autenticacion()
    if token:
        results['Autenticación'] = True
        results['API Pacientes'] = test_api_pacientes(token)
        results['API Tratamientos'] = test_api_tratamientos(token)
        results['API Dashboard'] = test_api_dashboard(token)
        results['API Externas'] = test_api_externas(token)
    else:
        results['Autenticación'] = False
    
    # Generar reporte
    generar_reporte(results)
    
    # Guardar resultados en archivo
    with open('test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': {
                'total': len(results),
                'passed': sum(results.values()),
                'failed': len(results) - sum(results.values())
            }
        }, f, indent=2)

if __name__ == "__main__":
    main()