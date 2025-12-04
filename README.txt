# Sistema TBC - Gestión Clínico-Epidemiológica

## Características Principales

### Módulos Implementados
- **Pacientes**: Ficha epidemiológica completa
- **Tratamientos**: Esquemas TAES con validación
- **Exámenes**: Flujo laboratorio completo
- **Contactos**: Estudio de contactos epidemiológico
- **Prevención**: Quimioprofilaxis y vacunación BCG
- **Laboratorio**: Red de laboratorios con control calidad
- **Indicadores**: Dashboards en tiempo real
- **Usuarios**: Gestión de 5 roles con permisos granulares

### API REST Completa (11 Endpoints)

GET    /api/pacientes/          # Listar pacientes (paginado)
POST   /api/pacientes/          # Crear paciente
GET    /api/tratamientos/       # Gestión tratamientos
GET    /api/dashboard/          # Estadísticas en tiempo real
GET    /api/external/clima/     # API clima externa
POST   /api/auth/token/         # Autenticación JWT
GET    /api/docs/               # Documentación Swagger

### Sistema de Seguridad
Autenticación dual: Sesiones web + Tokens JWT para API
5 roles de usuario: Admin, Médico, Enfermera, Tecnólogo, Paramédico
Permisos granulares: Por establecimiento y por acción
Control de acceso: Matriz completa por endpoint

### Instalación Rápida
1. Clonar repositorio
git clone https://github.com/JohnnyAlex77/proyectoTBC.git
cd sistema-tbc

2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

3. Instalar dependencias
pip install -r requirements.txt

4. Configurar base de datos MySQL
Crear base de datos sistema_tbc

Copiar archivo de configuración:
cp .env.example .env
Editar .env con tus credenciales MySQL

5. Aplicar migraciones
python manage.py migrate

6. Crear grupos y usuarios iniciales
python scripts/load_test_data.py

7. Iniciar servidor
python manage.py runserver

8. Acceder al sistema
Interfaz web: http://localhost:8000/

API Swagger: http://localhost:8000/api/docs/

API Redoc: http://localhost:8000/api/redoc/

Credenciales de Prueba
Rol	Usuario	Contraseña	Permisos
Administrador	admin	AdminTBC2024!	Acceso total
Médico	medico	MedicoTBC2024!	CRUD pacientes/tratamientos
Enfermera	enfermera	EnfermeraTBC2024!	Ver/editar pacientes
Tecnólogo	tecnologo	TecnologoTBC2024!	Solo lectura
Paramédico	paramedico	ParamedicoTBC2024!	Registro básico
