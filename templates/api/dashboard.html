<!-- templates/api/dashboard.html -->
{% extends 'base.html' %}
{% load static %}

{% block title %}Dashboard API - Sistema TBC{% endblock %}

{% block extra_css %}
<style>
.api-card {
    transition: transform 0.3s;
    border: 1px solid #dee2e6;
}
.api-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.1);
}
.api-endpoint {
    font-family: 'Courier New', monospace;
    background: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
}
.result-json {
    max-height: 400px;
    overflow-y: auto;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
}
</style>
{% endblock %}

{% block content %}
<div class="container-fluid py-4">
    <!-- Encabezado -->
    <div class="row mb-4">
        <div class="col-12">
            <h1 class="display-5 fw-bold text-primary">
                <i class="fas fa-code me-2"></i>Dashboard API TBC
            </h1>
            <p class="lead">
                Interfaz para probar y visualizar las APIs del sistema de gestión de tuberculosis
            </p>
            <div class="alert alert-info">
                <i class="fas fa-info-circle me-2"></i>
                Esta página permite probar las APIs RESTful del sistema. Todas las solicitudes requieren autenticación.
            </div>
        </div>
    </div>

    <!-- Estadísticas en tiempo real -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card api-card">
                <div class="card-header bg-primary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-chart-bar me-2"></i>Estadísticas del Sistema
                    </h5>
                </div>
                <div class="card-body">
                    <div class="row" id="estadisticas-container">
                        <div class="col-12 text-center py-5">
                            <div class="spinner-border text-primary" role="status">
                                <span class="visually-hidden">Cargando...</span>
                            </div>
                            <p class="mt-2 text-muted">Cargando estadísticas del sistema...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- APIs de Gestión -->
    <div class="row mb-4">
        <div class="col-md-6">
            <div class="card api-card h-100">
                <div class="card-header bg-success text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-user-injured me-2"></i>API Pacientes
                    </h5>
                </div>
                <div class="card-body">
                    <h6>Endpoints disponibles:</h6>
                    <div class="api-endpoint">
                        <code>GET /api/pacientes/</code> - Listar pacientes
                    </div>
                    <div class="api-endpoint">
                        <code>GET /api/pacientes/{id}/</code> - Detalle de paciente
                    </div>
                    <div class="api-endpoint">
                        <code>GET /api/pacientes/estadisticas/</code> - Estadísticas
                    </div>
                    
                    <button class="btn btn-outline-success mt-3" onclick="probarApiPacientes()">
                        <i class="fas fa-play me-2"></i>Probar API
                    </button>
                    
                    <div id="pacientes-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Resultado:</h6>
                        <pre id="pacientes-json"></pre>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-6">
            <div class="card api-card h-100">
                <div class="card-header bg-info text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-pills me-2"></i>API Tratamientos
                    </h5>
                </div>
                <div class="card-body">
                    <h6>Endpoints disponibles:</h6>
                    <div class="api-endpoint">
                        <code>GET /api/tratamientos/</code> - Listar tratamientos
                    </div>
                    <div class="api-endpoint">
                        <code>GET /api/tratamientos/activos/</code> - Tratamientos activos
                    </div>
                    <div class="api-endpoint">
                        <code>GET /api/tratamientos/proximos-a-terminar/</code> - Próximos a terminar
                    </div>
                    
                    <button class="btn btn-outline-info mt-3" onclick="probarApiTratamientos()">
                        <i class="fas fa-play me-2"></i>Probar API
                    </button>
                    
                    <div id="tratamientos-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Resultado:</h6>
                        <pre id="tratamientos-json"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- APIs Externas -->
    <div class="row mb-4">
        <div class="col-md-4">
            <div class="card api-card h-100">
                <div class="card-header bg-warning text-dark">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-map-marker-alt me-2"></i>Geocodificación
                    </h5>
                </div>
                <div class="card-body">
                    <form id="geocodificar-form" onsubmit="return false;">
                        <div class="mb-3">
                            <label for="direccion" class="form-label">Dirección</label>
                            <input type="text" class="form-control" id="direccion" 
                                   placeholder="Ej: Av. Principal 123" required>
                        </div>
                        <div class="mb-3">
                            <label for="comuna" class="form-label">Comuna</label>
                            <input type="text" class="form-control" id="comuna" 
                                   placeholder="Ej: Santiago">
                        </div>
                        <button type="button" class="btn btn-warning w-100" onclick="probarGeocodificacion()">
                            <i class="fas fa-search-location me-2"></i>Geocodificar
                        </button>
                    </form>
                    
                    <div id="geocodificar-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Resultado:</h6>
                        <pre id="geocodificar-json"></pre>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card api-card h-100">
                <div class="card-header bg-secondary text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-cloud-sun me-2"></i>Clima
                    </h5>
                </div>
                <div class="card-body">
                    <form id="clima-form" onsubmit="return false;">
                        <div class="mb-3">
                            <label for="ciudad-clima" class="form-label">Ciudad</label>
                            <input type="text" class="form-control" id="ciudad-clima" 
                                   placeholder="Ej: Santiago" value="Santiago" required>
                        </div>
                        <button type="button" class="btn btn-secondary w-100" onclick="probarClima()">
                            <i class="fas fa-temperature-low me-2"></i>Obtener Clima
                        </button>
                    </form>
                    
                    <div id="clima-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Resultado:</h6>
                        <pre id="clima-json"></pre>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-4">
            <div class="card api-card h-100">
                <div class="card-header bg-danger text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-chart-line me-2"></i>Análisis Epidemiológico
                    </h5>
                </div>
                <div class="card-body">
                    <form id="analisis-form" onsubmit="return false;">
                        <div class="mb-3">
                            <label for="comuna-analisis" class="form-label">Comuna</label>
                            <input type="text" class="form-control" id="comuna-analisis" 
                                   placeholder="Ej: Puente Alto" required>
                        </div>
                        <button type="button" class="btn btn-danger w-100" onclick="probarAnalisisEpidemiologico()">
                            <i class="fas fa-virus me-2"></i>Analizar
                        </button>
                    </form>
                    
                    <div id="analisis-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Resultado:</h6>
                        <pre id="analisis-json"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Estado de APIs -->
    <div class="row">
        <div class="col-12">
            <div class="card api-card">
                <div class="card-header bg-dark text-white">
                    <h5 class="card-title mb-0">
                        <i class="fas fa-server me-2"></i>Estado del Sistema
                    </h5>
                </div>
                <div class="card-body">
                    <button class="btn btn-dark" onclick="verificarEstadoApi()">
                        <i class="fas fa-sync-alt me-2"></i>Verificar Estado
                    </button>
                    
                    <div id="estado-resultado" class="result-json mt-3" style="display: none;">
                        <h6>Estado del sistema:</h6>
                        <pre id="estado-json"></pre>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
