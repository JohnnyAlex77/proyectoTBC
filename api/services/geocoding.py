"""
api/services/geocoding.py
Servicio de geocodificación para el Sistema TBC
Convierte direcciones en coordenadas geográficas usando API externa
Implementa cache para mejorar performance y reducir llamadas API
"""
import requests
import json
import time
from django.core.cache import cache
from django.conf import settings
from rest_framework.exceptions import APIException
from typing import Dict, Optional, Tuple
import logging

# Configurar logger
logger = logging.getLogger('api.external')

class GeocodingService:
    """
    Servicio para geocodificación de direcciones usando Nominatim (OpenStreetMap)
    Proporciona caché inteligente y manejo de errores robusto
    """
    
    # Configuración
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    REVERSE_URL = "https://nominatim.openstreetmap.org/reverse"
    CACHE_TIMEOUT = 86400  # 24 horas en segundos
    CACHE_KEY_PREFIX = "geocoding_"
    
    # Headers para cumplir con TOS de Nominatim
    DEFAULT_HEADERS = {
        'User-Agent': getattr(settings, 'NOMINATIM_USER_AGENT', 
                             'SistemaTBC/1.0 (contacto@sistematbc.cl)'),
        'Accept': 'application/json',
        'Accept-Language': 'es',
    }
    
    @classmethod
    def geocodificar(cls, direccion: str, comuna: str = None, 
                     ciudad: str = None, pais: str = "Chile") -> Dict:
        """
        Geocodifica una dirección a coordenadas geográficas
        
        Args:
            direccion: Dirección completa o parcial
            comuna: Comuna (opcional)
            ciudad: Ciudad (opcional)
            pais: País (default: Chile)
            
        Returns:
            Dict con información de geocodificación
            
        Raises:
            APIException: Si hay error en la geocodificación
        """
        # Limpiar y validar parámetros
        direccion = direccion.strip()
        if not direccion:
            raise ValueError("La dirección no puede estar vacía")
        
        # Crear clave de caché única
        cache_key = f"{cls.CACHE_KEY_PREFIX}{direccion}_{comuna}_{ciudad}_{pais}".lower().replace(" ", "_")
        
        # Intentar obtener del caché primero
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Geocodificación desde caché: {direccion}")
            cached_result['cache'] = True
            return cached_result
        
        try:
            # Construir consulta para API
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
            
            # Parámetros para la consulta
            params = {
                'q': query,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'cl',
                'addressdetails': 1,
                'accept-language': 'es',
            }
            
            logger.info(f"Solicitando geocodificación para: {query}")
            
            # Realizar consulta a API con timeout
            response = requests.get(
                cls.BASE_URL,
                params=params,
                headers=cls.DEFAULT_HEADERS,
                timeout=10
            )
            
            # Manejar respuesta
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    result = cls._procesar_respuesta_exitosa(data[0], query)
                else:
                    # No se encontraron resultados
                    result = cls._procesar_respuesta_fallida(query, comuna, ciudad, pais)
                
            elif response.status_code == 429:
                # Rate limit excedido
                logger.warning("Rate limit excedido en geocodificación, usando caché/fallback")
                result = cls._obtener_resultado_fallback(direccion, comuna, ciudad, pais)
                
            else:
                # Otro error HTTP
                logger.error(f"Error HTTP {response.status_code} en geocodificación")
                result = cls._procesar_respuesta_fallida(query, comuna, ciudad, pais)
            
            # Guardar en caché (incluso resultados fallidos por menos tiempo)
            cache_timeout = cls.CACHE_TIMEOUT if result.get('exitoso', False) else 3600  # 1 hora para fallos
            cache.set(cache_key, result, cache_timeout)
            
            # Añadir metadata
            result['cache_key'] = cache_key
            result['timestamp'] = time.time()
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Timeout en geocodificación")
            result = cls._procesar_respuesta_fallida(direccion, comuna, ciudad, pais, 
                                                     error="Timeout en la conexión")
            cache.set(cache_key, result, 300)  # 5 minutos para timeouts
            return result
            
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión en geocodificación")
            result = cls._procesar_respuesta_fallida(direccion, comuna, ciudad, pais,
                                                     error="Error de conexión")
            cache.set(cache_key, result, 300)
            return result
            
        except Exception as e:
            logger.error(f"Error inesperado en geocodificación: {str(e)}")
            raise APIException(f"Error en geocodificación: {str(e)}")
    
    @classmethod
    def geocodificar_inversa(cls, latitud: float, longitud: float) -> Dict:
        """
        Geocodificación inversa: convierte coordenadas en dirección
        
        Args:
            latitud: Latitud en grados decimales
            longitud: Longitud en grados decimales
            
        Returns:
            Dict con información de dirección
        """
        cache_key = f"{cls.CACHE_KEY_PREFIX}reverse_{latitud}_{longitud}"
        
        # Verificar caché
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'lat': latitud,
                'lon': longitud,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'es',
                'zoom': 18,  # Nivel de detalle (10-18)
            }
            
            response = requests.get(
                cls.REVERSE_URL,
                params=params,
                headers=cls.DEFAULT_HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = {
                    'exitoso': True,
                    'direccion': data.get('display_name', ''),
                    'latitud': latitud,
                    'longitud': longitud,
                    'detalles': data.get('address', {}),
                    'tipo': data.get('type', 'unknown'),
                    'clase': data.get('class', ''),
                    'fuente': 'OpenStreetMap (Nominatim)',
                    'timestamp': time.time(),
                }
            else:
                result = {
                    'exitoso': False,
                    'latitud': latitud,
                    'longitud': longitud,
                    'error': f"Error HTTP {response.status_code}",
                    'fuente': 'reverse_geocoding',
                    'timestamp': time.time(),
                }
            
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result
            
        except Exception as e:
            logger.error(f"Error en geocodificación inversa: {str(e)}")
            return {
                'exitoso': False,
                'latitud': latitud,
                'longitud': longitud,
                'error': str(e),
                'fuente': 'reverse_geocoding_error',
                'timestamp': time.time(),
            }
    
    @staticmethod
    def _procesar_respuesta_exitosa(data: Dict, query: str) -> Dict:
        """Procesa una respuesta exitosa de la API"""
        # Calcular exactitud basada en el tipo de resultado
        exactitud = GeocodingService._calcular_exactitud(data)
        
        # Extraer detalles de dirección
        address = data.get('address', {})
        
        result = {
            'exitoso': True,
            'direccion': data.get('display_name', query),
            'latitud': float(data.get('lat', 0)),
            'longitud': float(data.get('lon', 0)),
            'exactitud': exactitud,
            'tipo': data.get('type', 'unknown'),
            'importancia': float(data.get('importance', 0)),
            'fuente': 'OpenStreetMap (Nominatim)',
            'detalles': {
                'comuna': address.get('city', address.get('town', address.get('municipality', ''))),
                'region': address.get('state', address.get('county', '')),
                'pais': address.get('country', 'Chile'),
                'codigo_postal': address.get('postcode', ''),
                'barrio': address.get('neighbourhood', ''),
                'calle': address.get('road', ''),
                'numero': address.get('house_number', ''),
            },
            'raw_data': data if settings.DEBUG else None,  # Solo en desarrollo
        }
        
        # Añadir categorización
        result['categoria'] = GeocodingService._categorizar_resultado(data)
        
        return result
    
    @staticmethod
    def _procesar_respuesta_fallida(query: str, comuna: str = None, 
                                   ciudad: str = None, pais: str = "Chile",
                                   error: str = None) -> Dict:
        """Procesa una respuesta fallida de la API"""
        # Coordenadas por defecto basadas en la comuna/ciudad
        default_coords = GeocodingService._obtener_coordenadas_por_defecto(comuna, ciudad)
        
        result = {
            'exitoso': False,
            'direccion': query,
            'latitud': default_coords['latitud'],
            'longitud': default_coords['longitud'],
            'exactitud': 0.3,  # Baja exactitud para fallback
            'fuente': 'fallback',
            'modo': 'aproximado',
            'detalles': {
                'comuna': comuna or ciudad or '',
                'region': GeocodingService._obtener_region_por_comuna(comuna),
                'pais': pais,
                'nota': 'Geocodificación aproximada - verificar dirección manualmente',
            },
            'error': error or 'No se pudo geocodificar la dirección',
            'timestamp': time.time(),
        }
        
        return result
    
    @staticmethod
    def _obtener_resultado_fallback(direccion: str, comuna: str = None,
                                   ciudad: str = None, pais: str = "Chile") -> Dict:
        """Obtiene resultado de fallback cuando la API falla"""
        # Primero intentar con coordenadas por defecto
        result = GeocodingService._procesar_respuesta_fallida(direccion, comuna, ciudad, pais)
        
        # Añadir sugerencia para el usuario
        result['sugerencia'] = (
            "Verifique la dirección y reintente. "
            "Si el problema persiste, contacte al administrador."
        )
        
        return result
    
    @staticmethod
    def _calcular_exactitud(data: Dict) -> float:
        """Calcula la exactitud de la geocodificación basada en los datos"""
        exactitud = 0.5  # Valor base
        
        # Ajustar según tipo de resultado
        tipo = data.get('type', '')
        if tipo in ['house', 'building', 'apartment']:
            exactitud = 0.95  # Muy exacto (edificio específico)
        elif tipo in ['street', 'road', 'footway']:
            exactitud = 0.85  # Calle específica
        elif tipo in ['city', 'town', 'village', 'municipality']:
            exactitud = 0.7   # Ciudad/comuna
        elif tipo in ['state', 'county', 'region']:
            exactitud = 0.5   # Región
        elif tipo == 'country':
            exactitud = 0.3   # País
        
        # Ajustar según importancia (0-1 scale)
        importancia = float(data.get('importance', 0))
        if importancia > 0:
            exactitud = min(exactitud + (importancia * 0.2), 0.99)
        
        # Ajustar según otros factores
        address = data.get('address', {})
        if address.get('house_number'):
            exactitud = min(exactitud + 0.05, 0.99)
        if address.get('postcode'):
            exactitud = min(exactitud + 0.03, 0.99)
        
        return round(exactitud, 2)
    
    @staticmethod
    def _categorizar_resultado(data: Dict) -> str:
        """Categoriza el resultado de geocodificación"""
        tipo = data.get('type', '')
        
        categorias = {
            'house': 'edificio',
            'building': 'edificio',
            'apartment': 'edificio',
            'street': 'calle',
            'road': 'calle',
            'footway': 'calle',
            'city': 'ciudad',
            'town': 'ciudad',
            'village': 'pueblo',
            'municipality': 'municipio',
            'state': 'region',
            'county': 'region',
            'country': 'pais',
        }
        
        return categorias.get(tipo, 'desconocido')
    
    @staticmethod
    def _obtener_coordenadas_por_defecto(comuna: str = None, ciudad: str = None) -> Dict:
        """Obtiene coordenadas por defecto basadas en comuna/ciudad"""
        # Base de datos de coordenadas por comuna/ciudad en Chile
        coordenadas_chile = {
            # Región Metropolitana
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
            
            # Otras regiones
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
        
        # Buscar por comuna o ciudad
        lugar = (comuna or ciudad or '').lower().strip()
        
        if lugar in coordenadas_chile:
            return coordenadas_chile[lugar]
        
        # Si no se encuentra, usar Santiago como default
        return {'latitud': -33.4489, 'longitud': -70.6693}
    
    @staticmethod
    def _obtener_region_por_comuna(comuna: str = None) -> str:
        """Obtiene la región basada en la comuna"""
        if not comuna:
            return "Región Metropolitana"
        
        # Mapeo de comunas a regiones (simplificado)
        regiones = {
            'santiago': 'Región Metropolitana',
            'puente alto': 'Región Metropolitana',
            'maipú': 'Región Metropolitana',
            'la florida': 'Región Metropolitana',
            'las condes': 'Región Metropolitana',
            'ñuñoa': 'Región Metropolitana',
            'san bernardo': 'Región Metropolitana',
            'peñalolén': 'Región Metropolitana',
            'el bosque': 'Región Metropolitana',
            'la pintana': 'Región Metropolitana',
            'valparaíso': 'Región de Valparaíso',
            'viña del mar': 'Región de Valparaíso',
            'concepción': 'Región del Biobío',
            'temuco': 'Región de La Araucanía',
            'antofagasta': 'Región de Antofagasta',
            'iquique': 'Región de Tarapacá',
            'arica': 'Región de Arica y Parinacota',
            'puerto montt': 'Región de Los Lagos',
            'punta arenas': 'Región de Magallanes',
        }
        
        comuna_lower = comuna.lower().strip()
        return regiones.get(comuna_lower, "Región Metropolitana")
    
    @classmethod
    def validar_coordenadas(cls, latitud: float, longitud: float) -> Tuple[bool, str]:
        """
        Valida que las coordenadas sean válidas para Chile
        
        Args:
            latitud: Latitud a validar
            longitud: Longitud a validar
            
        Returns:
            Tuple (es_valido, mensaje_error)
        """
        # Rango válido para Chile aprox.
        CHILE_LAT_MIN = -56.0
        CHILE_LAT_MAX = -17.0
        CHILE_LON_MIN = -76.0
        CHILE_LON_MAX = -66.0
        
        mensajes_error = []
        
        if not (-90 <= latitud <= 90):
            mensajes_error.append("Latitud fuera de rango válido (-90 a 90)")
        elif not (CHILE_LAT_MIN <= latitud <= CHILE_LAT_MAX):
            mensajes_error.append(f"Latitud fuera de Chile ({CHILE_LAT_MIN} a {CHILE_LAT_MAX})")
        
        if not (-180 <= longitud <= 180):
            mensajes_error.append("Longitud fuera de rango válido (-180 a 180)")
        elif not (CHILE_LON_MIN <= longitud <= CHILE_LON_MAX):
            mensajes_error.append(f"Longitud fuera de Chile ({CHILE_LON_MIN} a {CHILE_LON_MAX})")
        
        if mensajes_error:
            return False, "; ".join(mensajes_error)
        
        return True, "Coordenadas válidas"


# Función de conveniencia para uso rápido
def geocodificar_direccion(direccion: str, comuna: str = None, **kwargs) -> Dict:
    """
    Función de conveniencia para geocodificar una dirección
    
    Args:
        direccion: Dirección a geocodificar
        comuna: Comuna (opcional)
        **kwargs: Otros parámetros para GeocodingService.geocodificar
        
    Returns:
        Dict con resultado de geocodificación
    """
    return GeocodingService.geocodificar(direccion, comuna=comuna, **kwargs)


def geocodificar_inversa(latitud: float, longitud: float) -> Dict:
    """
    Función de conveniencia para geocodificación inversa
    
    Args:
        latitud: Latitud
        longitud: Longitud
        
    Returns:
        Dict con dirección correspondiente
    """
    return GeocodingService.geocodificar_inversa(latitud, longitud)