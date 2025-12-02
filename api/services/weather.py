"""
api/services/weather.py
Servicio de clima para el Sistema TBC
Obtiene condiciones climáticas actuales usando API externa
Soporta modo demo para desarrollo sin API key
"""
import requests
import json
import time
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings
from rest_framework.exceptions import APIException
from typing import Dict, Optional
import logging

# Configurar logger
logger = logging.getLogger('api.external')

class WeatherService:
    """
    Servicio para obtener datos climáticos usando OpenWeatherMap API
    Implementa caché, manejo de errores y modo demo
    """
    
    # Configuración
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
    CACHE_TIMEOUT = 1800  # 30 minutos en segundos
    CACHE_KEY_PREFIX = "weather_"
    
    # Headers para requests
    DEFAULT_HEADERS = {
        'User-Agent': 'SistemaTBC/1.0 (contacto@sistematbc.cl)',
        'Accept': 'application/json',
    }
    
    # Iconos de clima mapeados a Font Awesome
    WEATHER_ICONS = {
        '01d': 'fas fa-sun',           # clear sky day
        '01n': 'fas fa-moon',          # clear sky night
        '02d': 'fas fa-cloud-sun',     # few clouds day
        '02n': 'fas fa-cloud-moon',    # few clouds night
        '03d': 'fas fa-cloud',         # scattered clouds
        '03n': 'fas fa-cloud',
        '04d': 'fas fa-cloud',         # broken clouds
        '04n': 'fas fa-cloud',
        '09d': 'fas fa-cloud-rain',    # shower rain
        '09n': 'fas fa-cloud-rain',
        '10d': 'fas fa-cloud-sun-rain', # rain day
        '10n': 'fas fa-cloud-moon-rain', # rain night
        '11d': 'fas fa-bolt',          # thunderstorm
        '11n': 'fas fa-bolt',
        '13d': 'fas fa-snowflake',     # snow
        '13n': 'fas fa-snowflake',
        '50d': 'fas fa-smog',          # mist
        '50n': 'fas fa-smog',
    }
    
    @classmethod
    def obtener_clima(cls, ciudad: str, pais: str = "CL", 
                     modo_demo: Optional[bool] = None) -> Dict:
        """
        Obtiene condiciones climáticas actuales para una ciudad
        
        Args:
            ciudad: Nombre de la ciudad
            pais: Código de país (default: CL para Chile)
            modo_demo: Forzar modo demo (None = auto-detect)
            
        Returns:
            Dict con datos climáticos
            
        Raises:
            APIException: Si hay error y no hay modo demo
        """
        # Determinar si usar modo demo
        if modo_demo is None:
            modo_demo = getattr(settings, 'API_DEMO_MODE', False) or not cls._tiene_api_key()
        
        if modo_demo:
            logger.info(f"Usando modo demo para clima: {ciudad}")
            return cls._datos_demo(ciudad)
        
        # Crear clave de caché
        cache_key = f"{cls.CACHE_KEY_PREFIX}{ciudad}_{pais}".lower().replace(" ", "_")
        
        # Verificar caché primero
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Clima desde caché: {ciudad}")
            cached_result['cache'] = True
            cached_result['actualizado_cache'] = cached_result.get('timestamp', 0)
            cached_result['timestamp'] = time.time()
            return cached_result
        
        try:
            # Construir parámetros para API
            params = {
                'q': f"{ciudad},{pais}",
                'appid': cls._obtener_api_key(),
                'units': 'metric',  # Celsius
                'lang': 'es',
            }
            
            logger.info(f"Solicitando clima para: {ciudad}, {pais}")
            
            # Realizar request a API
            response = requests.get(
                cls.BASE_URL,
                params=params,
                headers=cls.DEFAULT_HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = cls._procesar_respuesta_exitosa(data)
                
            elif response.status_code == 401:
                # API key inválida
                logger.error("API key de OpenWeatherMap inválida o expirada")
                result = cls._datos_demo(ciudad)
                result['error'] = "API key inválida, usando datos demo"
                
            elif response.status_code == 404:
                # Ciudad no encontrada
                logger.warning(f"Ciudad no encontrada: {ciudad}")
                result = cls._datos_demo(ciudad)
                result['error'] = "Ciudad no encontrada, usando datos demo"
                
            elif response.status_code == 429:
                # Rate limit excedido
                logger.warning("Rate limit excedido en OpenWeatherMap")
                result = cls._datos_demo(ciudad)
                result['error'] = "Rate limit excedido, usando datos demo"
                
            else:
                # Otro error HTTP
                logger.error(f"Error HTTP {response.status_code} en clima")
                result = cls._datos_demo(ciudad)
                result['error'] = f"Error HTTP {response.status_code}, usando datos demo"
            
            # Guardar en caché
            cache_timeout = cls.CACHE_TIMEOUT if result.get('exitoso', False) else 600  # 10 min para errores
            cache.set(cache_key, result, cache_timeout)
            
            # Añadir metadata
            result['cache_key'] = cache_key
            result['timestamp'] = time.time()
            result['modo'] = 'real' if result.get('exitoso') else 'demo_fallback'
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Timeout obteniendo clima")
            result = cls._datos_demo(ciudad)
            result['error'] = "Timeout en conexión, usando datos demo"
            cache.set(cache_key, result, 300)  # 5 min para timeouts
            return result
            
        except requests.exceptions.ConnectionError:
            logger.error("Error de conexión obteniendo clima")
            result = cls._datos_demo(ciudad)
            result['error'] = "Error de conexión, usando datos demo"
            cache.set(cache_key, result, 300)
            return result
            
        except Exception as e:
            logger.error(f"Error inesperado obteniendo clima: {str(e)}")
            result = cls._datos_demo(ciudad)
            result['error'] = f"Error: {str(e)}, usando datos demo"
            return result
    
    @classmethod
    def obtener_pronostico(cls, ciudad: str, pais: str = "CL", 
                          dias: int = 3, modo_demo: Optional[bool] = None) -> Dict:
        """
        Obtiene pronóstico para varios días
        
        Args:
            ciudad: Nombre de la ciudad
            pais: Código de país
            dias: Número de días de pronóstico (1-5)
            modo_demo: Forzar modo demo
            
        Returns:
            Dict con pronóstico
        """
        # Limitar días a 5 (máximo de API free)
        dias = max(1, min(dias, 5))
        
        if modo_demo is None:
            modo_demo = getattr(settings, 'API_DEMO_MODE', False) or not cls._tiene_api_key()
        
        if modo_demo:
            return cls._pronostico_demo(ciudad, dias)
        
        cache_key = f"{cls.CACHE_KEY_PREFIX}forecast_{ciudad}_{pais}_{dias}"
        
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            params = {
                'q': f"{ciudad},{pais}",
                'appid': cls._obtener_api_key(),
                'units': 'metric',
                'lang': 'es',
                'cnt': dias * 8,  # 8 mediciones por día
            }
            
            response = requests.get(
                cls.FORECAST_URL,
                params=params,
                headers=cls.DEFAULT_HEADERS,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                result = cls._procesar_pronostico_exitoso(data, dias)
            else:
                result = cls._pronostico_demo(ciudad, dias)
                result['error'] = f"Error {response.status_code}, usando demo"
            
            cache.set(cache_key, result, cls.CACHE_TIMEOUT)
            return result
            
        except Exception as e:
            logger.error(f"Error en pronóstico: {str(e)}")
            return cls._pronostico_demo(ciudad, dias)
    
    @staticmethod
    def _procesar_respuesta_exitosa(data: Dict) -> Dict:
        """Procesa respuesta exitosa de OpenWeatherMap"""
        # Extraer datos principales
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        wind = data.get('wind', {})
        clouds = data.get('clouds', {})
        sys = data.get('sys', {})
        
        # Calcular calidad del aire (índice simplificado)
        calidad_aire = WeatherService._calcular_calidad_aire(main, wind, clouds)
        
        # Obtener icono Font Awesome
        icon_code = weather.get('icon', '01d')
        icono_fa = WeatherService.WEATHER_ICONS.get(icon_code, 'fas fa-question')
        
        # Crear resultado
        result = {
            'exitoso': True,
            'ciudad': data.get('name', 'Desconocido'),
            'pais': sys.get('country', 'CL'),
            'temperatura': round(main.get('temp', 0), 1),
            'sensacion_termica': round(main.get('feels_like', 0), 1),
            'temperatura_min': round(main.get('temp_min', 0), 1),
            'temperatura_max': round(main.get('temp_max', 0), 1),
            'humedad': main.get('humidity', 0),
            'presion': main.get('pressure', 0),
            'descripcion': weather.get('description', '').capitalize(),
            'condicion_principal': weather.get('main', 'Clear'),
            'icono': icon_code,
            'icono_fontawesome': icono_fa,
            'viento_velocidad': round(wind.get('speed', 0) * 3.6, 1),  # m/s a km/h
            'viento_direccion': wind.get('deg', 0),
            'viento_rafaga': round(wind.get('gust', 0) * 3.6, 1),
            'visibilidad': data.get('visibility', 0) / 1000,  # metros a km
            'nubosidad': clouds.get('all', 0),
            'amanecer': sys.get('sunrise', 0),
            'atardecer': sys.get('sunset', 0),
            'calidad_aire': calidad_aire['nivel'],
            'indice_calidad_aire': calidad_aire['indice'],
            'recomendacion_salud': calidad_aire['recomendacion'],
            'coordenadas': data.get('coord', {}),
            'fuente': 'OpenWeatherMap',
            'unidades': {
                'temperatura': '°C',
                'viento': 'km/h',
                'presion': 'hPa',
                'visibilidad': 'km',
            },
            'timestamp_api': data.get('dt', 0),
        }
        
        # Añadir información temporal
        result['hora_local'] = time.strftime('%H:%M', time.localtime())
        result['fecha'] = datetime.now().strftime('%Y-%m-%d')
        
        # Añadir condiciones especiales
        result['condiciones_especiales'] = WeatherService._detectar_condiciones_especiales(
            result['condicion_principal'], result['temperatura'], result['humedad']
        )
        
        return result
    
    @staticmethod
    def _procesar_pronostico_exitoso(data: Dict, dias: int) -> Dict:
        """Procesa pronóstico exitoso"""
        pronostico_diario = []
        
        # Agrupar por día
        pronostico_por_dia = {}
        for item in data.get('list', []):
            fecha = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
            if fecha not in pronostico_por_dia:
                pronostico_por_dia[fecha] = {
                    'temperaturas': [],
                    'condiciones': [],
                    'fecha': fecha,
                }
            
            main = item.get('main', {})
            weather = item.get('weather', [{}])[0]
            
            pronostico_por_dia[fecha]['temperaturas'].append(main.get('temp', 0))
            pronostico_por_dia[fecha]['condiciones'].append(weather.get('main', 'Clear'))
        
        # Procesar cada día
        hoy = datetime.now().strftime('%Y-%m-%d')
        for i, (fecha, datos) in enumerate(list(pronostico_por_dia.items())[:dias]):
            if fecha == hoy:
                continue  # Saltar hoy si ya tenemos datos actuales
            
            temps = datos['temperaturas']
            condicion_principal = max(set(datos['condiciones']), key=datos['condiciones'].count)
            
            pronostico_diario.append({
                'dia': i + 1,
                'fecha': fecha,
                'temperatura_min': round(min(temps), 1),
                'temperatura_max': round(max(temps), 1),
                'temperatura_promedio': round(sum(temps) / len(temps), 1),
                'condicion_principal': condicion_principal,
                'descripcion': f"Pronóstico para {fecha}",
            })
        
        return {
            'exitoso': True,
            'ciudad': data.get('city', {}).get('name', ''),
            'pais': data.get('city', {}).get('country', 'CL'),
            'dias_pronostico': dias,
            'pronostico': pronostico_diario,
            'fuente': 'OpenWeatherMap',
            'timestamp': time.time(),
        }
    
    @staticmethod
    def _datos_demo(ciudad: str) -> Dict:
        """Genera datos demo para desarrollo"""
        # Datos basados en ciudad y época del año (simulado)
        datos_por_ciudad = {
            'santiago': {
                'temp_base': 22.5,
                'humedad_base': 45,
                'variacion_temp': 8,
                'condicion': 'Despejado',
                'icono': '01d',
            },
            'puente alto': {
                'temp_base': 20.8,
                'humedad_base': 55,
                'variacion_temp': 7,
                'condicion': 'Parcialmente nublado',
                'icono': '02d',
            },
            'maipú': {
                'temp_base': 21.2,
                'humedad_base': 50,
                'variacion_temp': 6,
                'condicion': 'Despejado',
                'icono': '01d',
            },
            'la florida': {
                'temp_base': 21.8,
                'humedad_base': 52,
                'variacion_temp': 7,
                'condicion': 'Parcialmente nublado',
                'icono': '02d',
            },
            'ñuñoa': {
                'temp_base': 22.1,
                'humedad_base': 48,
                'variacion_temp': 6,
                'condicion': 'Despejado',
                'icono': '01d',
            },
            'valparaíso': {
                'temp_base': 18.5,
                'humedad_base': 70,
                'variacion_temp': 5,
                'condicion': 'Nublado',
                'icono': '04d',
            },
            'concepción': {
                'temp_base': 16.8,
                'humedad_base': 75,
                'variacion_temp': 4,
                'condicion': 'Lluvia ligera',
                'icono': '10d',
            },
            'temuco': {
                'temp_base': 15.2,
                'humedad_base': 65,
                'variacion_temp': 6,
                'condicion': 'Nublado',
                'icono': '04d',
            },
            'antofagasta': {
                'temp_base': 24.5,
                'humedad_base': 35,
                'variacion_temp': 8,
                'condicion': 'Despejado',
                'icono': '01d',
            },
            'iquique': {
                'temp_base': 26.2,
                'humedad_base': 30,
                'variacion_temp': 7,
                'condicion': 'Despejado',
                'icono': '01d',
            },
        }
        
        ciudad_lower = ciudad.lower().strip()
        ciudad_data = datos_por_ciudad.get(ciudad_lower, {
            'temp_base': 20.0,
            'humedad_base': 50,
            'variacion_temp': 5,
            'condicion': 'Despejado',
            'icono': '01d',
        })
        
        # Variación por hora del día
        hora_actual = datetime.now().hour
        if 6 <= hora_actual < 12:
            variacion_hora = 2  # Mañana fresca
        elif 12 <= hora_actual < 18:
            variacion_hora = 4  # Tarde más caliente
        elif 18 <= hora_actual < 22:
            variacion_hora = 1  # Atardecer
        else:
            variacion_hora = -3  # Noche fría
        
        temp_actual = ciudad_data['temp_base'] + variacion_hora
        icono = ciudad_data['icono'] if 6 <= hora_actual < 20 else ciudad_data['icono'].replace('d', 'n')
        
        # Calcular calidad del aire demo
        calidad_demo = WeatherService._calcular_calidad_aire_demo(temp_actual, ciudad_data['humedad_base'])
        
        return {
            'exitoso': True,
            'ciudad': ciudad.title(),
            'pais': 'CL',
            'temperatura': round(temp_actual, 1),
            'sensacion_termica': round(temp_actual - 1.2, 1),
            'temperatura_min': round(ciudad_data['temp_base'] - ciudad_data['variacion_temp'], 1),
            'temperatura_max': round(ciudad_data['temp_base'] + ciudad_data['variacion_temp'], 1),
            'humedad': ciudad_data['humedad_base'],
            'presion': 1013,
            'descripcion': ciudad_data['condicion'],
            'condicion_principal': ciudad_data['condicion'].split()[0],
            'icono': icono,
            'icono_fontawesome': WeatherService.WEATHER_ICONS.get(icono, 'fas fa-question'),
            'viento_velocidad': round(3.1 + (hora_actual / 10), 1),
            'viento_direccion': 180,
            'visibilidad': 10,
            'nubosidad': 10 if 'nublado' in ciudad_data['condicion'].lower() else 0,
            'amanecer': 1678956000,
            'atardecer': 1678999200,
            'calidad_aire': calidad_demo['nivel'],
            'indice_calidad_aire': calidad_demo['indice'],
            'recomendacion_salud': calidad_demo['recomendacion'],
            'coordenadas': {'lat': -33.4489, 'lon': -70.6693},
            'fuente': 'demo',
            'modo': 'demo',
            'unidades': {
                'temperatura': '°C',
                'viento': 'km/h',
                'presion': 'hPa',
                'visibilidad': 'km',
            },
            'condiciones_especiales': [],
            'timestamp': time.time(),
            'hora_local': datetime.now().strftime('%H:%M'),
            'fecha': datetime.now().strftime('%Y-%m-%d'),
        }
    
    @staticmethod
    def _pronostico_demo(ciudad: str, dias: int) -> Dict:
        """Genera pronóstico demo"""
        pronostico = []
        hoy = datetime.now()
        
        datos_ciudad = WeatherService._datos_demo(ciudad)
        temp_base = datos_ciudad['temperatura']
        
        for i in range(1, dias + 1):
            fecha = (hoy + timedelta(days=i)).strftime('%Y-%m-%d')
            
            # Variar temperatura un poco cada día
            variacion = (i * 2) - (dias)
            temp_dia = temp_base + variacion
            
            # Condiciones alternadas
            condiciones = ['Despejado', 'Parcialmente nublado', 'Nublado', 'Lluvia ligera']
            condicion = condiciones[i % len(condiciones)]
            
            pronostico.append({
                'dia': i,
                'fecha': fecha,
                'temperatura_min': round(temp_dia - 3, 1),
                'temperatura_max': round(temp_dia + 3, 1),
                'temperatura_promedio': round(temp_dia, 1),
                'condicion_principal': condicion,
                'descripcion': f"{condicion} en {ciudad}",
            })
        
        return {
            'exitoso': True,
            'ciudad': ciudad.title(),
            'pais': 'CL',
            'dias_pronostico': dias,
            'pronostico': pronostico,
            'fuente': 'demo',
            'modo': 'demo',
            'timestamp': time.time(),
        }
    
    @staticmethod
    def _calcular_calidad_aire(main: Dict, wind: Dict, clouds: Dict) -> Dict:
        """Calcula calidad del aire basada en datos climáticos"""
        temperatura = main.get('temp', 20)
        humedad = main.get('humidity', 50)
        viento = wind.get('speed', 0) * 3.6  # m/s a km/h
        nubosidad = clouds.get('all', 0)
        
        # Puntuación base (0-100)
        puntuacion = 75
        
        # Ajustes por temperatura (óptimo 18-24°C)
        if temperatura < 10 or temperatura > 30:
            puntuacion -= 20
        elif 18 <= temperatura <= 24:
            puntuacion += 10
        
        # Ajustes por humedad (óptimo 40-60%)
        if humedad < 30 or humedad > 80:
            puntuacion -= 15
        elif 40 <= humedad <= 60:
            puntuacion += 10
        
        # Ajustes por viento (algo de viento es bueno)
        if viento < 1:
            puntuacion -= 5  # Aire estancado
        elif viento > 20:
            puntuacion -= 10  # Mucho viento puede levantar polvo
        
        # Ajustes por nubosidad (nubes pueden atrapar contaminantes)
        if nubosidad > 80:
            puntuacion -= 5
        
        # Limitar rango
        puntuacion = max(0, min(100, puntuacion))
        
        # Determinar nivel
        if puntuacion >= 80:
            nivel = "Excelente"
            recomendacion = "Condiciones ideales para actividades al aire libre"
        elif puntuacion >= 60:
            nivel = "Buena"
            recomendacion = "Buenas condiciones para la mayoría de actividades"
        elif puntuacion >= 40:
            nivel = "Moderada"
            recomendacion = "Personas sensibles deben considerar reducir actividades prolongadas al aire libre"
        elif puntuacion >= 20:
            nivel = "Pobre"
            recomendacion = "Evitar actividades prolongadas al aire libre, especialmente personas con problemas respiratorios"
        else:
            nivel = "Muy pobre"
            recomendacion = "Evitar actividades al aire libre. Personas con problemas respiratorios deben permanecer en interiores"
        
        return {
            'nivel': nivel,
            'indice': puntuacion,
            'recomendacion': recomendacion,
        }
    
    @staticmethod
    def _calcular_calidad_aire_demo(temperatura: float, humedad: float) -> Dict:
        """Calcula calidad del aire demo"""
        # Simulación simple basada en temperatura y humedad
        if 18 <= temperatura <= 24 and 40 <= humedad <= 60:
            return {
                'nivel': 'Excelente',
                'indice': 85,
                'recomendacion': 'Condiciones ideales para actividades al aire libre',
            }
        elif 15 <= temperatura <= 28 and 30 <= humedad <= 70:
            return {
                'nivel': 'Buena',
                'indice': 70,
                'recomendacion': 'Buenas condiciones para la mayoría de actividades',
            }
        else:
            return {
                'nivel': 'Moderada',
                'indice': 45,
                'recomendacion': 'Personas sensibles deben considerar reducir actividades al aire libre',
            }
    
    @staticmethod
    def _detectar_condiciones_especiales(condicion: str, temperatura: float, humedad: float) -> list:
        """Detecta condiciones climáticas especiales que pueden afectar la salud"""
        condiciones_especiales = []
        
        # Condiciones de frío extremo
        if temperatura < 10:
            condiciones_especiales.append({
                'tipo': 'frio_extremo',
                'nivel': 'alta' if temperatura < 5 else 'moderada',
                'mensaje': 'Temperaturas bajas pueden aumentar el riesgo de enfermedades respiratorias',
                'recomendacion': 'Abrigarse adecuadamente y evitar exposición prolongada al frío',
            })
        
        # Condiciones de calor extremo
        elif temperatura > 30:
            condiciones_especiales.append({
                'tipo': 'calor_extremo',
                'nivel': 'alta' if temperatura > 35 else 'moderada',
                'mensaje': 'Temperaturas altas pueden causar deshidratación y afectar medicamentos',
                'recomendacion': 'Mantenerse hidratado y evitar exposición directa al sol en horas peak',
            })
        
        # Alta humedad
        if humedad > 80:
            condiciones_especiales.append({
                'tipo': 'alta_humedad',
                'nivel': 'moderada',
                'mensaje': 'Alta humedad puede dificultar la respiración y favorecer el crecimiento de hongos',
                'recomendacion': 'Mantener ambientes ventilados y controlar humedad en interiores',
            })
        
        # Baja humedad
        elif humedad < 30:
            condiciones_especiales.append({
                'tipo': 'baja_humedad',
                'nivel': 'moderada',
                'mensaje': 'Baja humedad puede irritar vías respiratorias y piel',
                'recomendacion': 'Usar humidificador si es necesario y mantenerse hidratado',
            })
        
        # Condiciones climáticas específicas
        if 'lluvia' in condicion.lower():
            condiciones_especiales.append({
                'tipo': 'lluvia',
                'nivel': 'baja',
                'mensaje': 'Condiciones lluviosas pueden aumentar humedad y afectar desplazamientos',
                'recomendacion': 'Tomar precauciones al desplazarse y mantener medicamentos secos',
            })
        
        return condiciones_especiales
    
    @classmethod
    def _tiene_api_key(cls) -> bool:
        """Verifica si hay API key configurada"""
        api_key = cls._obtener_api_key()
        return bool(api_key and api_key.strip() and not api_key.startswith('tu_api_key'))
    
    @classmethod
    def _obtener_api_key(cls) -> str:
        """Obtiene la API key de configuración"""
        # Intentar obtener de diferentes fuentes
        api_key = getattr(settings, 'OPENWEATHERMAP_API_KEY', '')
        
        if not api_key:
            # Intentar de EXTERNAL_APIS config
            external_apis = getattr(settings, 'EXTERNAL_APIS', {})
            api_key = external_apis.get('OPENWEATHERMAP', {}).get('API_KEY', '')
        
        return api_key


# Funciones de conveniencia
def obtener_clima_ciudad(ciudad: str, pais: str = "CL", **kwargs) -> Dict:
    """
    Función de conveniencia para obtener clima
    
    Args:
        ciudad: Nombre de la ciudad
        pais: Código de país
        **kwargs: Otros parámetros para WeatherService.obtener_clima
        
    Returns:
        Dict con datos climáticos
    """
    return WeatherService.obtener_clima(ciudad, pais, **kwargs)


def obtener_pronostico_ciudad(ciudad: str, pais: str = "CL", dias: int = 3, **kwargs) -> Dict:
    """
    Función de conveniencia para obtener pronóstico
    
    Args:
        ciudad: Nombre de la ciudad
        pais: Código de país
        dias: Días de pronóstico
        **kwargs: Otros parámetros
        
    Returns:
        Dict con pronóstico
    """
    return WeatherService.obtener_pronostico(ciudad, pais, dias, **kwargs)


def es_condicion_extrema(temperatura: float, humedad: float) -> bool:
    """
    Determina si las condiciones son extremas para salud respiratoria
    
    Args:
        temperatura: Temperatura en °C
        humedad: Humedad relativa en %
        
    Returns:
        bool: True si condiciones son extremas
    """
    # Condiciones consideradas extremas
    if temperatura < 5 or temperatura > 35:
        return True
    if humedad < 20 or humedad > 85:
        return True
    return False