// Obtener token CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Configurar headers para solicitudes AJAX
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
        'X-Requested-With': 'XMLHttpRequest'
    };
}

// Cargar estadísticas al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarEstadisticas();
});

// Función para cargar estadísticas del dashboard
function cargarEstadisticas() {
    fetch('/api/dashboard/estadisticas/', {
        headers: getHeaders()
    })
    .then(response => {
        if (!response.ok) throw new Error('Error en la respuesta');
        return response.json();
    })
    .then(data => {
        mostrarEstadisticas(data);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('estadisticas-container').innerHTML = 
            '<div class="alert alert-danger">Error cargando estadísticas. Verifique su autenticación.</div>';
    });
}

// Función para mostrar estadísticas en formato tarjetas
function mostrarEstadisticas(data) {
    const container = document.getElementById('estadisticas-container');
    
    const html = `
        <div class="col-md-3 mb-3">
            <div class="card text-white bg-primary">
                <div class="card-body text-center">
                    <h6 class="card-title">Total Pacientes</h6>
                    <h2 class="card-text display-6">${data.pacientes.total}</h2>
                    <small>${data.pacientes.nuevos_ultimo_mes || 0} nuevos último mes</small>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-white bg-success">
                <div class="card-body text-center">
                    <h6 class="card-title">Tratamientos Activos</h6>
                    <h2 class="card-text display-6">${data.tratamientos.activos || 0}</h2>
                    <small>${data.tratamientos.completados || 0} completados</small>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-white bg-info">
                <div class="card-body text-center">
                    <h6 class="card-title">Exámenes</h6>
                    <h2 class="card-text display-6">${data.examenes.total || 0}</h2>
                    <small>${data.examenes.positivos || 0} positivos</small>
                </div>
            </div>
        </div>
        <div class="col-md-3 mb-3">
            <div class="card text-white bg-warning">
                <div class="card-body text-center">
                    <h6 class="card-title">Contactos</h6>
                    <h2 class="card-text display-6">${data.contactos.total || 0}</h2>
                    <small>${data.contactos.estudiados || 0} estudiados</small>
                </div>
            </div>
        </div>
        <div class="col-12 mt-2">
            <small class="text-muted">
                <i class="fas fa-clock me-1"></i> Actualizado: ${new Date().toLocaleString()}
            </small>
        </div>
    `;
    
    container.innerHTML = html;
}

