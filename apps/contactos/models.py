from django.db import models

class ContactosContacto(models.Model):
    # Opciones para parentesco
    PARENTESCO_OPCIONES = [
        ('', 'Seleccione parentesco'),
        ('esposo_esposa', 'Esposo/a'),
        ('hijo_hija', 'Hijo/a'),
        ('padre_madre', 'Padre/Madre'),
        ('hermano_hermana', 'Hermano/a'),
        ('abuelo_abuela', 'Abuelo/a'),
        ('nieto_nieta', 'Nieto/a'),
        ('tio_tia', 'Tío/a'),
        ('sobrino_sobrina', 'Sobrino/a'),
        ('primo_prima', 'Primo/a'),
        ('cuñado_cuñada', 'Cuñado/a'),
        ('suegro_suegra', 'Suegro/a'),
        ('yerno_nuera', 'Yerno/Nuera'),
        ('otro_familiar', 'Otro Familiar'),
        ('no_familiar', 'No Familiar'),
        ('vecino', 'Vecino'),
        ('compañero_trabajo', 'Compañero de Trabajo'),
        ('compañero_estudio', 'Compañero de Estudio'),
        ('otro', 'Otro'),
    ]
    
    # Opciones para tipo de contacto
    TIPO_CONTACTO_OPCIONES = [
        ('', 'Seleccione tipo de contacto'),
        ('intradomiciliario', 'Intradomiciliario'),
        ('extradomiciliario', 'Extradomiciliario'),
        ('laboral', 'Laboral'),
        ('escolar', 'Escolar'),
        ('social', 'Social'),
        ('otro', 'Otro'),
    ]
    
    # Opciones para estado del estudio
    ESTADO_ESTUDIO_OPCIONES = [
        ('', 'Seleccione estado'),
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completado', 'Completado'),
        ('rechazado', 'Rechazado'),
        ('no_aplica', 'No Aplica'),
    ]

    id = models.BigAutoField(primary_key=True)
    rut_contacto = models.CharField(max_length=12)
    nombre_contacto = models.CharField(max_length=200)
    parentesco = models.CharField(
        max_length=100, 
        choices=PARENTESCO_OPCIONES,
        default=''
    )
    tipo_contacto = models.CharField(
        max_length=100, 
        choices=TIPO_CONTACTO_OPCIONES,
        default=''
    )
    fecha_registro = models.DateField()
    telefono = models.CharField(max_length=15, blank=True, null=True)
    estado_estudio = models.CharField(
        max_length=100, 
        choices=ESTADO_ESTUDIO_OPCIONES,
        default='pendiente'
    )
    
    paciente_indice = models.ForeignKey(
        'pacientes.PacientesPaciente',
        on_delete=models.CASCADE,
        db_column='paciente_indice_id'
    )
    
    class Meta:
        db_table = 'contactos_contacto'
    
    def __str__(self):
        return f"{self.nombre_contacto} ({self.rut_contacto})"