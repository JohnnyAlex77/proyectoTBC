-- =============================================
-- SISTEMA GESTIÓN TBC - ESQUEMA ACTUALIZADO
-- Basado en modelos Django existentes
-- =============================================

-- Crear base de datos
CREATE DATABASE IF NOT EXISTS sistema_tbc_demo 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE sistema_tbc_demo;

-- =============================================
-- TABLAS DEL SISTEMA DJANGO (MÍNIMAS)
-- =============================================

-- TABLA: auth_user (Esencial para Django)
CREATE TABLE auth_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
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
    
    INDEX idx_auth_user_username (username),
    INDEX idx_auth_user_email (email)
);

-- =============================================
-- TABLAS DEL SISTEMA TBC (ACTUALIZADAS)
-- =============================================

-- TABLA: usuarios_usuario (Modelo extendido)
CREATE TABLE usuarios_usuario (
    user_id BIGINT PRIMARY KEY,
    rut VARCHAR(15) UNIQUE NOT NULL,
    rol VARCHAR(50) NOT NULL,
    establecimiento VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NULL,
    fecha_creacion TIMESTAMP NULL,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_usuario_rut (rut),
    INDEX idx_usuario_rol (rol),
    INDEX idx_usuario_establecimiento (establecimiento),
    FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) 
        ON DELETE CASCADE
);

