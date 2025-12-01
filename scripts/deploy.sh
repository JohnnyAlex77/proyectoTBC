#!/bin/bash
# scripts/deploy.sh
# Script para despliegue automático del Sistema TBC API

echo "========================================="
echo "  DEPLOY SISTEMA TBC API - EVALUACIÓN 4  "
echo "========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 1. Verificar dependencias
echo "1. Verificando dependencias..."
if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado"
    exit 1
fi
print_status "Python3 encontrado: $(python3 --version)"

if ! command -v pip &> /dev/null; then
    print_error "pip no está instalado"
    exit 1
fi
print_status "pip encontrado: $(pip --version)"

# 2. Verificar entorno virtual
echo ""
echo "2. Configurando entorno virtual..."
if [ ! -d "venv" ]; then
    print_warning "Creando entorno virtual..."
    python3 -m venv venv
    print_status "Entorno virtual creado"
fi

# Activar entorno virtual
source venv/bin/activate
print_status "Entorno virtual activado"

# 3. Instalar/actualizar dependencias
echo ""
echo "3. Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
print_status "Dependencias instaladas"

# 4. Verificar configuración
echo ""
echo "4. Verificando configuración..."
if [ ! -f "sistemaTBC/settings/local.py" ]; then
    print_warning "Creando configuración local..."
    cp sistemaTBC/settings/local.example.py sistemaTBC/settings/local.py
    print_status "Configuración local creada (editar según necesidad)"
fi

# 5. Aplicar migraciones
echo ""
echo "5. Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate
print_status "Migraciones aplicadas"

# 6. Crear superusuario si no existe
echo ""
echo "6. Configurando superusuario..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

# Crear superusuario si no existe
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@sistematbc.cl',
        password='AdminTBC2024!'
    )
    print("Superusuario creado:")
    print("  Usuario: admin")
    print("  Email: admin@sistematbc.cl")
    print("  Contraseña: AdminTBC2024!")
else:
    print("Superusuario ya existe")
EOF

# 7. Cargar datos de prueba
echo ""
echo "7. Cargando datos de prueba..."
if [ -f "scripts/load_test_data.py" ]; then
    python manage.py shell < scripts/load_test_data.py
    print_status "Datos de prueba cargados"
else
    print_warning "Script de datos de prueba no encontrado"
fi

# 8. Colectar archivos estáticos
echo ""
echo "8. Colectando archivos estáticos..."
python manage.py collectstatic --noinput
print_status "Archivos estáticos recolectados"

# 9. Ejecutar tests
echo ""
echo "9. Ejecutando tests..."
if [ -f "scripts/test_apis.py" ]; then
    python manage.py test api.tests
    print_status "Tests completados"
else
    print_warning "Tests no configurados"
fi

# 10. Iniciar servidor de desarrollo
echo ""
echo "========================================="
echo "  SISTEMA TBC API LISTO PARA USAR        "
echo "========================================="
echo ""
echo -e "${GREEN}URLs disponibles:${NC}"
echo "  • API REST: http://localhost:8000/api/"
echo "  • Admin: http://localhost:8000/admin/"
echo "  • Dashboard API: http://localhost:8000/api/dashboard/"
echo "  • Documentación: http://localhost:8000/api/docs/"
echo ""
echo -e "${GREEN}Credenciales de prueba:${NC}"
echo "  • Superusuario: admin / AdminTBC2024!"
echo "  • Médico: medico / MedicoTBC2024!"
echo "  • Enfermera: enfermera / EnfermeraTBC2024!"
echo ""
echo -e "${YELLOW}Para detener el servidor: Ctrl+C${NC}"
echo ""

# Iniciar servidor
python manage.py runserver