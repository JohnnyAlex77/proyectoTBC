-- SISTEMA GESTIÓN TBC - ESQUEMA BASE DE DATOS

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sistema_tbc 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE sistema_tbc;

-- TABLA: USUARIOS_USUARIO
CREATE TABLE USUARIOS_USUARIO (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) NOT NULL DEFAULT '',
    last_name VARCHAR(150) NOT NULL DEFAULT '',
    email VARCHAR(254) NOT NULL DEFAULT '',
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rut VARCHAR(12) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL,
    establecimiento VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL DEFAULT '',
    
    INDEX idx_usuario_username (username),
    INDEX idx_usuario_rut (rut),
    INDEX idx_usuario_rol (rol)
);

-- TABLA: PACIENTES_PACIENTE

CREATE TABLE PACIENTES_PACIENTE (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo VARCHAR(1) NOT NULL CHECK (sexo IN ('M', 'F')),
    domicilio TEXT NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    establecimiento_salud VARCHAR(100) NOT NULL,
    fecha_diagnostico DATE NULL,
    tipo_tbc VARCHAR(50) NOT NULL DEFAULT 'Pulmonar',
    baciloscopia_inicial VARCHAR(50) NULL,
    cultivo_inicial VARCHAR(50) NULL,
    poblacion_prioritaria VARCHAR(100) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) NOT NULL DEFAULT 'Sospechoso',
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_paciente_rut (rut),
    INDEX idx_paciente_estado (estado),
    INDEX idx_paciente_establecimiento (establecimiento_salud),
    INDEX idx_paciente_usuario_registro (usuario_registro_id),
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- TABLA: TRATAMIENTOS_TRATAMIENTO
CREATE TABLE TRATAMIENTOS_TRATAMIENTO (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    esquema VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino_estimada DATE NOT NULL,
    fecha_termino_real DATE NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    resultado_final VARCHAR(100) NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_tratamiento_paciente (paciente_id),
    INDEX idx_tratamiento_esquema (esquema),
    INDEX idx_tratamiento_fecha_inicio (fecha_inicio),
    INDEX idx_tratamiento_usuario_registro (usuario_registro_id),
    FOREIGN KEY (paciente_id) 
        REFERENCES PACIENTES_PACIENTE(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- TABLA: TRATAMIENTOS_ESQUEMAMEDICAMENTO
CREATE TABLE TRATAMIENTOS_ESQUEMAMEDICAMENTO (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    medicamento VARCHAR(100) NOT NULL,
    dosis_mg INT NOT NULL,
    frecuencia VARCHAR(50) NOT NULL,
    fase VARCHAR(50) NOT NULL,
    duracion_semanas INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE NOT NULL,
    tratamiento_id BIGINT NOT NULL,
    
    INDEX idx_esquema_tratamiento (tratamiento_id),
    INDEX idx_esquema_medicamento (medicamento),
    INDEX idx_esquema_fechas (fecha_inicio, fecha_termino),
    FOREIGN KEY (tratamiento_id) 
        REFERENCES TRATAMIENTOS_TRATAMIENTO(id) 
        ON DELETE CASCADE
);

-- TABLA: TRATAMIENTOS_DOSISADMINISTRADA
CREATE TABLE TRATAMIENTOS_DOSISADMINISTRADA (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_dosis DATE NOT NULL,
    administrada BOOLEAN NOT NULL DEFAULT FALSE,
    hora_administracion TIME NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    esquema_medicamento_id BIGINT NOT NULL,
    usuario_administracion_id BIGINT NOT NULL,
    
    INDEX idx_dosis_esquema (esquema_medicamento_id),
    INDEX idx_dosis_fecha (fecha_dosis),
    INDEX idx_dosis_administrada (administrada),
    INDEX idx_dosis_usuario (usuario_administracion_id),
    UNIQUE KEY unique_dosis_por_dia (esquema_medicamento_id, fecha_dosis),
    FOREIGN KEY (esquema_medicamento_id) 
        REFERENCES TRATAMIENTOS_ESQUEMAMEDICAMENTO(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_administracion_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- TABLA: EXAMENES_EXAMENBACTERIOLOGICO
CREATE TABLE EXAMENES_EXAMENBACTERIOLOGICO (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_examen VARCHAR(100) NOT NULL,
    tipo_muestra VARCHAR(100) NOT NULL,
    fecha_muestra DATE NOT NULL,
    fecha_resultado DATE NULL,
    resultado VARCHAR(100) NULL,
    resultado_cuantitativo VARCHAR(50) NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_examen_paciente (paciente_id),
    INDEX idx_examen_tipo (tipo_examen),
    INDEX idx_examen_fecha_muestra (fecha_muestra),
    INDEX idx_examen_usuario_registro (usuario_registro_id),
    FOREIGN KEY (paciente_id) 
        REFERENCES PACIENTES_PACIENTE(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- TABLA: CONTACTOS_CONTACTO
CREATE TABLE CONTACTOS_CONTACTO (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rut_contacto VARCHAR(12) NOT NULL,
    nombre_contacto VARCHAR(200) NOT NULL,
    parentesco VARCHAR(100) NOT NULL,
    tipo_contacto VARCHAR(100) NOT NULL,
    fecha_registro DATE NOT NULL,
    telefono VARCHAR(15) NULL,
    estado_estudio VARCHAR(100) NOT NULL DEFAULT 'Pendiente',
    paciente_indice_id BIGINT NOT NULL,
    
    INDEX idx_contacto_paciente_indice (paciente_indice_id),
    INDEX idx_contacto_rut (rut_contacto),
    INDEX idx_contacto_estado (estado_estudio),
    FOREIGN KEY (paciente_indice_id) 
        REFERENCES PACIENTES_PACIENTE(id) 
        ON DELETE CASCADE
);

-- TABLA: CONTACTOS_ESTUDIOCONTACTO
CREATE TABLE CONTACTOS_ESTUDIOCONTACTO (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_estudio DATE NOT NULL,
    tipo_estudio VARCHAR(100) NOT NULL,
    resultado VARCHAR(100) NULL,
    observaciones TEXT NULL,
    contacto_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_estudio_contacto (contacto_id),
    INDEX idx_estudio_fecha (fecha_estudio),
    INDEX idx_estudio_usuario (usuario_registro_id),
    FOREIGN KEY (contacto_id) 
        REFERENCES CONTACTOS_CONTACTO(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- TABLA: PREVENCION_QUIMIOPROFILAXIS
CREATE TABLE PREVENCION_QUIMIOPROFILAXIS (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    medicamento VARCHAR(100) NOT NULL,
    dosis_mg INT NOT NULL,
    frecuencia VARCHAR(50) NOT NULL,
    fecha_inicio DATE NOT NULL,
    duracion_meses INT NOT NULL,
    estado VARCHAR(50) NOT NULL DEFAULT 'Activo',
    motivo_suspension VARCHAR(200) NULL,
    paciente_id BIGINT NULL,
    contacto_id BIGINT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_quimio_paciente (paciente_id),
    INDEX idx_quimio_contacto (contacto_id),
    INDEX idx_quimio_estado (estado),
    INDEX idx_quimio_usuario (usuario_registro_id),
    CHECK (paciente_id IS NOT NULL OR contacto_id IS NOT NULL),
    FOREIGN KEY (paciente_id) 
        REFERENCES PACIENTES_PACIENTE(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (contacto_id) 
        REFERENCES CONTACTOS_CONTACTO(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES USUARIOS_USUARIO(user_id) 
        ON DELETE RESTRICT
);

-- VISTAS ÚTILES PARA REPORTES
-- Vista para pacientes en tratamiento activo
CREATE VIEW V_PACIENTES_TRATAMIENTO_ACTIVO AS
SELECT 
    p.rut,
    p.nombre,
    p.estado,
    t.esquema,
    t.fecha_inicio,
    t.fecha_termino_estimada,
    t.peso_kg
FROM PACIENTES_PACIENTE p
INNER JOIN TRATAMIENTOS_TRATAMIENTO t ON p.id = t.paciente_id
WHERE t.fecha_termino_real IS NULL 
AND t.fecha_inicio <= CURDATE()
AND t.fecha_termino_estimada >= CURDATE();

-- Vista para contactos pendientes de estudio
CREATE VIEW V_CONTACTOS_PENDIENTES AS
SELECT 
    c.rut_contacto,
    c.nombre_contacto,
    c.parentesco,
    c.tipo_contacto,
    p.nombre as paciente_indice,
    p.rut as rut_indice
FROM CONTACTOS_CONTACTO c
INNER JOIN PACIENTES_PACIENTE p ON c.paciente_indice_id = p.id
WHERE c.estado_estudio = 'Pendiente';