-- TABLA: pacientes_paciente
CREATE TABLE pacientes_paciente (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rut VARCHAR(12) UNIQUE NOT NULL,
    nombre VARCHAR(200) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    sexo VARCHAR(1) NOT NULL,
    domicilio TEXT NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    telefono VARCHAR(15) NOT NULL,
    establecimiento_salud VARCHAR(100) NOT NULL,
    fecha_diagnostico DATE NULL,
    tipo_tbc VARCHAR(50) NOT NULL,
    baciloscopia_inicial VARCHAR(50) NULL,
    cultivo_inicial VARCHAR(50) NULL,
    poblacion_prioritaria VARCHAR(100) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(50) NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_paciente_rut (rut),
    INDEX idx_paciente_estado (estado),
    INDEX idx_paciente_establecimiento (establecimiento_salud),
    INDEX idx_paciente_usuario_registro (usuario_registro_id),
    INDEX idx_paciente_fecha_diagnostico (fecha_diagnostico),
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- TABLA: contactos_contacto
CREATE TABLE contactos_contacto (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rut_contacto VARCHAR(12) NOT NULL,
    nombre_contacto VARCHAR(200) NOT NULL,
    parentesco VARCHAR(100) NOT NULL,
    tipo_contacto VARCHAR(100) NOT NULL,
    fecha_registro DATE NOT NULL,
    telefono VARCHAR(15) NULL,
    estado_estudio VARCHAR(100) NOT NULL,
    paciente_indice_id BIGINT NOT NULL,
    
    INDEX idx_contacto_rut (rut_contacto),
    INDEX idx_contacto_estado (estado_estudio),
    INDEX idx_contacto_paciente_indice (paciente_indice_id),
    INDEX idx_contacto_fecha_registro (fecha_registro),
    FOREIGN KEY (paciente_indice_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE
);

-- TABLA: tratamientos_tratamiento
CREATE TABLE tratamientos_tratamiento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    esquema VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino_estimada DATE NOT NULL,
    fecha_termino_real DATE NULL,
    peso_kg DECIMAL(5,2) NOT NULL,
    resultado_final VARCHAR(100) NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP NULL,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_tratamiento_paciente (paciente_id),
    INDEX idx_tratamiento_esquema (esquema),
    INDEX idx_tratamiento_fecha_inicio (fecha_inicio),
    INDEX idx_tratamiento_usuario_registro (usuario_registro_id),
    INDEX idx_tratamiento_estado (resultado_final),
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- TABLA: tratamientos_esquemamedicamento
CREATE TABLE tratamientos_esquemamedicamento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    medicamento VARCHAR(100) NOT NULL,
    dosis_mg INT NOT NULL,
    frecuencia VARCHAR(50) NOT NULL,
    fase VARCHAR(50) NOT NULL,
    duracion_semanas INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino DATE NOT NULL,
    
    INDEX idx_esquema_medicamento (medicamento),
    INDEX idx_esquema_fase (fase),
    INDEX idx_esquema_fechas (fecha_inicio, fecha_termino)
);

-- TABLA: tratamientos_dosisadministrada
CREATE TABLE tratamientos_dosisadministrada (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_dosis DATE NOT NULL,
    administrada BOOLEAN NOT NULL,
    hora_administracion TIME NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_administracion_id BIGINT NOT NULL,
    
    INDEX idx_dosis_fecha (fecha_dosis),
    INDEX idx_dosis_administrada (administrada),
    INDEX idx_dosis_usuario (usuario_administracion_id)
);

-- TABLA: examenes_examenbacteriologico
CREATE TABLE examenes_examenbacteriologico (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_examen VARCHAR(100) NOT NULL,
    tipo_muestra VARCHAR(100) NOT NULL,
    fecha_toma_muestra DATE NOT NULL,
    fecha_ingreso_laboratorio DATE NULL,
    fecha_resultado DATE NULL,
    resultado VARCHAR(100) NOT NULL,
    resultado_cuantitativo VARCHAR(50) NULL,
    sensibilidad VARCHAR(100) NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    fecha_solicitud DATE NOT NULL,
    laboratorio VARCHAR(200) NULL,
    numero_muestra_lab VARCHAR(100) NULL,
    observaciones_muestra TEXT NULL,
    observaciones_resultado TEXT NULL,
    otro_tipo_muestra VARCHAR(100) NULL,
    prioridad VARCHAR(20) NOT NULL,
    resistencia_estreptomicina BOOLEAN NOT NULL DEFAULT FALSE,
    resistencia_etambutol BOOLEAN NOT NULL DEFAULT FALSE,
    resistencia_fluoroquinolonas BOOLEAN NOT NULL DEFAULT FALSE,
    resistencia_isoniazida BOOLEAN NOT NULL DEFAULT FALSE,
    resistencia_pirazinamida BOOLEAN NOT NULL DEFAULT FALSE,
    resistencia_rifampicina BOOLEAN NOT NULL DEFAULT FALSE,
    resultado_cualitativo TEXT NULL,
    usuario_toma_muestra_id BIGINT NULL,
    estado_examen VARCHAR(50) NOT NULL,
    
    INDEX idx_examen_paciente (paciente_id),
    INDEX idx_examen_tipo (tipo_examen),
    INDEX idx_examen_fecha_muestra (fecha_toma_muestra),
    INDEX idx_examen_resultado (resultado),
    INDEX idx_examen_estado (estado_examen),
    INDEX idx_examen_usuario_registro (usuario_registro_id),
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT,
    FOREIGN KEY (usuario_toma_muestra_id) 
        REFERENCES auth_user(id) 
        ON DELETE SET NULL
);

-- TABLA: examenes_ppd
CREATE TABLE examenes_ppd (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_aplicacion DATE NOT NULL,
    fecha_lectura DATE NOT NULL,
    milimetro_induration INT UNSIGNED NOT NULL,
    resultado VARCHAR(50) NOT NULL,
    lugar_aplicacion VARCHAR(100) NOT NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_aplicacion_id BIGINT NULL,
    usuario_lectura_id BIGINT NULL,
    
    INDEX idx_ppd_paciente (paciente_id),
    INDEX idx_ppd_fecha_aplicacion (fecha_aplicacion),
    INDEX idx_ppd_resultado (resultado),
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_aplicacion_id) 
        REFERENCES auth_user(id) 
        ON DELETE SET NULL,
    FOREIGN KEY (usuario_lectura_id) 
        REFERENCES auth_user(id) 
        ON DELETE SET NULL
);

