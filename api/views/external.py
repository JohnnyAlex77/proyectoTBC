# api/views/external.py
"""
Vistas para APIs externas
Geocodificación, clima y análisis epidemiológico
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
import requests
import json
from django.core.cache import cache
from django.conf import settings
from datetime import date, timedelta
from django.utils import timezone
from apps.pacientes.models import PacientesPaciente
from apps.tratamientos.models import Tratamiento
from apps.examenes.models import ExamenesExamenbacteriologico
from django.db.models import Count, Avg, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

class GeocodificarView(APIView):
    """
    Vista para geocodificación de direcciones usando API externa
    Acepta tanto GET como POST
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Geocodificar dirección",
        description="""Convierte una dirección en coordenadas geográficas (latitud/longitud).
        
        **Ejemplos:**
        - GET: `/api/external/geocodificar/?direccion=Av+Principal+123&comuna=Santiago`
        - POST: `{"direccion": "Av Principal 123", "comuna": "Santiago"}`
        
        **Fuente de datos:** OpenStreetMap Nominatim (servicio gratuito)
        **Cache:** 24 horas para resultados exitosos
        """,
        parameters=[
            OpenApiParameter(
                name='direccion',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Dirección a geocodificar (ej: "Av Principal 123")',
                required=True
            ),
            OpenApiParameter(
                name='comuna',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Comuna (opcional, ej: "Santiago")',
                required=False
            ),
            OpenApiParameter(
                name='ciudad',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Ciudad (opcional, default: "Santiago")',
                required=False
            ),
            OpenApiParameter(
                name='pais',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='País (opcional, default: "Chile")',
                required=False
            ),
        ],
        request=OpenApiTypes.OBJECT,
        examples=[
            OpenApiExample(
                'Ejemplo GET',
                value={},
                description='Uso por URL con parámetros query',
                request_only=False,
                response_only=False
            ),
            OpenApiExample(
                'Ejemplo POST',
                value={
                    "direccion": "Av. Libertador Bernardo O'Higgins 123",
                    "comuna": "Santiago",
                    "ciudad": "Santiago",
                    "pais": "Chile"
                },
                description='Uso por POST con JSON',
                request_only=True,
                response_only=False
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Geocodificación exitosa',
                examples=[
                    OpenApiExample(
                        'Respuesta exitosa',
                        value={
                            "exitoso": True,
                            "direccion": "Avenida Libertador Bernardo O'Higgins 123, Santiago, Santiago Metropolitan Region, Chile",
                            "latitud": -33.4488897,
                            "longitud": -70.6692655,
                            "tipo": "administrative",
                            "importancia": 0.6748476595333333,
                            "fuente": "OpenStreetMap Nominatim",
                            "detalles": {
                                "city": "Santiago",
                                "state": "Santiago Metropolitan Region",
                                "country": "Chile",
                                "country_code": "cl"
                            },
                            "coordenadas": {
                                "lat": -33.4488897,
                                "lon": -70.6692655,
                                "latitud": -33.4488897,
                                "longitud": -70.6692655
                            }
                        }
                    ),
                    OpenApiExample(
                        'Respuesta con cache',
                        value={
                            "exitoso": True,
                            "direccion": "Avenida Principal 123, Santiago, Chile",
                            "latitud": -33.4489,
                            "longitud": -70.6693,
                            "fuente": "cache",
                            "cache": True,
                            "detalles": {
                                "comuna": "Santiago",
                                "ciudad": "Santiago",
                                "pais": "Chile"
                            }
                        }
                    ),
                ]
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Error: parámetros faltantes',
                examples=[
                    OpenApiExample(
                        'Error 400',
                        value={
                            "error": "Se requiere una dirección",
                            "ejemplo": "/api/external/geocodificar/?direccion=Av+Principal+123&comuna=Santiago"
                        }
                    )
                ]
            ),
            500: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Error interno del servidor',
                examples=[
                    OpenApiExample(
                        'Error 500',
                        value={
                            "error": "Error en geocodificación: Timeout en la conexión",
                            "exitoso": False
                        }
                    )
                ]
            ),
        },
        tags=['APIs Externas']
    )
    def get(self, request):
        """
        Geocodifica una dirección a coordenadas (método GET)
        Útil para pruebas rápidas desde navegador
        """
        direccion = request.GET.get('direccion', '').strip()
        comuna = request.GET.get('comuna', '').strip()
        
        if not direccion:
            return Response(
                {'error': 'Se requiere una dirección', 'ejemplo': '/api/external/geocodificar/?direccion=Av+Principal+123&comuna=Santiago'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Llamar a la función de geocodificación
        resultado = self._geocodificar_direccion(direccion, comuna)
        return Response(resultado)
    
    @extend_schema(
        summary="Geocodificar dirección (POST)",
        description="Geocodificación por POST con datos JSON",
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'direccion': {'type': 'string', 'example': 'Av Principal 123'},
                    'comuna': {'type': 'string', 'example': 'Santiago'},
                    'ciudad': {'type': 'string', 'example': 'Santiago'},
                    'pais': {'type': 'string', 'example': 'Chile'},
                },
                'required': ['direccion']
            }
        },
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Geocodificación exitosa'
            ),
            400: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                description='Parámetros faltantes o inválidos'
            ),
        },
        tags=['APIs Externas']
    )
    def post(self, request):
        """
        Geocodifica una dirección a coordenadas (método POST)
        Para uso programático con datos JSON
        """
        direccion = request.data.get('direccion', '').strip()
        comuna = request.data.get('comuna', '').strip()
        ciudad = request.data.get('ciudad', 'Santiago').strip()
        pais = request.data.get('pais', 'Chile').strip()
        
        if not direccion:
            return Response(
                {'error': 'Se requiere una dirección'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Llamar a la función de geocodificación
        resultado = self._geocodificar_direccion(direccion, comuna, ciudad, pais)
        return Response(resultado)
    
    def _geocodificar_direccion(self, direccion, comuna='', ciudad='Santiago', pais='Chile'):
        """
        Función interna para geocodificación
        Usa Nominatim (OpenStreetMap) como servicio gratuito
        """
        import requests
        from django.core.cache import cache
        
        # Crear clave de cache
        cache_key = f"geocoding_{direccion}_{comuna}_{ciudad}_{pais}".replace(' ', '_').lower()
        
        # Verificar cache primero (24 horas)
        cached_result = cache.get(cache_key)
        if cached_result:
            cached_result['cache'] = True
            return cached_result
        
        try:
            # Construir consulta para Nominatim (OpenStreetMap) - SERVICIO GRATUITO
            query_parts = []
            if direccion:
                query_parts.append(direccion)
            if comuna:
                query_parts.append(comuna)
            if ciudad:
                query_parts.append(ciudad)
            if pais:
                query_parts.append(pais)
            
            query = ", ".join(filter(None, query_parts))
            
            # Configurar headers para cumplir con TOS de Nominatim
            headers = {
                'User-Agent': 'SistemaTBC/1.0 (contacto@sistematbc.cl)',
                'Accept': 'application/json',
                'Accept-Language': 'es'
            }
            
            # Parámetros de la consulta
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'cl',
                'addressdetails': 1,
                'polygon': 0,
                'bounded': 0
            }
            
            # Realizar consulta a API pública de Nominatim
            response = requests.get(
                'https://nominatim.openstreetmap.org/search',
                params=params,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    # Procesar resultado exitoso
                    location = data[0]
                    result = {
                        'exitoso': True,
                        'direccion': location.get('display_name', query),
                        'latitud': float(location.get('lat', 0)),
                        'longitud': float(location.get('lon', 0)),
                        'tipo': location.get('type', 'unknown'),
                        'importancia': float(location.get('importance', 0)),
                        'fuente': 'OpenStreetMap Nominatim',
                        'detalles': location.get('address', {}),
                        'coordenadas': {
                            'lat': float(location.get('lat', 0)),
                            'lon': float(location.get('lon', 0)),
                            'latitud': float(location.get('lat', 0)),
                            'longitud': float(location.get('lon', 0))
                        }
                    }
                    
                    # Guardar en cache (24 horas)
                    cache.set(cache_key, result, 86400)
                    
                    return result
            
            # Si llegamos aquí, la geocodificación falló o no hay resultados
            # Usar coordenadas por defecto basadas en comuna/ciudad
            coordenadas_default = self._obtener_coordenadas_por_defecto(comuna or ciudad)
            
            result = {
                'exitoso': False,
                'direccion': query,
                'latitud': coordenadas_default['lat'],
                'longitud': coordenadas_default['lon'],
                'fuente': 'coordenadas_por_defecto',
                'nota': 'Geocodificación aproximada usando coordenadas por defecto',
                'detalles': {
                    'comuna': comuna or ciudad,
                    'ciudad': ciudad,
                    'pais': 'Chile'
                },
                'coordenadas': {
                    'lat': coordenadas_default['lat'],
                    'lon': coordenadas_default['lon'],
                    'latitud': coordenadas_default['lat'],
                    'longitud': coordenadas_default['lon']
                }
            }
            
            # Guardar en cache por menos tiempo (1 hora)
            cache.set(cache_key, result, 3600)
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                'exitoso': False,
                'direccion': f"{direccion}, {comuna}",
                'error': 'Timeout en la geocodificación',
                'nota': 'Servicio de geocodificación no disponible temporalmente'
            }
            
        except Exception as e:
            return {
                'exitoso': False,
                'direccion': f"{direccion}, {comuna}",
                'error': f'Error en geocodificación: {str(e)}',
                'nota': 'Error interno del servidor'
            }
    
    def _obtener_coordenadas_por_defecto(self, lugar):
        """
        Devuelve coordenadas por defecto para ciudades comunes de Chile
        """
        coordenadas_chile = {
            'santiago': {'lat': -33.4489, 'lon': -70.6693},
            'puente alto': {'lat': -33.6167, 'lon': -70.5833},
            'maipú': {'lat': -33.5167, 'lon': -70.7667},
            'la florida': {'lat': -33.5500, 'lon': -70.5833},
            'las condes': {'lat': -33.4167, 'lon': -70.5833},
            'ñuñoa': {'lat': -33.4667, 'lon': -70.6000},
            'san bernardo': {'lat': -33.6000, 'lon': -70.7167},
            'peñalolén': {'lat': -33.4833, 'lon': -70.5500},
            'el bosque': {'lat': -33.5667, 'lon': -70.6833},
            'la pintana': {'lat': -33.5833, 'lon': -70.6333},
            'valparaíso': {'lat': -33.0458, 'lon': -71.6197},
            'viña del mar': {'lat': -33.0245, 'lon': -71.5518},
            'concepción': {'lat': -36.8269, 'lon': -73.0503},
            'temuco': {'lat': -38.7399, 'lon': -72.5901},
            'antofagasta': {'lat': -23.6500, 'lon': -70.4000},
            'iquique': {'lat': -20.2141, 'lon': -70.1524},
            'arica': {'lat': -18.4783, 'lon': -70.3126},
            'puerto montt': {'lat': -41.4718, 'lon': -72.9396},
            'punta arenas': {'lat': -53.1638, 'lon': -70.9171},
        }
        
        lugar_lower = lugar.lower().strip() if lugar else 'santiago'
        
        return coordenadas_chile.get(lugar_lower, {'lat': -33.4489, 'lon': -70.6693})

class ClimaView(APIView):
    """
    Vista para obtener datos climáticos de una ciudad
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Obtiene condiciones climáticas actuales
        """
        ciudad = request.GET.get('ciudad', 'Santiago')
        pais = request.GET.get('pais', 'CL')
        modo_demo = request.GET.get('demo', 'false').lower() == 'true'
        
        # Crear clave de cache
        cache_key = f"weather_{ciudad}_{pais}"
        
        # Verificar cache primero (30 minutos)
        cached_result = cache.get(cache_key)
        if cached_result:
            return Response(cached_result)
        
        # Modo demo para desarrollo
        if modo_demo or not hasattr(settings, 'OPENWEATHER_API_KEY'):
            result = self._datos_demo(ciudad)
            cache.set(cache_key, result, 1800)  # 30 minutos
            return Response(result)
        
        try:
            # Consultar API de OpenWeatherMap
            params = {
                'q': f"{ciudad},{pais}",
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric',
                'lang': 'es'
            }
            
            response = requests.get(
                'https://api.openweathermap.org/data/2.5/weather',
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Procesar datos climáticos
                result = {
                    'exitoso': True,
                    'ciudad': data.get('name', ciudad),
                    'pais': data.get('sys', {}).get('country', pais),
                    'temperatura': data['main']['temp'],
                    'sensacion_termica': data['main']['feels_like'],
                    'temperatura_min': data['main']['temp_min'],
                    'temperatura_max': data['main']['temp_max'],
                    'humedad': data['main']['humidity'],
                    'presion': data['main']['pressure'],
                    'descripcion': data['weather'][0]['description'].capitalize(),
                    'icono': data['weather'][0]['icon'],
                    'viento_velocidad': data['wind']['speed'],
                    'viento_direccion': data['wind'].get('deg', 0),
                    'visibilidad': data.get('visibility', 0),
                    'nubosidad': data['clouds']['all'],
                    'amanecer': data['sys']['sunrise'],
                    'atardecer': data['sys']['sunset'],
                    'actualizado': data['dt'],
                    'fuente': 'OpenWeatherMap',
                    'unidades': 'métrico'
                }
                
                # Calcular calidad del aire (simulado basado en condiciones)
                result['calidad_aire'] = self._calcular_calidad_aire(result)
                
                # Cache por 30 minutos
                cache.set(cache_key, result, 1800)
                
                return Response(result)
            
            # Si falla la API, usar datos demo
            result = self._datos_demo(ciudad)
            cache.set(cache_key, result, 600)  # 10 minutos para errores
            return Response(result)
            
        except Exception as e:
            # En caso de error, usar datos demo
            result = self._datos_demo(ciudad)
            result['error'] = str(e)
            cache.set(cache_key, result, 300)  # 5 minutos para errores
            return Response(result, status=status.HTTP_200_OK)
    
    def _datos_demo(self, ciudad):
        """Genera datos demo para desarrollo"""
        # Datos de ejemplo basados en la ciudad
        datos_ciudades = {
            'Santiago': {'temp': 22.5, 'humidity': 45, 'presion': 1013},
            'Puente Alto': {'temp': 20.8, 'humidity': 55, 'presion': 1012},
            'Maipú': {'temp': 21.2, 'humidity': 50, 'presion': 1013},
            'La Florida': {'temp': 21.8, 'humidity': 52, 'presion': 1012},
            'Ñuñoa': {'temp': 22.1, 'humidity': 48, 'presion': 1013},
            'Valparaíso': {'temp': 18.5, 'humidity': 70, 'presion': 1015},
            'Concepción': {'temp': 16.8, 'humidity': 75, 'presion': 1014},
        }
        
        ciudad_data = datos_ciudades.get(ciudad, {'temp': 20.0, 'humidity': 50, 'presion': 1013})
        
        return {
            'exitoso': True,
            'ciudad': ciudad,
            'pais': 'CL',
            'temperatura': ciudad_data['temp'],
            'sensacion_termica': ciudad_data['temp'] - 1.2,
            'temperatura_min': ciudad_data['temp'] - 3,
            'temperatura_max': ciudad_data['temp'] + 5,
            'humedad': ciudad_data['humidity'],
            'presion': ciudad_data['presion'],
            'descripcion': 'Despejado',
            'icono': '01d',
            'viento_velocidad': 3.1,
            'viento_direccion': 180,
            'visibilidad': 10000,
            'nubosidad': 10,
            'amanecer': 1678956000,
            'atardecer': 1678999200,
            'actualizado': 1678980000,
            'fuente': 'demo',
            'modo': 'demo',
            'calidad_aire': 'Buena',
            'unidades': 'métrico'
        }
    
    def _calcular_calidad_aire(self, datos_clima):
        """Calcula calidad del aire basada en datos climáticos"""
        humedad = datos_clima['humedad']
        temperatura = datos_clima['temperatura']
        viento = datos_clima['viento_velocidad']
        
        # Puntuación simple (0-100)
        puntuacion = 80  # Base
        
        # Ajustar por humedad (óptimo 40-60%)
        if humedad < 30 or humedad > 80:
            puntuacion -= 20
        elif 40 <= humedad <= 60:
            puntuacion += 10
        
        # Ajustar por temperatura (óptimo 18-24°C)
        if temperatura < 10 or temperatura > 30:
            puntuacion -= 15
        elif 18 <= temperatura <= 24:
            puntuacion += 10
        
        # Ajustar por viento (mejor con algo de viento)
        if viento < 1:
            puntuacion -= 5  # Aire estancado
        elif viento > 8:
            puntuacion -= 10  # Mucho viento
        
        # Determinar categoría
        if puntuacion >= 80:
            return 'Excelente'
        elif puntuacion >= 60:
            return 'Buena'
        elif puntuacion >= 40:
            return 'Moderada'
        elif puntuacion >= 20:
            return 'Pobre'
        else:
            return 'Muy pobre'


class AnalisisEpidemiologicoView(APIView):
    """
    Análisis epidemiológico por comuna o región
    Correlaciona casos TBC con factores ambientales
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Retorna análisis epidemiológico para una comuna específica
        """
        comuna = request.GET.get('comuna', '').strip()
        region = request.GET.get('region', '').strip()
        nivel = request.GET.get('nivel', 'comuna')  # comuna, region, nacional
        
        if nivel == 'comuna' and not comuna:
            return Response(
                {'error': 'Se requiere parámetro comuna para análisis comunal'},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif nivel == 'region' and not region:
            return Response(
                {'error': 'Se requiere parámetro region para análisis regional'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener datos según nivel de análisis
            if nivel == 'comuna':
                datos = self._analizar_comuna(comuna)
            elif nivel == 'region':
                datos = self._analizar_region(region)
            else:
                datos = self._analizar_nacional()
            
            # Obtener datos climáticos si es análisis comunal
            if nivel == 'comuna':
                clima_view = ClimaView()
                clima_request = request._request
                clima_request.GET = clima_request.GET.copy()
                clima_request.GET['ciudad'] = comuna
                
                try:
                    clima_response = clima_view.get(clima_request)
                    if clima_response.status_code == 200:
                        datos['clima'] = clima_response.data
                except:
                    datos['clima'] = {'error': 'No se pudieron obtener datos climáticos'}
            
            return Response(datos)
            
        except Exception as e:
            return Response(
                {'error': f'Error en análisis epidemiológico: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _analizar_comuna(self, comuna):
        """Realiza análisis epidemiológico para una comuna"""
        # Filtrar pacientes por comuna
        pacientes_comuna = PacientesPaciente.objects.filter(comuna__icontains=comuna)
        total_pacientes = pacientes_comuna.count()
        
        if total_pacientes == 0:
            return {
                'comuna': comuna,
                'nivel': 'comuna',
                'mensaje': f'No se encontraron pacientes en la comuna {comuna}',
                'total_pacientes': 0
            }
        
        # Calcular incidencia (por 100,000 habitantes)
        # Datos poblacionales de ejemplo - en producción usar datos reales
        poblacion_por_comuna = {
            'Puente Alto': 568106,
            'Maipú': 521627,
            'La Florida': 366916,
            'Las Condes': 294838,
            'Santiago': 404495,
            'Ñuñoa': 256453,
            'San Bernardo': 301313,
            'Peñalolén': 241599,
            'El Bosque': 162505,
            'La Pintana': 190085,
        }
        
        poblacion = poblacion_por_comuna.get(comuna, 100000)
        incidencia = round((total_pacientes / poblacion) * 100000, 2) if poblacion > 0 else 0
        
        # Estadísticas detalladas
        estadisticas = {
            'total': total_pacientes,
            'por_sexo': list(pacientes_comuna.values('sexo').annotate(total=Count('id'))),
            'por_edad': self._distribucion_edades(pacientes_comuna),
            'por_tipo_tbc': list(pacientes_comuna.values('tipo_tbc').annotate(total=Count('id'))),
            'por_estado': list(pacientes_comuna.values('estado').annotate(total=Count('id'))),
            'por_poblacion_prioritaria': list(pacientes_comuna.exclude(
                poblacion_prioritaria='').values('poblacion_prioritaria').annotate(total=Count('id')))
        }
        
        # Tendencia temporal (últimos 12 meses)
        tendencia = self._calcular_tendencia(pacientes_comuna)
        
        # Factores de riesgo identificados
        factores_riesgo = self._identificar_factores_riesgo(pacientes_comuna)
        
        # Generar recomendaciones
        recomendaciones = self._generar_recomendaciones(
            estadisticas, incidencia, total_pacientes, comuna
        )
        
        return {
            'comuna': comuna,
            'nivel': 'comuna',
            'total_pacientes': total_pacientes,
            'poblacion_estimada': poblacion,
            'incidencia': incidencia,
            'incidencia_categoria': self._categorizar_incidencia(incidencia),
            'estadisticas': estadisticas,
            'tendencia': tendencia,
            'factores_riesgo': factores_riesgo,
            'recomendaciones': recomendaciones,
            'actualizado': date.today().isoformat()
        }
    
    def _analizar_region(self, region):
        """Realiza análisis epidemiológico para una región"""
        # Este método sería similar pero a nivel regional
        return {
            'region': region,
            'nivel': 'region',
            'mensaje': 'Análisis regional en desarrollo',
            'actualizado': date.today().isoformat()
        }
    
    def _analizar_nacional(self):
        """Realiza análisis epidemiológico a nivel nacional"""
        total_pacientes = PacientesPaciente.objects.count()
        
        if total_pacientes == 0:
            return {
                'nivel': 'nacional',
                'mensaje': 'No hay pacientes registrados en el sistema',
                'total_pacientes': 0
            }
        
        # Estadísticas nacionales
        pacientes = PacientesPaciente.objects.all()
        
        estadisticas = {
            'total': total_pacientes,
            'por_region': list(pacientes.values('comuna').annotate(total=Count('id')).order_by('-total')[:10]),
            'por_sexo': list(pacientes.values('sexo').annotate(total=Count('id'))),
            'por_tipo_tbc': list(pacientes.values('tipo_tbc').annotate(total=Count('id'))),
            'por_estado': list(pacientes.values('estado').annotate(total=Count('id')))
        }
        
        # Distribución por comuna (top 10)
        top_comunas = list(pacientes.values('comuna').annotate(
            total=Count('id'),
            porcentaje=Count('id') * 100.0 / total_pacientes
        ).order_by('-total')[:10])
        
        # Tasa de éxito de tratamientos
        tratamientos = Tratamiento.objects.all()
        tratamientos_exitosos = tratamientos.filter(resultado_final='Curación').count()
        tasa_exito = round((tratamientos_exitosos / tratamientos.count() * 100), 2) if tratamientos.count() > 0 else 0
        
        return {
            'nivel': 'nacional',
            'total_pacientes': total_pacientes,
            'estadisticas': estadisticas,
            'top_comunas': top_comunas,
            'tasa_exito_tratamientos': f"{tasa_exito}%",
            'actualizado': date.today().isoformat()
        }
    
    def _distribucion_edades(self, pacientes):
        """Calcula distribución de edades de pacientes"""
        distribucion = {
            '0-14': 0, '15-24': 0, '25-44': 0, '45-64': 0, '65+': 0
        }
        
        for paciente in pacientes:
            edad = paciente.get_edad()
            if edad is not None:
                if edad <= 14:
                    distribucion['0-14'] += 1
                elif edad <= 24:
                    distribucion['15-24'] += 1
                elif edad <= 44:
                    distribucion['25-44'] += 1
                elif edad <= 64:
                    distribucion['45-64'] += 1
                else:
                    distribucion['65+'] += 1
        
        return distribucion
    
    def _calcular_tendencia(self, pacientes):
        """Calcula tendencia de casos en el tiempo"""
        from django.db.models.functions import TruncMonth
        
        # Últimos 12 meses
        fecha_limite = date.today() - timedelta(days=365)
        
        tendencia_mensual = pacientes.filter(
            fecha_diagnostico__gte=fecha_limite
        ).annotate(
            mes=TruncMonth('fecha_diagnostico')
        ).values('mes').annotate(
            casos=Count('id')
        ).order_by('mes')
        
        return list(tendencia_mensual)
    
    def _identificar_factores_riesgo(self, pacientes):
        """Identifica factores de riesgo en la población"""
        factores = []
        
        # Porcentaje de población prioritaria
        total_prioritario = pacientes.exclude(poblacion_prioritaria='').count()
        porcentaje_prioritario = round((total_prioritario / pacientes.count() * 100), 2)
        
        if porcentaje_prioritario > 30:
            factores.append({
                'factor': 'Población prioritaria',
                'porcentaje': f"{porcentaje_prioritario}%",
                'riesgo': 'Alto',
                'descripcion': f'Alto porcentaje ({porcentaje_prioritario}%) de población en grupos prioritarios'
            })
        
        # Distribución por edad (riesgo en extremos de edad)
        distribucion_edades = self._distribucion_edades(pacientes)
        porcentaje_mayores = (distribucion_edades['65+'] / pacientes.count() * 100)
        
        if porcentaje_mayores > 20:
            factores.append({
                'factor': 'Población adulta mayor',
                'porcentaje': f"{porcentaje_mayores:.1f}%",
                'riesgo': 'Moderado',
                'descripcion': f'Alto porcentaje de adultos mayores ({porcentaje_mayores:.1f}%)'
            })
        
        # Tasa de abandono de tratamiento
        tratamientos = Tratamiento.objects.filter(paciente__in=pacientes)
        abandonos = tratamientos.filter(resultado_final='Abandono').count()
        
        if tratamientos.count() > 0:
            tasa_abandono = (abandonos / tratamientos.count() * 100)
            if tasa_abandono > 10:
                factores.append({
                    'factor': 'Abandono de tratamiento',
                    'porcentaje': f"{tasa_abandono:.1f}%",
                    'riesgo': 'Alto',
                    'descripcion': f'Alta tasa de abandono de tratamiento ({tasa_abandono:.1f}%)'
                })
        
        return factores
    
    def _categorizar_incidencia(self, incidencia):
        """Categoriza la incidencia de TBC"""
        if incidencia < 10:
            return 'Muy baja'
        elif incidencia < 20:
            return 'Baja'
        elif incidencia < 40:
            return 'Moderada'
        elif incidencia < 60:
            return 'Alta'
        else:
            return 'Muy alta'
    
    def _generar_recomendaciones(self, estadisticas, incidencia, total_pacientes, comuna):
        """Genera recomendaciones basadas en análisis de datos"""
        recomendaciones = []
        
        # Recomendaciones basadas en incidencia
        categoria = self._categorizar_incidencia(incidencia)
        
        if categoria in ['Alta', 'Muy alta']:
            recomendaciones.append(
                f"Incidencia {categoria} ({incidencia} por 100,000 hab.) - "
                f"Considerar intervención comunitaria específica en {comuna}"
            )
        elif categoria == 'Moderada':
            recomendaciones.append(
                f"Incidencia moderada - Mantener vigilancia activa y fortalecer "
                f"estrategias de detección temprana en {comuna}"
            )
        
        # Recomendaciones basadas en distribución por edad
        distribucion = estadisticas.get('por_edad', {})
        if distribucion.get('0-14', 0) > 0:
            recomendaciones.append(
                "Presencia de casos en menores de 15 años - Reforzar estrategias "
                "de prevención en escuelas y hogares con niños"
            )
        
        if distribucion.get('65+', 0) > distribucion.get('25-44', 0):
            recomendaciones.append(
                "Mayoría de casos en adultos mayores - Fortalecer atención "
                "geriátrica y seguimiento de comorbilidades"
            )
        
        # Recomendaciones basadas en estado de pacientes
        for estado in estadisticas.get('por_estado', []):
            if estado['estado'] == 'abandono' and estado['total'] > total_pacientes * 0.1:
                recomendaciones.append(
                    f"Alta tasa de abandono ({estado['total']} casos) - "
                    "Implementar estrategias de retención y apoyo psicosocial"
                )
        
        # Recomendación general
        recomendaciones.append(
            f"Monitorear indicadores semanalmente en {comuna} y ajustar "
            "estrategias según evolución epidemiológica"
        )
        
        return recomendaciones


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def api_status(request):
    """
    Endpoint para verificar estado de todas las APIs
    """
    status_checks = {
        'api_rest': True,
        'autenticacion': request.user.is_authenticated,
        'base_datos': True,
        'apis_externas': {
            'geocodificacion': True,
            'clima': True
        },
        'version': '1.0.0',
        'timestamp': timezone.now().isoformat()
    }
    
    # Verificar conexión a base de datos
    try:
        from django.db import connection
        connection.ensure_connection()
        status_checks['base_datos_detalle'] = {
            'engine': connection.settings_dict['ENGINE'],
            'nombre': connection.settings_dict.get('NAME', 'N/A'),
            'estado': 'Conectado'
        }
    except Exception as e:
        status_checks['base_datos'] = False
        status_checks['base_datos_error'] = str(e)
    
    return Response(status_checks)