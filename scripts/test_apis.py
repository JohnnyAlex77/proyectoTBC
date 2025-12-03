"""
Script para verificar que todas las APIs están funcionando correctamente
"""
import requests
import json
import sys

def test_api_endpoints():
    """Test completo de todos los endpoints API"""
    
    base_url = "http://localhost:8000/api"
    resultados = []
    
    print("🔧 TESTEANDO APIS DEL SISTEMA TBC")
    print("=" * 60)
    
    # 1. Obtener token (si usas autenticación)
    print("\n1. 🔐 Probando autenticación...")
    try:
        auth_response = requests.post(f"{base_url}/auth/token/", 
                                    data={"username": "admin", "password": "AdminTBC2024!"})
        if auth_response.status_code == 200:
            token = auth_response.json().get('token')
            print("   ✅ Autenticación exitosa")
            headers = {'Authorization': f'Token {token}'}
        else:
            print("   ⚠️  Autenticación falló, usando modo no autenticado")
            headers = {}
    except:
        headers = {}
    
    # 2. Probar endpoints principales
    endpoints = [
        ("/pacientes/", "GET", "API Pacientes"),
        ("/tratamientos/", "GET", "API Tratamientos"),
        ("/dashboard/estadisticas/", "GET", "Dashboard Estadísticas"),
        ("/status/", "GET", "Estado del Sistema"),
    ]
    
    print("\n2. 📊 Probando APIs principales...")
    for endpoint, method, nombre in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", headers=headers)
            elif method == "POST":
                response = requests.post(f"{base_url}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                print(f"   ✅ {nombre}: HTTP {response.status_code}")
                resultados.append((endpoint, True))
            else:
                print(f"   ❌ {nombre}: HTTP {response.status_code} - {response.text[:100]}")
                resultados.append((endpoint, False))
        except Exception as e:
            print(f"   ❌ {nombre}: ERROR - {str(e)}")
            resultados.append((endpoint, False))
    
    # 3. Probar documentación
    print("\n3. 📚 Probando documentación...")
    docs_endpoints = [
        ("/docs/", "Swagger UI"),
        ("/redoc/", "ReDoc"),
        ("/swagger/", "Swagger (alternativo)"),
    ]
    
    for endpoint, nombre in docs_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}")
            if response.status_code == 200:
                print(f"   ✅ {nombre}: HTTP {response.status_code}")
                resultados.append((endpoint, True))
            else:
                print(f"   ❌ {nombre}: HTTP {response.status_code}")
                resultados.append((endpoint, False))
        except Exception as e:
            print(f"   ❌ {nombre}: ERROR - {str(e)}")
            resultados.append((endpoint, False))
    
    # 4. Probar APIs externas
    print("\n4. 🌐 Probando APIs externas...")
    
    # Geocodificación (GET)
    try:
        geo_response = requests.get(f"{base_url}/external/geocodificar/?direccion=Av+Principal+123&comuna=Santiago")
        if geo_response.status_code in [200, 201]:
            geo_data = geo_response.json()
            print(f"   ✅ Geocodificación (GET): HTTP {geo_response.status_code}")
            print(f"      Lat: {geo_data.get('latitud')}, Lon: {geo_data.get('longitud')}")
            resultados.append(("/external/geocodificar/ (GET)", True))
        else:
            print(f"   ❌ Geocodificación (GET): HTTP {geo_response.status_code}")
            resultados.append(("/external/geocodificar/ (GET)", False))
    except Exception as e:
        print(f"   ❌ Geocodificación (GET): ERROR - {str(e)}")
        resultados.append(("/external/geocodificar/ (GET)", False))
    
    # Clima
    try:
        clima_response = requests.get(f"{base_url}/external/clima/?ciudad=Santiago")
        if clima_response.status_code == 200:
            clima_data = clima_response.json()
            print(f"   ✅ Clima: HTTP {clima_response.status_code}")
            print(f"      Temp: {clima_data.get('temperatura')}°C en {clima_data.get('ciudad')}")
            resultados.append(("/external/clima/", True))
        else:
            print(f"   ❌ Clima: HTTP {clima_response.status_code}")
            resultados.append(("/external/clima/", False))
    except Exception as e:
        print(f"   ❌ Clima: ERROR - {str(e)}")
        resultados.append(("/external/clima/", False))
    
    # 5. Resumen
    print("\n" + "=" * 60)
    print("📈 RESUMEN DE PRUEBAS:")
    
    exitos = sum(1 for _, estado in resultados if estado)
    total = len(resultados)
    
    print(f"Total endpoints probados: {total}")
    print(f"Exitosos: {exitos}")
    print(f"Fallidos: {total - exitos}")
    print(f"Tasa de éxito: {(exitos/total*100):.1f}%")
    
    if exitos == total:
        print("\n🎉 ¡TODAS LAS APIS ESTÁN FUNCIONANDO CORRECTAMENTE!")
        return True
    else:
        print("\n⚠️  Algunas APIs presentan problemas:")
        for endpoint, estado in resultados:
            if not estado:
                print(f"  - {endpoint}")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)