// Función para probar API de pacientes
function probarApiPacientes() {
    fetch('/api/pacientes/', {
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('pacientes-resultado');
        const jsonElement = document.getElementById('pacientes-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        // Resaltar sintaxis
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al obtener pacientes: ' + error.message);
    });
}

// Función para probar API de tratamientos
function probarApiTratamientos() {
    fetch('/api/tratamientos/activos/', {
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('tratamientos-resultado');
        const jsonElement = document.getElementById('tratamientos-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al obtener tratamientos: ' + error.message);
    });
}

// Función para probar geocodificación
function probarGeocodificacion() {
    const direccion = document.getElementById('direccion').value;
    const comuna = document.getElementById('comuna').value;
    
    if (!direccion) {
        alert('Por favor ingrese una dirección');
        return;
    }
    
    fetch('/api/external/geocodificar/', {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify({
            direccion: direccion,
            comuna: comuna,
            pais: 'Chile'
        })
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('geocodificar-resultado');
        const jsonElement = document.getElementById('geocodificar-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error en geocodificación: ' + error.message);
    });
}

// Función para probar clima
function probarClima() {
    const ciudad = document.getElementById('ciudad-clima').value;
    
    if (!ciudad) {
        alert('Por favor ingrese una ciudad');
        return;
    }
    
    fetch('/api/external/clima/?ciudad=' + encodeURIComponent(ciudad), {
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('clima-resultado');
        const jsonElement = document.getElementById('clima-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al obtener clima: ' + error.message);
    });
}

// Función para probar análisis epidemiológico
function probarAnalisisEpidemiologico() {
    const comuna = document.getElementById('comuna-analisis').value;
    
    if (!comuna) {
        alert('Por favor ingrese una comuna');
        return;
    }
    
    fetch('/api/external/analisis-epidemiologico/?comuna=' + encodeURIComponent(comuna), {
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('analisis-resultado');
        const jsonElement = document.getElementById('analisis-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error en análisis epidemiológico: ' + error.message);
    });
}

// Función para verificar estado de la API
function verificarEstadoApi() {
    fetch('/api/status/', {
        headers: getHeaders()
    })
    .then(response => response.json())
    .then(data => {
        const resultado = document.getElementById('estado-resultado');
        const jsonElement = document.getElementById('estado-json');
        
        jsonElement.textContent = JSON.stringify(data, null, 2);
        resultado.style.display = 'block';
        
        hljs.highlightElement(jsonElement);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al verificar estado: ' + error.message);
    });
}
</script>

<!-- Incluir highlight.js para resaltar JSON -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/highlight.min.js"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.8.0/styles/github.min.css">
<script>hljs.highlightAll();</script>
{% endblock %}