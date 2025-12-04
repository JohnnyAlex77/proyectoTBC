"""
Script para verificar que todas las APIs del Sistema TBC están funcionando correctamente
Revisa endpoints principales y APIs externas con manejo de errores robusto
"""

import requests
import json
import sys
import time
from datetime import datetime


class APITester:
    """Clase principal para testear endpoints del API TBC"""
    
    def __init__(self, base_url="http://localhost:8000"):
        """Inicializa el tester con URL base y configuración"""
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.token = None
        self.headers = {}
        self.results = []
        
        # Configurar timeout para requests
        self.timeout = 10
        
        print("Script de prueba API - Sistema TBC")
        print("=" * 60)
    
    def authenticate(self, username="admin", password="AdminTBC2024!"):
        """Autentica contra la API usando JWT o Token auth"""
        print("\n1. Probando autenticacion...")
        
        try:
            # Intentar autenticación con el endpoint correcto
            auth_endpoints = [
                (f"{self.api_url}/auth/token/", {"username": username, "password": password}),
                (f"{self.api_url}/auth/login/", {"username": username, "password": password}),
            ]
            
            auth_success = False
            for auth_url, auth_data in auth_endpoints:
                try:
                    response = self.session.post(auth_url, data=auth_data, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        
                        # Manejar diferentes formatos de respuesta
                        if 'access' in response_data:  # JWT
                            self.token = response_data['access']
                            self.headers = {'Authorization': f'Bearer {self.token}'}
                            auth_success = True
                            print(f"   OK - Autenticacion JWT exitosa")
                            break
                        elif 'token' in response_data:  # Token tradicional
                            self.token = response_data['token']
                            self.headers = {'Authorization': f'Token {self.token}'}
                            auth_success = True
                            print(f"   OK - Autenticacion Token exitosa")
                            break
                        elif 'key' in response_data:  # API Key
                            self.token = response_data['key']
                            self.headers = {'Authorization': f'Token {self.token}'}
                            auth_success = True
                            print(f"   OK - Autenticacion API Key exitosa")
                            break
                except requests.exceptions.RequestException:
                    continue
            
            if not auth_success:
                print("   ADVERTENCIA - No se pudo autenticar, probando endpoints publicos")
                self.headers = {}
                
        except Exception as e:
            print(f"   ERROR - Excepcion en autenticacion: {str(e)}")
            self.headers = {}
    
    def test_endpoint(self, endpoint, method="GET", name="", data=None, requires_auth=True):
        """Testea un endpoint individual"""
        full_url = f"{self.api_url}{endpoint}"
        
        # Headers apropiados
        headers = self.headers if requires_auth else {}
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = self.session.get(full_url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                headers = headers.copy()
                headers['Content-Type'] = 'application/json'
                response = self.session.post(full_url, headers=headers, 
                                           json=data if data else {}, 
                                           timeout=self.timeout)
            elif method == "PUT":
                headers = headers.copy()
                headers['Content-Type'] = 'application/json'
                response = self.session.put(full_url, headers=headers, 
                                          json=data if data else {}, 
                                          timeout=self.timeout)
            elif method == "DELETE":
                response = self.session.delete(full_url, headers=headers, timeout=self.timeout)
            else:
                return False, "Metodo HTTP no valido"
            
            response_time = time.time() - start_time
            
            # Evaluar respuesta
            status_ok = response.status_code in [200, 201, 204]
            is_json = 'application/json' in response.headers.get('Content-Type', '').lower()
            
            if status_ok:
                status_msg = f"HTTP {response.status_code} ({response_time:.2f}s)"
                
                # Para respuestas JSON, verificar estructura basica
                if is_json and response.content:
                    try:
                        json_data = response.json()
                        # Verificar si es una respuesta de paginacion
                        if isinstance(json_data, dict):
                            if 'results' in json_data:
                                item_count = len(json_data['results'])
                                status_msg += f", {item_count} items"
                            elif 'count' in json_data:
                                status_msg += f", total: {json_data['count']} items"
                    except json.JSONDecodeError:
                        pass
                        
                success = True
                message = f"   OK - {name}: {status_msg}"
                
            else:
                success = False
                error_detail = response.text[:200] if response.text else "Sin contenido"
                message = f"   FALLO - {name}: HTTP {response.status_code} - {error_detail}"
            
        except requests.exceptions.Timeout:
            success = False
            message = f"   FALLO - {name}: Timeout (>{self.timeout}s)"
            
        except requests.exceptions.ConnectionError:
            success = False
            message = f"   FALLO - {name}: Error de conexion - Verifica que el servidor este corriendo en {self.base_url}"
            
        except Exception as e:
            success = False
            message = f"   FALLO - {name}: Excepcion - {str(e)}"
        
        print(message)
        self.results.append((endpoint, success, message))
        return success
    
    def test_main_apis(self):
        """Testea las APIs principales del sistema"""
        print("\n2. Probando APIs principales...")
        
        endpoints = [
            # Endpoints de pacientes
            ("/pacientes/", "GET", "API Pacientes - Listado"),
            ("/pacientes/estadisticas/", "GET", "API Pacientes - Estadisticas"),
            
            # Endpoints de tratamientos
            ("/tratamientos/", "GET", "API Tratamientos - Listado"),
            ("/tratamientos/activos/", "GET", "API Tratamientos - Activos"),
            
            # Dashboard
            ("/dashboard/estadisticas/", "GET", "Dashboard - Estadisticas"),
            ("/dashboard/alertas/", "GET", "Dashboard - Alertas"),
            
            # Utilidades
            ("/status/", "GET", "Estado del Sistema", False),  # No requiere auth
        ]
        
        for endpoint_info in endpoints:
            if len(endpoint_info) == 4:
                endpoint, method, name, requires_auth = endpoint_info
            else:
                endpoint, method, name = endpoint_info
                requires_auth = True
            
            self.test_endpoint(endpoint, method, name, requires_auth=requires_auth)
    
    def test_documentation(self):
        """Testea endpoints de documentacion"""
        print("\n3. Probando documentacion...")
        
        docs_endpoints = [
            ("/docs/", "GET", "Swagger UI", False),
            ("/redoc/", "GET", "ReDoc", False),
            ("/schema/", "GET", "Esquema OpenAPI", False),
            ("/swagger/", "GET", "Swagger (alternativo)", False),
        ]
        
        for endpoint, method, name, requires_auth in docs_endpoints:
            self.test_endpoint(endpoint, method, name, requires_auth=requires_auth)
    
    def test_external_apis(self):
        """Testea las APIs externas"""
        print("\n4. Probando APIs externas...")
        
        # Geocodificacion - POST (como se usa en el codigo)
        geo_data = {
            "direccion": "Av. Libertador Bernardo O'Higgins 123",
            "comuna": "Santiago",
            "ciudad": "Santiago",
            "pais": "Chile"
        }
        
        self.test_endpoint(
            "/external/geocodificar/", 
            "POST", 
            "Geocodificacion (POST)", 
            data=geo_data
        )
        
        # Geocodificacion - GET (para compatibilidad)
        self.test_endpoint(
            "/external/geocodificar/?direccion=Av%20Principal%20123&comuna=Santiago", 
            "GET", 
            "Geocodificacion (GET)"
        )
        
        # Clima
        self.test_endpoint(
            "/external/clima/?ciudad=Santiago", 
            "GET", 
            "API Clima"
        )
        
        # Analisis epidemiológico
        self.test_endpoint(
            "/external/analisis-epidemiologico/?comuna=Puente%20Alto", 
            "GET", 
            "Analisis Epidemiologico"
        )
    
    def test_authentication_endpoints(self):
        """Testea endpoints de autenticacion"""
        print("\n5. Probando endpoints de autenticacion...")
        
        # Este endpoint no deberia requerir autenticacion
        self.test_endpoint(
            "/auth/token/", 
            "POST", 
            "Login API", 
            data={"username": "test", "password": "test"},
            requires_auth=False
        )
        
        # Endpoint de REST framework
        self.test_endpoint(
            "/auth/", 
            "GET", 
            "REST Framework Auth",
            requires_auth=False
        )
    
    def generate_report(self):
        """Genera reporte detallado de los tests"""
        print("\n" + "=" * 60)
        print("RESUMEN DE PRUEBAS:")
        
        total = len(self.results)
        successes = sum(1 for _, success, _ in self.results if success)
        failures = total - successes
        
        print(f"Total endpoints probados: {total}")
        print(f"Exitosos: {successes}")
        print(f"Fallidos: {failures}")
        
        if total > 0:
            success_rate = (successes / total) * 100
            print(f"Tasa de exito: {success_rate:.1f}%")
        else:
            print("Tasa de exito: N/A")
        
        # Mostrar fallos detallados
        if failures > 0:
            print("\nEndpoints con problemas:")
            for endpoint, success, message in self.results:
                if not success:
                    print(f"  - {message}")
        
        # Verificaciones adicionales
        print("\nVerificaciones adicionales:")
        
        # Verificar que el servidor este corriendo
        try:
            response = self.session.get(self.base_url, timeout=5)
            if response.status_code == 200:
                print("  OK - Servidor principal accesible")
            else:
                print(f"  ADVERTENCIA - Servidor responde con HTTP {response.status_code}")
        except:
            print(f"  ERROR - No se puede conectar al servidor en {self.base_url}")
        
        # Verificar acceso a interfaz web
        try:
            response = self.session.get(f"{self.base_url}/api/docs/", timeout=5)
            if response.status_code == 200:
                print("  OK - Documentacion Swagger accesible")
            else:
                print(f"  ADVERTENCIA - Swagger responde con HTTP {response.status_code}")
        except:
            print("  ERROR - No se puede acceder a la documentacion")
        
        return successes == total
    
    def run_all_tests(self):
        """Ejecuta todos los tests en secuencia"""
        # Primero probar sin autenticacion para verificar servidor basico
        print("Iniciando pruebas sin autenticacion...")
        self.test_endpoint("/status/", "GET", "Estado inicial", requires_auth=False)
        
        # Luego autenticar
        self.authenticate()
        
        # Ejecutar suites de test
        self.test_main_apis()
        self.test_documentation()
        self.test_external_apis()
        self.test_authentication_endpoints()
        
        # Generar reporte
        all_passed = self.generate_report()
        
        # Recomendaciones
        print("\n" + "=" * 60)
        print("RECOMENDACIONES:")
        
        if not self.token:
            print("1. La autenticacion fallo. Verifica:")
            print("   - Credenciales en el script")
            print("   - Endpoints de autenticacion en api/urls.py")
            print("   - Servicio de autenticacion ejecutandose")
        
        failures = [msg for _, success, msg in self.results if not success and "Error de conexion" in msg]
        if failures:
            print("2. Errores de conexion detectados. Verifica:")
            print(f"   - Servidor Django corriendo en {self.base_url}")
            print("   - Puertos no bloqueados por firewall")
            print("   - Servicio MySQL ejecutandose")
        
        # Verificar estructura de API
        print("\3. Si hay errores 404, verifica:")
        print("   - Rutas definidas en api/urls.py")
        print("   - Namespace correcto en urls principales")
        print("   - Aplicacion 'api' en INSTALLED_APPS")
        
        return all_passed


def main():
    """Funcion principal"""
    
    # Configurar URL base (puede modificarse por argumento)
    import argparse
    parser = argparse.ArgumentParser(description='Testear APIs del Sistema TBC')
    parser.add_argument('--url', default='http://localhost:8000', 
                       help='URL base del servidor (default: http://localhost:8000)')
    parser.add_argument('--username', default='admin', 
                       help='Usuario para autenticacion (default: admin)')
    parser.add_argument('--password', default='AdminTBC2024!', 
                       help='Password para autenticacion (default: AdminTBC2024!)')
    
    args = parser.parse_args()
    
    # Crear y ejecutar tester
    tester = APITester(base_url=args.url)
    
    # Sobrescribir credenciales si se proporcionan
    import builtins
    builtins.__dict__['AUTH_USERNAME'] = args.username
    builtins.__dict__['AUTH_PASSWORD'] = args.password
    
    try:
        print(f"Iniciando pruebas contra: {args.url}")
        print(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        all_passed = tester.run_all_tests()
        
        if all_passed:
            print("\n" + "=" * 60)
            print("RESULTADO: Todas las APIs estan funcionando correctamente.")
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("RESULTADO: Algunas APIs presentan problemas. Revisa los errores arriba.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nPruebas interrumpidas por el usuario.")
        sys.exit(2)
    except Exception as e:
        print(f"\nERROR inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(3)


if __name__ == "__main__":
    main()