-- TABLA: examenes_radiologicos
CREATE TABLE examenes_radiologicos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_radiografia VARCHAR(50) NOT NULL,
    fecha_examen DATE NOT NULL,
    hallazgos VARCHAR(50) NOT NULL,
    descripcion_hallazgos TEXT NOT NULL,
    localizacion_lesiones VARCHAR(200) NULL,
    establecimiento_realizacion VARCHAR(200) NOT NULL,
    numero_informe VARCHAR(100) NULL,
    observaciones TEXT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_radiologico_paciente (paciente_id),
    INDEX idx_radiologico_tipo (tipo_radiografia),
    INDEX idx_radiologico_fecha (fecha_examen),
    INDEX idx_radiologico_hallazgos (hallazgos),
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- TABLA: prevencion_quimioprofilaxis
CREATE TABLE prevencion_quimioprofilaxis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_paciente VARCHAR(10) NOT NULL,
    medicamento VARCHAR(20) NOT NULL,
    dosis VARCHAR(100) NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_termino_prevista DATE NOT NULL,
    fecha_termino_real DATE NULL,
    esquema VARCHAR(50) NOT NULL,
    adherencia_porcentaje INT NOT NULL,
    efectos_adversos TEXT NOT NULL,
    estado VARCHAR(15) NOT NULL,
    observaciones TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    contacto_id BIGINT NULL,
    paciente_id BIGINT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_quimio_tipo (tipo_paciente),
    INDEX idx_quimio_estado (estado),
    INDEX idx_quimio_contacto (contacto_id),
    INDEX idx_quimio_paciente (paciente_id),
    INDEX idx_quimio_fecha_inicio (fecha_inicio),
    CHECK (contacto_id IS NOT NULL OR paciente_id IS NOT NULL),
    FOREIGN KEY (contacto_id) 
        REFERENCES contactos_contacto(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- TABLA: prevencion_vacunacion_bcg
CREATE TABLE prevencion_vacunacion_bcg (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_vacunacion DATE NOT NULL,
    lote VARCHAR(50) NOT NULL,
    establecimiento VARCHAR(200) NOT NULL,
    reaccion VARCHAR(10) NOT NULL,
    observaciones_reaccion TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paciente_id BIGINT NOT NULL,
    usuario_registro_id BIGINT NOT NULL,
    
    INDEX idx_vacunacion_paciente (paciente_id),
    INDEX idx_vacunacion_fecha (fecha_vacunacion),
    INDEX idx_vacunacion_reaccion (reaccion),
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- TABLA: prevencion_seguimiento
CREATE TABLE prevencion_seguimiento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo_seguimiento VARCHAR(20) NOT NULL,
    fecha_seguimiento DATE NOT NULL,
    resultado TEXT NOT NULL,
    observaciones TEXT NOT NULL,
    proximo_control DATE NULL,
    quimioprofilaxis_id BIGINT NULL,
    usuario_registro_id BIGINT NOT NULL,
    vacunacion_id BIGINT NULL,
    
    INDEX idx_seguimiento_tipo (tipo_seguimiento),
    INDEX idx_seguimiento_fecha (fecha_seguimiento),
    INDEX idx_seguimiento_quimio (quimioprofilaxis_id),
    INDEX idx_seguimiento_vacunacion (vacunacion_id),
    CHECK (quimioprofilaxis_id IS NOT NULL OR vacunacion_id IS NOT NULL),
    FOREIGN KEY (quimioprofilaxis_id) 
        REFERENCES prevencion_quimioprofilaxis(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (vacunacion_id) 
        REFERENCES prevencion_vacunacion_bcg(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_registro_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- =============================================
-- MÓDULO LABORATORIO
-- =============================================

-- TABLA: laboratorio_red_laboratorios
CREATE TABLE laboratorio_red_laboratorios (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    tipo VARCHAR(3) NOT NULL,
    direccion VARCHAR(300) NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    responsable VARCHAR(200) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_lab_nombre (nombre),
    INDEX idx_lab_tipo (tipo),
    INDEX idx_lab_comuna (comuna),
    INDEX idx_lab_activo (activo)
);

-- TABLA: laboratorio_control_calidad
CREATE TABLE laboratorio_control_calidad (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_control DATE NOT NULL,
    tipo_control VARCHAR(20) NOT NULL,
    resultado VARCHAR(15) NOT NULL,
    observaciones TEXT NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    usuario_responsable_id BIGINT NOT NULL,
    laboratorio_id BIGINT NOT NULL,
    
    INDEX idx_control_fecha (fecha_control),
    INDEX idx_control_resultado (resultado),
    INDEX idx_control_laboratorio (laboratorio_id),
    FOREIGN KEY (usuario_responsable_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT,
    FOREIGN KEY (laboratorio_id) 
        REFERENCES laboratorio_red_laboratorios(id) 
        ON DELETE CASCADE
);

-- TABLA: laboratorio_indicadores
CREATE TABLE laboratorio_indicadores (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    periodo VARCHAR(7) NOT NULL,
    muestras_recibidas INT NOT NULL,
    muestras_procesadas INT NOT NULL,
    positivos INT NOT NULL,
    contaminacion_porcentaje DECIMAL(5,2) NOT NULL,
    tiempo_respuesta_promedio DECIMAL(5,2) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    laboratorio_id BIGINT NOT NULL,
    
    UNIQUE KEY unique_lab_periodo (laboratorio_id, periodo),
    INDEX idx_ind_lab_periodo (laboratorio_id, periodo),
    INDEX idx_ind_periodo (periodo),
    FOREIGN KEY (laboratorio_id) 
        REFERENCES laboratorio_red_laboratorios(id) 
        ON DELETE CASCADE
);

-- TABLA: laboratorio_tarjetero
CREATE TABLE laboratorio_tarjetero (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    fecha_deteccion DATE NOT NULL,
    tipo_muestra VARCHAR(20) NOT NULL,
    resultado VARCHAR(100) NOT NULL,
    fecha_notificacion DATE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    examen_id BIGINT NOT NULL,
    laboratorio_referencia_id BIGINT NOT NULL,
    paciente_id BIGINT NOT NULL,
    usuario_notificador_id BIGINT NOT NULL,
    
    INDEX idx_tarjetero_paciente (paciente_id),
    INDEX idx_tarjetero_examen (examen_id),
    INDEX idx_tarjetero_fecha_deteccion (fecha_deteccion),
    INDEX idx_tarjetero_laboratorio (laboratorio_referencia_id),
    FOREIGN KEY (examen_id) 
        REFERENCES examenes_examenbacteriologico(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (laboratorio_referencia_id) 
        REFERENCES laboratorio_red_laboratorios(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (paciente_id) 
        REFERENCES pacientes_paciente(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (usuario_notificador_id) 
        REFERENCES auth_user(id) 
        ON DELETE RESTRICT
);

-- =============================================
-- MÓDULO INDICADORES
-- =============================================

-- TABLA: indicadores_establecimiento
CREATE TABLE indicadores_establecimiento (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    region VARCHAR(100) NOT NULL,
    
    INDEX idx_estab_codigo (codigo),
    INDEX idx_estab_tipo (tipo),
    INDEX idx_estab_region (region)
);

-- TABLA: indicadores_indicadorescohorte
CREATE TABLE indicadores_indicadorescohorte (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    año INT NOT NULL,
    trimestre VARCHAR(2) NOT NULL,
    casos_nuevos INT NOT NULL DEFAULT 0,
    casos_retratamiento INT NOT NULL DEFAULT 0,
    curados INT NOT NULL DEFAULT 0,
    abandonos INT NOT NULL DEFAULT 0,
    fallecidos INT NOT NULL DEFAULT 0,
    fracasos INT NOT NULL DEFAULT 0,
    trasladados INT NOT NULL DEFAULT 0,
    establecimiento_id BIGINT NOT NULL,
    
    UNIQUE KEY unique_cohorte_periodo (año, trimestre, establecimiento_id),
    INDEX idx_cohorte_establecimiento (establecimiento_id),
    INDEX idx_cohorte_periodo (año, trimestre),
    FOREIGN KEY (establecimiento_id) 
        REFERENCES indicadores_establecimiento(id) 
        ON DELETE CASCADE
);

-- TABLA: indicadores_indicadoresoperacionales
CREATE TABLE indicadores_indicadoresoperacionales (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    periodo DATE NOT NULL,
    sintomaticos_respiratorios INT NOT NULL DEFAULT 0,
    baciloscopias_realizadas INT NOT NULL DEFAULT 0,
    casos_tb_encontrados INT NOT NULL DEFAULT 0,
    contactos_identificados INT NOT NULL DEFAULT 0,
    contactos_estudiados INT NOT NULL DEFAULT 0,
    pacientes_taes INT NOT NULL DEFAULT 0,
    pacientes_adherentes INT NOT NULL DEFAULT 0,
    tiempo_promedio_diagnostico INT NOT NULL DEFAULT 0,
    establecimiento_id BIGINT NOT NULL,
    
    UNIQUE KEY unique_operacional_periodo (establecimiento_id, periodo),
    INDEX idx_operacional_establecimiento (establecimiento_id),
    INDEX idx_operacional_periodo (periodo),
    FOREIGN KEY (establecimiento_id) 
        REFERENCES indicadores_establecimiento(id) 
        ON DELETE CASCADE
);

-- TABLA: indicadores_indicadoresprevencion
CREATE TABLE indicadores_indicadoresprevencion (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    periodo DATE NOT NULL,
    contactos_elegibles_qp INT NOT NULL DEFAULT 0,
    contactos_iniciados_qp INT NOT NULL DEFAULT 0,
    contactos_completados_qp INT NOT NULL DEFAULT 0,
    recien_nacidos INT NOT NULL DEFAULT 0,
    recien_nacidos_vacunados INT NOT NULL DEFAULT 0,
    tiempo_promedio_inicio_qp INT NOT NULL DEFAULT 0,
    establecimiento_id BIGINT NOT NULL,
    
    INDEX idx_prevencion_establecimiento (establecimiento_id),
    INDEX idx_prevencion_periodo (periodo),
    FOREIGN KEY (establecimiento_id) 
        REFERENCES indicadores_establecimiento(id) 
        ON DELETE CASCADE
);

-- TABLA: indicadores_alerta
CREATE TABLE indicadores_alerta (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,
    nivel VARCHAR(10) NOT NULL,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_vencimiento TIMESTAMP NOT NULL,
    fecha_resolucion TIMESTAMP NULL,
    resuelta BOOLEAN NOT NULL DEFAULT FALSE,
    datos_relacionados JSON NOT NULL,
    usuario_asignado_id BIGINT NULL,
    establecimiento_id BIGINT NOT NULL,
    
    INDEX idx_alerta_tipo (tipo),
    INDEX idx_alerta_nivel (nivel),
    INDEX idx_alerta_resuelta (resuelta),
    INDEX idx_alerta_fecha_vencimiento (fecha_vencimiento),
    INDEX idx_alerta_establecimiento (establecimiento_id),
    FOREIGN KEY (usuario_asignado_id) 
        REFERENCES auth_user(id) 
        ON DELETE SET NULL,
    FOREIGN KEY (establecimiento_id) 
        REFERENCES indicadores_establecimiento(id) 
        ON DELETE CASCADE
);

-- TABLA: indicadores_reportepersonalizado
CREATE TABLE indicadores_reportepersonalizado (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT NOT NULL,
    parametros JSON NOT NULL,
    columnas_visibles JSON NOT NULL,
    filtros JSON NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    compartido BOOLEAN NOT NULL DEFAULT FALSE,
    usuario_creador_id BIGINT NOT NULL,
    
    INDEX idx_reporte_nombre (nombre),
    INDEX idx_reporte_compartido (compartido),
    INDEX idx_reporte_usuario (usuario_creador_id),
    FOREIGN KEY (usuario_creador_id) 
        REFERENCES auth_user(id) 
        ON DELETE CASCADE
);

-- TABLA: indicadores_reportepersonalizado_usuarios_compartidos
CREATE TABLE indicadores_reportepersonalizado_usuarios_compartidos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    reportepersonalizado_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    
    UNIQUE KEY unique_reporte_usuario (reportepersonalizado_id, user_id),
    INDEX idx_reporte_compartido_reporte (reportepersonalizado_id),
    INDEX idx_reporte_compartido_usuario (user_id),
    FOREIGN KEY (reportepersonalizado_id) 
        REFERENCES indicadores_reportepersonalizado(id) 
        ON DELETE CASCADE,
    FOREIGN KEY (user_id) 
        REFERENCES auth_user(id) 
        ON DELETE CASCADE
);

-- =============================================
-- VISTAS PARA REPORTES
-- =============================================

-- Vista para pacientes en tratamiento activo
CREATE VIEW v_pacientes_tratamiento_activo AS
SELECT 
    p.rut,
    p.nombre,
    p.estado as estado_paciente,
    t.esquema,
    t.fecha_inicio,
    t.fecha_termino_estimada,
    t.peso_kg,
    DATEDIFF(t.fecha_termino_estimada, CURDATE()) as dias_restantes
FROM pacientes_paciente p
INNER JOIN tratamientos_tratamiento t ON p.id = t.paciente_id
WHERE t.fecha_termino_real IS NULL 
AND t.fecha_inicio <= CURDATE()
AND t.fecha_termino_estimada >= CURDATE();

-- Vista para contactos pendientes de estudio
CREATE VIEW v_contactos_pendientes AS
SELECT 
    c.rut_contacto,
    c.nombre_contacto,
    c.parentesco,
    c.tipo_contacto,
    p.nombre as paciente_indice,
    p.rut as rut_indice,
    c.fecha_registro,
    DATEDIFF(CURDATE(), c.fecha_registro) as dias_pendiente
FROM contactos_contacto c
INNER JOIN pacientes_paciente p ON c.paciente_indice_id = p.id
WHERE c.estado_estudio = 'Pendiente';

-- Vista para indicadores resumen por establecimiento
CREATE VIEW v_indicadores_resumen AS
SELECT 
    e.nombre as establecimiento,
    e.tipo,
    e.region,
    ic.año,
    ic.trimestre,
    ic.casos_nuevos,
    ic.curados,
    ic.abandonos,
    ROUND((ic.curados / (ic.casos_nuevos + ic.casos_retratamiento)) * 100, 2) as tasa_exito,
    ROUND((ic.abandonos / (ic.casos_nuevos + ic.casos_retratamiento)) * 100, 2) as tasa_abandono
FROM indicadores_indicadorescohorte ic
INNER JOIN indicadores_establecimiento e ON ic.establecimiento_id = e.id
WHERE ic.año = YEAR(CURDATE());

-- Vista para alertas activas
CREATE VIEW v_alertas_activas AS
SELECT 
    a.tipo,
    a.nivel,
    a.titulo,
    a.descripcion,
    e.nombre as establecimiento,
    CONCAT(u.first_name, ' ', u.last_name) as usuario_asignado,
    a.fecha_vencimiento,
    DATEDIFF(a.fecha_vencimiento, CURDATE()) as dias_para_vencer
FROM indicadores_alerta a
INNER JOIN indicadores_establecimiento e ON a.establecimiento_id = e.id
LEFT JOIN auth_user u ON a.usuario_asignado_id = u.id
WHERE a.resuelta = FALSE
AND a.fecha_vencimiento >= CURDATE();

-- =============================================
-- PROCEDIMIENTOS ALMACENADOS ÚTILES
-- =============================================

DELIMITER //

-- Procedimiento para calcular indicadores de cohorte
CREATE PROCEDURE sp_calcular_indicadores_cohorte(
    IN p_establecimiento_id BIGINT,
    IN p_año INT,
    IN p_trimestre VARCHAR(2)
)
BEGIN
    -- Este procedimiento calcularía automáticamente los indicadores
    -- Basado en los datos de pacientes y tratamientos
    -- Implementación simplificada para ejemplo
    SELECT 'Procedimiento para cálculo de indicadores' as mensaje;
END //

-- Procedimiento para generar alertas automáticas
CREATE PROCEDURE sp_generar_alertas_automaticas()
BEGIN
    -- Alertas para tratamientos próximos a vencer
    INSERT INTO indicadores_alerta (tipo, nivel, titulo, descripcion, fecha_vencimiento, datos_relacionados, establecimiento_id)
    SELECT 
        'VENCIMIENTO',
        'ALTA',
        'Tratamiento próximo a vencer',
        CONCAT('El tratamiento de ', p.nombre, ' vence en ', DATEDIFF(t.fecha_termino_estimada, CURDATE()), ' días'),
        DATE_ADD(CURDATE(), INTERVAL 7 DAY),
        JSON_OBJECT('paciente_id', p.id, 'tratamiento_id', t.id, 'tipo_objeto', 'tratamiento'),
        1  -- Establecimiento por defecto
    FROM tratamientos_tratamiento t
    INNER JOIN pacientes_paciente p ON t.paciente_id = p.id
    WHERE t.fecha_termino_real IS NULL
    AND DATEDIFF(t.fecha_termino_estimada, CURDATE()) BETWEEN 1 AND 7
    AND NOT EXISTS (
        SELECT 1 FROM indicadores_alerta a 
        WHERE a.datos_relacionados->>'$.tratamiento_id' = t.id 
        AND a.tipo = 'VENCIMIENTO' 
        AND a.resuelta = FALSE
    );
END //

DELIMITER ;

-- =============================================
-- TRIGGERS PARA MANTENER INTEGRIDAD
-- =============================================

DELIMITER //

-- Trigger para actualizar fecha_actualizacion en usuarios_usuario
CREATE TRIGGER tg_usuarios_actualizacion 
BEFORE UPDATE ON usuarios_usuario
FOR EACH ROW
BEGIN
    SET NEW.fecha_actualizacion = CURRENT_TIMESTAMP;
END //

-- Trigger para crear perfil de usuario automáticamente
CREATE TRIGGER tg_crear_perfil_usuario 
AFTER INSERT ON auth_user
FOR EACH ROW
BEGIN
    INSERT INTO usuarios_usuario (
        user_id, 
        rut, 
        rol, 
        establecimiento, 
        telefono, 
        fecha_creacion
    ) VALUES (
        NEW.id,
        CONCAT('temp-', NEW.username),
        'enfermera',
        'Sin asignar',
        '',
        CURRENT_TIMESTAMP
    );
END //

DELIMITER ;